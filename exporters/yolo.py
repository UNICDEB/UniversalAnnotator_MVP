
import os, json
from models import ProjectState
from io_utils import ensure_dir, image_stem

def _bbox_from_rect(points):
    (x1,y1),(x2,y2) = points
    x = min(x1,x2); y=min(y1,y2)
    w = abs(x2-x1); h = abs(y2-y1)
    return x,y,w,h

def _norm_box(x,y,w,h, W,H):
    cx = (x + w/2.0) / W
    cy = (y + h/2.0) / H
    nw = w / W
    nh = h / H
    return cx, cy, nw, nh

# def export_yolo_folder(state: ProjectState, out_dir=None):
#     if out_dir is None: out_dir = os.path.join(state.folder, "export_yolo")
#     ensure_dir(out_dir)
#     # classes.txt
#     with open(os.path.join(out_dir, "classes.txt"), "w", encoding="utf-8") as f:
#         for c in state.classes:
#             f.write(c + "\n")
#     class_to_id = {c:i for i,c in enumerate(state.classes)}

#     # Per image
#     for img in state.images:
#         ann = state.anns.get(img)
#         if not ann: continue
#         W,H = ann.width, ann.height
#         yolo_lines = []
#         seg_lines = []
#         kps = []

#         for sh in ann.shapes:
#             cid = class_to_id.get(sh.cls, 0)
#             if sh.type == "rect":
#                 x,y,w,h = _bbox_from_rect(sh.points)
#                 cx,cy,nw,nh = _norm_box(x,y,w,h, W,H)
#                 yolo_lines.append(f"{cid} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
#             elif sh.type in ("polygon","polyline"):
#                 coords = []
#                 for x,y in sh.points:
#                     coords.append(x/W); coords.append(y/H)
#                 seg_lines.append(str(cid) + " " + " ".join([f"{v:.6f}" for v in coords]))
#             elif sh.type == "keypoint":
#                 (x,y) = sh.points[0]
#                 kps.append({"class": sh.cls, "x": x/W, "y": y/H, "v": 2})

#         stem = image_stem(img)
#         # Standard YOLO boxes
#         with open(os.path.join(out_dir, f"{stem}.txt"), "w", encoding="utf-8") as f:
#             f.write("\n".join(yolo_lines))
#         # YOLO-seg polygons (optional, sidecar)
#         if seg_lines:
#             with open(os.path.join(out_dir, f"{stem}.seg.txt"), "w", encoding="utf-8") as f:
#                 f.write("\n".join(seg_lines))
#         # Keypoints sidecar JSON (simple; adapt to YOLO-pose as needed)
#         if kps:
#             with open(os.path.join(out_dir, f"{stem}.keypoints.json"), "w", encoding="utf-8") as f:
#                 json.dump({"image": stem, "keypoints": kps}, f, indent=2)


def export_yolo_folder(state: ProjectState, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(state.folder, "export_yolo")
    ensure_dir(out_dir)
    # Write classes.txt
    with open(os.path.join(out_dir, "classes.txt"), "w", encoding="utf-8") as f:
        for c in state.classes:
            f.write(c + "\n")
    class_to_id = {c: i for i, c in enumerate(state.classes)}

    for img in state.images:
        ann = state.anns.get(img)
        if not ann:
            continue
        W, H = ann.width, ann.height
        yolo_lines = []
        seg_lines = []
        kps = []

        for sh in ann.shapes:
            if not sh.cls or sh.cls not in class_to_id:
                # Skip shapes with missing or invalid class
                continue
            cid = class_to_id[sh.cls]
            if sh.type == "rect":
                x, y, w, h = _bbox_from_rect(sh.points)
                cx, cy, nw, nh = _norm_box(x, y, w, h, W, H)
                yolo_lines.append(f"{cid} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
            elif sh.type == "circle":
                (cx, cy), (ex, ey) = sh.points
                r = ((cx - ex) ** 2 + (cy - ey) ** 2) ** 0.5
                x = cx - r
                y = cy - r
                w = h = 2 * r
                cx_norm, cy_norm, nw, nh = _norm_box(x, y, w, h, W, H)
                yolo_lines.append(f"{cid} {cx_norm:.6f} {cy_norm:.6f} {nw:.6f} {nh:.6f}")
            elif sh.type == "line":
                (x1, y1), (x2, y2) = sh.points
                x = min(x1, x2)
                y = min(y1, y2)
                w = abs(x2 - x1)
                h = abs(y2 - y1)
                cx, cy, nw, nh = _norm_box(x, y, w, h, W, H)
                yolo_lines.append(f"{cid} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
            elif sh.type in ("polygon", "polyline"):
                coords = []
                for x, y in sh.points:
                    coords.append(x / W)
                    coords.append(y / H)
                seg_line = f"{cid} " + " ".join([f"{v:.6f}" for v in coords])
                yolo_lines.append(seg_line)
                seg_lines.append(seg_line)
            elif sh.type == "keypoint":
                (x, y) = sh.points[0]
                kps.append({"class": sh.cls, "x": x / W, "y": y / H, "v": 2})

        stem = image_stem(img)
        # Write all YOLO lines (rect, circle, line as bbox, polygon/polyline as seg)
        with open(os.path.join(out_dir, f"{stem}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(yolo_lines))
        if seg_lines:
            with open(os.path.join(out_dir, f"{stem}.seg.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(seg_lines))
        if kps:
            with open(os.path.join(out_dir, f"{stem}.keypoints.json"), "w", encoding="utf-8") as f:
                json.dump({"image": stem, "keypoints": kps}, f, indent=2)