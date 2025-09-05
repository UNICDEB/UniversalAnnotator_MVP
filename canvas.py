# from PySide6.QtWidgets import (
#     QWidget,
#     QGraphicsView,
#     QGraphicsScene,
#     QGraphicsPixmapItem,
#     QComboBox,
#     QListWidget,
#     QLabel,
#     QPushButton,
#     QVBoxLayout,
# )

# from PySide6.QtGui import (
#     QPixmap,
#     QImage,
#     QPainterPath,
#     QMouseEvent,   # ✅ from QtGui
#     QPainter,      # ✅ needed for Antialiasing + drawing
# )

# from PySide6.QtCore import (
#     Qt,
#     QPointF,
#     QRectF,
# )

# import cv2
# import numpy as np
# import uuid

# from models import Shape, ImageAnn



# class AnnotCanvas(QGraphicsView):
#     def __init__(self, state):
#         super().__init__()
#         self.state = state
#         self.scene = QGraphicsScene(self)
#         self.setScene(self.scene)
#         self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
#         self.pix = None
#         self.active_cls = ""
#         self.mode = "select"  # 'rect','polygon','circle','line','polyline','keypoint'
#         self.temp_points = []
#         self.setMouseTracking(True)

#     def load_image(self, path: str):
#         self.scene.clear()
#         img = cv2.imread(path)
#         h, w = img.shape[:2]
#         rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         qimg = QImage(rgb.data, w, h, w*3, QImage.Format_RGB888)
#         self.pix = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
#         self.scene.addItem(self.pix)
#         self.fitInView(self.pix, Qt.KeepAspectRatio)
#         # redraw shapes
#         ann = self.state.anns.get(path)
#         if ann:
#             for s in ann.shapes:
#                 self._draw_shape(s)

#     def set_active_class(self, cls: str):
#         if cls and cls not in self.state.classes:
#             self.state.classes.append(cls)
#         self.active_cls = cls

#     def keyPressEvent(self, e):
#         keymap = {
#             Qt.Key_V: "select",
#             Qt.Key_R: "rect",
#             Qt.Key_P: "polygon",
#             Qt.Key_C: "circle",
#             Qt.Key_L: "line",
#             Qt.Key_Y: "polyline",
#             Qt.Key_K: "keypoint",
#         }
#         if e.key() in keymap:
#             self.mode = keymap[e.key()]
#         elif e.key() == Qt.Key_Escape:
#             self.temp_points.clear()
#         else:
#             super().keyPressEvent(e)

#     def mousePressEvent(self, e: QMouseEvent):
#         if not self.state.images: return
#         scene_pos = self.mapToScene(e.pos())
#         if self.mode in ("rect","circle","line"):
#             self.temp_points = [ [scene_pos.x(), scene_pos.y()] ]
#         elif self.mode in ("polygon","polyline"):
#             self.temp_points.append([scene_pos.x(), scene_pos.y()])
#         elif self.mode == "keypoint":
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "keypoint", [[scene_pos.x(), scene_pos.y()]], {})
#             self._store_shape(sh)
#             self._draw_shape(sh)
#         else:
#             super().mousePressEvent(e)

#     def mouseReleaseEvent(self, e: QMouseEvent):
#         scene_pos = self.mapToScene(e.pos())
#         if self.mode == "rect" and self.temp_points:
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "rect", [p1, p2], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         elif self.mode == "circle" and self.temp_points:
#             c = self.temp_points[0]; edge = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "circle", [c, edge], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         elif self.mode == "line" and self.temp_points:
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "line", [p1, p2], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         elif self.mode in ("polygon","polyline"):
#             # Finish on right-click
#             pass
#         else:
#             super().mouseReleaseEvent(e)

#     def mouseDoubleClickEvent(self, e: QMouseEvent):
#         if self.mode in ("polygon","polyline") and len(self.temp_points) >= 2:
#             sh = Shape(str(uuid.uuid4()), self.active_cls, self.mode, self.temp_points[:], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         else:
#             super().mouseDoubleClickEvent(e)

#     def _store_shape(self, sh: Shape):
#         path = self.state.images[self.state.index]
#         ann = self.state.anns.get(path)
#         ann.shapes.append(sh)

