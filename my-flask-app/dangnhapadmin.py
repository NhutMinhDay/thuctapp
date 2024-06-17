
from flask import Blueprint, request, jsonify
from db import get_db_connection  # Assuming you have a function to get DB connection
import hashlib  # For hashing passwords with MD5

log = Blueprint('log', __name__)

@log.route('/loginAdmin', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('user')
        password = data.get('MK')

        if not username or not password:
            return jsonify({'error': 'Username và password là bắt buộc'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # First query to get the user credentials
        query = "SELECT ID_ADMIN, MK FROM admin WHERE USER = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            id_admin, stored_password = user
            if password == stored_password:
                # Second query to get the admin details
                query = """
                    SELECT *
                    FROM admin
                    WHERE ID_ADMIN = %s
                """
                
                cursor.execute(query, (id_admin,))
                admin = cursor.fetchone()

                cursor.close()
                conn.close()

                if admin:
                    admin_data = {
                        'ID_ADMIN': admin[0],
                        'TEN_ADMIN': admin[1],
                        'USER': admin[2],
                    }

                    return jsonify({
                        'message': 'Đăng nhập thành công',
                        'username': username,
                        'admin': admin_data,
                        'id_admin': id_admin,
                    }), 200
                else:
                    return jsonify({'error': 'Không tìm thấy thông tin admin'}), 404
            else:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Username hoặc password không đúng'}), 401
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username hoặc password không đúng'}), 401
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500




