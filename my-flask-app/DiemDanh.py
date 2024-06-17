from flask import Flask, Blueprint, request, jsonify
from db import get_db_connection
from datetime import datetime

app = Flask(__name__)
diemdanh = Blueprint("diemdanh", __name__)


from datetime import datetime

@diemdanh.route("/thongkengaylam", methods=["GET"])
def get_thong_ke_ngay_lam():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        current_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT * FROM THONGKE_DIEMDANH_NGAY WHERE ngaylam = %s", (current_date,))
        entries = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(entries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    

def insert_sangvao(ID_NV, thoi_gian_vao_sang):
    ngay_lam = datetime.now().strftime("%Y-%m-%d")
    check_query = """SELECT COUNT(*) FROM THONGKE_DIEMDANH_NGAY WHERE ID_NV = %s AND NgayLam = %s"""
    insert_query = """INSERT INTO THONGKE_DIEMDANH_NGAY (ID_NV, THOIGIAN_VAO_SANG, NgayLam) 
                      VALUES (%s, %s, %s)"""
    insert_tuple = (ID_NV, thoi_gian_vao_sang, ngay_lam)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(check_query, (ID_NV, ngay_lam))
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        return

    cursor.execute(insert_query, insert_tuple)
    conn.commit()
    conn.close()

    return jsonify({"message": "Insert sáng vào thành công"}), 201


def update_sangra(ID_NV, thoi_gian_ra_sang):
    ngay_lam = datetime.now().strftime("%Y-%m-%d")

    update_query = """UPDATE THONGKE_DIEMDANH_NGAY SET THOIGIAN_RA_SANG = %s WHERE ID_NV = %s AND NgayLam = %s"""
    update_tuple = (thoi_gian_ra_sang, ID_NV, ngay_lam)

    conn = get_db_connection()  
    cursor = conn.cursor()
    cursor.execute(update_query, update_tuple)
    conn.commit()
    conn.close()

    return jsonify({"message": "Cập nhật thành công"}), 200


def update_chieuvao(ID_NV,thoi_gian_vao_chieu):
    
    ngay_lam = datetime.now().strftime("%Y-%m-%d")
    # ngay_lam='2024-06-10'
    update_query = """UPDATE THONGKE_DIEMDANH_NGAY SET THOIGIAN_VAO_CHIEU = %s WHERE ID_NV = %s AND NgayLam = %s"""
    update_tuple = (thoi_gian_vao_chieu, ID_NV, ngay_lam)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(update_query, update_tuple)
    conn.commit()
    conn.close()

    return jsonify({"message": "Cập nhật thời gian vào chiều thành công"}), 200



def update_chieura(ID_NV ,thoi_gian_ra_chieu):
    ngay_lam = datetime.now().strftime("%Y-%m-%d")
    # ngay_lam='2024-06-10'
    update_query = """UPDATE THONGKE_DIEMDANH_NGAY SET THOIGIAN_RA_CHIEU = %s WHERE ID_NV = %s AND NgayLam = %s"""
    update_tuple = (thoi_gian_ra_chieu, ID_NV, ngay_lam)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(update_query, update_tuple)

    count_query_vao_sang = "SELECT COUNT(*) FROM THONGKE_DIEMDANH_NGAY WHERE ID_NV = %s AND NgayLam = %s AND THOIGIAN_VAO_SANG IS NOT NULL"
    cursor.execute(count_query_vao_sang, (ID_NV, ngay_lam))
    count_result_vao_sang = cursor.fetchone()[0]

    count_query_ra_sang = "SELECT COUNT(*) FROM THONGKE_DIEMDANH_NGAY WHERE ID_NV = %s AND NgayLam = %s AND THOIGIAN_RA_SANG IS NOT NULL"
    cursor.execute(count_query_ra_sang, (ID_NV, ngay_lam))
    count_result_ra_sang = cursor.fetchone()[0]

    count_query_vao_chieu = "SELECT COUNT(*) FROM THONGKE_DIEMDANH_NGAY WHERE ID_NV = %s AND NgayLam = %s AND THOIGIAN_VAO_CHIEU IS NOT NULL"
    cursor.execute(count_query_vao_chieu, (ID_NV, ngay_lam))
    count_result_vao_chieu = cursor.fetchone()[0]

    count_query_ra_chieu = "SELECT COUNT(*) FROM THONGKE_DIEMDANH_NGAY WHERE ID_NV = %s AND NgayLam = %s AND THOIGIAN_RA_CHIEU IS NOT NULL"
    cursor.execute(count_query_ra_chieu, (ID_NV, ngay_lam))
    count_result_ra_chieu = cursor.fetchone()[0]

    if (
        count_result_vao_sang == 1
        and count_result_ra_sang == 1
        and count_result_vao_chieu == 1
        and count_result_ra_chieu == 1
    ):
        update_ketqua_query = """UPDATE THONGKE_DIEMDANH_NGAY SET KETQUADIEMDANH = 'điểm danh thành công 1 ngày' WHERE ID_NV = %s AND NgayLam = %s"""
        cursor.execute(update_ketqua_query, (ID_NV, ngay_lam))
        conn.commit()
        conn.close()
        return (
            jsonify({"message": "Cập nhật thời gian ra chiều và kiểm tra thành công"}),
            200,
        )
    else:
        conn.commit()
        conn.close()
        return (
            jsonify(
                {"message": "Không đủ mốc thời gian, không thể cập nhật KETQUADIEMDANH"}
            ),
            400,
        )
        
        

# Định nghĩa các route cho API
@diemdanh.route('/insert_sangvao', methods=['POST'])
def api_insert_sangvao():
    data = request.get_json()
    print(data)
    ID_NV = data.get('ID_NV')
    print(ID_NV)
    thoi_gian_vao_sang = datetime.now()
    return insert_sangvao(ID_NV, thoi_gian_vao_sang)

@diemdanh.route('/update_sangra', methods=['POST'])
def api_update_sangra():
    data = request.get_json()
    ID_NV = data.get('ID_NV')
    thoi_gian_ra_sang = datetime.now()
    return update_sangra(ID_NV, thoi_gian_ra_sang)

@diemdanh.route('/update_chieuvao', methods=['POST'])
def api_update_chieuvao():
    data = request.get_json()
    ID_NV = data.get('ID_NV')
    thoi_gian_vao_chieu = datetime.now()
    return update_chieuvao(ID_NV, thoi_gian_vao_chieu)

@diemdanh.route('/update_chieura', methods=['POST'])
def api_update_chieura():
    data = request.get_json()
    ID_NV = data.get('ID_NV')
    thoi_gian_ra_chieu = datetime.now()
    return update_chieura(ID_NV, thoi_gian_ra_chieu)


# app.register_blueprint(diemdanh, url_prefix="/api/diemdanh")

# if __name__ == '__main__':
#     app.run(debug=True)
    