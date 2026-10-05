"""
fix_labelimg.py
LabelImg ke known bugs fix karta hai (float to int issue).
SIRF EK BAAR CHALAYEIN agar labelImg crash ho raha ho.
"""

import os
import sys
import shutil

def find_labelimg_path():
    """LabelImg kahan installed hai woh dhoondo."""
    try:
        import labelImg
        base = os.path.dirname(labelImg.__file__)
        canvas = os.path.join(os.path.dirname(base), "libs", "canvas.py")
        labelimg = os.path.join(base, "labelImg.py")
        return canvas, labelimg
    except ImportError:
        print("[ERROR] labelImg installed nahi hai. Pehle install karein:")
        print("  pip install labelImg")
        return None, None

def fix_file(path, replacements):
    if not os.path.exists(path):
        print(f"[SKIP] File nahi mili: {path}")
        return
    
    # Backup banao
    backup = path + ".backup"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
        print(f"[BACKUP] {backup}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    for old, new in replacements:
        if old in content and new not in content:
            content = content.replace(old, new)
            changed = True
    
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {path}")
    else:
        print(f"[OK] {path} already fixed ya changes apply nahi hue")

def main():
    canvas_path, labelimg_path = find_labelimg_path()
    if not canvas_path:
        return
    
    print(f"[INFO] canvas.py: {canvas_path}")
    print(f"[INFO] labelImg.py: {labelimg_path}")
    
    # canvas.py fixes
    canvas_fixes = [
        (
            'p.drawLine(0, self.prev_point.y(), self.pixmap.width(), self.prev_point.y())',
            'p.drawLine(0, int(self.prev_point.y()), int(self.pixmap.width()), int(self.prev_point.y()))'
        ),
        (
            'p.drawLine(self.prev_point.x(), 0, self.prev_point.x(), self.pixmap.height())',
            'p.drawLine(int(self.prev_point.x()), 0, int(self.prev_point.x()), int(self.pixmap.height()))'
        ),
        (
            'p.drawLine(self.prev_point.x(), self.prev_point.y(), point.x(), point.y())',
            'p.drawLine(int(self.prev_point.x()), int(self.prev_point.y()), int(point.x()), int(point.y()))'
        ),
    ]
    
    fix_file(canvas_path, canvas_fixes)
    
    # labelImg.py fixes
    labelimg_fixes = [
        (
            'bar.setValue(bar.value() + bar.singleStep() * units)',
            'bar.setValue(int(bar.value() + bar.singleStep() * units))'
        ),
    ]
    
    fix_file(labelimg_path, labelimg_fixes)
    
    print("\n[DONE] Ab labelImg chalao: labelImg")

if __name__ == "__main__":
    main()