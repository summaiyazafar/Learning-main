"""
label_tool.py  —  Custom YOLO Annotation GUI (Tkinter)
=======================================================
A lightweight labeling tool for drawing bounding boxes on images.
Labels are saved in YOLO format (.txt) for use with YOLOv8 training.

Usage:
    python scripts/label_tool.py

Mouse Controls:
    Left-drag on empty area    : Draw a new bounding box
    Click on a box             : Select it (white resize handles appear)
    Drag a corner / edge handle: Resize the selected box
    Drag inside selected box   : Move the box
    Right-click on a box       : Delete it

Keyboard Shortcuts:
    0 – 5          : Select label class (also changes selected box's class)
    N / D / Right  : Save current image and go to Next
    P / A / Left   : Save current image and go to Previous
    R              : Copy boxes from the previous image (for similar frames)
    U              : Undo last drawn box
    Delete         : Delete selected box
    Esc            : Deselect all boxes
    C              : Clear all boxes on current image
    Ctrl+S         : Save current image labels
"""

import os
import tkinter as tk
from PIL import Image, ImageTk

# =================== SETTINGS ===================
ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR  = os.path.join(ROOT_DIR, "images")
LABELS_DIR  = os.path.join(ROOT_DIR, "labels")
CLASSES_FILE = os.path.join(ROOT_DIR, "classes.txt")

# Colors for each class (by index)
COLORS = ["#00c800", "#ff3030", "#ff8c00", "#00b4ff", "#e040fb", "#ffd700", "#00e5c0"]

# Handle grab radius in pixels (for resizing a box by dragging its corners/edges)
HANDLE_R = 9

# Mouse cursor shapes for each resize handle direction
CURSORS = {
    "nw": "size_nw_se", "se": "size_nw_se",
    "ne": "size_ne_sw", "sw": "size_ne_sw",
    "n":  "size_ns",    "s":  "size_ns",
    "e":  "size_we",    "w":  "size_we",
}
# ================================================

# ---- Load classes ----
if not os.path.exists(CLASSES_FILE):
    raise SystemExit(f"[ERROR] classes.txt not found: {CLASSES_FILE}")
with open(CLASSES_FILE, encoding="utf-8") as f:
    CLASSES = [line.strip() for line in f if line.strip()]

os.makedirs(LABELS_DIR, exist_ok=True)

