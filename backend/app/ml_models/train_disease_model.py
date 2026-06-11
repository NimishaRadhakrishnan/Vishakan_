import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0

# Output classes for agricultural diseases
CLASSES = ["Blast", "Powdery Mildew", "Root Rot", "Healthy"]

def build_and_save_disease_model():
    """
    Builds a transfer learning model using EfficientNetB0, compiles it,
    and serializes it to disease_model.h5.
    
    In a real production environment, this script is run on a dataset of leaf images.
    Here we construct and compile the model architecture and save it to ensure the
    backend service can load a valid Keras model file.
    """
    print("Building EfficientNetB0 transfer learning model...")
    
    # Load base model pre-trained on ImageNet without top classification layer
    base_model = EfficientNetB0(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    
    # Freeze the base model layers
    base_model.trainable = False
    
    # Construct classification head
    inputs = layers.Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(len(CLASSES), activation="softmax")(x)
    
    model = models.Model(inputs, outputs)
    
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    print("Model summary:")
    model.summary()
    
    output_dir = "backend/app/ml_models"
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "disease_model.h5")
    
    # Save the compiled model structure
    model.save(model_path)
    print(f"Disease detection model structure saved successfully to {model_path}")

if __name__ == "__main__":
    # We check if TF is available and run.
    try:
        build_and_save_disease_model()
    except Exception as e:
        print(f"Error compiling/saving TensorFlow model: {e}")
        print("Note: In environments without TensorFlow pre-installed, "
              "the service fallback will handle predictions gracefully.")
