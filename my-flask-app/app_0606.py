# app.py
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
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

from time import sleep, time
from deepface.modules import detection
from typing import Union
from dangnhap import login_bp
import base64
import numpy as np
import cv2
from datetime import datetime, timedelta
import json




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





import queue

MA_NHANVIEN = queue.Queue()
VECTO = []
VECTO_QR = []

# VECTO = [
#     [11, 12, 13, 14]
# ]
# VECTO_QR = [
#     {
#         "VT_LEFT": "[0.1, 0.2, 0.3, 0.4]",
#         "VT_TOP": "[0.1, 0.2, 0.3, 0.4]",
#         "VT_RIGHT": "[0.1, 0.2, 0.3, 0.4]",
#         "VT_BETWEEN": "[0.1, 0.2, 0.3, 0.4]",
#         "VT_BOTTOM": "[0.1, 0.2, 0.3, 0.4]"
#     }
# ]


def extract_time(datetime_obj):
    try:
        return datetime_obj.strftime("%H:%M:%S")
    except Exception as e:
        print(f"Lỗi khi định dạng thời gian: {e}")
        return None


def check_attendance_success(start_time):
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M:%S")
        current_time = datetime.now()
        end_time_obj = start_time_obj + timedelta(minutes=30)

        start_time_str = start_time_obj.strftime("%H:%M:%S")
        current_time_str = current_time.strftime("%H:%M:%S")
        end_time_str = end_time_obj.strftime("%H:%M:%S")

        print("Khoảng Time:[ ", start_time_str, current_time_str, end_time_str + "]")

        return start_time_str <= current_time_str <= end_time_str
    except Exception as e:
        print(f"Error while checking attendance condition: {e}")
        return False, "", "", ""


@app.route("/get_times", methods=["GET"])
def get_times(current_time):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM thoigian_diemdanh"
        cursor.execute(query)
        result = cursor.fetchall()
        # current_time = datetime.now()
        print("Thời gian hiện tại: ", current_time)
        for row in result:
            dd_sangdau = extract_time(row["DD_SANGDAU"])
            dd_sangcuoi = extract_time(row["DD_SANGCUOI"])
            dd_chieudau = extract_time(row["DD_CHIEUDAU"])
            dd_chieucuoi = extract_time(row["DD_CHIEUCUOI"])

            attendance_success_sangdau = check_attendance_success(dd_sangdau)
            attendance_success_sangcuoi = check_attendance_success(dd_sangcuoi)
            attendance_success_chieudau = check_attendance_success(dd_chieudau)
            attendance_success_chieucuoi = check_attendance_success(dd_chieucuoi)

            print(
                "MỐC THỜI GIAN CỐ ĐỊNH TỪ CSDL:",
                dd_sangdau,
                dd_sangcuoi,
                dd_chieudau,
                dd_chieucuoi,
            )
            print(
                "KẾT QUẢ KIỂM TRA:",
                attendance_success_sangdau,
                attendance_success_sangcuoi,
                attendance_success_chieudau,
                attendance_success_chieucuoi,
            )
            if attendance_success_sangdau:
                insert_sangvao(MA_NHANVIEN.get(), current_time)
                print("Điểm danh đầu sáng thành công (đưa vào bảng điểm danh VÀO).")
                connection.commit()
                return (
                    jsonify(
                        {
                            "message": "Điểm danh đầu sáng thành công (đưa vào bảng điểm danh VÀO)."
                        }
                    ),
                    200,
                )
            elif attendance_success_sangcuoi:
                update_sangra(MA_NHANVIEN.get(), current_time)
                print("Điểm danh cuối sáng thành công (đưa vào bảng điểm danh RA).")
                connection.commit()
                return (
                    jsonify(
                        {
                            "message": "Điểm danh cuối sáng thành công (đưa vào bảng điểm danh RA)."
                        }
                    ),
                    200,
                )
            elif attendance_success_chieudau:
                update_chieuvao(MA_NHANVIEN.get(), current_time)
                print("Điểm danh đầu chiều thành công (đưa vào bảng điểm danh VÀO).")
                connection.commit()
                return (
                    jsonify(
                        {
                            "message": "Điểm danh đầu chiều thành công (đưa vào bảng điểm danh VÀO)."
                        }
                    ),
                    200,
                )
            elif attendance_success_chieucuoi:
                update_chieura(MA_NHANVIEN.get(), current_time)
                print("Điểm danh cuối chiều thành công (đưa vào bảng điểm danh RA).")
                connection.commit()
                return (
                    jsonify(
                        {
                            "message": "Điểm danh cuối chiều thành công (đưa vào bảng điểm danh RA)."
                        }
                    ),
                    200,
                )

            else:
                print("KHÔNG NẰM TRONG THỜI GIAN ĐIỂM DANH")
                return jsonify({"message": "KHÔNG NẰM TRONG THỜI GIAN ĐIỂM DANH"}), 200

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


