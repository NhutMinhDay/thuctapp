
# # TK.py
# # TK.py
# # TK.py code này ổn nhất lần cuối 11/6/2024

# from flask import Flask, Blueprint, request, jsonify
# import datetime
# from db import get_db_connection  # Import your database connection function from db.py

# # Create Flask application
# app = Flask(__name__)

# # Create Blueprint 'edit'
# edit = Blueprint('edit', __name__)


# # Lấy Danh sách sinh viên 
# @edit.route('/edit/list', methods=['GET'])
# def list_all_users():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         query = """
#             SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
#             FROM NHANVIEN
#         """
#         cursor.execute(query)
#         employees = cursor.fetchall()

#         employee_list = []
#         for employee in employees:
#             employee_data = {
#                 'id_nv': employee[0],
#                 'ma_qr': employee[1],
#                 'name': employee[2],
#                 'address': employee[3],
#                 'email': employee[4],
#                 'phone': employee[5],
#                 'gender': employee[6],
#                 'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7]
#             }
#             employee_list.append(employee_data)

#         return jsonify(employee_list), 200

#     except Exception as e:
#         app.logger.error(f"Lỗi khi lấy danh sách nhân viên: {e}")
#         return jsonify({'error': str(e)}), 500

#     finally:
#         cursor.close()
#         conn.close()

# #  lay theo id
# @edit.route('/edit/<id_nv>', methods=['GET'])
# def get_user_by_id(id_nv):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         query = """
#             SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
#             FROM NHANVIEN 
#             WHERE ID_NV = %s
#         """
#         cursor.execute(query, (id_nv,))
#         employee = cursor.fetchone()

#         if employee:
#             employee_data = {
#                 'id_nv': employee[0],
#                 'ma_qr': employee[1],
#                 'name': employee[2],
#                 'address': employee[3],
#                 'email': employee[4],
#                 'phone': employee[5],
#                 'gender': employee[6],
#                 'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7]
#             }
#             return jsonify(employee_data), 200
#         else:
#             return jsonify({'error': 'Không tìm thấy thông tin nhân viên'}), 404
#     except Exception as e:
#         app.logger.error(f"Lỗi khi lấy thông tin nhân viên: {e}")
#         return jsonify({'error': str(e)}), 500
#     finally:
#         cursor.close()
#         conn.close()



# # Sửa NV
# @edit.route('/edit/update/<id_nv>', methods=['PUT'])
# def update_user_by_id_corrected(id_nv):
#     data = request.get_json()
#     ma_qr = data.get('ma_qr')
#     ten_nv = data.get('ten_nv')
#     diachi_nv = data.get('diachi_nv')
#     email_nv = data.get('email_nv')
#     sdt_nv = data.get('sdt_nv')
#     gioitinh_nv = data.get('gioitinh_nv')
#     ngaysinh_nv = data.get('ngaysinh_nv')

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         update_query = """
#             UPDATE NHANVIEN
#             SET MA_QR = %s, TEN_NV = %s, DIACHI_NV = %s, EMAIL_NV = %s, SDT_NV = %s, GIOITINH_NV = %s, NGAYSINH_NV = %s
#             WHERE ID_NV = %s
#         """
#         cursor.execute(update_query, (ma_qr, ten_nv, diachi_nv, email_nv, sdt_nv, gioitinh_nv, ngaysinh_nv, id_nv))
#         conn.commit()

#         if cursor.rowcount > 0:
#             # Query again to get the updated employee information
#             cursor.execute("""
#                 SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
#                 FROM NHANVIEN 
#                 WHERE ID_NV = %s
#             """, (id_nv,))
#             employee = cursor.fetchone()

#             if employee:
#                 employee_data = {
#                     'id_nv': employee[0],
#                     'ma_qr': employee[1],
#                     'name': employee[2],
#                     'address': employee[3],
#                     'email': employee[4],
#                     'phone': employee[5],
#                     'gender': employee[6],
#                     'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7],

