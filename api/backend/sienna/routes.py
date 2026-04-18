from flask import Blueprint, jsonify, current_app, request
from backend.db_connection import get_db

sienna = Blueprint("sienna_routes", __name__)

@sienna.route('/admin/listings', methods = ['GET'])
def get_all_listings():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info(f'GET /sienna/admin/listing')

        cursor.execute('''SELECT Listing.*, 
                        Landlord.firstname AS landlordName, 
                        Broker.name AS brokerName
                       FROM Listing
                       LEFT JOIN Landlord ON Listing.landlordID = Landlord.landlordID
                       LEFT JOIN Broker ON Litsting.brokerID = Broker.brokerID''')
        listings = cursor.fetchall()

        return jsonify(listings), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving listing: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
    
@sienna.route('/admin/listings', methods = ['PUT'])
def bulk_deactivate_listings():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info(f'PUT /sienna/admind/listings')
        cursor.execute('''UPDATE listing SET status = 'inactive' 
                       WHERE status = 'available'
                       AND availableDate < DATE_SUB(NOW(), INTERVAL 90 DAY) ''')
        get_db().commit()

        return jsonify({"message": "Outdated listings marked inactive"}), 200
    except Exception as e:
        current_app.logger.error(f'Error bulk updating listings: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/landlords', methods = ['GET'])
def get_unverified_landlords():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.longer.info(f'GET /sienna/admin/landlords')
        cursor.execute('SELECT * FROM Landlord WHERE isVerified = FALSE')
        landlords = cursor.fetchall()

        return jsonify(landlords), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving unverified landloards: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/landlord/<landlord_id>', methods = ["PUT"])
def update_landloard_verified(landlord_id):
    cursor = get_db().cursor(dictionary = True)
    try:
         current_app.longer.info(f'PUT /sienna/admin/landlords/{landlord_id}')

         data = request.json
         verified = data.get('verified')

         cursor.execute('UPDATE Landlord SET isVerified = %s WHERE landlordID = %s',
                        (verified, landlord_id))
    except Exception as e:
        current_app.logger.error(f'Error updating landlord {landlord_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/users/<user_id>', methods = ['PUT'])
def suspend_user(user_id):
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info(f'PUT /sienna/admin/users/{user_id}')

        data = request.json
        status = data.get('userStatus')

        cursor.execute('UPDATE Users SET userStatus = %s WHERE userID = %s',
                       (status, user_id))
        get_db().commit()

        return jsonify({"message": f"User {user_id} status update to {status}"}), 200
    except Exception as e:
        current_app.logger.error(f'Error suspending user {user_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/reports', methods = ['GET'])
def get_all_reports():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info('GET /sienna/admin/reports')

        cursor.execute(''' SELECT Reports.*, Users.userName AS senderName
                       FROM Reports
                       JOIN Users ON Reports.senderID = Users.userID''')
        reports = cursor.fetchall()

        return jsonify(reports), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving reports: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/reports', methods = ['PUT'])
def update_report_status():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info('PUT /sienna/admin/reports')

        data = request.json
        admin_id = data.get('adminID')
        user_id = data.get('userID')
        listing_id = data.get('listingID')
        report_id = data.get('reportID')
        action_type = data.get('actionType')
        action_reason = data.get('actionReason')

        cursor.execute(''' INSERT INTO ModerationAction
                       (adminID, userID, listingID, reportID, actionType, actionReason)
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                       (admin_id, user_id, listing_id, report_id, action_type, action_reason))
        get_db().commit()

        return jsonify({"message": "Moderation action recorded"}), 200
    except Exception as e:
        current_app.logger.error(f'Error handling report action: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/moderation', methods = ['POST'])
def log_moderation_action():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info('POST /sienna/admin/moderation')

        data = request.json
        admin_id = data.get('adminID')
        user_id = data.get('userID')
        listing_id = data.get('listingID')
        report_id = data.get('reportID')
        action_type = data.get('actionType')
        action_reason = data.get('actionReason')

        cursor.execute('''INSERT INTO ModerationAction
                       (adinID, userID, listingID, reportID, acionType, actionReason)
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                       (admin_id, user_id, listing_id, report_id, action_type, action_reason))
        get_db().commit()

        return jsonify({"message": "Moderation action logged"}), 201
    except Exception as e:
        current_app.logger.error(f'Error logging moderation action: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/brokers', methods = ['GET'])
def get_all_brokers():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info('GET /sienna/admin/brokers')

        cursor.execute('SELECT brokerID, brokerName, brokerPhone, brokerEmail FROM Broker')
        brokers = cursor.fetchall()

        return jsonify(brokers), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving brokers: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@sienna.route('/admin/brokers/<broker_id>', methods = ['PUT'])
def update_broker_status(broker_id):
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info(f'PUT /sienna/admin/brokers/{broker_id}')
        
        data = request.json
        user_status = data.get('userStatus')

        cursor.execute('''UPDATE Users
                       SET userStatus = %s
                       WHERE userID = (SELECT userID FROM Broker WHERE brokerID = %s)''',
                       (user_status, broker_id))
        get_db().commit()

        return jsonify({"message": "Broker status updated"}), 200
    except Exception as e:
        current_app.logger.error(f'Error updating broker {broker_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
    