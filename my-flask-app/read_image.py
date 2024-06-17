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
