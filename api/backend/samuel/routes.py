from flask import Blueprint, jsonify, current_app, request
from backend.db_connection import get_db

samuel = Blueprint("samuel_routes", __name__)

@samuel.route('/renters/<renter_id>/preferences', methods=['GET'])
def get_renter_preferences(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET samuel//renters/{renter_id}/preferences')
        
        cursor.execute('''SELECT label, value FROM RenterPreferences
                       JOIN ApartmentFeatures features ON RenterPreferences.featureId = features.featureId
                       WHERE renterID = %s''', (renter_id,))
        
        preferences = cursor.fetchall()

        current_app.logger.info(f'Retrieved preferences for renter {renter_id}')
        return jsonify(preferences), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving preferences for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@samuel.route('/renters/<renter_id>/preferences', methods=['PUT'])
def update_renter_preferences(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /samuel/renters/{renter_id}/preferences')

        preferences = request.json

        cursor.execute('DELETE FROM RenterPreferences WHERE renterID = %s', (renter_id,))

        for key, value in preferences.items():
            # check if the feature already exists
            cursor.execute('SELECT featureId FROM ApartmentFeatures WHERE label = %s AND value = %s', (key, value))
            feature = cursor.fetchone()
            if not feature:
                cursor.execute('INSERT INTO ApartmentFeatures (label, value) VALUES (%s, %s)', (key, value))
                feature_id = cursor.lastrowid
            else:
                feature_id = feature['featureId']

            cursor.execute('INSERT INTO RenterPreferences (renterID, featureId) VALUES (%s, %s)', (renter_id, feature_id))

        get_db().commit()
        current_app.logger.info(f'Updated preferences for renter {renter_id}')
        return jsonify({"message": "Preferences updated successfully"}), 201
    except Exception as e:
        current_app.logger.error(f'Error updating preferences for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@samuel.route('/renters/<renter_id>/deal_breakers', methods=['GET'])
def get_renter_dealbreakers(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /samuel/renters/{renter_id}/dealbreakers')

        cursor.execute('''SELECT label, value FROM Dealbreakers
                       JOIN ApartmentFeatures features ON Dealbreakers.featureId = features.featureId
                       WHERE renterID = %s''', (renter_id,))

        dealbreakers = cursor.fetchall()

        current_app.logger.info(f'Retrieved dealbreakers for renter {renter_id}')
        return jsonify(dealbreakers), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving dealbreakers for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@samuel.route('/renters/<renter_id>/deal_breakers', methods=['PUT'])
def update_renter_dealbreakers(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /samuel/renters/{renter_id}/dealbreakers')

        dealbreakers = request.json

        cursor.execute('DELETE FROM Dealbreakers WHERE renterID = %s', (renter_id,))

        for key, value in dealbreakers.items():
            # check if the feature already exists
            cursor.execute('SELECT featureId FROM ApartmentFeatures WHERE label = %s AND value = %s', (key, value))
            feature = cursor.fetchone()
            if not feature:
                cursor.execute('INSERT INTO ApartmentFeatures (label, value) VALUES (%s, %s)', (key, value))
                feature_id = cursor.lastrowid
            else:
                feature_id = feature['featureId']

            cursor.execute('INSERT INTO Dealbreakers (renterID, featureId) VALUES (%s, %s)', (renter_id, feature_id))

        get_db().commit()
        current_app.logger.info(f'Updated dealbreakers for renter {renter_id}')
        return jsonify({"message": "Dealbreakers updated successfully"}), 201
    except Exception as e:
        current_app.logger.error(f'Error updating dealbreakers for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@samuel.route('/neighborhoods/<neighborhood_id>', methods=['GET'])
def get_neighborhood_info(neighborhood_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /samuel/neighborhoods/{neighborhood_id}')

        cursor.execute('SELECT neighborhoodName, neighborhoodInsights FROM Neighborhood WHERE neighborhoodID = %s', (neighborhood_id,))
        info = cursor.fetchone()

        if not info:
            return jsonify({"error": "Neighborhood not found"}), 404

        current_app.logger.info(f'Retrieved insights for neighborhood {neighborhood_id}')
        return jsonify(info), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving insights for neighborhood {neighborhood_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        
@samuel.route('/renters/<renter_id>/inquiries', methods=['GET'])
def get_renter_inquiries(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /samuel/renters/{renter_id}/inquiries')

        cursor.execute('''SELECT Inquiry.* FROM Inquiry
                       JOIN Renter ON Renter.email = Inquiry.senderEmail
                       WHERE renterID = %s''', (renter_id,))
        inquiries = cursor.fetchall()

        current_app.logger.info(f'Retrieved inquiries for renter {renter_id}')
        return jsonify(inquiries), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving inquiries for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@samuel.route('/renters/<renter_id>/inquiries', methods=['POST'])
def create_renter_inquiry(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /samuel/renters/{renter_id}/inquiries')

        data = request.json
        message = data.get('message')
        listing_id = data.get('listing_id')
        sender_name = data.get('sender_name')

        cursor.execute('SELECT email FROM Renter WHERE renterID = %s', (renter_id,))
        renter = cursor.fetchone()
        if not renter:
            return jsonify({"error": "Renter not found"}), 404
        
        sender_email = renter['email']

        cursor.execute('INSERT INTO Inquiry (senderEmail, message, listingID, senderName) VALUES (%s, %s, %s, %s)', (sender_email, message, listing_id, sender_name))
        get_db().commit()

        current_app.logger.info(f'Created inquiry for renter {renter_id}')
        return jsonify({"message": "Inquiry created successfully"}), 201
    except Exception as e:
        current_app.logger.error(f'Error creating inquiry for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        
@samuel.route('/listings/<listing_id>/images', methods=['GET'])
def get_listing_images(listing_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /samuel/listings/{listing_id}/images')

        cursor.execute('SELECT imageURL FROM ListingImage WHERE listingID = %s', (listing_id,))
        images = cursor.fetchall()

        current_app.logger.info(f'Retrieved image URLs for listing {listing_id}')
        return jsonify(images), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving images for listing {listing_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@samuel.route('/renters/<renter_id>/classmate-listings', methods=['GET'])
def get_classmate_listings(renter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /samuel/renters/{renter_id}/classmate-listings')
        
        cursor.execute('''SELECT DISTINCT Listing.* FROM Listing
                       JOIN Inquiry ON Listing.listingID = Inquiry.listingID
                       JOIN Renter ON Renter.email = Inquiry.senderEmail
                       WHERE Renter.renterID = %s''', (renter_id,))
        listings = cursor.fetchall()

        current_app.logger.info(f'Retrieved classmate listings for renter {renter_id}')
        return jsonify(listings), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving classmate listings for renter {renter_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()