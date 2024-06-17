# dangkinhanvien.py
from flask import Blueprint, request, jsonify
from db import get_db_connection, mysql
import cv2
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt
import base64


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
            facial_area = faces[0]["facial_area"]
            x = facial_area["x"]
            y = facial_area["y"]
            w = facial_area["w"]
            h = facial_area["h"]
            
            roi1 = image[y : y + h, x : x + w]
            embedding12 = DeepFace.verification.__extract_faces_and_embeddings(
                img_path=roi1,
                model_name="Facenet512",
                enforce_detection=False,
                detector_backend="yolov8",
            )
            if embedding12:
                return embedding12[0][0]

    except Exception as e:
        print(f"Error processing image: {e}")
        return


register_bp = Blueprint("register_bp", __name__)


@register_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    db = get_db_connection()
    cursor = db.cursor()
    image_top = process_image(data["image_top"])
    embedding_top = get_face_embedding(image_top)
    image_bottom = process_image(data["image_bottom"])
    embedding_bottom = get_face_embedding(image_bottom)
    image_left = process_image(data["image_left"])
    embedding_left = get_face_embedding(image_left)
    image_right = process_image(data["image_right"])
    embedding_right = get_face_embedding(image_right)
    image_between = process_image(data["image_between"])
    embedding_between = get_face_embedding(image_between)
    embedding_top_str = str(embedding_top)
    embedding_bottom_str = str(embedding_bottom)
    embedding_left_str = str(embedding_left)
    embedding_right_str = str(embedding_right)
    embedding_between_str = str(embedding_between)
    
    
    try:
        # Insert into NHANVIEN table
        cursor.execute(
            """
            INSERT INTO NHANVIEN (ID_NV, MA_QR, TEN_NV, DIACHI_NV, EMAIL_NV, SDT_NV, GIOITINH_NV, NGAYSINH_NV)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                data["id_nv"],
                data["ma_qr"],
                data["ten_nv"],
                data["diachi_nv"],
                data["email_nv"],
                data["sdt_nv"],
                data["gioitinh_nv"],
                data["ngaysinh_nv"],
            ),
        )

        # Insert into TAIKHOAN_NV table
        cursor.execute(
            """
            INSERT INTO TAIKHOAN_NV (ID_NV, USERNAME, PASSWORD, TRANGTHAI_TAIKHOAN, THOIGIAN_TAO, THOIGIAN_XOA)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                data["id_nv"],
                data["username"],
                data["password"],
                data["trangthai_taikhoan"],
                data["thoigian_tao"],
                data["thoigian_xoa"],
            ),
        )

        # Insert into IMAGE_BASE64_NV table
        cursor.execute(
            """
            INSERT INTO IMAGE_BASE64_NV (ID_NV, IMAGE_TOP, IMAGE_BOTTOM, IMAGE_LEFT, IMAGE_RIGHT, IMAGE_BETWEEN)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                data["id_nv"],
                data["image_top"],
                data["image_bottom"],
                data["image_left"],
                data["image_right"],
                data["image_between"],
            ),
        )

        cursor.execute(
            """
            INSERT INTO VECTO_ANH (VT_BOTTOM, VT_TOP, VT_LEFT, VT_RIGHT, VT_BETWEEN, ID_NV)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                embedding_bottom_str,
                embedding_top_str,
                embedding_left_str,
                embedding_right_str,
                embedding_between_str,
                data["id_nv"],
            ),
        )

        db.commit()

        return jsonify({"message": "Employee registered successfully!"}), 201
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        db.close()
