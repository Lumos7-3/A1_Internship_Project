import cv2
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# === Paths ===
base_dir = os.path.dirname(os.path.abspath(__file__))  # folder where this script is
image_folder = os.path.join(base_dir, 'images')
label_folder = os.path.join(base_dir, 'labels')

# Class names
class_names = {0: 'plate', 1: 'character_intact', 2: 'character_broken'}

# --- Initialize GUI ---
root = tk.Tk()
root.title("License Plate Character Detection")
root.geometry("1400x900")
root.configure(bg="#121212")  # black background

# --- Left panel (navigation + table) ---
left_frame = tk.Frame(root, bg="#1A1A1A", width=400)
left_frame.pack(side="left", fill="y")

# Navigation buttons
nav_frame = tk.Frame(left_frame, bg="#1A1A1A")
nav_frame.pack(side="top", pady=10)

btn_style = {"bg": "#FF3333", "fg": "white", "font": ('Helvetica', 12, 'bold'),
             "activebackground": "#FF5555", "activeforeground": "white", "bd": 0}

prev_btn = tk.Button(nav_frame, text="◀ Previous", **btn_style, padx=10, pady=5)
prev_btn.grid(row=0, column=0, padx=5)

next_btn = tk.Button(nav_frame, text="Next ▶", **btn_style, padx=10, pady=5)
next_btn.grid(row=0, column=1, padx=5)

# Summary Table
columns = ('Filename', 'Intact', 'Broken', 'Status')
tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=30)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor='center')
tree.pack(side="top", fill="both", expand=True, padx=10, pady=10)

scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side='right', fill='y')

# Style the table
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                background="#1A1A1A",
                foreground="white",
                fieldbackground="#1A1A1A",
                rowheight=28,
                font=('Helvetica', 10))
style.configure("Treeview.Heading",
                background="#FF3333",
                foreground="white",
                font=('Helvetica', 11, 'bold'))
style.map("Treeview", background=[("selected", "#FF5555")])

# --- Right panel (image display) ---
right_frame = tk.Frame(root, bg="#121212")
right_frame.pack(side="right", fill="both", expand=True)

# Info label
info_label = tk.Label(right_frame, text="", bg="#121212", fg="white",
                      font=('Helvetica', 14, 'bold'))
info_label.pack(side="top", pady=10)

# Image canvas
img_canvas = tk.Canvas(right_frame, bg="#000000", highlightthickness=0)
img_canvas.pack(fill="both", expand=True, padx=10, pady=10)
img_label = tk.Label(img_canvas, bg="#000000")
img_window = img_canvas.create_window(0, 0, window=img_label, anchor="nw")

# --- Load images ---
print("Looking for images in:", image_folder)
if not os.path.exists(image_folder):
    print("❌ ERROR: Image folder not found ->", image_folder)
    image_files = []
else:
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg','.png','.jpeg'))]

current_index = 0
zoom_scale = 1.0  # default zoom

# --- Process image ---
def process_image(image_file):
    img_path = os.path.join(image_folder, image_file)
    label_path = os.path.join(label_folder, os.path.splitext(image_file)[0]+'.txt')
    img = cv2.imread(img_path)
    if img is None:
        return None, 0, 0, "Cannot read image"
    h, w = img.shape[:2]
    intact_count = 0
    broken_count = 0
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                cls, x_center, y_center, bw, bh = map(float, parts)
                cls = int(cls)
                x_center *= w
                y_center *= h
                bw *= w
                bh *= h
                x1 = int(x_center - bw / 2)
                y1 = int(y_center - bh / 2)
                x2 = int(x_center + bw / 2)
                y2 = int(y_center + bh / 2)
                color = (255, 0, 0) if cls == 0 else (0, 255, 0) if cls == 1 else (0, 0, 255)
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, class_names[cls], (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                if cls == 1:
                    intact_count += 1
                elif cls == 2:
                    broken_count += 1
    plate_status = "Intact" if broken_count == 0 else "Broken"
    return img, intact_count, broken_count, plate_status

# --- Show image (with zoom) ---
def show_image(idx):
    global zoom_scale
    if idx < 0 or idx >= len(image_files):
        return
    image_file = image_files[idx]
    img, intact_count, broken_count, plate_status = process_image(image_file)
    if img is None:
        info_label.config(text=f"Cannot read {image_file}")
        img_label.config(image='')
        return
    info_label.config(
        text=f"{image_file} | Intact: {intact_count}, Broken: {broken_count}, Status: {plate_status}",
        fg="#00FF88" if plate_status == "Intact" else "#FF3333"
    )

    canvas_width = max(img_canvas.winfo_width(), 200)
    canvas_height = max(img_canvas.winfo_height(), 200)
    h, w = img.shape[:2]

    # Base scale to fit canvas
    scale_w = canvas_width * 0.9 / w
    scale_h = canvas_height * 0.9 / h
    base_scale = min(scale_w, scale_h, 1.0)

    # Apply zoom
    scale = base_scale * zoom_scale
    new_w, new_h = int(w * scale), int(h * scale)

    img_resized = cv2.resize(img, (new_w, new_h))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_tk = ImageTk.PhotoImage(Image.fromarray(img_rgb))
    img_label.imgtk = img_tk
    img_label.config(image=img_tk)

    x_offset = max((canvas_width - new_w)//2, 0)
    y_offset = max((canvas_height - new_h)//2, 0)
    img_canvas.coords(img_window, x_offset, y_offset)

    highlight_current_in_table(idx)

# --- Highlight current row ---
def highlight_current_in_table(idx):
    for i, item in enumerate(tree.get_children()):
        if i == idx:
            tree.selection_set(item)
            tree.see(item)
        else:
            tree.selection_remove(item)

# --- Populate table ---
for image_file in image_files:
    img, intact_count, broken_count, plate_status = process_image(image_file)
    tree.insert('', tk.END, values=(image_file, intact_count, broken_count, plate_status))

# --- Navigation ---
def next_image(event=None):
    global current_index
    current_index = (current_index + 1) % len(image_files)
    show_image(current_index)

def prev_image(event=None):
    global current_index
    current_index = (current_index - 1) % len(image_files)
    show_image(current_index)

prev_btn.config(command=prev_image)
next_btn.config(command=next_image)
root.bind("<Right>", next_image)
root.bind("<Left>", prev_image)

# --- Zoom with scroll ---
def zoom(event):
    global zoom_scale
    if event.delta > 0 or event.num == 4:  # scroll up
        zoom_scale *= 1.1
    elif event.delta < 0 or event.num == 5:  # scroll down
        zoom_scale /= 1.1
    zoom_scale = max(0.2, min(zoom_scale, 5.0))  # clamp
    show_image(current_index)

root.bind("<MouseWheel>", zoom)   # Windows
root.bind("<Button-4>", zoom)     # Linux scroll up
root.bind("<Button-5>", zoom)     # Linux scroll down

# --- Start GUI ---
if image_files:
    show_image(current_index)
else:
    info_label.config(text="❌ No images found in the 'images' folder.", fg="red")

root.mainloop()
