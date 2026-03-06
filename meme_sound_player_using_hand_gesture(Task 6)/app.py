import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'

import cv2
import numpy as np
import mediapipe as mp
import base64
from flask import Flask, render_template, Response, request, jsonify

from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarksConnections,
    RunningMode,
    drawing_utils as mp_draw,
)
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec

app = Flask(__name__)

FINGER_TIPS  = [4, 8, 12, 16, 20]
FINGER_PIPS  = [3, 6, 10, 14, 18]

LANDMARK_SPEC   = DrawingSpec(color=(0, 255, 0),  thickness=2, circle_radius=4)
CONNECTION_SPEC = DrawingSpec(color=(255, 255, 0), thickness=2)

# Absolute path so it works regardless of working directory
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")


def fingers_up(hand_landmarks, handedness_label):
    lm = hand_landmarks
    up = []
    if handedness_label == "Right":
        up.append(lm[4].x < lm[3].x)
    else:
        up.append(lm[4].x > lm[3].x)
    for i in range(1, 5):
        up.append(lm[FINGER_TIPS[i]].y < lm[FINGER_PIPS[i]].y)
    return up


def classify_gesture(up):
    thumb, index, middle, ring, pinky = up
    if not any(up):                                                    return "Fist"
    if not index and not ring and not pinky and middle:                return "Middle"
    if all(up):                                                        return "Four"
    if index and pinky and thumb and not middle and not ring:          return "Spiderman"
    if index and not middle and not ring and not pinky:                return "Pointing / One"
    if index and middle and not ring and not pinky:                    return "Peace / Two"
    if index and middle and ring and not pinky:                        return "Three"
    if index and middle and ring and pinky and not thumb:              return "Open Hand"
    if thumb and pinky and not index and not middle and not ring:      return "Call Me"
    if thumb and not index and not middle and not ring and not pinky:  return "Thumbs Up"
    if not thumb and not index and not middle and not ring and pinky:  return "Pinky Up"
    return f"Unknown ({sum(up)} fingers)"
 

def draw_hand_landmarks(bgr_image, hand_landmarks_list):
    connections = list(HandLandmarksConnections.HAND_CONNECTIONS)
    for hand_landmarks in hand_landmarks_list:
        mp_draw.draw_landmarks(
            bgr_image, hand_landmarks, connections,
            landmark_drawing_spec=LANDMARK_SPEC,
            connection_drawing_spec=CONNECTION_SPEC,
        )


def make_landmarker(mode):
    opts = HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mode,
        num_hands=2,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return HandLandmarker.create_from_options(opts)


# Two separate landmarkers - one per mode (cannot share between VIDEO/IMAGE)
video_landmarker = make_landmarker(RunningMode.VIDEO)

camera          = None
current_gesture = "No Hand Detected"
_frame_ts_ms    = 0


def process_frame_video(bgr_img, timestamp_ms):
    """For live webcam - uses VIDEO mode landmarker."""
    global current_gesture

    rgb_img  = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
    result   = video_landmarker.detect_for_video(mp_image, timestamp_ms)

    gesture = "No Hand Detected"
    if result.hand_landmarks:
        draw_hand_landmarks(bgr_img, result.hand_landmarks)
        for idx, hand_landmarks in enumerate(result.hand_landmarks):
            handedness_label = result.handedness[idx][0].display_name
            up_list  = fingers_up(hand_landmarks, handedness_label)
            gesture  = classify_gesture(up_list)
        cv2.putText(bgr_img, gesture, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    current_gesture = gesture
    return bgr_img


def process_frame_image(bgr_img, image_landmarker):
    """For uploaded video - uses IMAGE mode landmarker."""
    global current_gesture

    rgb_img  = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
    result   = image_landmarker.detect(mp_image)

    gesture = "No Hand Detected"
    if result.hand_landmarks:
        draw_hand_landmarks(bgr_img, result.hand_landmarks)
        for idx, hand_landmarks in enumerate(result.hand_landmarks):
            handedness_label = result.handedness[idx][0].display_name
            up_list  = fingers_up(hand_landmarks, handedness_label)
            gesture  = classify_gesture(up_list)
        cv2.putText(bgr_img, gesture, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    current_gesture = gesture
    return bgr_img


def gen_webcam_frames():
    global camera, _frame_ts_ms
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break

        _frame_ts_ms += 33
        frame = process_frame_video(frame, _frame_ts_ms)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() +
               b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/webcam_feed')
def webcam_feed():
    return Response(gen_webcam_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stop_webcam')
def stop_webcam():
    global camera
    if camera:
        camera.release()
        camera = None
    return jsonify({"status": "stopped"})


@app.route('/gesture_status')
def gesture_status():
    return jsonify({"gesture": current_gesture})


@app.route('/upload_video', methods=['POST'])
def upload_video():
    file = request.files['video']
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_video.mp4")
    file.save(path)

    image_landmarker = make_landmarker(RunningMode.IMAGE)

    cap        = cv2.VideoCapture(path)
    frames_b64 = []
    gestures   = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        processed = process_frame_image(frame.copy(), image_landmarker)
        _, buf = cv2.imencode('.jpg', processed)
        frames_b64.append(base64.b64encode(buf).decode('utf-8'))
        gestures.append(current_gesture)

    cap.release()
    image_landmarker.close()
    os.remove(path)

    return jsonify({"frames": frames_b64, "gestures": gestures})


if __name__ == '__main__':
    app.run(debug=False)   # debug=False prevents double-loading the model