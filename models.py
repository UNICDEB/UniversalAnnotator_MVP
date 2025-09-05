
import os, json, glob
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import cv2

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}

@dataclass
class Shape:
    id: str
    cls: str
    type: str  # 'rect', 'polygon', 'circle', 'line', 'polyline', 'keypoint'
    points: list    # list of [x,y] for polygon/polyline; for rect: [[x1,y1],[x2,y2]]; circle: [center,[edge]]; line: [[x1,y1],[x2,y2]]; keypoint: [[x,y]]
    extra: dict = field(default_factory=dict)

@dataclass
class ImageAnn:
    image_path: str
    width: int
    height: int
    shapes: List[Shape] = field(default_factory=list)

@dataclass
class ProjectState:
    folder: Optional[str] = None
    images: List[str] = field(default_factory=list)
    index: int = 0
    classes: List[str] = field(default_factory=list)
    anns: Dict[str, ImageAnn] = field(default_factory=dict)

    # def load_folder(self, folder: str):
    #     self.folder = folder
    #     imgs = []
    #     for ext in IMAGE_EXTS:
    #         imgs.extend(glob.glob(os.path.join(folder, f"*{ext}")))
    #     self.images = sorted(imgs)
    #     self.index = 0
    #     self.anns.clear()
    #     # try load project classes
    #     proj = os.path.join(folder, ".ua.json")
    #     if os.path.exists(proj):
    #         try:
    #             data = json.load(open(proj, "r", encoding="utf-8"))
    #             self.classes = data.get("classes", [])
    #         except Exception:
    #             pass

    
    def load_folder(self, folder: str):
        self.folder = folder
        imgs = []
        for ext in IMAGE_EXTS:
            imgs.extend(glob.glob(os.path.join(folder, f"*{ext}")))
        self.images = sorted(imgs)
        self.index = 0
        self.anns.clear()
        # Load classes from project file if exists
        proj = os.path.join(folder, ".ua.json")
        if os.path.exists(proj):
            try:
                data = json.load(open(proj, "r", encoding="utf-8"))
                self.classes = data.get("classes", [])
            except Exception:
                pass

        # Load per-image annotation files
        for img_path in self.images:
            stem = os.path.splitext(os.path.basename(img_path))[0]
            ann_path = os.path.join(folder, f".ua.{stem}.json")
            if os.path.exists(ann_path):
                try:
                    data = json.load(open(ann_path, "r", encoding="utf-8"))
                    shapes = [Shape(**s) for s in data.get("shapes", [])]
                    # Get image size
                    img = cv2.imread(img_path)
                    if img is not None:
                        h, w = img.shape[:2]
                    else:
                        h = w = 0
                    self.anns[img_path] = ImageAnn(img_path, w, h, shapes)
                except Exception:
                    pass



    def open_image(self, image_path: str):
        self.index = self.images.index(image_path)
        if image_path in self.anns:
            return
        img = cv2.imread(image_path)
        if img is None: raise RuntimeError(f"Failed to read image: {image_path}")
        h, w = img.shape[:2]
        per_image = self._per_image_path(image_path)
        if os.path.exists(per_image):
            data = json.load(open(per_image, "r", encoding="utf-8"))
            shapes = [Shape(**s) for s in data.get("shapes", [])]
            self.anns[image_path] = ImageAnn(image_path, w, h, shapes)
        else:
            self.anns[image_path] = ImageAnn(image_path, w, h, [])

    def save_current(self):
        if not self.images: return
        path = self.images[self.index]
        ann = self.anns.get(path)
        if not ann: return
        per_image = self._per_image_path(path)
        os.makedirs(os.path.dirname(per_image), exist_ok=True)
        json.dump({"shapes":[asdict(s) for s in ann.shapes]}, open(per_image, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        # project file
        if self.folder:
            json.dump({"classes": self.classes}, open(os.path.join(self.folder, ".ua.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def _per_image_path(self, image_path: str) -> str:
        stem = os.path.splitext(os.path.basename(image_path))[0]
        return os.path.join(self.folder, f".ua.{stem}.json")
