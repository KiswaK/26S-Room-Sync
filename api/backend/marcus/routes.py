from flask import Blueprint, request, jsonify, make_response
from backend.db_connection import db

landlord = Blueprint('landlord', __name__)



# Get all active listings for a landlord
@landlord.route('/landlord/<int:landlord_id>/listings', methods=['GET'])
def get_landlord_listings(landlord_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT l.listingID,
               a.unitNumber,
               l.status,
               l.availableDate,
               l.brokerFee
        FROM   Listing   l
        JOIN   Apartment a ON l.apartmentID = a.apartmentID
        WHERE  l.landlordID = %s
        AND    l.status    != 'archived'
        ORDER  BY l.availableDate ASC
    ''', (landlord_id,))
    rows = cursor.fetchall()
    return make_response(jsonify(rows), 200)


# 2.1 — Post a new listing
@landlord.route('/landlord/<int:landlord_id>/listings', methods=['POST'])
def create_listing(landlord_id):
    data       = request.get_json()
    apt_id     = data['apartmentID']
    broker_id  = data.get('brokerID', None)
    avail_date = data['availableDate']
    broker_fee = data.get('brokerFee', 0.00)
    cosigner   = data.get('cosignerName', None)

    cursor = db.get_db().cursor()
    cursor.execute('''
        INSERT INTO Listing (
            apartmentID,
            landlordID,
            brokerID,
            renterID,
            availableDate,
            status,
            cosignerName,
            brokerFee
        )
        VALUES (%s, %s, %s, NULL, %s, 'available', %s, %s)
    ''', (apt_id, landlord_id, broker_id, avail_date, cosigner, broker_fee))
    db.get_db().commit()
    return make_response(jsonify({'message': 'Listing created successfully'}), 201)


# Update a listing's status (e.g. rented, available, archived)
@landlord.route('/landlord/<int:landlord_id>/listings/<int:listing_id>/status', methods=['PUT'])
def update_listing_status(landlord_id, listing_id):
    data   = request.get_json()
    status = data['status']

    cursor = db.get_db().cursor()
    cursor.execute('''
        UPDATE Listing
        SET    status = %s
        WHERE  listingID  = %s
        AND    landlordID = %s
    ''', (status, listing_id, landlord_id))
    db.get_db().commit()
    return make_response(jsonify({'message': f'Listing {listing_id} status updated to {status}'}), 200)


# Archive a listing
@landlord.route('/landlord/<int:landlord_id>/listings/<int:listing_id>', methods=['DELETE'])
def archive_listing(landlord_id, listing_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        UPDATE Listing
        SET    status = 'archived'
        WHERE  listingID  = %s
        AND    landlordID = %s
    ''', (listing_id, landlord_id))
    db.get_db().commit()
    return make_response(jsonify({'message': f'Listing {listing_id} archived'}), 200)


# Mark a listing as available again
@landlord.route('/landlord/<int:landlord_id>/listings/<int:listing_id>/reopen', methods=['PUT'])
def reopen_listing(landlord_id, listing_id):
    data       = request.get_json()
    avail_date = data.get('availableDate')

    cursor = db.get_db().cursor()
    cursor.execute('''
        UPDATE Listing
        SET    status        = 'available',
               availableDate = %s
        WHERE  listingID  = %s
        AND    landlordID = %s
    ''', (avail_date, listing_id, landlord_id))
    db.get_db().commit()
    return make_response(jsonify({'message': f'Listing {listing_id} reopened'}), 200)




