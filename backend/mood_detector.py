# backend/mood_detector.py

import cv2
import numpy as np
import mediapipe as mp
from deepface import DeepFace
import os
from collections import Counter
from io import BytesIO
from PIL import Image
import base64

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)


def detect_mood_from_image(image_data):
    """
    Detect mood from a single image (numpy array or base64 string).
    
    Args:
        image_data: Either numpy array (BGR format) or base64 encoded string
        
    Returns:
        dict with keys: emotion, confidence (if available)
    """
    try:
        # Convert base64 to numpy array if needed
        if isinstance(image_data, str):
            image_data = base64.b64decode(image_data)
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        else:
            frame = image_data
        
        if frame is None:
            return {'emotion': 'Unknown', 'confidence': 0, 'error': 'Could not decode image'}
        
        # Convert to RGB for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        
        if not results.detections:
            return {'emotion': 'Unknown', 'confidence': 0, 'error': 'No face detected'}
        
        # Process the first detected face
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        ih, iw, _ = frame.shape
        x = int(bboxC.xmin * iw)
        y = int(bboxC.ymin * ih)
        w = int(bboxC.width * iw)
        h = int(bboxC.height * ih)
        
        # Ensure valid coordinates
        x = max(0, x)
        y = max(0, y)
        w = min(w, iw - x)
        h = min(h, ih - y)
        
        face_roi = frame[y:y + h, x:x + w]
        
        if face_roi.size == 0:
            return {'emotion': 'Unknown', 'confidence': 0, 'error': 'Invalid face region'}
        
        # Analyze emotion using DeepFace
        try:
            emotion_result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            if isinstance(emotion_result, list):
                emotion_result = emotion_result[0]
            
            dominant_emotion = emotion_result['dominant_emotion']
            emotions = emotion_result.get('emotion', {})
            confidence = emotions.get(dominant_emotion, 0)
            
            return {
                'emotion': dominant_emotion,
                'confidence': round(confidence, 2),
                'all_emotions': emotions
            }
        except Exception as e:
            return {'emotion': 'Unknown', 'confidence': 0, 'error': str(e)}
    
    except Exception as e:
        return {'emotion': 'Unknown', 'confidence': 0, 'error': str(e)}


def detect_mood():
    """Legacy function for local webcam (if still needed for demo)."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_counter = 0
    emotion_history = []
    max_history = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                face_roi = frame[y:y + h, x:x + w]

                if frame_counter % 10 == 0:
                    try:
                        emotion_result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                        if isinstance(emotion_result, list):
                            emotion_result = emotion_result[0]
                        dominant_emotion = emotion_result['dominant_emotion']
                    except Exception as e:
                        print(f"DeepFace failed: {e}")
                        dominant_emotion = "Unknown"

                    emotion_history.append(dominant_emotion)
                    if len(emotion_history) > max_history:
                        emotion_history.pop(0)

                if emotion_history:
                    smoothed_emotion = Counter(emotion_history).most_common(1)[0][0]
                    cv2.putText(frame, smoothed_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        frame_counter += 1
        cv2.imshow('Face and Mood Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1) 

    if emotion_history:
        return Counter(emotion_history).most_common(1)[0][0]
    return "Your Decoded Mood"

