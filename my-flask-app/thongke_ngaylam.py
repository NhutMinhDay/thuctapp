from flask import Blueprint, request, jsonify
from db import get_db_connection
import calendar
from datetime import datetime, timedelta

thongkengaylam = Blueprint("thongkengaylam", __name__)
# liệt kê danh sách điểm danh
@thongkengaylam.route("/api/thongkengaylam", methods=["GET"])
def get_qr_entries():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM qlns.thongke_diemdanh_ngay")
    entries = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(entries)

# liệt kê danh sách ngày làm tổng trong tổng các tháng(toàn bộ id_nv)
@thongkengaylam.route("/api/thongkengaylam1111", methods=["GET"])
def get_qr_111entries():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT DiemDanhID, ID_NV, NgayLam, KETQUADIEMDANH, THOIGIAN_VAO_SANG, THOIGIAN_RA_SANG, THOIGIAN_VAO_CHIEU, THOIGIAN_RA_CHIEU
        FROM THONGKE_DIEMDANH_NGAY
        WHERE KETQUADIEMDANH LIKE %s
    """,
        ("%thành công%",),
    )
    entries = cursor.fetchall()
    success_count = len(entries)
    cursor.close()
    db.close()
    return jsonify({"entries": entries, "success_count": success_count})

# http://127.0.0.1:5000/api/thongkengaylamcount/B2016984
@thongkengaylam.route('/api/thongkengaylamcount/<string:id_nv>', methods=['GET'])
def count_successful_days(id_nv):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute('''
        SELECT NV.TEN_NV, COUNT(TK.ID_NV) AS success_days_count
        FROM NHANVIEN NV
        LEFT JOIN THONGKE_DIEMDANH_NGAY TK ON NV.ID_NV = TK.ID_NV
        WHERE NV.ID_NV = %s AND TK.KETQUADIEMDANH LIKE %s
    ''', (id_nv, "%thành công%"))

    employee_data = cursor.fetchone()

    if not employee_data or not employee_data['TEN_NV']:
        cursor.close()
        db.close()
        return jsonify({"error": "Employee not found or no successful attendance days"}), 404

    cursor.execute('''
        SELECT * FROM THONGKE_DIEMDANH_NGAY
        WHERE ID_NV = %s
    ''', (id_nv,))

    attendance_records = cursor.fetchall()

    cursor.close()
    db.close()

    response = {
        "ID_NV": id_nv,
        "TEN_NV": employee_data['TEN_NV'],
        "success_days_count": employee_data['success_days_count'],
        "attendance_records": attendance_records
    }

    return jsonify(response)

# http://localhost:5000/api/monthly-attendance/4/2024
# thống kê ngày làm của nhân viên trong tất cả các tháng
@thongkengaylam.route("/api/monthly-attendance/<int:month>/<int:year>", methods=["GET"])
def get_monthly_attendance(month, year):
    try:
        # Connect to the database
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Execute the SQL query
        query = """
            SELECT ID_NV,
                   MONTH(NgayLam) AS Thang,
                   YEAR(NgayLam) AS Nam,
                   COUNT(CASE WHEN KETQUADIEMDANH LIKE '%thành công%' THEN 1 ELSE NULL END) AS SoNgayLam,
                   COUNT(*) AS TongNgay
            FROM THONGKE_DIEMDANH_NGAY
            WHERE MONTH(NgayLam) = %s AND YEAR(NgayLam) = %s
            GROUP BY ID_NV, MONTH(NgayLam), YEAR(NgayLam)
        """
        cursor.execute(query, (month, year))
        results = cursor.fetchall()

        # Close cursor and database connection
        cursor.close()
        db.close()

        # Prepare JSON response
        response = []
        for result in results:
            response.append(
                {
                    "ID_NV": result["ID_NV"],
                    "Thang": result["Thang"],
                    "Nam": result["Nam"],
                    "SoNgayLam": result["SoNgayLam"],
                    "TongNgay": result["TongNgay"],
                }
            )

        return jsonify(response), 200

    except Exception as e:
        # Handle other unexpected errors
        return jsonify({"error": f"Unexpected error: {e}"}), 500

# http://127.0.0.1:5000/api/thongke/ngaylam
# Tất cả nv tất cả tháng
@thongkengaylam.route('/api/thongke/ngaylam', methods=['GET'])
def thong_ke_ngay_lam():
    try:
        # Connect to the database
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Execute the SQL query
        query = """
            SELECT ID_NV,
                   MONTH(NgayLam) AS Thang,
                   YEAR(NgayLam) AS Nam,
                   COUNT(CASE WHEN KETQUADIEMDANH LIKE '%thành công%' THEN 1 ELSE NULL END) AS SoNgayLam,
                   COUNT(*) AS TongNgay
            FROM THONGKE_DIEMDANH_NGAY
            GROUP BY ID_NV, MONTH(NgayLam), YEAR(NgayLam)
            ORDER BY Nam, Thang, ID_NV;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Close cursor and database connection
        cursor.close()
        db.close()

        # Prepare JSON response
        response = []
        for result in results:
            response.append(
                {
                    "ID_NV": result["ID_NV"],
                    "Thang": result["Thang"],
                    "Nam": result["Nam"],
                    "SoNgayLam": result["SoNgayLam"],
                    "TongNgay": result["TongNgay"],
                }
            )

        return jsonify(response), 200

    except Exception as e:
        # Handle other unexpected errors
        return jsonify({"error": f"Unexpected error: {e}"}), 500




#thống kê ngày nghỉ và ngày làm
# Endpoint API để thực hiện thống kê số ngày làm và số ngày nghỉ của tất cả nhân viên trong tất cả các tháng
def generate_valid_days(year, month):
    num_days = calendar.monthrange(year, month)[1]
    all_days = [datetime(year, month, day) for day in range(1, num_days + 1)]
    valid_days = [day for day in all_days if day.weekday() < 5]  # Loại bỏ thứ Bảy (5) và Chủ Nhật (6)
    return len(valid_days)



# Endpoint API để thực hiện thống kê số ngày làm và số ngày nghỉ của tất cả nhân viên trong tất cả các tháng
@thongkengaylam.route('/api/thongke/ngaynghi', methods=['GET'])
def ngaynghi():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT ID_NV,
                   MONTH(NgayLam) AS Thang,
                   YEAR(NgayLam) AS Nam,
                   COUNT(CASE WHEN KETQUADIEMDANH LIKE '%thành công%' THEN 1 ELSE NULL END) AS SoNgayLam,
                   COUNT(*) AS TongNgay
            FROM THONGKE_DIEMDANH_NGAY
            GROUP BY ID_NV, MONTH(NgayLam), YEAR(NgayLam)
            ORDER BY Nam, Thang, ID_NV;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        db.close()

        response = []

        total_valid_days_in_month = {}

        for result in results:
            year = result["Nam"]
            month = result["Thang"]
            if (year, month) not in total_valid_days_in_month:
                total_valid_days_in_month[(year, month)] = generate_valid_days(year, month)

        for result in results:
            year = result["Nam"]
            month = result["Thang"]
            so_ngay_lam = result["SoNgayLam"]
            tong_ngay = total_valid_days_in_month[(year, month)]
            so_ngay_nghi = tong_ngay - so_ngay_lam

            response.append(
                {
                    "ID_NV": result["ID_NV"],
                    "Thang": result["Thang"],
                    "Nam": result["Nam"],
                    "SoNgayLam": result["SoNgayLam"],
                    "SoNgayNghi": so_ngay_nghi,
                    "TongNgay": tong_ngay,
                }
            )

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500