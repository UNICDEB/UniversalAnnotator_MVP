
# Universal Annotator (Compact MVP)

A compact, extensible image annotation tool that supports **rectangle, polygon, circle, line, polyline, and keypoint** annotations, with export to **YOLO (.txt)**, **Pascal VOC (.xml)**, and **COCO (.json)**. Built with **PySide6**.

> This is an MVP scaffold meant to get you productive quickly. It’s modular: add tools, shapes, and exporters without touching the core.

## Features (MVP)
- Shapes: Rectangle, Polygon, Circle, Line, Polyline, Keypoint
- Keyboard-friendly tooling (V to select/move, R rect, P polygon, C circle, L line, Y polyline, K keypoint)
- Open image folder, per-image labels, class dropdown
- Exports:
  - YOLO: boxes and segmentation polygons (YOLOv5/8 `-seg` style), keypoints (per-image JSON alongside YOLO if needed)
  - Pascal VOC XML (boxes); non-box shapes included as custom tags
  - COCO JSON: bboxes, polygons, and keypoints
- Project autosave (`.ua.json`) and per-image autosave (`.ua.<stem>.json`)

## Quickstart
```bash
pip install -r requirements.txt
python main.py
```
- Click **Open Folder** to select your image directory.
- Pick a class from the dropdown (or type a new one).
- Choose a tool (R/P/C/L/Y/K) and annotate.
- **Ctrl+S** to save per-image; **Export** menu to dump datasets.

## Notes
- Pascal VOC natively supports only bounding boxes; polygons/lines/keypoints are added under `<ua:extra>` in the XML for round-trip fidelity.
- YOLO keypoints are saved to `image_stem.keypoints.json` to avoid mixing formats.
- COCO exporter produces a minimal, single-file dataset (`coco_annotations.json`) for the current folder.

## Folder Layout
```
UniversalAnnotator/
  main.py
  app.py
  canvas.py
  shapes.py
  tools.py
  models.py
  io_utils.py
  exporters/
    __init__.py
    yolo.py
    voc.py
    coco.py
  requirements.txt
  README.md
```

## Roadmap
- Multi-object attributes, occlusion/visibility flags
- Instance segmentation (freehand brush), ellipse/rotated-rect
- Track IDs (video), interpolation, semi-automatic tools (GrabCut/SAM/YOLO assist)
- Team workflows, review/QA, active learning hooks
