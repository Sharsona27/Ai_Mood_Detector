import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from collections import Counter
from deepface import DeepFace

# Load your custom-trained model
custom_model = load_model("models/custom_emotion_model.h5")
custom_labels = ['bored', 'contempt', 'disgust', 'fear', 'joy', 'surprise', 'upset']

# Setup MediaPipe face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

def predict_combined_emotion():
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
