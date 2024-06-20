# app.py
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import requests
from DiemDanh import (
    insert_sangvao,
    update_sangra,
    update_chieuvao,
    update_chieura,
    diemdanh,
)
from thoigian_diemdanh import thoigian_diemdanh
from quanli_QR import qr_nv
from db import check_db_connection
from quanli_imagenv import image_base64_nv
from dangkinhanvien import register_bp
from deepface import DeepFace
from vecto_nhanvien import vecto1
from db import get_db_connection
from deepface.modules import detection
from typing import Union
from dangnhap import login_bp
import base64
import numpy as np
import cv2
from datetime import datetime, timedelta
import json
from TK import edit
from dangnhapadmin import log
from dangnhapmanagers import loginmanager
from thongke_ngaylam import thongkengaylam

app = Flask(__name__)
CORS(app)
check_db_connection()
app.register_blueprint(diemdanh, url_prefix="/api/diemdanh")
app.register_blueprint(thoigian_diemdanh)
app.register_blueprint(qr_nv)
app.register_blueprint(image_base64_nv)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp, url_prefix="/api")
app.register_blueprint(vecto1)
app.register_blueprint(edit)
app.register_blueprint(log)
app.register_blueprint(loginmanager)
app.register_blueprint(thongkengaylam)

status = {"distances": [], "result": "", "TenNhanVien": "", "status_fetched": False}

def extract_time(datetime_obj):
    try:
        return datetime_obj.strftime("%H:%M:%S")
    except Exception as e:
        return None


def check_attendance_success(start_time):
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M:%S")
        current_time = datetime.now()
        end_time_obj = start_time_obj + timedelta(minutes=30)

        start_time_str = start_time_obj.strftime("%H:%M:%S")
        current_time_str = current_time.strftime("%H:%M:%S")
        end_time_str = end_time_obj.strftime("%H:%M:%S")

        return start_time_str <= current_time_str <= end_time_str
    except Exception as e:
        # print(f"Error while checking attendance condition: {e}")
        return False, "", "", ""


def fetch_and_check_times(ma_nhanvien):
    current_time = datetime.now()

    try:
        cleaned_data = ma_nhanvien.strip()
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        with connection.cursor(dictionary=True) as cursor:

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM nhanvien WHERE ID_NV = %s", (cleaned_data,))
            nhanvien_info = cursor.fetchone()
        if nhanvien_info:
            status["TenNhanVien"]=nhanvien_info["TEN_NV"].strip()

        query = "SELECT * FROM thoigian_diemdanh"
        cursor.execute(query)
        result = cursor.fetchall()
        
        for row in result:
            dd_sangdau = extract_time(row["DD_SANGDAU"])
            dd_sangcuoi = extract_time(row["DD_SANGCUOI"])
            dd_chieudau = extract_time(row["DD_CHIEUDAU"])
            dd_chieucuoi = extract_time(row["DD_CHIEUCUOI"])

            attendance_success_sangdau = check_attendance_success(dd_sangdau)
            attendance_success_sangcuoi = check_attendance_success(dd_sangcuoi)
            attendance_success_chieudau = check_attendance_success(dd_chieudau)
            attendance_success_chieucuoi = check_attendance_success(dd_chieucuoi)

            if attendance_success_sangdau:
                insert_sangvao(cleaned_data, current_time)
                return {
                    "message": "Điểm danh đầu sáng thành công (đưa vào bảng điểm danh VÀO)."
                }, 200

            elif attendance_success_sangcuoi:
                update_sangra(cleaned_data, current_time)
                return {
                    "message": "Điểm danh cuối sáng thành công (đưa vào bảng điểm danh RA)."
                }, 200

            elif attendance_success_chieudau:
                update_chieuvao(cleaned_data, current_time)
                return {
                    "message": "Điểm danh đầu chiều thành công (đưa vào bảng điểm danh VÀO)."
                }, 200

            elif attendance_success_chieucuoi:
                update_chieura(cleaned_data, current_time)
                return {
                    "message": "Điểm danh cuối chiều thành công (đưa vào bảng điểm danh RA)."
                }, 200

            else:
                return {"message": "KHÔNG NẰM TRONG THỜI GIAN ĐIỂM DANH"}, 200
    finally:
        if connection:
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


def process_image(image_data_base64):
    image_data = image_data_base64.replace("data:image/jpeg;base64,", "")
    image_data = base64.b64decode(image_data)
    image_np = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image


def get_face_embedding(image):
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print("Ảnh đã được chuyển sang định dạng RGB.")
        faces = DeepFace.detection.extract_faces(
            image, detector_backend="yolov8", enforce_detection=False
        )
        # print(faces)
        facial_area = faces[0]["facial_area"]
        x = facial_area["x"]
        y = facial_area["y"]
        w = facial_area["w"]
        h = facial_area["h"]
        print(f"Detected face - x: {x}, y: {y}, w: {w}, h: {h}")
        roi1 = image[y : y + h, x : x + w]
        embedding12 = DeepFace.verification.__extract_faces_and_embeddings(
            img_path=roi1,
            detector_backend="yolov8",
            model_name="Facenet512",
            enforce_detection=False,
        )
        print("Số lượng phần tử:", len(embedding12[0][0]))
        return embedding12[0][0]