#     def _draw_shape(self, sh: Shape):
#         pen_width = 2
#         if sh.type == "rect":
#             (x1,y1),(x2,y2) = sh.points
#             rect = QRectF(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
#             self.scene.addRect(rect)
#         elif sh.type == "circle":
#             (cx,cy),(ex,ey) = sh.points
#             r = ((cx-ex)**2 + (cy-ey)**2)**0.5
#             rect = QRectF(cx-r, cy-r, 2*r, 2*r)
#             self.scene.addEllipse(rect)
#         elif sh.type == "line":
#             (x1,y1),(x2,y2) = sh.points
#             self.scene.addLine(x1,y1,x2,y2)
#         elif sh.type in ("polygon","polyline"):
#             path = QPainterPath()
#             pts = [QPointF(x,y) for x,y in sh.points]
#             if not pts: return
#             path.moveTo(pts[0])
#             for p in pts[1:]:
#                 path.lineTo(p)
#             if sh.type == "polygon":
#                 path.closeSubpath()
#             self.scene.addPath(path)
#         elif sh.type == "keypoint":
#             (x,y) = sh.points[0]
#             r = 3.0
#             self.scene.addEllipse(QRectF(x-r, y-r, 2*r, 2*r))

# from PySide6.QtWidgets import (
#     QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
#     QMenu      # ✅ keep QMenu here
# )

# from PySide6.QtGui import (
#     QPixmap, QImage, QPainterPath, QMouseEvent, QPainter, QColor,
#     QAction    # ✅ QAction must come from QtGui
# )

# from PySide6.QtCore import Qt, QPointF, QRectF
# from PySide6.QtGui import QPen, QColor
# import cv2, numpy as np, uuid, random

# from models import Shape, ImageAnn


# # 🎨 Fixed color map for classes
# COLOR_MAP = {}

# def get_color(cls: str) -> QColor:
#     if cls not in COLOR_MAP:
#         COLOR_MAP[cls] = QColor(*[random.randint(50, 255) for _ in range(3)])
#     return COLOR_MAP[cls]


# class AnnotCanvas(QGraphicsView):
#     def __init__(self, state):
#         super().__init__()
#         self.state = state
#         self.scene = QGraphicsScene(self)
#         self.setScene(self.scene)
#         self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
#         self.pix = None
#         self.active_cls = ""
#         self.mode = "select"  # rect, polygon, circle, line, keypoint
#         self.temp_points = []
#         self.setMouseTracking(True)

#         # ✅ Enable zoom
#         self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
#         self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

#     def load_image(self, path: str):
#         self.scene.clear()
#         img = cv2.imread(path)
#         h, w = img.shape[:2]
#         rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         qimg = QImage(rgb.data, w, h, w*3, QImage.Format_RGB888)
#         self.pix = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
#         self.scene.addItem(self.pix)
#         self.fitInView(self.pix, Qt.KeepAspectRatio)

#         ann = self.state.anns.get(path)
#         if ann:
#             for s in ann.shapes:
#                 self._draw_shape(s)

#     def set_active_class(self, cls: str):
#         if cls and cls not in self.state.classes:
#             self.state.classes.append(cls)
#         self.active_cls = cls

#     # ✅ Zoom with mouse wheel
#     def wheelEvent(self, event):
#         zoom_in, zoom_out = 1.25, 0.8
#         if event.angleDelta().y() > 0:
#             self.scale(zoom_in, zoom_in)
#         else:
#             self.scale(zoom_out, zoom_out)

#     # ✅ Context menu for choosing shape type
#     def contextMenuEvent(self, event):
#         menu = QMenu(self)
#         actions = {
#             "Rectangle": "rect",
#             "Polygon": "polygon",
#             "Circle": "circle",
#             "Line": "line",
#             "Keypoint": "keypoint"
#         }
#         for name, mode in actions.items():
#             act = QAction(name, self)
#             act.triggered.connect(lambda _, m=mode: self._set_mode(m))
#             menu.addAction(act)
#         menu.exec(event.globalPos())

#     def _set_mode(self, mode):
#         self.mode = mode
#         self.temp_points.clear()

#     def mousePressEvent(self, e: QMouseEvent):
#         if not self.state.images: return
#         scene_pos = self.mapToScene(e.pos())
#         if self.mode in ("rect", "circle", "line"):
#             self.temp_points = [[scene_pos.x(), scene_pos.y()]]
#         elif self.mode in ("polygon", "polyline"):
#             self.temp_points.append([scene_pos.x(), scene_pos.y()])
#         elif self.mode == "keypoint":
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "keypoint",
#                        [[scene_pos.x(), scene_pos.y()]], {})
#             self._store_shape(sh)
#             self._draw_shape(sh)
#         else:
#             super().mousePressEvent(e)

