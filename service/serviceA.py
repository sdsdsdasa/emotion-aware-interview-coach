from ultralytics import YOLO
import numpy as np
from PIL import Image
import io
import torch
import cv2
import os

# ==== Load Model ======================================================
model = YOLO('./existModel/best.onnx') 

# ==== Run Model ======================================================
def run_model(input_data):
    """
    Run model on flexible input types using `load_input`.
    - if input is a video: process frames until end
    - if input is an image: run a single prediction and show annotated result
    """
    kind, payload = load_input(input_data)

    if kind == "video":
        cap = payload

        while True:
            ret, frame = cap.read()

            if not ret:
                print("📌 End of video or failed to read frame.")
                break

            # Convert to grayscale
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # YOLO expects 3 channels — convert grayscale → 3-channel
            gray_image_3d = cv2.merge([gray_image, gray_image, gray_image])

            # Run YOLO
            results = model(gray_image_3d)
            result = results[0]

            # Extract emotions
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                emotion = result.names[cls_id]
                print(f"Detected emotion: {emotion} ({conf:.2f})")

            # Annotated frame (boxes + labels)
            try:
                annotated = result.plot()
            except AttributeError:
                print("❌ Error: result.plot() failed for ONNX inference")
                break

            # Display output
            cv2.imshow("YOLO Video Analysis", annotated)

            # ESC key to stop early
            if cv2.waitKey(1) & 0xFF == 27:
                print("⏹️ ESC pressed, stopping early...")
                break

        cap.release()
        cv2.destroyAllWindows()
        print("🎉 Video analysis completed.")

    elif kind == "image":
        pil_img = payload

        # Convert PIL -> BGR numpy for OpenCV & model compatibility
        img_np = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # If grayscale expected, convert (preserve original behavior)
        gray_image = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        gray_image_3d = cv2.merge([gray_image, gray_image, gray_image])

        results = model(gray_image_3d)
        result = results[0]

        # Print detections
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            emotion = result.names[cls_id]
            print(f"Detected emotion: {emotion} ({conf:.2f})")

        try:
            annotated = result.plot()
        except AttributeError:
            print("❌ Error: result.plot() failed for ONNX inference")
            return

        # Show annotated image
        cv2.imshow("YOLO Image Analysis", annotated)
        print("Press any key in the image window to continue...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        raise ValueError(f"Unsupported input kind from load_input: {kind}")


# ==== General Functions ======================================================
# Accept ANY input type
VIDEO_EXT = (".mp4", ".mov", ".avi", ".mkv", ".wmv")
def load_input(input_data):
    """
    Accept ANY input type:
    - image path
    - video path
    - numpy array
    - PIL Image
    - raw bytes (e.g. API upload)
    
    Returns either:
    - ("image", PIL Image)
    - ("video", cv2.VideoCapture object)
    """

    # ---------- Case 1: File path ----------
    if isinstance(input_data, str):
        lower = input_data.lower()

        if lower.endswith(VIDEO_EXT):
            # it's a video
            cap = cv2.VideoCapture(input_data)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_data}")
            return ("video", cap)

        else:
            # it's an image
            if not os.path.exists(input_data):
                raise ValueError(f"Image file does not exist: {input_data}")
            return ("image", Image.open(input_data))

    # ---------- Case 2: Raw byte stream ----------
    if isinstance(input_data, bytes):
        try:
            return ("image", Image.open(io.BytesIO(input_data)))
        except:
            raise ValueError("Bytes could not be decoded as an image.")

    # ---------- Case 3: PIL Image ----------
    if isinstance(input_data, Image.Image):
        return ("image", input_data)

    # ---------- Case 4: Numpy array (OpenCV image) ----------
    if isinstance(input_data, np.ndarray):
        return ("image", Image.fromarray(input_data))

    raise ValueError("Unsupported input type for Stage 1.")


# # Start tracking objects in a video
# model.track(source="path/to/video.mp4")

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


# ==== Prediction ======================================================
# predict emotion
def predict_emotion(model, frame):
    results = model(frame)[0]

    if len(results.boxes) == 0:
        return None  # no face detected

    box = results.boxes[0]  # assume 1 face
    cls = int(box.cls)
    conf = float(box.conf)

    emotion = model.names[cls]

    return {
        "emotion": emotion,
        "confidence": conf
    }



