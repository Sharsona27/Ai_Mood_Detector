import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from collections import Counter

# Load your trained model
custom_model = load_model("models/custom_emotion_model.h5")

# Labels as per your trained dataset
custom_labels = ['bored', 'contempt', 'disgust', 'fear', 'joy', 'surprise', 'upset']

# Initialize MediaPipe face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Video capture
cap = cv2.VideoCapture(0)

frame_counter = 0
emotion_history = []
max_history = 5  # for smoothing

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

            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

            face_roi = frame[y:y + h, x:x + w]

            try:
                # Preprocess face for custom model
                custom_face = cv2.resize(face_roi, (224, 224))  # same size as training
                custom_face = custom_face.astype("float32") / 255.0
                custom_face = img_to_array(custom_face)
                custom_face = np.expand_dims(custom_face, axis=0)

                # Predict emotion
                custom_preds = custom_model.predict(custom_face, verbose=0)
                custom_label = custom_labels[np.argmax(custom_preds)]

                # Add to history for smoothing
                emotion_history.append(custom_label)
                if len(emotion_history) > max_history:
                    emotion_history.pop(0)

                # Show smoothed emotion
                smoothed_label = Counter(emotion_history).most_common(1)[0][0]
                cv2.putText(frame, f"Mood: {smoothed_label}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 100, 100), 2)

            except Exception as e:
                print("Error:", e)

    frame_counter += 1
    cv2.imshow("Custom Mood Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

