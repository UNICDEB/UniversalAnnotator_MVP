
import os, json, itertools
from models import ProjectState
from io_utils import ensure_dir, image_stem

def export_coco_folder(state: ProjectState, out_dir=None):
    if out_dir is None: out_dir = os.path.join(state.folder, "export_coco")
    ensure_dir(out_dir)

    images = []
    annotations = []
    categories = [{"id": i+1, "name": c, "supercategory": "object"} for i, c in enumerate(state.classes)]
    cat_map = {c["name"]: c["id"] for c in categories}
    ann_id = 1

    for idx, img in enumerate(state.images, start=1):
        ann = state.anns.get(img)
        if not ann: continue
        images.append({"id": idx, "file_name": os.path.basename(img), "width": ann.width, "height": ann.height})
        for sh in ann.shapes:
            cid = cat_map.get(sh.cls, 1)
            coco_ann = {"id": ann_id, "image_id": idx, "category_id": cid, "iscrowd": 0}
            if sh.type == "rect":
                (x1,y1),(x2,y2) = sh.points
                x, y = float(min(x1,x2)), float(min(y1,y2))
                w, h = float(abs(x2-x1)), float(abs(y2-y1))
                coco_ann["bbox"] = [x,y,w,h]
                coco_ann["area"] = w*h
                coco_ann["segmentation"] = []
            elif sh.type in ("polygon","polyline"):
                # COCO expects closed polygons for segmentation
                pts = list(itertools.chain.from_iterable(sh.points))
                if sh.type == "polyline" and len(sh.points) >= 3:
                    pts += list(sh.points[0])  # close minimally
                coco_ann["segmentation"] = [ [float(v) for v in itertools.chain.from_iterable(sh.points)] ]
                coco_ann["bbox"] = _bbox_from_points(sh.points)
                coco_ann["area"] = _polygon_area(sh.points)
            elif sh.type == "circle":
                # approximate as bbox + no segmentation
                (cx,cy),(ex,ey) = sh.points
                r = ((cx-ex)**2 + (cy-ey)**2)**0.5
                x, y, w, h = cx-r, cy-r, 2*r, 2*r
                coco_ann["bbox"] = [x,y,w,h]
                coco_ann["area"] = 3.14159 * r * r
                coco_ann["segmentation"] = []
            elif sh.type == "line":
                coco_ann["segmentation"] = [ [float(v) for v in itertools.chain.from_iterable(sh.points)] ]
                coco_ann["bbox"] = _bbox_from_points(sh.points)
                coco_ann["area"] = 0.0
            elif sh.type == "keypoint":
                (x,y) = sh.points[0]
                coco_ann["keypoints"] = [float(x), float(y), 2]
                coco_ann["num_keypoints"] = 1
                coco_ann["bbox"] = [float(x)-1, float(y)-1, 2.0, 2.0]
                coco_ann["area"] = 0.0
                coco_ann["segmentation"] = []
            annotations.append(coco_ann); ann_id += 1

    out = {"images": images, "annotations": annotations, "categories": categories}
    with open(os.path.join(out_dir, "coco_annotations.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

def _bbox_from_points(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x_min, y_min = min(xs), min(ys)
    x_max, y_max = max(xs), max(ys)
    return [float(x_min), float(y_min), float(x_max-x_min), float(y_max-y_min)]

def _polygon_area(pts):
    area = 0.0
    n = len(pts)
    if n < 3: return 0.0
    for i in range(n):
        x1,y1 = pts[i]
        x2,y2 = pts[(i+1)%n]
        area += x1*y2 - x2*y1
    return abs(area)/2.0