# Hàm này sẽ tổng quát toàn bộ quá trình điểm danh:
# lấy QR => chụp ảnh => so sánh (bao gồm chức năng kiểm tra thời gian điểm danh) => trả về kết quả
@app.route("/print-vectors", methods=["GET"])
def print_vectors():
    if VECTO and VECTO_QR:
        distances = {}
        threshold = 0.6

        try:
            vector_1 = np.array(VECTO[0], dtype=np.float64)
            vector_matrix = np.zeros((5, len(vector_1)))
            current_time = datetime.now()
            keys = ["VT_LEFT", "VT_TOP", "VT_RIGHT", "VT_BETWEEN", "VT_BOTTOM"]
            for idx, key in enumerate(keys):
                vector_matrix[idx] = np.array(
                    json.loads(VECTO_QR[0][key]), dtype=np.float64
                )
            print(vector_matrix)
            for idx, key in enumerate(keys):
                distance = cosine_distance(vector_1, vector_matrix[idx])
                distances[key] = distance
                print(distance)

            min_distance_idx = np.argmin(list(distances.values()))

            min_distance_key = list(distances.keys())[min_distance_idx]
            min_distance = distances[min_distance_key]
            result_message = f"Khoảng cách nhỏ nhất: {min_distance}"
            print(result_message)
            # get_times()
            if min_distance < threshold:
                result_message += " (Check-in thành công!)"
                get_times(current_time)
            else:
                result_message += " (Không đủ điểm khớp.)"

            return jsonify({"distances": distances, "result": result_message}), 200

        except Exception as e:
            return jsonify({"error": f"Error: {e}"}), 500

    else:
        return jsonify({"error": "VECTO hoặc VECTO_QR rỗng. Không thể xử lý."}), 400


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
            # print("Vecto: ", (embedding12[0][0]))
            print("Số lượng phần tử:", len(embedding12[0][0]))
            # cv2.imshow("Image", roi1)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            if embedding12:
                return embedding12[0][0]
    except Exception as e:
        print(f"Error processing image: {e}")


@app.route("/save-image", methods=["POST"])
def save_image():
    try:
        data = request.json
        image_data = data["image"]
        image_top = process_image(image_data)
        embedding = get_face_embedding(image_top)
        VECTO.append(embedding)
        print("Number of vectors:", len(VECTO))
        print_vectors()
        return jsonify(
            {
                "message": "Ảnh đã được đem từ web về flask, và chuyển thành vecto 1 chiều!",
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
        print("mã nhân viên quét từ qr web đem về python:", data)
        if not data:
            return jsonify({"message": "No data received"}), 400

        cleaned_data = data.strip()

        db = get_db_connection()
        if not db:
            return jsonify({"message": "Database connection failed"}), 500

        with db.cursor(dictionary=True) as cursor:
            # Kiểm tra xem ID_NV có tồn tại trong bảng VECTO_ANH không
            check_query = "SELECT COUNT(*) FROM VECTO_ANH WHERE ID_NV = %s"
            cursor.execute(check_query, (cleaned_data,))
            check_result = cursor.fetchone()
            VECTO.clear()
            VECTO_QR.clear()
            print("Làm rỗng trước khi quét QR mới:", VECTO, VECTO_QR)
            if check_result["COUNT(*)"] > 0:
                print(f"ID_NV {cleaned_data} tồn tại trong cơ sở dữ liệu")
                MA_NHANVIEN.put(cleaned_data)
                print("QUEUE có dữ liệu:", MA_NHANVIEN.get())

                query = "SELECT VT_BOTTOM, VT_TOP, VT_RIGHT, VT_LEFT, VT_BETWEEN FROM VECTO_ANH WHERE ID_NV = %s"
                cursor.execute(query, (cleaned_data,))
                result = cursor.fetchone()
                VECTO_QR.append(result)
                return jsonify(result), 200
            else:
                return jsonify({"message": "No matching data found"}), 404
        db.close()

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


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

        if confidence >= 0.84:
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


@app.route("/print_vectors_data", methods=["GET"])
def print_vectors_data():
    print("VECTO:", VECTO)
    print("VECTO_QR:", VECTO_QR)
    return jsonify({"VECTO": VECTO, "VECTO_QR": VECTO_QR}), 200


if __name__ == "__main__":
    app.run(debug=True)
