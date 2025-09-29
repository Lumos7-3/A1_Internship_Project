# License Plate Character Detection Viewer

This project provides a **GUI tool** to visualize license plate character detection results.  
It loads images and their YOLO-format label files, draws bounding boxes for different classes, and summarizes results in a table.

---

## 📂 Project Structure
```
project/
│   read_annotations.py      # Main script (entry point)
│
├── images/                  # Folder containing input images (.jpg, .png, .jpeg)
└── labels/                  # Folder containing YOLO-format label files (.txt)
```

---

## ⚙️ Dependencies
- Python **3.7+**
- [OpenCV](https://pypi.org/project/opencv-python/)  
- [Pillow](https://pypi.org/project/Pillow/)  

Install them with:
```bash
pip install opencv-python pillow
```

> `tkinter` and `os` are included in the Python standard library, no need to install.

---

## ▶️ How to Run
From the project folder:
```bash
python read_annotations.py
```

The application will:
- Open a GUI window.  
- Display images with bounding boxes (colored by class).  
- Show a summary table with counts of intact/broken characters.  
- Allow navigation between images (`←` and `→` keys or buttons).  
- Support zoom in/out using the mouse scroll wheel.  

---

## 📝 Assumptions
- Each image in `images/` has a matching `.txt` annotation in `labels/`.  
- Annotations follow YOLO format:
  ```
  <class_id> <x_center> <y_center> <width> <height>
  ```
  where values are **normalized (0–1)**.  
- Supported classes:
  - `0 = plate`
  - `1 = character_intact`
  - `2 = character_broken`
- Script is intended to run on local machines (GUI required).  
