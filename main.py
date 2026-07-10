from fastapi import FastAPI
import tensorflow as tf

app = FastAPI()

# Load trained model
model = tf.keras.models.load_model("model/plant_model.keras")

@app.get("/")
def home():
    return {"message": "Plant Disease Detection API is running successfully!"}

@app.get("/ping")
def ping():
    return {"status": "alive"}