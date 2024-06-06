from flask import Flask, Response, jsonify
import cv2
import threading
from time import sleep, time
from deepface.modules import detection
from deepface import DeepFace

app = Flask(__name__)

cap = cv2.VideoCapture(0)
lock = threading.Lock()
IMAGE = []
last_capture_time = 0
capture_interval = 10

def generate_frames():
    fps = 16  
    frame_duration = 1 / fps  
    frame_width = 480
    frame_height = 360
    
    while True:
        with lock:
            ref, frame = cap.read()
            if not ref:
                break

            start_time = time() 
            frame = cv2.resize(frame, (frame_width, frame_height))
            
            face_objs = detection.extract_faces(img_path=frame, enforce_detection=False, detector_backend='yolov8')
            if face_objs:
                confidence = face_objs[0]['confidence']
                if confidence > 0.84:
                    global last_capture_time
                    if time() - last_capture_time > capture_interval:
                        last_capture_time = time()
                        facial_area = face_objs[0]['facial_area']
                        x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        print(f"Detected face - x: {x}, y: {y}, w: {w}, h: {h}")
                        roi1 = frame[y : y + h, x : x + w]
                        roi = cv2.cvtColor(roi1, cv2.COLOR_BGR2RGB)
                        embedding12 = DeepFace.verification.__extract_faces_and_embeddings(
                            img_path=roi,
                            detector_backend="yolov8",
                            model_name="Facenet512",
                            enforce_detection=False,
                        )
                        # print("Vecto: ", (embedding12[0][0]))
                        print("Số lượng phần tử:", len(embedding12[0][0]))
                        cv2.imshow("Image", roi)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()

                        IMAGE.append(embedding12[0][0])
                
                        print(f"Captured and stored frame at confidence {confidence}")
                        print(IMAGE)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            processing_time = time() - start_time

            sleep_time = frame_duration - processing_time
            if sleep_time > 0:
                sleep(sleep_time)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_images')
def get_images():
    global IMAGE
    return jsonify(IMAGE)

if __name__ == "__main__":
    app.run(debug=True)