def handle_scan(data):
    cleaned_data = data.strip()
    db = get_db_connection()
    with db.cursor(dictionary=True) as cursor:
        query = "SELECT VT_BOTTOM, VT_TOP, VT_RIGHT, VT_LEFT, VT_BETWEEN FROM VECTO_ANH WHERE ID_NV = %s"
        cursor.execute(query, (cleaned_data,))
        result = cursor.fetchone()
    db.close()
    return result




import time
@app.route("/save-image", methods=["POST"])
def save_image():
    try:
        start_time = time.time()
        threshold = 0.4

        data = request.json
        qr_image = data["data"] 
        print("\nẢnh thông tin mã qr: ", str(qr_image))

        scan_start = time.time()
        a = handle_scan(qr_image)
        scan_end = time.time()
        print(f"QR scan time: {scan_end - scan_start} seconds")

        image_data = data["image"]  # ảnh gương mặt
        process_start = time.time()
        image_top = process_image(image_data)
        process_end = time.time()
        print(f"Image processing time: {process_end - process_start} seconds")

        embedding_start = time.time()
        embedding = get_face_embedding(image_top)
        embedding_end = time.time()
        print(f"Embedding calculation time: {embedding_end - embedding_start} seconds")

        cosine_start = time.time()
        top = cosine_distance(eval(a["VT_TOP"]), embedding)
        bottom = cosine_distance(eval(a["VT_BOTTOM"]), embedding)
        left = cosine_distance(eval(a["VT_LEFT"]), embedding)
        right = cosine_distance(eval(a["VT_RIGHT"]), embedding)
        between = cosine_distance(eval(a["VT_BETWEEN"]), embedding)
        cosine_end = time.time()
        print(f"Cosine distance calculation time: {cosine_end - cosine_start} seconds")

        distances = [top, bottom, left, right, between]
        min_index = np.argmin(distances)
        min_value = distances[min_index]
        print("Giá trị nhỏ nhất là:", min_value)
        
        fetch_start = time.time()
        if min_value < threshold:
            result, status_code = fetch_and_check_times(qr_image)
        fetch_end = time.time()
        print(f"Fetch and check times: {fetch_end - fetch_start} seconds")

        if min_value < threshold:
            result_message = " (Check-in thành công !!!)"
        else:
            result_message = " (Không đủ điểm khớp, vui lòng thử lại !!!)"

        status["distances"] = distances
        status["result"] = result_message
        status["status_fetched"] = False
        # status["MaNhanVien"]=qr_image.strip()

        end_time = time.time()
        print(f"Total time: {end_time - start_time} seconds")

        return jsonify({"distances": distances, "result": result_message}), 200

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return jsonify({"error": str(e)}), 500


# @app.route("/save-image", methods=["POST"])
# def save_image():
#     try:
#         threshold = 0.4

#         data = request.json
#         qr_image = data["data"] 
#         print("\nẢnh thông tin mã qr: ", str(qr_image))

#         a = handle_scan(qr_image)
#         image_data = data["image"]  # ảnh gương mặt
#         image_top = process_image(image_data)
#         embedding = get_face_embedding(image_top)

#         top = cosine_distance(eval(a["VT_TOP"]), embedding)
#         bottom = cosine_distance(eval(a["VT_BOTTOM"]), embedding)
#         left = cosine_distance(eval(a["VT_LEFT"]), embedding)
#         right = cosine_distance(eval(a["VT_RIGHT"]), embedding)
#         between = cosine_distance(eval(a["VT_BETWEEN"]), embedding)

#         distances = [top, bottom, left, right, between]
#         min_index = np.argmin(distances)
#         min_value = distances[min_index]
#         print("Giá trị nhỏ nhất là:", min_value)
#         if min_value < threshold:
#             result, status_code = fetch_and_check_times(qr_image)
#         if min_value < threshold:
#             result_message = " (Check-in thành công !!!)"
#         else:
#             result_message = " (Không đủ điểm khớp, vui lòng thử lại !!!)"

#         status["distances"] = distances
#         status["result"] = result_message
#         status["status_fetched"] = False
#         # status["MaNhanVien"]=qr_image.strip()

#         return jsonify({"distances": distances, "result": result_message}), 200

#     except Exception as e:
#         print(f"Đã xảy ra lỗi: {e}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/check-status", methods=["GET"])
# def check_status():
#     return jsonify(status), 200


@app.route("/check-status", methods=["GET"])
def check_status():
    if not status["status_fetched"]:
        status["status_fetched"] = True
        return jsonify(status), 200
    else:
        status["distances"] = []
        status["result"] = ""
        status["TenNhanVien"] = ""
        status["status_fetched"] = False
        return jsonify(status), 200
    

@app.route("/verify-face", methods=["POST"])
def verify_face():
    try:
        if "image" not in request.files:
            return jsonify({"success": False, "message": "No image provided"}), 400

        file = request.files["image"]
        image_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        face_objs = detection.extract_faces(
            img_path=image, detector_backend="yolov8", enforce_detection=False
        )

        if len(face_objs) == 0:
            return jsonify({"success": False, "message": "No face detected"}), 400

        confidence = face_objs[0]["confidence"]
        facial_area = face_objs[0]["facial_area"]

        if confidence >= 0.6:
            cv2.rectangle(
                image,
                (facial_area["x"], facial_area["y"]),
                (
                    facial_area["x"] + facial_area["w"],
                    facial_area["y"] + facial_area["h"],
                ),
                (255, 0, 0),
                2,
            )

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Face detected",
                        "confidence": confidence,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Face not detected with sufficient confidence",
                    }
                ),
                400,
            )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
