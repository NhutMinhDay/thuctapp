# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from thoigian_diemdanh import thoigian_diemdanh
from quanli_QR import qr_nv
from db import check_db_connection
from quanli_imagenv import image_base64_nv
from dangkinhanvien import register_bp
from deepface import DeepFace
from vecto_nhanvien import vecto1
from db import get_db_connection
# from layqr_nhanvien import layqr_nv
# from read_image import read_image
from typing import Any, Dict, List, Tuple, Union
from dangnhap import login_bp
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import time
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)
check_db_connection()
app.register_blueprint(thoigian_diemdanh)
app.register_blueprint(qr_nv)
app.register_blueprint(image_base64_nv)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp, url_prefix="/api")
app.register_blueprint(vecto1)
# app.register_blueprint(layqr_nv)
# start_time = time.time()
image_count = 0

# VECTO = []
# VECTO_QR = []

VECTO = [
    [11, 12, 13, 14]
]
VECTO_QR = [
    {
        "VT_LEFT": "[0.1, 0.2, 0.3, 0.4]",
        "VT_TOP": "[0.1, 0.2, 0.3, 0.4]",
        "VT_RIGHT": "[0.1, 0.2, 0.3, 0.4]",
        "VT_BETWEEN": "[0.1, 0.2, 0.3, 0.4]",
        "VT_BOTTOM": "[0.1, 0.2, 0.3, 0.4]"
    }
]

def extract_time(datetime_obj):
    try:
        return datetime_obj.strftime('%H:%M:%S')
    except Exception as e:
        print(f"Lỗi khi định dạng thời gian: {e}")
        return None


def check_attendance_success(start_time):
    try:
        start_time_obj = datetime.strptime(start_time, '%H:%M:%S')
        current_time = datetime.now()
        end_time_obj = start_time_obj + timedelta(minutes=30)
        
        start_time_str = start_time_obj.strftime('%H:%M:%S')
        current_time_str = current_time.strftime('%H:%M:%S')
        end_time_str = end_time_obj.strftime('%H:%M:%S')
        
        print("Start: ", start_time_str)
        print("current: ", current_time_str)
        print("End: ", end_time_str)
        
        return start_time_str <= current_time_str <= end_time_str
    except Exception as e:
        print(f"Error while checking attendance condition: {e}")
        return False, "", "", ""

@app.route('/get_times', methods=['GET'])
def get_times():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM thoigian_diemdanh"
        cursor.execute(query)
        result = cursor.fetchall()
        
        processed_result = []
        for row in result:
            dd_sangdau = extract_time(row["DD_SANGDAU"])
            dd_sangcuoi = extract_time(row["DD_SANGCUOI"])
            dd_chieudau = extract_time(row["DD_CHIEUDAU"])
            dd_chieucuoi = extract_time(row["DD_CHIEUCUOI"])
            
            attendance_success = check_attendance_success(dd_sangdau)
            attendance_success1 = check_attendance_success(dd_sangcuoi)
            attendance_success2 = check_attendance_success(dd_chieudau)
            attendance_success3 = check_attendance_success(dd_chieucuoi)
            print("Check TIME: ", attendance_success, attendance_success1, attendance_success2, attendance_success3)
            overall_success = attendance_success or attendance_success1 or attendance_success2 or attendance_success3
            processed_row = {
                "DD_SANGDAU": dd_sangdau,
                "DD_SANGCUOI": dd_sangcuoi,
                "DD_CHIEUDAU": dd_chieudau,
                "DD_CHIEUCUOI": dd_chieucuoi,
                "Attendance_Success": "Thành công" if overall_success else "Không thành công"
            }
            processed_result.append(processed_row)
        if processed_result:
            return jsonify(processed_result), 200
        else:
            return jsonify({"error": "Không tìm thấy dữ liệu"}), 404
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ MySQL: {e}")
        return jsonify({"error": "Đã xảy ra lỗi khi lấy dữ liệu"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
        
            
def cosine_distance(
    source_representation: Union[np.ndarray, list],
    test_representation: Union[np.ndarray, list],
) -> np.float64:
    if isinstance(source_representation, list):
        source_representation = np.array(source_representation)

    if isinstance(test_representation, list):
        test_representation = np.array(test_representation)

    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

@app.route("/print-vectors", methods=["GET"])
def print_vectors():
    matches = 0
    distances = {}
    threshold = 0.3

    for key in ["VT_LEFT", "VT_TOP", "VT_RIGHT", "VT_BETWEEN", "VT_BOTTOM"]:
        vector_1 = np.array(VECTO[0], dtype=np.float64)
        vector_2 = np.array(json.loads(VECTO_QR[0][key]), dtype=np.float64)
        distance = cosine_distance(vector_1, vector_2)
        distances[key] = distance
        if distance < threshold:
            matches += 1

    result_message = "Check-in thành công!" if matches >= 3 else "Không đủ điểm khớp."
    print(distances)

    # VECTO.clear()
    # VECTO_QR.clear()

    return jsonify({"distances": distances, "result": result_message}), 200

def process_image(image_data_base64):
    image_data = image_data_base64.replace("data:image/jpeg;base64,", "")
    image_data = base64.b64decode(image_data)
    image_np = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image

def get_face_embedding(image):
    try:
        if image.shape[2] == 3: 
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            print("Ảnh đã được chuyển sang định dạng RGB.")
            faces = DeepFace.detection.extract_faces(image, detector_backend='opencv')
            # print(faces)
            facial_area = faces[0]['facial_area']
            x = facial_area['x']
            y = facial_area['y']
            w = facial_area['w']
            h = facial_area['h']
            print(f"Detected face - x: {x}, y: {y}, w: {w}, h: {h}")
            roi1 = image[y:y+h, x:x+w]
            embedding12 = DeepFace.verification.__extract_faces_and_embeddings(img_path=roi1, model_name='Facenet512')
            # print("Vecto: ", (embedding12[0][0]))
            print("Số lượng phần tử:", len(embedding12[0][0]))
            cv2.imshow('Image', roi1)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            if embedding12:
                return embedding12[0][0]
            else:
                print("No face detected in the image.")
                return None
        else:
            print("Image must be in color format (RGB).")
            return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route("/save-image", methods=["POST"])
def save_image():
    try:
        data = request.json
        image_data = data["image"]
        image_top = process_image(image_data)
        embedding = get_face_embedding(image_top)
        print(embedding)
        VECTO.append(embedding)
        print("VECTO sau khi thêm embedding:", VECTO)
        print("Number of vectors:", len(VECTO))
        print_vectors()
        return jsonify(
            {
                "message": "Lưu hình ảnh thành công và vector đã được in!",
                "embedding": embedding,
            }
        )
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/scan", methods=["POST"])
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
            VECTO_QR.append(result)
            # print(VECTO_QR)
        db.close()

        return (
            jsonify(result)
            if result
            else jsonify({"message": "No matching data found"})
        ), (200 if result else 404)
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/log', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

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
                    SELECT ID_ADMIN, TEN_ADMIN, USER
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


if __name__ == "__main__":
    app.run(debug=True)
