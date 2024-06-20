from flask import Blueprint, request, jsonify
from flask_cors import CORS
from db import get_db_connection
import hashlib

loginmanager = Blueprint('loginmanager', __name__)
CORS(loginmanager)  # Enable CORS for this blueprint

@loginmanager.route('/loginmanager', methods=['POST'])
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
        query = "SELECT ID_ADMIN, MK, ROLE FROM admin WHERE USER = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            id_admin, stored_password, role = user
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
                        'ROLE': role,
                    }

                    return jsonify({
                        'message': 'Đăng nhập thành công',
                        'username': username,
                        'admin': admin_data,
                        'id_admin': id_admin,
                        'role': role,
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
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# app.register_blueprint(loginmanager, url_prefix='/')































# @loginmanager.route('/loginmanager', methods=['POST'])
# def login():
#     try:
#         username = request.json.get('username')
#         password = request.json.get('password')

#         db = get_db_connection()
#         cursor = db.cursor(dictionary=True)

#         # Hash password with MD5
#         hashed_password = hashlib.md5(password.encode()).hexdigest()

#         cursor.execute('SELECT * FROM ADMIN WHERE USER = %s', (username,))
#         admin = cursor.fetchone()

#         if admin and admin['MK'] == hashed_password:
#             # Đăng nhập thành công
#             del admin['MK']  # Do not return password in admin info
#             return jsonify({'success': True, 'admin': admin}), 200
#         else:
#             # Đăng nhập thất bại
#             return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500
#     finally:
#         cursor.close()
#         db.close()
