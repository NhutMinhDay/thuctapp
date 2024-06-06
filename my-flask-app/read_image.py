import time
import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import Blueprint, request, jsonify
from db import get_db_connection, mysql

read_image = Blueprint('read_image', __name__)

assets_dir = 'D:/QLNS/assets1'
os.makedirs(assets_dir, exist_ok=True)

image_count = 0

def capture_image():
    global image_count
    while True:
        time.sleep(30)
        image_count += 1
        image_name = f"capture_{image_count}.jpg"
        save_image(image_name)

def save_image(image_name):
    print("Đã chụp:", image_name)

# Start capturing images in a separate thread
capture_thread = threading.Thread(target=capture_image)
capture_thread.start()

app = Flask(__name__)
CORS(app)

@read_image.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'message': 'Không có ảnh được tải lên'}), 400

    image = request.files['image']
    image.save(os.path.join(assets_dir, f"capture_{image_count}.jpg"))
    return jsonify({'message': 'Tải lên thành công'}), 200



# import os
# import cv2
# import threading
# import time
# from flask import Blueprint, request, jsonify
# from deepface import DeepFace

# # Define image directory and similarity threshold
# image_directory = "D:\\facev1\\namnam\\"
# threshold = 0.7

# # Resize dimensions
# resize_dim = (128, 128)

# # Function to load and resize images from directory
# def load_images_from_directory(directory, size):
#     images = []
#     for filename in os.listdir(directory):
#         if filename.lower().endswith((".jpg", ".png")):
#             img_path = os.path.join(directory, filename)
#             img = cv2.imread(img_path)
#             if img is not None:
#                 img_resized = cv2.resize(img, size)
#                 img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
#                 images.append(img_rgb)
#     return images

# # Load and resize images from directory
# images = load_images_from_directory(image_directory, resize_dim)
# print(f"Loaded {len(images)} images.")

# # Start webcam
# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("Error: Could not open webcam.")
#     exit()

# # Define Blueprint for the route
# read_image = Blueprint('read_image', __name__)

# # Define directory to save uploaded images
# assets_dir = 'D:/QLNS/assets'
# os.makedirs(assets_dir, exist_ok=True)

# # Variable to count images
# image_count = 0

# # Upload route to handle image uploads
# @read_image.route('/upload', methods=['POST'])
# def upload():
#     global image_count
#     if 'image' not in request.files:
#         return jsonify({'message': 'Không có ảnh được tải lên'}), 400

#     image = request.files['image']
#     image_count += 1
#     image.save(os.path.join(assets_dir, f"capture_{image_count}.jpg"))

#     # Webcam capture and DeepFace comparison logic
#     def capture_and_compare():
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print("Error: Failed to capture frame from webcam.")
#                 break

#             frame_resized = cv2.resize(frame, resize_dim)
#             frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

#             # Perform DeepFace comparison with each image
#             for img_rgb in images:
#                 result = DeepFace.verify(img_rgb, frame_rgb, enforce_detection=False)
#                 if result["verified"] and result["distance"] < threshold:
#                     toado = result["facial_areas"]["img2"]
#                     x, y, w, h = toado["x"], toado["y"], toado["w"], toado["h"]
#                     # Adjust coordinates to original frame size
#                     x = int(x * (frame.shape[1] / resize_dim[0]))
#                     y = int(y * (frame.shape[0] / resize_dim[1]))
#                     w = int(w * (frame.shape[1] / resize_dim[0]))
#                     h = int(h * (frame.shape[0] / resize_dim[1]))
#                     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#                     print("Similarity:", result["distance"], "Coordinates:", x, y, w, h)
#                     print("Đúng! Ảnh từ webcam được chấp nhận.")

#                     # Capture and save the recognized face image
#                     save_directory = "D:\\QLNS\\assets\\"
#                     if not os.path.exists(save_directory):
#                         os.makedirs(save_directory)

#                     save_path = os.path.join(save_directory, f"captured_image_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
#                     cv2.imwrite(save_path, frame[y:y+h, x:x+w])
#                     print("Ảnh khuôn mặt đã được lưu vào:", save_path)

#             # Display the original frame with rectangles
#             cv2.imshow("Webcam", frame)

#             # Exit the loop if 'q' is pressed
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#     threading.Thread(target=capture_and_compare).start()

#     # Return a response indicating success or failure of the upload
#     return jsonify({'message': 'Tải lên thành công'}), 200
