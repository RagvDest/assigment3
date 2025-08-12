import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
    host=settings.REDIS_IP,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_ID,
    decode_responses=True
)

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(weights='imagenet')


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    class_name = None
    pred_probability = None
    # TODO: Implement the code to predict the class of the image_name

    # Load image
    image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
    logging.info(f"Loading image from path: {image_path}")
    img = image.load_img(image_path, target_size=(224, 224))
    

    # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    # Get predictions using model methods and decode predictions using resnet50 decode_predictions
    preds = model.predict(x)
    decoded_preds = decode_predictions(preds, top=1)[0]
    class_name, pred_probability = decoded_preds[0][1], decoded_preds[0][2]
        
    # Convert probabilities to float and round it
    pred_probability = round(float(pred_probability), 4)
    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        # Take a new job from Redis
        _, job_data = db.brpop(settings.REDIS_QUEUE)
        # Decode the JSON data for the given job
        job = json.loads(job_data)
        image_name = job.get("image_name")
        if image_name is None:
            continue
        # Important! Get and keep the original job ID
        job_id = job.get("id")
        # Run the loaded ml model (use the predict() function)
        class_name, pred_probability = predict(image_name)
        print(f"Predicted: {class_name} ({pred_probability})")
        # Prepare a new JSON with the results
        output = {"prediction": class_name, "score": pred_probability}

        # Store the job results on Redis using the original
        # job ID as the key
        db.set(job_id, json.dumps(output))

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
