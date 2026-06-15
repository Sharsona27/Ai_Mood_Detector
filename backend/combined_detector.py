import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from collections import Counter
from deepface import DeepFace
import base64
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load your custom-trained model
custom_model = load_model("models/custom_emotion_model.h5")
custom_labels = ['bored', 'contempt', 'disgust', 'fear', 'joy', 'surprise', 'upset']


def get_face_detector():
    mp_face_detection = mp.solutions.face_detection
    return mp_face_detection.FaceDetection(
        model_selection=1,
        min_detection_confidence=0.5
    )


def detect_combined_emotion_from_image(image_data):
    """
    Detect emotion from a single image using both custom model and DeepFace.
    
    Args:
        image_data: Either numpy array (BGR format) or base64 encoded string
        
    Returns:
        dict with keys: emotion, confidence, custom_emotion, deepface_emotion
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
        face_detection = get_face_detector()
        results = face_detection.process(rgb_frame)
        
        if not results.detections:
            return {'emotion': 'Unknown', 'confidence': 0, 'error': 'No face detected'}
        
        # Process the first detected face
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        ih, iw, _ = frame.shape
        x = int(bbox.xmin * iw)
        y = int(bbox.ymin * ih)
        w = int(bbox.width * iw)
        h = int(bbox.height * ih)
        
        # Ensure valid coordinates
        x = max(0, x)
        y = max(0, y)
        w = min(w, iw - x)
        h = min(h, ih - y)
        
        face_roi = frame[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return {'emotion': 'Unknown', 'confidence': 0, 'error': 'Invalid face region'}
        
        custom_label = 'Unknown'
        deep_label = 'Unknown'
        
        try:
            # --- Custom Model Prediction ---
            custom_face = cv2.resize(face_roi, (224, 224))
            custom_face = custom_face.astype("float32") / 255.0
            custom_face = img_to_array(custom_face)
            custom_face = np.expand_dims(custom_face, axis=0)
            
            preds = custom_model.predict(custom_face, verbose=0)
            custom_label = custom_labels[np.argmax(preds)]
            custom_confidence = float(np.max(preds))
        except Exception as e:
            print(f"Custom model error: {e}")
            custom_confidence = 0
        
        try:
            # --- DeepFace Prediction ---
            deep_result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            if isinstance(deep_result, list):
                deep_result = deep_result[0]
            deep_label = deep_result['dominant_emotion']
            deep_emotions = deep_result.get('emotion', {})
            deep_confidence = deep_emotions.get(deep_label, 0)
        except Exception as e:
            print(f"DeepFace error: {e}")
            deep_confidence = 0
        
        # --- Consensus or Fallback Logic ---
        if custom_label.lower() == deep_label.lower():
            final_mood = custom_label
            confidence = max(custom_confidence, deep_confidence)
        else:
            # Soft merge both predictions
            final_mood = f"{custom_label} / {deep_label}"
            confidence = (custom_confidence + deep_confidence) / 2
        
        return {
            'emotion': final_mood,
            'confidence': round(confidence, 2),
            'custom_emotion': custom_label,
            'custom_confidence': round(custom_confidence, 2),
            'deepface_emotion': deep_label,
            'deepface_confidence': round(deep_confidence, 2)
        }
    
    except Exception as e:
        return {'emotion': 'Unknown', 'confidence': 0, 'error': str(e)}


def predict_combined_emotion():
    """Legacy function for local webcam (if still needed for demo)."""
    cap = cv2.VideoCapture(0)
    custom_emotion_history = []
    deepface_emotion_history = []
    max_history = 7
    final_mood = "Detecting..."

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_detection = get_face_detector()
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x = int(bbox.xmin * iw)
                y = int(bbox.ymin * ih)
                w = int(bbox.width * iw)
                h = int(bbox.height * ih)

                face_roi = frame[y:y+h, x:x+w]

                try:
                    # --- Custom Model Prediction ---
                    custom_face = cv2.resize(face_roi, (224, 224))
                    custom_face = custom_face.astype("float32") / 255.0
                    custom_face = img_to_array(custom_face)
                    custom_face = np.expand_dims(custom_face, axis=0)

                    preds = custom_model.predict(custom_face, verbose=0)
                    custom_label = custom_labels[np.argmax(preds)]
                    custom_emotion_history.append(custom_label)

                    # --- DeepFace Prediction ---
                    deep_result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                    deep_label = deep_result[0]['dominant_emotion']
                    deepface_emotion_history.append(deep_label)

                    # --- Limit history size ---
                    if len(custom_emotion_history) > max_history:
                        custom_emotion_history.pop(0)
                    if len(deepface_emotion_history) > max_history:
                        deepface_emotion_history.pop(0)

                    # --- Consensus or Fallback Logic ---
                    smooth_custom = Counter(custom_emotion_history).most_common(1)[0][0]
                    smooth_deep = Counter(deepface_emotion_history).most_common(1)[0][0]

                    if smooth_custom.lower() == smooth_deep.lower():
                        final_mood = smooth_custom
                    else:
                        # Soft merge both predictions
                        final_mood = f"{smooth_custom} / {smooth_deep}"

                    # --- Drawing on Frame ---
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    cv2.putText(frame, f"Custom: {smooth_custom}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 100), 2)
                    cv2.putText(frame, f"DeepFace: {smooth_deep}", (x, y + h + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 200, 255), 2)

                except Exception as e:
                    print("Prediction error:", e)

        cv2.imshow("Combined Mood Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return final_mood