#     def mouseReleaseEvent(self, e: QMouseEvent):
#         scene_pos = self.mapToScene(e.pos())
#         if self.mode == "rect" and self.temp_points:
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "rect", [p1, p2], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         elif self.mode == "circle" and self.temp_points:
#             c = self.temp_points[0]; edge = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "circle", [c, edge], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         elif self.mode == "line" and self.temp_points:
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), self.active_cls, "line", [p1, p2], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         else:
#             super().mouseReleaseEvent(e)

#     def mouseDoubleClickEvent(self, e: QMouseEvent):
#         if self.mode in ("polygon", "polyline") and len(self.temp_points) >= 2:
#             sh = Shape(str(uuid.uuid4()), self.active_cls, self.mode,
#                        self.temp_points[:], {})
#             self._store_shape(sh); self._draw_shape(sh)
#             self.temp_points.clear()
#         else:
#             super().mouseDoubleClickEvent(e)

#     def _store_shape(self, sh: Shape):
#         path = self.state.images[self.state.index]
#         ann = self.state.anns.get(path)
#         ann.shapes.append(sh)


#     def _draw_shape(self, sh: Shape):
#         # Assign color per class (deterministic by class name)
#         colors = [
#             QColor("red"), QColor("green"), QColor("blue"),
#             QColor("orange"), QColor("purple"), QColor("cyan")
#         ]
#         color = colors[hash(sh.cls) % len(colors)] if sh.cls else QColor("yellow")

#         pen = QPen(color, 3)   # ✅ thicker lines, solid color
#         pen.setCosmetic(True)  # ✅ keep width constant when zooming

#         if sh.type == "rect":
#             (x1, y1), (x2, y2) = sh.points
#             rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
#             self.scene.addRect(rect, pen)
#         elif sh.type == "circle":
#             (cx, cy), (ex, ey) = sh.points
#             r = ((cx - ex) ** 2 + (cy - ey) ** 2) ** 0.5
#             rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
#             self.scene.addEllipse(rect, pen)
#         elif sh.type == "line":
#             (x1, y1), (x2, y2) = sh.points
#             self.scene.addLine(x1, y1, x2, y2, pen)
#         elif sh.type in ("polygon", "polyline"):
#             path = QPainterPath()
#             pts = [QPointF(x, y) for x, y in sh.points]
#             if not pts:
#                 return
#             path.moveTo(pts[0])
#             for p in pts[1:]:
#                 path.lineTo(p)
#             if sh.type == "polygon":
#                 path.closeSubpath()
#             self.scene.addPath(path, pen)
#         elif sh.type == "keypoint":
#             (x, y) = sh.points[0]
#             r = 4.0
#             self.scene.addEllipse(QRectF(x - r, y - r, 2 * r, 2 * r), pen)



from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QMenu
)

from PySide6.QtGui import (
    QPixmap, QImage, QPainterPath, QMouseEvent, QPainter,
    QAction, QPen, QColor
)

from PySide6.QtCore import Qt, QPointF, QRectF
import cv2, numpy as np, uuid

from models import Shape, ImageAnn


# 🎨 Fixed color map for classes
COLOR_MAP = {}

def get_color(cls: str) -> QColor:
    """Return consistent color for each class."""
    if cls not in COLOR_MAP:
        # Pick bright deterministic color based on class name hash
        palette = [
            QColor("red"), QColor("green"), QColor("blue"),
            QColor("orange"), QColor("purple"), QColor("cyan"),
            QColor("magenta"), QColor("yellow")
        ]
        COLOR_MAP[cls] = palette[hash(cls) % len(palette)]
    return COLOR_MAP[cls]


