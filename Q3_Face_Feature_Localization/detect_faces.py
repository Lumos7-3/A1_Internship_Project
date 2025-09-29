import cv2
import mediapipe as mp
from PIL import Image, ImageTk
import tkinter as tk

# Mediapipe face detection (bounding boxes)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5
)

# Mediapipe face mesh (nose & eyes)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Webcam
cap = cv2.VideoCapture(0)

# Tkinter setup
root = tk.Tk()
root.title("Real-time Face Tracking")
root.geometry("950x700")
root.configure(bg="black")

# Canvas for subtle design
canvas = tk.Canvas(root, width=950, height=700, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Subtle diagonal line design
for i in range(0, 950, 25):
    canvas.create_line(i, 0, 0, i, fill="#111111")

# Frame for content
frame = tk.Frame(canvas, bg="black")
frame.place(relwidth=0.95, relheight=0.95, relx=0.025, rely=0.025)

# Title
title = tk.Label(frame, text="Real-time Face Tracking",
                 font=("Helvetica Neue", 20, "bold"), fg="white", bg="black", pady=10)
title.pack(fill="x")

# Video label
lbl = tk.Label(frame, bg="black", bd=5, relief="sunken")
lbl.pack(pady=10, expand=True)

running = True
latest_frame = None

def show_frame():
    global running, latest_frame
    if not running:
        return

    ret, frame_cv = cap.read()
    if not ret:
        root.after(10, show_frame)
        return

    rgb = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
    results_mesh = face_mesh.process(rgb)
    results_det = face_detection.process(rgb)

    # Draw bounding boxes
    if results_det.detections:
        for idx, detection in enumerate(results_det.detections):
            bboxC = detection.location_data.relative_bounding_box
            h, w, _ = frame_cv.shape
            x1 = int(bboxC.xmin * w)
            y1 = int(bboxC.ymin * h)
            x2 = x1 + int(bboxC.width * w)
            y2 = y1 + int(bboxC.height * h)
            cv2.rectangle(frame_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_cv, f'Face-{idx+1}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Draw nose tip & eye centers
    if results_mesh.multi_face_landmarks:
        h, w, _ = frame_cv.shape
        for face_landmarks in results_mesh.multi_face_landmarks:
            # Nose tip
            nose = face_landmarks.landmark[1]
            nose_pt = (int(nose.x * w), int(nose.y * h))
            cv2.circle(frame_cv, nose_pt, 6, (0, 0, 255), -1)

            # Left eye center
            left_indices = [33, 133, 159, 145, 153, 154]
            x_left = sum([face_landmarks.landmark[i].x for i in left_indices]) / len(left_indices)
            y_left = sum([face_landmarks.landmark[i].y for i in left_indices]) / len(left_indices)
            left_pt = (int(x_left * w), int(y_left * h))
            cv2.circle(frame_cv, left_pt, 6, (0, 0, 255), -1)

            # Right eye center
            right_indices = [263, 362, 386, 374, 380, 385]
            x_right = sum([face_landmarks.landmark[i].x for i in right_indices]) / len(right_indices)
            y_right = sum([face_landmarks.landmark[i].y for i in right_indices]) / len(right_indices)
            right_pt = (int(x_right * w), int(y_right * h))
            cv2.circle(frame_cv, right_pt, 6, (0, 0, 255), -1)

    latest_frame = frame_cv.copy()

    # Convert for Tkinter
    frame_rgb = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    lbl.config(image=imgtk)
    lbl.image = imgtk

    root.after(10, show_frame)

def toggle_webcam():
    global running
    running = not running
    if running:
        show_frame()

def save_snapshot():
    global latest_frame
    if latest_frame is not None:
        filename = "snapshot.jpg"
        cv2.imwrite(filename, latest_frame)
        print(f"✅ Snapshot saved as {filename}")

def quit_app():
    cap.release()
    root.destroy()

# Buttons at the bottom
btn_frame = tk.Frame(frame, bg="black")
btn_frame.pack(side="bottom", pady=15)

btn1 = tk.Button(btn_frame, text="▶ Webcam", command=toggle_webcam,
                 bg="#27ae60", fg="white", font=("Helvetica Neue", 11, "bold"), padx=8, pady=4)
btn1.grid(row=0, column=0, padx=10)

btn2 = tk.Button(btn_frame, text="📸 Snapshot", command=save_snapshot,
                 bg="#f39c12", fg="white", font=("Helvetica Neue", 11, "bold"), padx=8, pady=4)
btn2.grid(row=0, column=1, padx=10)

btn3 = tk.Button(btn_frame, text="❌ Quit", command=quit_app,
                 bg="#c0392b", fg="white", font=("Helvetica Neue", 11, "bold"), padx=8, pady=4)
btn3.grid(row=0, column=2, padx=10)

# Start loop
show_frame()
root.mainloop()
cap.release()
