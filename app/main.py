import sys, os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# import local function
from service.serviceA import load_image, predict_emotion


# ==== Data ======================================================
image_path = "media/image/angry.jpeg"


# ==== Configuration ======================================================
image = load_image(image_path)
result = predict_emotion(image)



print("Stage 1 Prediction:", result)