class AnnotCanvas(QGraphicsView):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
        self.pix = None
        self.active_cls = ""
        self.mode = "select"  # rect, polygon, circle, line, keypoint
        self.temp_points = []
        self.setMouseTracking(True)

        # ✅ Enable zoom
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def load_image(self, path: str):
        self.scene.clear()
        img = cv2.imread(path)
        h, w = img.shape[:2]
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, w*3, QImage.Format_RGB888)
        self.pix = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        self.scene.addItem(self.pix)
        self.fitInView(self.pix, Qt.KeepAspectRatio)

        ann = self.state.anns.get(path)
        if ann:
            for s in ann.shapes:
                self._draw_shape(s)

    def set_active_class(self, cls: str):
        """Set the current active class (only once, no partial names)."""
        cls = cls.strip()
        if cls and cls not in self.state.classes:
            self.state.classes.append(cls)
        self.active_cls = cls

    # ✅ Zoom with mouse wheel
    def wheelEvent(self, event):
        zoom_in, zoom_out = 1.25, 0.8
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)

    # ✅ Context menu for choosing shape type
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        actions = {
            "Rectangle": "rect",
            "Polygon": "polygon",
            "Circle": "circle",
            "Line": "line",
            "Keypoint": "keypoint"
        }
        for name, mode in actions.items():
            act = QAction(name, self)
            act.triggered.connect(lambda _, m=mode: self._set_mode(m))
            menu.addAction(act)
        menu.exec(event.globalPos())

    def _set_mode(self, mode):
        self.mode = mode
        self.temp_points.clear()

    def mousePressEvent(self, e: QMouseEvent):
        if not self.state.images: 
            return
        scene_pos = self.mapToScene(e.pos())
        if self.mode in ("rect", "circle", "line"):
            self.temp_points = [[scene_pos.x(), scene_pos.y()]]
        elif self.mode in ("polygon", "polyline"):
            self.temp_points.append([scene_pos.x(), scene_pos.y()])
        elif self.mode == "keypoint":
            sh = Shape(str(uuid.uuid4()), self.active_cls, "keypoint",
                       [[scene_pos.x(), scene_pos.y()]], {})
            self._store_shape(sh)
            self._draw_shape(sh)
        else:
            super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent):
        scene_pos = self.mapToScene(e.pos())
        if self.mode == "rect" and self.temp_points:
            p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
            sh = Shape(str(uuid.uuid4()), self.active_cls, "rect", [p1, p2], {})
            self._store_shape(sh); self._draw_shape(sh)
            self.temp_points.clear()
        elif self.mode == "circle" and self.temp_points:
            c = self.temp_points[0]; edge = [scene_pos.x(), scene_pos.y()]
            sh = Shape(str(uuid.uuid4()), self.active_cls, "circle", [c, edge], {})
            self._store_shape(sh); self._draw_shape(sh)
            self.temp_points.clear()
        elif self.mode == "line" and self.temp_points:
            p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
            sh = Shape(str(uuid.uuid4()), self.active_cls, "line", [p1, p2], {})
            self._store_shape(sh); self._draw_shape(sh)
            self.temp_points.clear()
        else:
            super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e: QMouseEvent):
        if self.mode in ("polygon", "polyline") and len(self.temp_points) >= 2:
            sh = Shape(str(uuid.uuid4()), self.active_cls, self.mode,
                       self.temp_points[:], {})
            self._store_shape(sh); self._draw_shape(sh)
            self.temp_points.clear()
        else:
            super().mouseDoubleClickEvent(e)

    def _store_shape(self, sh: Shape):
        path = self.state.images[self.state.index]
        ann = self.state.anns.get(path)
        ann.shapes.append(sh)

    def _draw_shape(self, sh: Shape):
        # ✅ Consistent bright colors per class
        color = get_color(sh.cls) if sh.cls else QColor("yellow")

        # ✅ Thicker visible lines
        pen = QPen(color, 4)
        pen.setCosmetic(True)  # keep width constant during zoom

        if sh.type == "rect":
            (x1, y1), (x2, y2) = sh.points
            rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            self.scene.addRect(rect, pen)
        elif sh.type == "circle":
            (cx, cy), (ex, ey) = sh.points
            r = ((cx - ex) ** 2 + (cy - ey) ** 2) ** 0.5
            rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
            self.scene.addEllipse(rect, pen)
        elif sh.type == "line":
            (x1, y1), (x2, y2) = sh.points
            self.scene.addLine(x1, y1, x2, y2, pen)
        elif sh.type in ("polygon", "polyline"):
            path = QPainterPath()
            pts = [QPointF(x, y) for x, y in sh.points]
            if not pts:
                return
            path.moveTo(pts[0])
            for p in pts[1:]:
                path.lineTo(p)
            if sh.type == "polygon":
                path.closeSubpath()
            self.scene.addPath(path, pen)
        elif sh.type == "keypoint":
            (x, y) = sh.points[0]
            r = 5.0
            self.scene.addEllipse(QRectF(x - r, y - r, 2 * r, 2 * r), pen)
