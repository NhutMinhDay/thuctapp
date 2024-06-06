from flask import Blueprint, request, jsonify
from db import get_db_connection

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username và password là bắt buộc'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # First query to get the user credentials
    query = "SELECT ID_NV, PASSWORD FROM taikhoan_nv WHERE USERNAME = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user:
        id_nv, stored_password = user
        if password == stored_password:
            # Second query to get the employee details
            query = """
                SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
                FROM NHANVIEN 
                WHERE ID_NV = %s
            """
            cursor.execute(query, (id_nv,))
            employee = cursor.fetchone()

            cursor.close()
            conn.close()

            if employee:
                employee_data = {
                    'ID_NV': employee[0],
                    'MA_QR': employee[1],
                    'TEN_NV': employee[2],
                    'DIACHI_NV': employee[3],
                    'EMAIL_NV': employee[4],
                    'SDT_NV': employee[5],
                    'GIOITINH_NV': employee[6],
                    'NGAYSINH_NV': employee[7].isoformat()  # Convert date to string
                }

                return jsonify({
                    'message': 'Đăng nhập thành công',
                    'username': username,
                    'employee': employee_data,
                    'id_nv': id_nv
                }), 200
            else:
                return jsonify({'error': 'Không tìm thấy thông tin nhân viên'}), 404
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username hoặc password không đúng'}), 401
    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Username hoặc password không đúng'}), 401
