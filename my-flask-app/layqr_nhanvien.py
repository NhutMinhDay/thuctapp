from flask import Blueprint, request, jsonify
from db import get_db_connection

layqr_nv= Blueprint('layqr_nv', __name__)

@layqr_nv.route('/scan', methods=['POST'])
def handle_scan():
    try:
        data = request.json.get("data")
        if not data:
            return jsonify({"message": "No data received"}), 400

        cleaned_data = data.strip()
        
        db = get_db_connection()
        if not db:
            return jsonify({"message": "Database connection failed"}), 500

        with db.cursor(dictionary=True) as cursor:
            query = "SELECT VT_BOTTOM, VT_TOP, VT_RIGHT, VT_LEFT, VT_BETWEEN FROM VECTO_ANH WHERE ID_NV = %s"
            cursor.execute(query, (cleaned_data,))
            result = cursor.fetchone()

        db.close()

        return (jsonify(result) if result else jsonify({"message": "No matching data found"})), 200 if result else 404
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