# ==== Analyze Video ======================================================
def analyze_video(model, input_data, output_dir="captured_frames", conf_threshold=0.5):
    os.makedirs(output_dir, exist_ok=True)

    kind, payload = load_input(input_data)
    timeline = []
    last_emotion = None
    last_conf = 0.0

    if kind == "video":
        cap = payload

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            timestamp_seconds = ms / 1000
            timestamp_str = format_timestamp(timestamp_seconds)

            # Predict emotion
            result = predict_emotion(model, frame)
            if result is None:
                emotion = "unknown"
                confidence = 0.0
            else:
                emotion = result["emotion"]
                confidence = result["confidence"]

            # First confident detection: record initial state
            if last_emotion is None:
                if confidence >= conf_threshold and emotion != "unknown":
                    entry = f"{timestamp_str} {emotion} ({confidence:.2f})"
                    timeline.append(entry)
                last_emotion = emotion
                last_conf = confidence
                continue

            # Record when emotion changes and meets confidence threshold
            if emotion != last_emotion and confidence >= conf_threshold:
                entry = f"{timestamp_str} {last_emotion} -> {emotion} ({confidence:.2f})"
                timeline.append(entry)

            last_emotion = emotion
            last_conf = confidence

        cap.release()
        return timeline

    elif kind == "image":
        pil_img = payload
        # Convert PIL -> BGR numpy for OpenCV & model compatibility
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        timestamp_str = "00:00"

        result = predict_emotion(model, frame)
        if result is None:
            return [f"{timestamp_str} unknown (0.00)"]

        emotion = result["emotion"]
        confidence = result["confidence"]

        timeline = []
        if confidence >= conf_threshold and emotion != "unknown":
            timeline.append(f"{timestamp_str} {emotion} ({confidence:.2f})")

        return timeline

    else:
        raise ValueError(f"Unsupported input kind for analyze_video: {kind}")



def analyze_emotion_changes(model, input_data, output_dir="change_frames", conf_threshold=0.5):
    """
    Detect emotion changes in a video or single image.
    Saves frames when emotion changes (and meets confidence threshold) and returns a timeline.
    """
    os.makedirs(output_dir, exist_ok=True)

    kind, payload = load_input(input_data)
    timeline = []
    last_emotion = None
    last_conf = 0.0

    if kind == "video":
        cap = payload

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            timestamp_seconds = ms / 1000
            timestamp_str = format_timestamp(timestamp_seconds)

            result = predict_emotion(model, frame)
            if result is None:
                emotion = "unknown"
                confidence = 0.0
            else:
                emotion = result["emotion"]
                confidence = result["confidence"]

            # First detection: record if confident
            if last_emotion is None:
                if confidence >= conf_threshold:
                    timeline.append(f"{timestamp_str} {emotion} ({confidence:.2f})")
                last_emotion = emotion
                last_conf = confidence
                continue

            # Record change when emotion differs and meets confidence
            if emotion != last_emotion and confidence >= conf_threshold:
                timeline.append(f"{timestamp_str} {last_emotion} -> {emotion} ({confidence:.2f})")

            last_emotion = emotion
            last_conf = confidence

        cap.release()
        return timeline

    elif kind == "image":
        pil_img = payload
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        result = predict_emotion(model, frame)
        if result is None:
            return ["00:00 unknown (0.00)"]

        emotion = result["emotion"]
        confidence = result["confidence"]
        timeline = []
        if confidence >= conf_threshold:
            timeline.append(f"00:00 {emotion} ({confidence:.2f})")

        return timeline

    else:
        raise ValueError(f"Unsupported input kind for analyze_emotion_changes: {kind}")


if __name__ == "__main__":
    import sys

    # Example default paths (replace with your actual files if needed)
    DEFAULT_VIDEO = r"media/video/example2.mp4"
    DEFAULT_IMAGE = r"media/image/image.png"

    # Use command-line arg if provided, otherwise default to an example video path
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VIDEO

    # Output directory and confidence threshold (can be overridden)
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "change_frames"
    conf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5

    print(f"Using input: {input_path}  out_dir: {out_dir}  conf: {conf}")

    timeline = analyze_emotion_changes(model, input_path, output_dir=out_dir, conf_threshold=conf)

    print("Emotion change timeline:")
    for entry in timeline:
        print(entry)

    # persist timeline
    os.makedirs(out_dir, exist_ok=True)
    timeline_file = os.path.join(out_dir, "timeline.txt")
    with open(timeline_file, "w", encoding="utf-8") as f:
        for entry in timeline:
            f.write(entry + "\n")

    print(f"Saved {len(timeline)} change entries to {timeline_file}")