# =========================================================
# IMPORTS
# =========================================================
from datasets import load_dataset, DatasetDict
from PIL import Image
import os
import shutil


# =========================================================
# CONFIG SECTION — CHANGE SETTINGS HERE
# =========================================================

CONFIG = {
    "dataset_name": "deanngkl/raf-db-7emotions",

    # Train/Validation/Test split ratios (must sum to 1.0)
    "split_train": 0.70,
    "split_val": 0.15,
    "split_test": 0.15,

    # Export directory for YOLO dataset
    "output_dir": "yolo_rafdb",

    # Random seed for reproducibility
    'seed': 42,

    # Show example image during inspection
    "show_sample_image": False,

    # Shuffle dataset before splitting
    "shuffle": True,

    # Whether to export YOLO dataset to disk
    "export_yolo": True,
}

# delete old data file
if os.path.exists(CONFIG["output_dir"]):
    shutil.rmtree(CONFIG["output_dir"])
    print("Removing old yolo_rafdb folder...")


# =========================================================
# 1. Load Dataset
# =========================================================
def load_rafdb_dataset():
    print(f"[INFO] Loading dataset: {CONFIG['dataset_name']} ...")
    dataset = load_dataset(CONFIG["dataset_name"])

    print(dataset)

    # Optional: show a sample image
    if CONFIG["show_sample_image"]:
        sample = dataset["train"][0]
        print("[INFO] Sample label:", sample["label"])
        sample["image"].show()

    return dataset


# =========================================================
# 2. Ensure PIL image format
# =========================================================
def preprocess_images(dataset):
    print("[INFO] Ensuring images are in PIL format...")

    def preprocess(sample):
        if not isinstance(sample["image"], Image.Image):
            sample["image"] = Image.fromarray(sample["image"])
        return sample

    return dataset.map(preprocess)


# =========================================================
# Shuffle dataset BEFORE splitting
# =========================================================
def shuffle_dataset(dataset, seed=CONFIG["seed"]):
    print("[INFO] Shuffling dataset before split...")
    return dataset.shuffle(seed=seed)


# =========================================================
# 3. Custom Split: Train/Val/Test = 70/15/15
# =========================================================
def custom_split(dataset):
    print("[INFO] Splitting dataset into custom ratios...")

    train_ratio = CONFIG["split_train"]
    val_ratio = CONFIG["split_val"]
    test_ratio = CONFIG["split_test"]

    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Split ratios must sum to 1.0!"

    # Only "train" split exists in RAF-DB HF version, so we split manually
    base = dataset["train"]

    if CONFIG["shuffle"]:
        print(f"[INFO] Shuffling dataset with seed={CONFIG['seed']}...")
        base = base.shuffle(seed=CONFIG["seed"])

    total = len(base)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    train_ds = base.select(range(0, train_end))
    val_ds = base.select(range(train_end, val_end))
    test_ds = base.select(range(val_end, total))

    print(f"Total: {total}")
    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

    return DatasetDict({
        "train": train_ds,
        "validation": val_ds,
        "test": test_ds
    })


# =========================================================
# 4. Convert bounding boxes to YOLO format
# =========================================================
def convert_bbox_to_yolo(bbox, img_width, img_height):
    x_min, y_min, w, h = bbox

    cx = x_min + w / 2
    cy = y_min + h / 2

    return [
        cx / img_width,
        cy / img_height,
        w / img_width,
        h / img_height
    ]


# =========================================================
# 5. Export dataset to YOLO format
# =========================================================
def export_split(ds, split):
    out_dir = CONFIG["output_dir"]
    print(f"[INFO] Exporting {split} split to YOLO format in '{out_dir}' ...")

    images_dir = f"{out_dir}/images/{split}"
    labels_dir = f"{out_dir}/labels/{split}"

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    for idx, sample in enumerate(ds):
        img = sample["image"]
        bbox = sample["bbox"]
        label = sample["label"]

        img_path = f"{images_dir}/{idx}.jpg"
        img.save(img_path)

        w, h = img.size
        cx, cy, bw, bh = convert_bbox_to_yolo(bbox, w, h)

        with open(f"{labels_dir}/{idx}.txt", "w") as f:
            f.write(f"{label} {cx} {cy} {bw} {bh}")

    print(f"[INFO] Finished exporting {split}.")


# =========================================================
# 6. Full Pipeline
# =========================================================
def run_pipeline():
    dataset = load_rafdb_dataset()
    dataset = preprocess_images(dataset)
    dataset = shuffle_dataset(dataset)
    dataset = custom_split(dataset)

    if CONFIG["export_yolo"]:
        export_split(dataset["train"], "train")
        export_split(dataset["validation"], "val")
        export_split(dataset["test"], "test")

    print("\n[INFO] Dataset preparation completed.")
    print("Next step:")
    print("  yolo train model=yolov11n.pt data=rafdb.yaml epochs=40 imgsz=640")


# =========================================================
# 7. Execute Script
# =========================================================
if __name__ == "__main__":
    run_pipeline()
