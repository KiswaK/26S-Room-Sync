from flask import Blueprint, jsonify, current_app, request
from backend.db_connection import get_db

ben = Blueprint("ben_routes", __name__)

#listings with occupancy and days on market
@ben.route('/brokers/<broker_id>/listings', methods=['GET'])
def get_broker_listings(broker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /ben/brokers/{broker_id}/listings')

        cursor.execute('''SELECT pr.reportID, pr.apartmentID, a.unitNumber,
                                 pr.occupancyRate, pr.daysOnMarket, pr.viewCount,
                                 pr.applicationsCount
                          FROM PerformanceReport pr
                          JOIN Apartment a ON pr.apartmentID = a.apartmentID
                          WHERE pr.brokerID = %s
                          ORDER BY pr.daysOnMarket DESC''', (broker_id,))
        listings = cursor.fetchall()

        current_app.logger.info(f'Retrieved listings for broker {broker_id}')
        return jsonify(listings), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving listings for broker {broker_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

#views and applications across apartments
@ben.route('/brokers/performance', methods=['GET'])
def get_brokers_performance():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /ben/brokers/performance')

        cursor.execute('''SELECT pr.brokerID, pr.apartmentID, a.unitNumber,
                                 pr.viewCount, pr.applicationsCount,
                                 pr.occupancyRate, pr.daysOnMarket,
                                 CASE
                                   WHEN pr.viewCount >= 100 AND pr.applicationsCount >= 10
                                   THEN 'High Interest'
                                   ELSE 'Low Interest'
                                 END AS interestLevel
                          FROM PerformanceReport pr
                          JOIN Apartment a ON pr.apartmentID = a.apartmentID
                          ORDER BY pr.viewCount DESC''')
        performance = cursor.fetchall()

        current_app.logger.info('Retrieved broker performance data')
        return jsonify(performance), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving broker performance: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

#inquiry counts per listing
@ben.route('/brokers/<broker_id>/inquiries', methods=['GET'])
def get_broker_inquiries(broker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /ben/brokers/{broker_id}/inquiries')

        cursor.execute('''SELECT l.listingID, a.unitNumber, l.status,
                                 COUNT(i.inquiryID) AS totalInquiries
                          FROM Listing l
                          JOIN Apartment a ON l.apartmentID = a.apartmentID
                          LEFT JOIN Inquiry i ON i.listingID = l.listingID
                          WHERE l.brokerID = %s
                          GROUP BY l.listingID, a.unitNumber, l.status
                          ORDER BY totalInquiries DESC''', (broker_id,))
        inquiries = cursor.fetchall()

        current_app.logger.info(f'Retrieved inquiries for broker {broker_id}')
        return jsonify(inquiries), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving inquiries for broker {broker_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

#listings assigned to each broker
@ben.route('/brokers/workload', methods=['GET'])
def get_broker_workload():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /ben/brokers/workload')

        cursor.execute('''SELECT b.brokerID, b.brokerName,
                                 COUNT(l.listingID) AS totalListings
                          FROM Broker b
                          LEFT JOIN Listing l ON l.brokerID = b.brokerID
                          GROUP BY b.brokerID, b.brokerName
                          ORDER BY totalListings DESC''')
        workload = cursor.fetchall()

        current_app.logger.info('Retrieved broker workload data')
        return jsonify(workload), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving broker workload: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

#update listing on behalf of landlord
@ben.route('/brokers/<broker_id>/listings/<listing_id>', methods=['PUT'])
def update_broker_listing(broker_id, listing_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /ben/brokers/{broker_id}/listings/{listing_id}')

        data = request.json
        status = data.get('status')
        broker_fee = data.get('brokerFee')
        available_date = data.get('availableDate')

        cursor.execute('''UPDATE Listing
                          SET status = COALESCE(%s, status),
                              brokerFee = COALESCE(%s, brokerFee),
                              availableDate = COALESCE(%s, availableDate)
                          WHERE listingID = %s AND brokerID = %s''',
                       (status, broker_fee, available_date, listing_id, broker_id))
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Listing not found or not assigned to this broker"}), 404

        current_app.logger.info(f'Updated listing {listing_id} for broker {broker_id}')
        return jsonify({"message": "Listing updated successfully"}), 200
    except Exception as e:
        current_app.logger.error(f'Error updating listing {listing_id} for broker {broker_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

#remove listing from broker portfolio
@ben.route('/brokers/<broker_id>/listings/<listing_id>', methods=['DELETE'])
def remove_broker_listing(broker_id, listing_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /ben/brokers/{broker_id}/listings/{listing_id}')

        cursor.execute('''UPDATE Listing
                          SET brokerID = NULL
                          WHERE listingID = %s AND brokerID = %s''',
                       (listing_id, broker_id))
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Listing not found or not assigned to this broker"}), 404

        current_app.logger.info(f'Removed listing {listing_id} from broker {broker_id} portfolio')
        return jsonify({"message": "Listing removed from portfolio"}), 200
    except Exception as e:
        current_app.logger.error(f'Error removing listing {listing_id} from broker {broker_id}: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