# Get views and inquiry counts for all listings
@landlord.route('/landlord/<int:landlord_id>/listings/performance', methods=['GET'])
def get_listing_performance(landlord_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT l.listingID,
               a.unitNumber,
               l.status,
               pr.viewCount,
               pr.applicationsCount,
               COUNT(i.inquiryID) AS totalInquiries
        FROM   Listing           l
        JOIN   Apartment         a  ON l.apartmentID = a.apartmentID
        JOIN   PerformanceReport pr ON l.listingID   = pr.listingID
        LEFT   JOIN Inquiry      i  ON l.listingID   = i.listingID
        WHERE  l.landlordID = %s
        AND    l.status    != 'archived'
        GROUP  BY l.listingID,
                  a.unitNumber,
                  l.status,
                  pr.viewCount,
                  pr.applicationsCount
        ORDER  BY pr.viewCount DESC
    ''', (landlord_id,))
    rows = cursor.fetchall()
    return make_response(jsonify(rows), 200)


# Get performance report for a single listing
@landlord.route('/landlord/<int:landlord_id>/listings/<int:listing_id>/performance', methods=['GET'])
def get_single_listing_performance(landlord_id, listing_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT pr.reportID,
               pr.viewCount,
               pr.applicationsCount,
               pr.occupancyRate,
               pr.daysOnMarket
        FROM   PerformanceReport pr
        JOIN   Listing           l ON pr.listingID = l.listingID
        WHERE  pr.listingID = %s
        AND    l.landlordID = %s
    ''', (listing_id, landlord_id))
    row = cursor.fetchone()
    return make_response(jsonify(row), 200)


# ------------------------------------------------------------
# INQUIRIES
# ------------------------------------------------------------

# Get all inquiries for a specific listing
@landlord.route('/landlord/<int:landlord_id>/listings/<int:listing_id>/inquiries', methods=['GET'])
def get_listing_inquiries(landlord_id, listing_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT i.inquiryID,
               i.senderName,
               i.senderEmail,
               i.message,
               i.sentAt,
               i.isRead
        FROM   Inquiry i
        JOIN   Listing l ON i.listingID = l.listingID
        WHERE  i.listingID  = %s
        AND    l.landlordID = %s
        ORDER  BY i.sentAt DESC
    ''', (listing_id, landlord_id))
    rows = cursor.fetchall()
    return make_response(jsonify(rows), 200)


# 
@landlord.route('/landlord/<int:landlord_id>/inquiries/<int:inquiry_id>/read', methods=['PUT'])
def mark_inquiry_read(landlord_id, inquiry_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        UPDATE Inquiry i
        JOIN   Listing l ON i.listingID = l.listingID
        SET    i.isRead = 1
        WHERE  i.inquiryID  = %s
        AND    l.landlordID = %s
    ''', (inquiry_id, landlord_id))
    db.get_db().commit()
    return make_response(jsonify({'message': f'Inquiry {inquiry_id} marked as read'}), 200)


# Delete a specific inquiry
@landlord.route('/landlord/<int:landlord_id>/inquiries/<int:inquiry_id>', methods=['DELETE'])
def delete_inquiry(landlord_id, inquiry_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        DELETE i FROM Inquiry i
        JOIN   Listing l ON i.listingID = l.listingID
        WHERE  i.inquiryID  = %s
        AND    l.landlordID = %s
    ''', (inquiry_id, landlord_id))
    db.get_db().commit()
    return make_response(jsonify({'message': f'Inquiry {inquiry_id} deleted'}), 200)




# Get all apartments belonging to a landlord
@landlord.route('/landlord/<int:landlord_id>/apartments', methods=['GET'])
def get_landlord_apartments(landlord_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT DISTINCT a.apartmentID,
                        a.unitNumber
        FROM   Apartment a
        JOIN   Listing   l ON a.apartmentID = l.apartmentID
        WHERE  l.landlordID = %s
    ''', (landlord_id,))
    rows = cursor.fetchall()
    return make_response(jsonify(rows), 200)


# Add a new apartment unit
@landlord.route('/landlord/<int:landlord_id>/apartments', methods=['POST'])
def add_apartment(landlord_id):
    data        = request.get_json()
    unit_number = data['unitNumber']

    cursor = db.get_db().cursor()
    cursor.execute('''
        INSERT INTO Apartment (unitNumber)
        VALUES (%s)
    ''', (unit_number,))
    db.get_db().commit()
    new_id = cursor.lastrowid
    return make_response(jsonify({'message': 'Apartment added', 'apartmentID': new_id}), 201)
