import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import os

# 1. Set the path to your dataset
data_dir = r"D:\Sonal\sem 6\DE\AI Mood Detector\Backend\AI_Mood_Detector\Training\custom_emotions"  # <- Change this if needed

# 2. Set image and batch size
img_size = (224, 224)
batch_size = 32

# 3. Create image generators for training and validation (with augmentation)
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    horizontal_flip=True,
    rotation_range=10,
    zoom_range=0.2
)

train_data = datagen.flow_from_directory(
    data_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_data = datagen.flow_from_directory(
    data_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# 4. Load MobileNetV2 as base model
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False  # Freeze base model for now

# 5. Build the custom classifier
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(train_data.num_classes, activation='softmax')  # Output layer
])

# 6. Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 7. Print summary
model.summary()

# 8. Train the model
history = model.fit(
    train_data,
    epochs=10,  # You can increase later
    validation_data=val_data
)

# 9. Save the model
model.save(r"D:\Sonal\sem 6\DE\AI Mood Detector\Backend\models\custom_emotion_model.h5")


print("✅ Training complete. Model saved as custom_emotion_model.h5")

print("✅ Saved again")