#                 }
#                 return jsonify(employee_data), 200
#         else:
#             return jsonify({'error': 'Không tìm thấy thông tin nhân viên'}), 404
#     except Exception as e:
#         conn.rollback()
#         app.logger.error(f"Lỗi khi cập nhật thông tin nhân viên: {e}")
#         return jsonify({'error': str(e)}), 500
#     finally:
#         cursor.close()
#         conn.close()






 

# # Register the 'edit' Blueprint with the Flask application
# app.register_blueprint(edit, url_prefix='/edit')

# # Run the Flask application
# if __name__ == '__main__':
#     app.run(debug=True)
















# TK.py
# TK.py
# TK.py code này ổn nhất lần cuối 11/6/2024

from flask import Flask, Blueprint, request, jsonify
import datetime
from db import get_db_connection  # Import your database connection function from db.py

# Create Flask application
app = Flask(__name__)

# Create Blueprint 'edit'
edit = Blueprint('edit', __name__)


# Lấy Danh sách sinh viên 
@edit.route('/edit/list', methods=['GET'])
def list_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
            FROM NHANVIEN
        """
        cursor.execute(query)
        employees = cursor.fetchall()

        employee_list = []
        for employee in employees:
            employee_data = {
                'id_nv': employee[0],
                'ma_qr': employee[1],
                'name': employee[2],
                'address': employee[3],
                'email': employee[4],
                'phone': employee[5],
                'gender': employee[6],
                'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7]
            }
            employee_list.append(employee_data)

        return jsonify(employee_list), 200

    except Exception as e:
        app.logger.error(f"Lỗi khi lấy danh sách nhân viên: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()















# Lấy Thông Tin Theo ID
@edit.route('/edit/<id_nv>', methods=['GET'])
def get_user_by_id(id_nv):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
            FROM NHANVIEN 
            WHERE ID_NV = %s
        """
        cursor.execute(query, (id_nv,))
        employee = cursor.fetchone()

        if employee:
            employee_data = {
                'id_nv': employee[0],
                'ma_qr': employee[1],
                'name': employee[2],
                'address': employee[3],
                'email': employee[4],
                'phone': employee[5],
                'gender': employee[6],
                'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7]
            }
            return jsonify(employee_data), 200
        else:
            return jsonify({'error': 'Không tìm thấy thông tin nhân viên'}), 404
    except Exception as e:
        app.logger.error(f"Lỗi khi lấy thông tin nhân viên: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# thêm nhân viên mới
@edit.route('/edit/user', methods=['POST'])
def add_user():
    data = request.get_json()
    id_nv = data.get('id_nv')
    ma_qr = data.get('ma_qr')
    ten_nv = data.get('ten_nv')
    diachi_nv = data.get('diachi_nv')
    email_nv = data.get('email_nv')
    sdt_nv = data.get('sdt_nv')
    gioitinh_nv = data.get('gioitinh_nv')
    ngaysinh_nv = data.get('ngaysinh_nv')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        
        insert_query = """
            INSERT INTO NHANVIEN (ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (id_nv, ma_qr, ten_nv, diachi_nv, email_nv, sdt_nv, gioitinh_nv, ngaysinh_nv))
        conn.commit()

        cursor.execute("""
            SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
            FROM NHANVIEN 
            WHERE ID_NV = %s
        """, (id_nv,))
        employee = cursor.fetchone()

        if employee:
            employee_data = {
                'id_nv': employee[0],
                'ma_qr': employee[1],
                'name': employee[2],
                'address': employee[3],
                'email': employee[4],
                'phone': employee[5],
                'gender': employee[6],
                'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7]
            }
            return jsonify(employee_data), 201
        else:
            return jsonify({'error': 'Lỗi khi lấy thông tin nhân viên sau khi chèn'}), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Lỗi khi thêm nhân viên: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# Sửa NV
@edit.route('/edit/update/<id_nv>', methods=['PUT'])
def update_user_by_id_corrected(id_nv):
    data = request.get_json()
    ma_qr = data.get('ma_qr')
    ten_nv = data.get('ten_nv')
    diachi_nv = data.get('diachi_nv')
    email_nv = data.get('email_nv')
    sdt_nv = data.get('sdt_nv')
    gioitinh_nv = data.get('gioitinh_nv')
    ngaysinh_nv = data.get('ngaysinh_nv')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        update_query = """
            UPDATE NHANVIEN
            SET MA_QR = %s, TEN_NV = %s, DIACHI_NV = %s, EMAIL_NV = %s, SDT_NV = %s, GIOITINH_NV = %s, NGAYSINH_NV = %s
            WHERE ID_NV = %s
        """
        cursor.execute(update_query, (ma_qr, ten_nv, diachi_nv, email_nv, sdt_nv, gioitinh_nv, ngaysinh_nv, id_nv))
        conn.commit()

        if cursor.rowcount > 0:
            # Query again to get the updated employee information
            cursor.execute("""
                SELECT ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV 
                FROM NHANVIEN 
                WHERE ID_NV = %s
            """, (id_nv,))
            employee = cursor.fetchone()

            if employee:
                employee_data = {
                    'id_nv': employee[0],
                    'ma_qr': employee[1],
                    'name': employee[2],
                    'address': employee[3],
                    'email': employee[4],
                    'phone': employee[5],
                    'gender': employee[6],
                    'dob': employee[7].isoformat() if isinstance(employee[7], datetime.date) else employee[7],

                }
                return jsonify(employee_data), 200
        else:
            return jsonify({'error': 'Không tìm thấy thông tin nhân viên'}), 404
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Lỗi khi cập nhật thông tin nhân viên: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()




#  Xóa NV theo Id
# @edit.route('/edit/delete/<int:search_id>', methods=['DELETE'])
# def delete_user_by_id(search_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         delete_query = """
#             DELETE FROM NHANVIEN
#             WHERE ID_NV = %s
#         """
#         cursor.execute(delete_query, (search_id,))
#         conn.commit()

#         if cursor.rowcount > 0:
#             return jsonify({'message': 'Xóa nhân viên thành công'}), 200
#         else:
#             return jsonify({'error': 'Không tìm thấy thông tin nhân viên'}), 404
#     except Exception as e:
#         conn.rollback()
#         app.logger.error(f"Lỗi khi xóa nhân viên: {e}")
#         return jsonify({'error': str(e)}), 500
#     finally:
#         cursor.close()
#         conn.close()















# Xóa NV 1 sang 0
@edit.route('/edit/updatetk/<id_nv>', methods=['PUT'])
def update_user_status(id_nv):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        update_query = """
            UPDATE TAIKHOAN_NV
            SET TRANGTHAI_TAIKHOAN = %s
            WHERE ID_NV = %s AND TRANGTHAI_TAIKHOAN = 1
        """

        cursor.execute(update_query, (request.json['trangthai'], id_nv))
        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({'message': 'Cập nhật trạng thái tài khoản thành công'}), 200
        else:
            return jsonify({'error': 'Không tìm thấy tài khoản với trạng thái 1 hoặc nhân viên không tồn tại'}), 404
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Lỗi khi cập nhật trạng thái tài khoản: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Khôi phục TK từ 0 sang 1
@edit.route('/edit/restore/<id_nv>', methods=['PUT'])
def restore_user_status(id_nv):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        restore_query = """
            UPDATE TAIKHOAN_NV
            SET TRANGTHAI_TAIKHOAN = 1
            WHERE ID_NV = %s AND TRANGTHAI_TAIKHOAN = 0
        """
        cursor.execute(restore_query, (id_nv,))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({'message': 'Khôi phục tài khoản thành công', 'new_status': 1}), 200
        else:
            return jsonify({'error': 'Không tìm thấy tài khoản để khôi phục'}), 404
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Lỗi khi khôi phục tài khoản: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

 

# Register the 'edit' Blueprint with the Flask application
app.register_blueprint(edit, url_prefix='/edit')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)

