from flask import Blueprint, current_app, jsonify, request

from backend.db_connection import get_db

ben = Blueprint("ben_routes", __name__)


@ben.route("/brokers/<int:broker_id>/listings", methods=["GET"])
def get_broker_listings(broker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /ben/brokers/{broker_id}/listings")
        cursor.execute(
            """
            SELECT l.listingID,
                   l.title,
                   l.status,
                   l.availableDate,
                   l.brokerFee,
                   a.unitNumber,
                   pr.occupancyRate,
                   pr.daysOnMarket,
                   pr.viewCount,
                   pr.applicationsCount
            FROM Listing AS l
            JOIN Apartment AS a
                ON l.apartmentID = a.apartmentID
            LEFT JOIN PerformanceReport AS pr
                ON pr.apartmentID = l.apartmentID
               AND pr.brokerID = l.brokerID
            WHERE l.brokerID = %s
            ORDER BY l.availableDate, l.listingID
            """,
            (broker_id,),
        )
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving listings for broker {broker_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@ben.route("/brokers/performance", methods=["GET"])
def get_brokers_performance():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /ben/brokers/performance")
        cursor.execute(
            """
            SELECT pr.reportID,
                   pr.brokerID,
                   b.brokerName,
                   pr.apartmentID,
                   a.unitNumber,
                   pr.viewCount,
                   pr.applicationsCount,
                   pr.occupancyRate,
                   pr.daysOnMarket,
                   CASE
                       WHEN pr.viewCount >= 100 AND pr.applicationsCount >= 10 THEN 'High Interest'
                       WHEN pr.viewCount >= 60 OR pr.applicationsCount >= 5 THEN 'Moderate Interest'
                       ELSE 'Low Interest'
                   END AS interestLevel
            FROM PerformanceReport AS pr
            JOIN Broker AS b
                ON pr.brokerID = b.brokerID
            JOIN Apartment AS a
                ON pr.apartmentID = a.apartmentID
            ORDER BY pr.viewCount DESC, pr.applicationsCount DESC
            """
        )
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving performance data: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@ben.route("/brokers/<int:broker_id>/inquiries", methods=["GET"])
def get_broker_inquiries(broker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /ben/brokers/{broker_id}/inquiries")
        cursor.execute(
            """
            SELECT l.listingID,
                   l.title,
                   l.status,
                   COUNT(i.inquiryID) AS totalInquiries
            FROM Listing AS l
            LEFT JOIN Inquiry AS i
                ON i.listingID = l.listingID
            WHERE l.brokerID = %s
            GROUP BY l.listingID, l.title, l.status
            ORDER BY totalInquiries DESC, l.listingID
            """,
            (broker_id,),
        )
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving inquiries for broker {broker_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@ben.route("/brokers/workload", methods=["GET"])
def get_broker_workload():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /ben/brokers/workload")
        cursor.execute(
            """
            SELECT b.brokerID,
                   b.brokerName,
                   COUNT(l.listingID) AS totalListings
            FROM Broker AS b
            LEFT JOIN Listing AS l
                ON l.brokerID = b.brokerID
            GROUP BY b.brokerID, b.brokerName
            ORDER BY totalListings DESC, b.brokerName
            """
        )
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving broker workload: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@ben.route("/brokers/<int:broker_id>/listings/<int:listing_id>", methods=["PUT"])
def update_broker_listing(broker_id, listing_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /ben/brokers/{broker_id}/listings/{listing_id}")
        data = request.get_json(silent=True) or {}

        allowed_fields = ["title", "status", "brokerFee", "availableDate"]
        assignments = []
        params = []

        for field in allowed_fields:
            if field in data and data[field] not in (None, ""):
                assignments.append(f"{field} = %s")
                params.append(data[field])

        if not assignments:
            return jsonify({"error": "At least one editable field is required"}), 400

        params.extend([listing_id, broker_id])
        cursor.execute(
            f"""
            UPDATE Listing
            SET {", ".join(assignments)}
            WHERE listingID = %s AND brokerID = %s
            """,
            params,
        )
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Listing not found for this broker"}), 404

        return jsonify({"message": "Listing updated successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating listing {listing_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@ben.route("/brokers/<int:broker_id>/listings/<int:listing_id>", methods=["DELETE"])
def remove_broker_listing(broker_id, listing_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /ben/brokers/{broker_id}/listings/{listing_id}")
        cursor.execute(
            """
            UPDATE Listing
            SET brokerID = NULL
            WHERE listingID = %s AND brokerID = %s
            """,
            (listing_id, broker_id),
        )
        get_db().commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Listing not found for this broker"}), 404

        return jsonify({"message": "Listing removed from broker portfolio"}), 200
    except Exception as e:
        current_app.logger.error(f"Error removing listing {listing_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