# ---- Collect images ----
IMAGES = sorted(
    f for f in os.listdir(IMAGES_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
)
if not IMAGES:
    raise SystemExit(f"[ERROR] No images found in: {IMAGES_DIR}")


# ---- YOLO label file helpers ----

def label_path(filename: str) -> str:
    """Return the corresponding .txt label path for an image filename."""
    return os.path.join(LABELS_DIR, os.path.splitext(filename)[0] + ".txt")


def load_boxes(filename: str) -> list:
    """Load bounding boxes from a YOLO .txt file.
    Returns list of [class_id, x1, y1, x2, y2] in normalized [0,1] coordinates.
    """
    boxes = []
    path  = label_path(filename)
    if os.path.exists(path):
        for line in open(path):
            parts = line.split()
            if len(parts) == 5:
                cls         = int(parts[0])
                cx, cy, w, h = map(float, parts[1:])
                # Convert YOLO center format to corner format for internal use
                boxes.append([cls, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])
    return boxes


def save_boxes(filename: str, boxes: list):
    """Save bounding boxes to a YOLO .txt file (center x, center y, w, h format)."""
    with open(label_path(filename), "w") as f:
        for cls, x1, y1, x2, y2 in boxes:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            w  = x2 - x1
            h  = y2 - y1
            f.write(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")


# ============================================================
#  Main Application
# ============================================================
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Fall Detection — Label Tool")
        root.geometry("1400x820")

        # State
        self.done          = {i for i, n in enumerate(IMAGES) if os.path.exists(label_path(n))}
        self.idx           = next((i for i in range(len(IMAGES)) if i not in self.done), 0)
        self.cur_cls       = 0          # Currently selected class index
        self.boxes         = []         # List of [cls, x1, y1, x2, y2] for current image
        self.prev_boxes    = []         # Boxes from the previous image (for R key copy)
        self.sel           = None       # Index of selected box (or None)
        self.sel_explicit  = False      # True if user deliberately clicked to select
        self.pil           = None       # PIL image
        self.photo         = None       # Tkinter-compatible PhotoImage
        self.cache_key     = None       # (width, height) of last rendered photo
        self.scale         = 1.0        # Current image scale factor
        self.dw, self.dh   = 1, 1       # Displayed image width / height in pixels
        self.mode          = None       # Interaction mode: None | "draw" | "move" | "resize"
        self.handle        = None       # Active resize handle name ("nw", "se", etc.)
        self.orig          = None       # Original box state before move/resize
        self.start         = (0, 0)     # Mouse press position
        self.temp          = None       # Temporary canvas rectangle while drawing
        self._prog         = False      # Suppress list-selection callbacks during programmatic updates
        self._redraw_job   = None       # Pending after() redraw job ID

        self.build_ui()
        self.load_image(self.idx)

    # ----------------------------------------------------------------
    #  UI Construction
    # ----------------------------------------------------------------
    def build_ui(self):
        r = self.root
        r.columnconfigure(1, weight=1)
        r.rowconfigure(0, weight=1)

        # --- Left toolbar ---
        left = tk.Frame(r, width=140, bg="#f0f0f0")
        left.grid(row=0, column=0, sticky="ns")

        toolbar_buttons = [
            ("Next Image  (N)",     lambda: self.go(self.idx + 1)),
            ("Prev Image  (P)",     lambda: self.go(self.idx - 1)),
            ("Next Unlabeled",      self.next_unlabeled),
            ("Save  (Ctrl+S)",      self.commit),
            ("Copy Prev  (R)",      self.copy_prev),
            ("Undo Box  (U)",       self.undo),
            ("Delete Box  (Del)",   self.delete_selected),
            ("Clear All  (C)",      self.clear_all),
        ]
        for text, cmd in toolbar_buttons:
            tk.Button(left, text=text, command=cmd, width=17, pady=8).pack(padx=6, pady=4)

        # --- Main canvas ---
        self.canvas = tk.Canvas(r, bg="#3c3c3c", highlightthickness=0, cursor="crosshair")
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas.bind("<Configure>",       lambda e: self.schedule_redraw())
        self.canvas.bind("<ButtonPress-1>",   self.on_press)
        self.canvas.bind("<B1-Motion>",       self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>",   self.on_right_click)
        self.canvas.bind("<Motion>",          self.on_hover)

        # --- Right panel ---
        right = tk.Frame(r, width=300)
        right.grid(row=0, column=2, sticky="ns")
        right.rowconfigure(5, weight=1)

        # Class list
        tk.Label(right, text="CLASSES  (click to select)", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=6, pady=(6, 0))
        self.class_lb = tk.Listbox(right, height=len(CLASSES), exportselection=False,
                                   font=("Arial", 12), width=28, activestyle="none")
        for i, cls in enumerate(CLASSES):
            self.class_lb.insert("end", f" {i}   {cls}")
            self.class_lb.itemconfig(i, fg=COLORS[i % len(COLORS)])
        self.class_lb.grid(row=1, column=0, padx=6, sticky="ew")
        self.class_lb.select_set(0)
        self.class_lb.bind("<<ListboxSelect>>", self.on_class_select)

        # Box list
        tk.Label(right, text="BOXES  (this image)", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", padx=6, pady=(10, 0))
        self.box_lb = tk.Listbox(right, height=6, exportselection=False,
                                 font=("Arial", 11), activestyle="none")
        self.box_lb.grid(row=3, column=0, padx=6, sticky="ew")
        self.box_lb.bind("<<ListboxSelect>>", self.on_box_select)

        # File list
        tk.Label(right, text="FILE LIST  (✔ = labeled)", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky="w", padx=6, pady=(10, 0))
        ff = tk.Frame(right)
        ff.grid(row=5, column=0, padx=6, pady=(0, 6), sticky="nsew")
        sb = tk.Scrollbar(ff)
        sb.pack(side="right", fill="y")
        self.file_lb = tk.Listbox(ff, exportselection=False, font=("Arial", 9),
                                  yscrollcommand=sb.set, activestyle="none")
        self.file_lb.pack(side="left", fill="both", expand=True)
        sb.config(command=self.file_lb.yview)
        for i in range(len(IMAGES)):
            self.file_lb.insert("end", self._file_text(i))
        self.file_lb.bind("<<ListboxSelect>>", self.on_file_select)

        # Status bar
        self.status = tk.Label(r, text="", anchor="w", bg="#e8e8e8", font=("Arial", 10))
        self.status.grid(row=1, column=0, columnspan=3, sticky="ew")

        # Keyboard bindings
        r.bind_all("<Key>",       self.on_key)
        r.bind_all("<Control-s>", lambda e: self.commit())
        r.bind_all("<Delete>",    lambda e: self.delete_selected())
        r.bind_all("<Escape>",    lambda e: self.deselect())
        r.bind_all("<Right>",     lambda e: self.go(self.idx + 1))
        r.bind_all("<Left>",      lambda e: self.go(self.idx - 1))
        r.protocol("WM_DELETE_WINDOW", self.close)

    def _file_text(self, i: int) -> str:
        return ("✔  " if i in self.done else "    ") + IMAGES[i]

    # ----------------------------------------------------------------
    #  Image loading and rendering
    # ----------------------------------------------------------------
    def load_image(self, i: int):
        self.idx          = i
        self.pil          = Image.open(os.path.join(IMAGES_DIR, IMAGES[i])).convert("RGB")
        self.boxes        = load_boxes(IMAGES[i])
        self.sel          = None
        self.sel_explicit = False
        self.cache_key    = None
        self.redraw()
        self.refresh_boxlist()

        self._prog = True
        self.file_lb.selection_clear(0, "end")
        self.file_lb.selection_set(i)
        self.file_lb.see(i)
        self._prog = False
        self.update_status()

    def schedule_redraw(self):
        """Debounce window-resize redraws."""
        if self._redraw_job:
            self.root.after_cancel(self._redraw_job)
        self._redraw_job = self.root.after(30, self.redraw)

    def redraw(self):
        """Re-render the canvas: scale image, draw all boxes and resize handles."""
        self._redraw_job = None
        if self.pil is None:
            return

        cw = max(self.canvas.winfo_width(),  10)
        ch = max(self.canvas.winfo_height(), 10)
        iw, ih = self.pil.size
        self.scale = min(cw / iw, ch / ih)
        w = max(int(iw * self.scale), 1)
        h = max(int(ih * self.scale), 1)

        # Only re-create the PhotoImage if dimensions changed
        if (w, h) != self.cache_key:
            self.photo     = ImageTk.PhotoImage(self.pil.resize((w, h), Image.BILINEAR))
            self.cache_key = (w, h)

        self.dw, self.dh = w, h
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        for k, (cls, x1, y1, x2, y2) in enumerate(self.boxes):
            color     = COLORS[cls % len(COLORS)]
            thickness = 3 if k == self.sel else 2
            self.canvas.create_rectangle(
                x1 * w, y1 * h, x2 * w, y2 * h,
                outline=color, width=thickness
            )
            label = CLASSES[cls] if cls < len(CLASSES) else str(cls)
            self.canvas.create_text(
                x1 * w + 4, max(y1 * h - 10, 10),
                text=label, anchor="w", fill=color, font=("Arial", 12, "bold")
            )
            # Draw resize handles for the selected box
            if k == self.sel:
                for _, px, py in self._handle_points(k):
                    self.canvas.create_rectangle(
                        px - 4, py - 4, px + 4, py + 4,
                        fill="white", outline=color, width=2
                    )

    def refresh_boxlist(self):
        """Refresh the box list widget on the right panel."""
        self.box_lb.delete(0, "end")
        for k, b in enumerate(self.boxes):
            cls = b[0]
            self.box_lb.insert("end", f" {cls}: {CLASSES[cls] if cls < len(CLASSES) else cls}")
            self.box_lb.itemconfig(k, fg=COLORS[cls % len(COLORS)])
        if self.sel is not None:
            self.box_lb.selection_set(self.sel)

    def update_status(self):
        """Update the status bar at the bottom of the window."""
        self.status.config(
            text=(
                f"  Image {self.idx + 1}/{len(IMAGES)}"
                f"   |   {IMAGES[self.idx]}"
                f"   |   Labeled: {len(self.done)}/{len(IMAGES)}"
                f"   |   Current class: {self.cur_cls} = {CLASSES[self.cur_cls]}"
                f"   |   Boxes: {len(self.boxes)}"
            )
        )

    # ----------------------------------------------------------------
    #  Geometry helpers
    # ----------------------------------------------------------------
    def _clamp(self, event) -> tuple:
        """Clamp mouse coordinates to within the displayed image boundaries."""
        return min(max(event.x, 0), self.dw), min(max(event.y, 0), self.dh)

    def _handle_points(self, k: int) -> list:
        """Return the 8 resize handle positions (name, canvas_x, canvas_y) for box k."""
        _, a, b, c, d = self.boxes[k]
        x1, y1 = a * self.dw, b * self.dh
        x2, y2 = c * self.dw, d * self.dh
        mx, my  = (x1 + x2) / 2, (y1 + y2) / 2
        # Corners first so they win over edge handles on small boxes
        return [
            ("nw", x1, y1), ("ne", x2, y1), ("se", x2, y2), ("sw", x1, y2),
            ("n",  mx, y1), ("s",  mx, y2), ("w",  x1, my), ("e",  x2, my),
        ]

    def _handle_at(self, k: int, x: float, y: float):
        """Return the handle name under cursor (x, y) for box k, or None."""
        for name, px, py in self._handle_points(k):
            if abs(x - px) <= HANDLE_R and abs(y - py) <= HANDLE_R:
                return name
        return None

    def _inside(self, k: int, x: float, y: float) -> bool:
        """Return True if (x, y) is inside box k."""
        _, a, b, c, d = self.boxes[k]
        return a * self.dw <= x <= c * self.dw and b * self.dh <= y <= d * self.dh

    def _hit(self, x: float, y: float):
        """Return the topmost box index under (x, y), or None."""
        for k in range(len(self.boxes) - 1, -1, -1):
            if self._inside(k, x, y):
                return k
        return None

    # ----------------------------------------------------------------
    #  Mouse event handlers
    # ----------------------------------------------------------------
    def on_hover(self, e):
        if self.mode is not None:
            return
        cursor = "crosshair"
        if self.sel is not None and self.sel < len(self.boxes):
            x, y = self._clamp(e)
            h    = self._handle_at(self.sel, x, y)
            if h:
                cursor = CURSORS[h]
            elif self._inside(self.sel, x, y):
                cursor = "fleur"
        self.canvas.config(cursor=cursor)

    def _begin_edit(self, mode: str, handle):
        self.mode        = mode
        self.handle      = handle
        self.orig        = list(self.boxes[self.sel])
        self.sel_explicit = True

    def on_press(self, e):
        x, y        = self._clamp(e)
        self.start  = (x, y)
        self.mode   = None

        if self.sel is not None and self.sel < len(self.boxes):
            h = self._handle_at(self.sel, x, y)
            if h:
                self._begin_edit("resize", h)
                return
            if self._inside(self.sel, x, y):
                self._begin_edit("move", None)
                return

        # Start drawing a new box
        self.mode = "draw"
        color     = COLORS[self.cur_cls % len(COLORS)]
        self.temp = self.canvas.create_rectangle(x, y, x, y, outline=color, width=2, dash=(4, 2))

    def on_motion(self, e):
        if self.mode is None:
            return
        x, y = self._clamp(e)

        if self.mode == "draw":
            if self.temp:
                self.canvas.coords(self.temp, self.start[0], self.start[1], x, y)
            return

        b = self.boxes[self.sel]
        if self.mode == "resize":
            nx, ny = x / self.dw, y / self.dh
            if "w" in self.handle: b[1] = nx
            if "e" in self.handle: b[3] = nx
            if "n" in self.handle: b[2] = ny
            if "s" in self.handle: b[4] = ny
        elif self.mode == "move":
            o  = self.orig
            bw = o[3] - o[1]
            bh = o[4] - o[2]
            dx = (x - self.start[0]) / self.dw
            dy = (y - self.start[1]) / self.dh
            nx = min(max(o[1] + dx, 0), 1 - bw)
            ny = min(max(o[2] + dy, 0), 1 - bh)
            b[1], b[2], b[3], b[4] = nx, ny, nx + bw, ny + bh
        self.redraw()

    def on_release(self, e):
        mode      = self.mode
        self.mode = None
        if mode is None:
            return

        x, y = self._clamp(e)

        if mode == "draw":
            x1, y1 = self.start
            if self.temp:
                self.canvas.delete(self.temp)
                self.temp = None
            if abs(x - x1) > 6 and abs(y - y1) > 6:
                # Save the new box in normalized coordinates
                self.boxes.append([
                    self.cur_cls,
                    min(x1, x) / self.dw, min(y1, y) / self.dh,
                    max(x1, x) / self.dw, max(y1, y) / self.dh,
                ])
                self.sel          = len(self.boxes) - 1
                self.sel_explicit = False   # Auto-selected after draw
            else:
                # Small click = select the box under cursor
                self.sel          = self._hit(x1, y1)
                self.sel_explicit = (self.sel is not None)

        elif mode == "resize":
            b = self.boxes[self.sel]
            b[1], b[3] = sorted((b[1], b[3]))
            b[2], b[4] = sorted((b[2], b[4]))
            if b[3] - b[1] < 0.005 or b[4] - b[2] < 0.005:
                self.boxes[self.sel] = list(self.orig)   # Revert if too small

        self.redraw()
        self.refresh_boxlist()
        self.update_status()
        self.on_hover(e)

    def on_right_click(self, e):
        k = self._hit(*self._clamp(e))
        if k is not None:
            self.boxes.pop(k)
            self.sel          = None
            self.sel_explicit = False
            self.redraw()
            self.refresh_boxlist()
            self.update_status()

    # ----------------------------------------------------------------
    #  List widget event handlers
    # ----------------------------------------------------------------
    def on_class_select(self, e):
        sel = self.class_lb.curselection()
        if sel:
            self.set_class(sel[0])

    def set_class(self, cls: int):
        if cls >= len(CLASSES):
            return
        self.cur_cls = cls
        self.class_lb.selection_clear(0, "end")
        self.class_lb.selection_set(cls)
        # Change the selected box's class only if the user deliberately selected it
        if self.sel is not None and self.sel_explicit and self.sel < len(self.boxes):
            self.boxes[self.sel][0] = cls
            self.redraw()
            self.refresh_boxlist()
        self.update_status()

    def on_box_select(self, e):
        sel = self.box_lb.curselection()
        if sel:
            self.sel          = sel[0]
            self.sel_explicit = True
            self.redraw()

    def on_file_select(self, e):
        if self._prog:
            return
        sel = self.file_lb.curselection()
        if sel and sel[0] != self.idx:
            self.go(sel[0])

    # ----------------------------------------------------------------
    #  Actions
    # ----------------------------------------------------------------
    def commit(self):
        """Save the current image's boxes to its .txt label file."""
        save_boxes(IMAGES[self.idx], self.boxes)
        self.done.add(self.idx)
        if self.boxes:
            self.prev_boxes = [list(b) for b in self.boxes]

        self._prog = True
        self.file_lb.delete(self.idx)
        self.file_lb.insert(self.idx, self._file_text(self.idx))
        self.file_lb.selection_set(self.idx)
        self._prog = False
        self.update_status()

    def go(self, i: int):
        """Save current image and navigate to image index i."""
        if i < 0 or i >= len(IMAGES):
            return
        self.commit()
        self.load_image(i)

    def next_unlabeled(self):
        """Jump to the next image that has not yet been labeled."""
        self.commit()
        for offset in range(len(IMAGES)):
            j = (self.idx + 1 + offset) % len(IMAGES)
            if j not in self.done:
                self.load_image(j)
                return
        self.status.config(text="  All images are labeled!")

    def deselect(self):
        self.sel          = None
        self.sel_explicit = False
        self.redraw()
        self.refresh_boxlist()

    def copy_prev(self):
        """Copy bounding boxes from the previously saved image."""
        self.boxes        = [list(b) for b in self.prev_boxes]
        self.sel          = None
        self.sel_explicit = False
        self.redraw()
        self.refresh_boxlist()
        self.update_status()

    def undo(self):
        """Remove the last drawn box."""
        if self.boxes:
            self.boxes.pop()
            self.sel          = None
            self.sel_explicit = False
            self.redraw()
            self.refresh_boxlist()
            self.update_status()

    def delete_selected(self):
        """Delete the currently selected box."""
        if self.sel is not None and self.sel < len(self.boxes):
            self.boxes.pop(self.sel)
            self.sel          = None
            self.sel_explicit = False
            self.redraw()
            self.refresh_boxlist()
            self.update_status()

    def clear_all(self):
        """Remove all boxes from the current image."""
        self.boxes.clear()
        self.sel          = None
        self.sel_explicit = False
        self.redraw()
        self.refresh_boxlist()
        self.update_status()

    def on_key(self, e):
        ch = e.char.lower() if e.char else ""
        if ch.isdigit():
            self.set_class(int(ch))
        elif ch in ("n", "d"):
            self.go(self.idx + 1)
        elif ch in ("p", "a"):
            self.go(self.idx - 1)
        elif ch == "r":
            self.copy_prev()
        elif ch == "u":
            self.undo()
        elif ch == "c":
            self.clear_all()

    def close(self):
        """Save before closing the window."""
        self.commit()
        self.root.destroy()


# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()