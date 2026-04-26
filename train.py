from ultralytics import YOLO
import torch

def train_model():
    # Load YOLO model (pretrained detection model)
    model = YOLO("yolo11n.pt")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Training on device: {device}")


    # Train using the YAML config
    model.train(
        data="rafdb.yaml",
        epochs=3,
        imgsz=640,
        batch=32,
        fraction=0.2,
        device=device
    )

    print("[INFO] Training completed!")

if __name__ == "__main__":
    train_model()
