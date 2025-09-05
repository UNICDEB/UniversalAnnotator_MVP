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



# # canvas.py
# from PySide6.QtWidgets import (
#     QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
#     QMenu, QInputDialog, QMessageBox, QGraphicsRectItem, QGraphicsEllipseItem
# )
# from PySide6.QtGui import QAction, QPixmap, QImage, QPainterPath, QMouseEvent, QPainter, QColor, QPen, QBrush
# from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF, QEvent, QObject

# import cv2, uuid, os

# from models import Shape, ImageAnn

# # ----------------------------
# # Load classes from classes.txt
# # ----------------------------
# CLASS_FILE = "classes.txt"
# if not os.path.exists(CLASS_FILE):
#     # create empty file if missing
#     with open(CLASS_FILE, "w", encoding="utf-8") as f:
#         f.write("head\nmouth\n")  # optional defaults

# def load_classes_from_file(path=CLASS_FILE):
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             return [line.strip() for line in f if line.strip()]
#     except FileNotFoundError:
#         return []

# # ----------------------------
# # Helpers: color palette
# # ----------------------------
# PALETTE = [
#     QColor("red"), QColor("green"), QColor("blue"),
#     QColor("orange"), QColor("purple"), QColor("cyan"),
#     QColor("magenta"), QColor("yellow")
# ]

# def class_color(name: str):
#     return PALETTE[hash(name) % len(PALETTE)] if name else QColor("yellow")


# # ----------------------------
# # Handle item for resizing rectangles
# # ----------------------------
# class CornerHandle(QGraphicsRectItem):
#     HANDLE_SIZE = 8.0

#     def __init__(self, cx: float, cy: float, corner_idx: int, parent_rect: "RectItem"):
#         s = CornerHandle.HANDLE_SIZE
#         super().__init__(-s/2, -s/2, s, s)
#         self.setBrush(QBrush(QColor("white")))
#         self.setPen(QPen(QColor("black"), 1))
#         self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
#         self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
#         self.setAcceptHoverEvents(True)
#         self.corner_idx = corner_idx  # 0:tl,1:tr,2:br,3:bl
#         self.parent_rect = parent_rect
#         # position is relative to parent rect item; we will reparent to scene and manage coords externally

#     def hoverEnterEvent(self, ev):
#         self.setCursor(Qt.SizeAllCursor)
#         super().hoverEnterEvent(ev)

#     def hoverLeaveEvent(self, ev):
#         self.unsetCursor()
#         super().hoverLeaveEvent(ev)

#     def itemChange(self, change, value):
#         # value is new position in scene coordinates when ItemPositionChange
#         if change == QGraphicsItem.ItemPositionChange:
#             # Notify parent rect to update geometry based on handle positions
#             new_scene_pos = value
#             self.parent_rect.handle_moved(self, new_scene_pos)
#         return super().itemChange(change, value)


# # ----------------------------
# # Rectangle visual item holding shape id and handles
# # ----------------------------
# class RectItem(QGraphicsRectItem):
#     def __init__(self, rect: QRectF, shape_id: str, cls_name: str):
#         super().__init__(rect)
#         self.shape_id = shape_id
#         self.cls_name = cls_name
#         self.handles = []  # list of CornerHandle (scene-based)
#         self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
#         self.setFlag(QGraphicsRectItem.ItemIsMovable, True)

#     def set_pen(self, pen: QPen):
#         self.setPen(pen)

#     def show_handles(self, scene: QGraphicsScene):
#         # create 4 handles in scene coords
#         if self.handles:
#             for h in self.handles:
#                 scene.addItem(h)
#         else:
#             rect = self.rect()
#             corners = [
#                 self.mapToScene(rect.topLeft()),
#                 self.mapToScene(rect.topRight()),
#                 self.mapToScene(rect.bottomRight()),
#                 self.mapToScene(rect.bottomLeft())
#             ]
#             for idx, p in enumerate(corners):
#                 h = CornerHandle(p.x(), p.y(), idx, self)
#                 h.setPos(p)
#                 scene.addItem(h)
#                 self.handles.append(h)

#     def hide_handles(self, scene: QGraphicsScene):
#         for h in list(self.handles):
#             scene.removeItem(h)
#         self.handles = []

#     def handle_moved(self, handle: CornerHandle, new_scene_pos: QPointF):
#         """
#         Called by a handle when it moves. Recompute rect from handle positions.
#         """
#         # gather current handle scene positions (use handle objects)
#         pts = []
#         for h in self.handles:
#             pos = h.scenePos()
#             pts.append((pos.x(), pos.y()))
#         # But one handle passed value is new_scene_pos; replace its index
#         pts[handle.corner_idx] = (new_scene_pos.x(), new_scene_pos.y())

#         # Determine new bounding rect in scene coordinates
#         xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
#         x_min, x_max = min(xs), max(xs)
#         y_min, y_max = min(ys), max(ys)

#         # Convert scene rect to local coordinates of this item
#         top_left_scene = QPointF(x_min, y_min)
#         bottom_right_scene = QPointF(x_max, y_max)
#         top_left_local = self.mapFromScene(top_left_scene)
#         bottom_right_local = self.mapFromScene(bottom_right_scene)
#         new_rect = QRectF(top_left_local, bottom_right_local).normalized()

#         self.prepareGeometryChange()
#         self.setRect(new_rect)

#         # reposition handles to new corners (scene coords)
#         new_corners_scene = [
#             self.mapToScene(self.rect().topLeft()),
#             self.mapToScene(self.rect().topRight()),
#             self.mapToScene(self.rect().bottomRight()),
#             self.mapToScene(self.rect().bottomLeft())
#         ]
#         for h, p in zip(self.handles, new_corners_scene):
#             # move handle to p (scene coords)
#             h.setPos(p)


# # ----------------------------
# # Main AnnotCanvas
# # ----------------------------
# class AnnotCanvas(QGraphicsView):
#     def __init__(self, state):
#         super().__init__()
#         self.state = state
#         self.scene = QGraphicsScene(self)
#         self.setScene(self.scene)
#         self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
#         self.pix_item = None

#         self.mode = "select"   # rect, polygon, circle, line, keypoint, select
#         self.temp_points = []
#         self.preview_item = None

#         # editing state
#         self.edit_mode = False
#         self.rect_items = {}  # shape_id -> RectItem (for rects)
#         self.item_to_shape = {}  # QGraphicsItem -> Shape.id mapping (for saving)

#         # Enable zoom
#         self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
#         self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

#     # ---------------- Image loading ----------------
#     def load_image(self, path: str):
#         self.scene.clear()
#         self.rect_items.clear()
#         self.item_to_shape.clear()
#         img = cv2.imread(path)
#         if img is None:
#             return
#         h, w = img.shape[:2]
#         rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         qimg = QImage(rgb.data, w, h, w*3, QImage.Format_RGB888)
#         self.pix_item = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
#         self.scene.addItem(self.pix_item)
#         self.fitInView(self.pix_item, Qt.KeepAspectRatio)

#         # redraw saved shapes
#         ann = self.state.anns.get(path)
#         if ann:
#             for s in ann.shapes:
#                 self._create_visual_from_shape(s)

#     # ---------------- Zoom ----------------
#     def wheelEvent(self, event):
#         zoom_in, zoom_out = 1.25, 0.8
#         if event.angleDelta().y() > 0:
#             self.scale(zoom_in, zoom_in)
#         else:
#             self.scale(zoom_out, zoom_out)

#     # ---------------- Context menu (tool selection + edit toggle) ----------------
#     def contextMenuEvent(self, event):
#         menu = QMenu(self)
#         # tool actions
#         tools = {
#             "Rectangle": "rect", "Polygon": "polygon",
#             "Circle": "circle", "Line": "line", "Keypoint": "keypoint",
#             "Select/Move": "select"
#         }
#         for name, mode in tools.items():
#             a = QAction(name, self)
#             a.triggered.connect(lambda _, m=mode: self.set_mode(m))
#             menu.addAction(a)

#         menu.addSeparator()
#         # Edit mode toggle
#         edit_action = QAction(("Disable Edit Mode" if self.edit_mode else "Enable Edit Mode"), self)
#         edit_action.triggered.connect(self.toggle_edit_mode)
#         menu.addAction(edit_action)

#         menu.exec(event.globalPos())

#     def set_mode(self, mode: str):
#         self.mode = mode
#         self.temp_points.clear()
#         if self.preview_item:
#             self.scene.removeItem(self.preview_item)
#             self.preview_item = None

#     # ---------------- Class chooser (only called when shape completed) ----------------
#     def _choose_class(self):
#         classes = load_classes_from_file()
#         if not classes:
#             QMessageBox.warning(self, "No Classes", f"{CLASS_FILE} is empty or missing!")
#             return ""
#         cls, ok = QInputDialog.getItem(self, "Select Class",
#                                        "Choose class for annotation:", classes, 0, False)
#         return cls if ok else ""

#     # ---------------- Mouse events ----------------
#     def mousePressEvent(self, e: QMouseEvent):
#         if not self.state.images:
#             return
#         scene_pos = self.mapToScene(e.pos())
#         if self.mode in ("rect", "circle", "line"):
#             self.temp_points = [[scene_pos.x(), scene_pos.y()]]
#         elif self.mode in ("polygon", "polyline"):
#             self.temp_points.append([scene_pos.x(), scene_pos.y()])
#         elif self.mode == "keypoint":
#             sh = Shape(str(uuid.uuid4()), "", "keypoint", [[scene_pos.x(), scene_pos.y()]], {})
#             self._store_shape_with_class(sh)  # will ask class
#             self._create_visual_from_shape(sh)
#         else:
#             super().mousePressEvent(e)

#     def mouseMoveEvent(self, e: QMouseEvent):
#         if not self.temp_points:
#             return
#         scene_pos = self.mapToScene(e.pos())
#         if self.preview_item:
#             self.scene.removeItem(self.preview_item)
#             self.preview_item = None

#         pen = QPen(QColor("yellow"), 2, Qt.DashLine)
#         if self.mode == "rect":
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             rect = QRectF(min(p1[0], p2[0]), min(p1[1], p2[1]),
#                           abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
#             self.preview_item = self.scene.addRect(rect, pen)
#         elif self.mode == "circle":
#             c = self.temp_points[0]; edge = [scene_pos.x(), scene_pos.y()]
#             r = ((c[0] - edge[0])**2 + (c[1] - edge[1])**2) ** 0.5
#             rect = QRectF(c[0]-r, c[1]-r, 2*r, 2*r)
#             self.preview_item = self.scene.addEllipse(rect, pen)
#         elif self.mode == "line":
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             self.preview_item = self.scene.addLine(p1[0], p1[1], p2[0], p2[1], pen)
#         elif self.mode in ("polygon", "polyline"):
#             path = QPainterPath()
#             pts = [QPointF(p[0], p[1]) for p in self.temp_points]
#             if pts:
#                 path.moveTo(pts[0])
#                 for p in pts[1:]:
#                     path.lineTo(p)
#                 path.lineTo(QPointF(scene_pos.x(), scene_pos.y()))
#                 self.preview_item = self.scene.addPath(path, pen)

#     def mouseReleaseEvent(self, e: QMouseEvent):
#         scene_pos = self.mapToScene(e.pos())
#         if self.preview_item:
#             self.scene.removeItem(self.preview_item)
#             self.preview_item = None

#         sh = None
#         if self.mode == "rect" and self.temp_points:
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             if abs(p2[0]-p1[0]) > 2 and abs(p2[1]-p1[1]) > 2:
#                 sh = Shape(str(uuid.uuid4()), "", "rect", [p1, p2], {})
#         elif self.mode == "circle" and self.temp_points:
#             c = self.temp_points[0]; edge = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), "", "circle", [c, edge], {})
#         elif self.mode == "line" and self.temp_points:
#             p1 = self.temp_points[0]; p2 = [scene_pos.x(), scene_pos.y()]
#             sh = Shape(str(uuid.uuid4()), "", "line", [p1, p2], {})

#         if sh:
#             # Only here we ask the user for a class (so right-click/select won't trigger it)
#             self._store_shape_with_class(sh)
#             self._create_visual_from_shape(sh)
#             self.temp_points.clear()
#         else:
#             super().mouseReleaseEvent(e)

#     def mouseDoubleClickEvent(self, e: QMouseEvent):
#         if self.mode in ("polygon", "polyline") and len(self.temp_points) >= 2:
#             sh = Shape(str(uuid.uuid4()), "", self.mode, self.temp_points[:], {})
#             self._store_shape_with_class(sh)
#             self._create_visual_from_shape(sh)
#             self.temp_points.clear()
#         else:
#             super().mouseDoubleClickEvent(e)

#     # ---------------- Store shape (ask class) ----------------
#     def _store_shape_with_class(self, sh: Shape):
#         cls = self._choose_class()
#         if cls:
#             sh.cls = cls
#             if cls not in self.state.classes:
#                 self.state.classes.append(cls)
#         # append to project ann
#         path = self.state.images[self.state.index]
#         ann = self.state.anns.get(path)
#         ann.shapes.append(sh)

#     # ---------------- Create visual item from Shape ----------------
#     def _create_visual_from_shape(self, sh: Shape):
#         pen = QPen(class_color(sh.cls), 4)
#         pen.setCosmetic(True)
#         if sh.type == "rect":
#             (x1, y1), (x2, y2) = sh.points
#             rect = QRectF(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))
#             ritem = RectItem(rect, sh.id, sh.cls)
#             ritem.set_pen(pen)
#             self.scene.addItem(ritem)
#             # map shape id -> item
#             self.rect_items[sh.id] = ritem
#             self.item_to_shape[ritem] = sh
#             # show handles when in edit mode
#             if self.edit_mode:
#                 ritem.show_handles(self.scene)

#         elif sh.type == "circle":
#             (cx, cy), (ex, ey) = sh.points
#             r = ((cx - ex)**2 + (cy - ey)**2) ** 0.5
#             rect = QRectF(cx-r, cy-r, 2*r, 2*r)
#             item = self.scene.addEllipse(rect, pen)
#             self.item_to_shape[item] = sh
#             item.setFlag(item.ItemIsMovable, True)
#             item.setFlag(item.ItemIsSelectable, True)

#         elif sh.type == "line":
#             (x1, y1), (x2, y2) = sh.points
#             item = self.scene.addLine(x1, y1, x2, y2, pen)
#             self.item_to_shape[item] = sh
#             item.setFlag(item.ItemIsMovable, True)
#             item.setFlag(item.ItemIsSelectable, True)

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
#             item = self.scene.addPath(path, pen)
#             self.item_to_shape[item] = sh
#             item.setFlag(item.ItemIsMovable, True)
#             item.setFlag(item.ItemIsSelectable, True)

#         elif sh.type == "keypoint":
#             (x, y) = sh.points[0]
#             r = 5.0
#             item = self.scene.addEllipse(QRectF(x-r, y-r, 2*r, 2*r), pen, QBrush(class_color(sh.cls)))
#             self.item_to_shape[item] = sh
#             item.setFlag(item.ItemIsMovable, True)
#             item.setFlag(item.ItemIsSelectable, True)

#     # ---------------- Edit mode toggle ----------------
#     def toggle_edit_mode(self):
#         self.edit_mode = not self.edit_mode
#         # show/hide handles for all rect items
#         for sid, ritem in self.rect_items.items():
#             if self.edit_mode:
#                 ritem.show_handles(self.scene)
#             else:
#                 ritem.hide_handles(self.scene)

#     # ---------------- Delete selected shape ----------------
#     def delete_selected(self):
#         selected = self.scene.selectedItems()
#         for it in selected:
#             # remove from scene and from underlying storage
#             if it in self.item_to_shape:
#                 sh = self.item_to_shape.pop(it)
#                 # remove shape from project's ann list
#                 path = self.state.images[self.state.index]
#                 ann = self.state.anns.get(path)
#                 if ann:
#                     ann.shapes = [x for x in ann.shapes if x.id != sh.id]
#             # if rect item, also cleanup handles
#             if isinstance(it, RectItem):
#                 it.hide_handles(self.scene)
#                 self.rect_items.pop(it.shape_id, None)
#             self.scene.removeItem(it)

#     # ---------------- Utility: save positions from moved items back to shapes ----------------
#     def sync_scene_to_shapes(self):
#         """
#         Call when you want to persist moved/resized shapes back into state.anns
#         (e.g., before saving/export).
#         """
#         path = self.state.images[self.state.index]
#         ann = self.state.anns.get(path)
#         if not ann:
#             return
#         # build map id->shape
#         shape_map = {s.id: s for s in ann.shapes}
#         # update rectangles from RectItem visuals
#         for sid, ritem in self.rect_items.items():
#             rect = ritem.rect()
#             # convert local rect to scene coords of top-left & bottom-right
#             tl = ritem.mapToScene(rect.topLeft())
#             br = ritem.mapToScene(rect.bottomRight())
#             if sid in shape_map:
#                 shape_map[sid].points = [[tl.x(), tl.y()], [br.x(), br.y()]]
#         # update other items if needed (left as future improvement)


# canvas.py
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QMenu, QInputDialog, QMessageBox, QGraphicsRectItem, QGraphicsEllipseItem
)
from PySide6.QtGui import QAction, QPixmap, QImage, QPainterPath, QMouseEvent, QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF, QEvent, QObject

import cv2, uuid, os

from models import Shape, ImageAnn

# ----------------------------
# Load classes from classes.txt
# ----------------------------
CLASS_FILE = "classes.txt"
if not os.path.exists(CLASS_FILE):
    with open(CLASS_FILE, "w", encoding="utf-8") as f:
        f.write("head\nmouth\n")

def load_classes_from_file(path=CLASS_FILE):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

# ----------------------------
# Helpers: color palette
# ----------------------------
PALETTE = [
    QColor("red"), QColor("green"), QColor("blue"),
    QColor("orange"), QColor("purple"), QColor("cyan"),
    QColor("magenta"), QColor("yellow")
]

def class_color(name: str):
    return PALETTE[hash(name) % len(PALETTE)] if name else QColor("yellow")


# ----------------------------
# Handle item for resizing rectangles
# ----------------------------
class CornerHandle(QGraphicsRectItem):
    HANDLE_SIZE = 8.0

    def __init__(self, cx: float, cy: float, corner_idx: int, parent_rect: "RectItem"):
        s = CornerHandle.HANDLE_SIZE
        super().__init__(-s/2, -s/2, s, s)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(QColor("black"), 1))
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.corner_idx = corner_idx
        self.parent_rect = parent_rect

    def hoverEnterEvent(self, ev):
        self.setCursor(Qt.SizeAllCursor)
        super().hoverEnterEvent(ev)

    def hoverLeaveEvent(self, ev):
        self.unsetCursor()
        super().hoverLeaveEvent(ev)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            new_scene_pos = value
            self.parent_rect.handle_moved(self, new_scene_pos)
        return super().itemChange(change, value)


# ----------------------------
# Rectangle visual item holding shape id and handles
# ----------------------------
class RectItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, shape_id: str, cls_name: str):
        super().__init__(rect)
        self.shape_id = shape_id
        self.cls_name = cls_name
        self.handles = []
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def set_pen(self, pen: QPen):
        self.setPen(pen)

    def show_handles(self, scene: QGraphicsScene):
        if self.handles:
            for h in self.handles:
                scene.addItem(h)
        else:
            rect = self.rect()
            corners = [
                self.mapToScene(rect.topLeft()),
                self.mapToScene(rect.topRight()),
                self.mapToScene(rect.bottomRight()),
                self.mapToScene(rect.bottomLeft())
            ]
            for idx, p in enumerate(corners):
                h = CornerHandle(p.x(), p.y(), idx, self)
                h.setPos(p)
                scene.addItem(h)
                self.handles.append(h)

    def hide_handles(self, scene: QGraphicsScene):
        for h in list(self.handles):
            scene.removeItem(h)
        self.handles = []

    def handle_moved(self, handle: CornerHandle, new_scene_pos: QPointF):
        pts = []
        for h in self.handles:
            pos = h.scenePos()
            pts.append((pos.x(), pos.y()))
        pts[handle.corner_idx] = (new_scene_pos.x(), new_scene_pos.y())
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        top_left_scene = QPointF(x_min, y_min)
        bottom_right_scene = QPointF(x_max, y_max)
        top_left_local = self.mapFromScene(top_left_scene)
        bottom_right_local = self.mapFromScene(bottom_right_scene)
        new_rect = QRectF(top_left_local, bottom_right_local).normalized()
        self.prepareGeometryChange()
        self.setRect(new_rect)
        new_corners_scene = [
            self.mapToScene(self.rect().topLeft()),
            self.mapToScene(self.rect().topRight()),
            self.mapToScene(self.rect().bottomRight()),
            self.mapToScene(self.rect().bottomLeft())
        ]
        for h, p in zip(self.handles, new_corners_scene):
            h.setPos(p)


# ----------------------------
# Main AnnotCanvas
# ----------------------------
class AnnotCanvas(QGraphicsView):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
        self.pix_item = None

        self.mode = "select"   # rect, polygon, circle, line, keypoint, select
        self.temp_points = []
        self.preview_item = None

        self.edit_mode = False
        self.rect_items = {}
        self.item_to_shape = {}

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    # ---------------- Image loading ----------------
    def load_image(self, path: str):
        self.scene.clear()
        self.rect_items.clear()
        self.item_to_shape.clear()
        img = cv2.imread(path)
        if img is None:
            return
        h, w = img.shape[:2]
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, w*3, QImage.Format_RGB888)
        self.pix_item = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        self.scene.addItem(self.pix_item)
        self.fitInView(self.pix_item, Qt.KeepAspectRatio)

        ann = self.state.anns.get(path)
        if ann:
            for s in ann.shapes:
                self._create_visual_from_shape(s)

    # ---------------- Zoom ----------------
    def wheelEvent(self, event):
        zoom_in, zoom_out = 1.25, 0.8
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)

    # ---------------- Context menu ----------------
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        tools = {
            "Rectangle": "rect", "Polygon": "polygon",
            "Circle": "circle", "Line": "line", "Keypoint": "keypoint",
            "Select/Move": "select"
        }
        for name, mode in tools.items():
            a = QAction(name, self)
            a.triggered.connect(lambda _, m=mode: self.set_mode(m))
            menu.addAction(a)
        menu.addSeparator()
        edit_action = QAction(("Disable Edit Mode" if self.edit_mode else "Enable Edit Mode"), self)
        edit_action.triggered.connect(self.toggle_edit_mode)
        menu.addAction(edit_action)
        menu.exec(event.globalPos())

    def set_mode(self, mode: str):
        self.mode = mode
        self.temp_points.clear()
        if self.preview_item:
            self.scene.removeItem(self.preview_item)
            self.preview_item = None

    # ---------------- Class chooser ----------------
    def _choose_class(self):
        classes = load_classes_from_file()
        if not classes:
            QMessageBox.warning(self, "No Classes", f"{CLASS_FILE} is empty or missing!")
            return ""
        cls, ok = QInputDialog.getItem(self, "Select Class",
                                       "Choose class for annotation:", classes, 0, False)
        return cls if ok else ""

    # ---------------- Mouse events ----------------
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() != Qt.LeftButton:
            super().mousePressEvent(e)
            return
        scene_pos = self.mapToScene(e.pos())
        if self.mode in ("rect", "circle", "line"):
            self.temp_points = [[scene_pos.x(), scene_pos.y()]]
        elif self.mode in ("polygon", "polyline"):
            self.temp_points.append([scene_pos.x(), scene_pos.y()])
        elif self.mode == "keypoint":
            sh = Shape(str(uuid.uuid4()), "", "keypoint", [[scene_pos.x(), scene_pos.y()]], {})
            self._store_shape_with_class(sh)
            self._create_visual_from_shape(sh)
        else:
            super().mousePressEvent(e)


    def mouseMoveEvent(self, e: QMouseEvent):
        if not self.temp_points:
            return

        scene_pos = self.mapToScene(e.pos())

        # Remove old preview
        if self.preview_item:
            self.scene.removeItem(self.preview_item)
            self.preview_item = None

        pen = QPen(QColor("yellow"), 2, Qt.DashLine)

        if self.mode == "rect":
            p1 = self.temp_points[0]
            p2 = [scene_pos.x(), scene_pos.y()]
            rect = QRectF(min(p1[0], p2[0]), min(p1[1], p2[1]),
                        abs(p2[0]-p1[0]), abs(p2[1]-p1[1]))
            self.preview_item = self.scene.addRect(rect, pen)
        elif self.mode == "circle":
            c = self.temp_points[0]
            edge = [scene_pos.x(), scene_pos.y()]
            r = ((c[0]-edge[0])**2 + (c[1]-edge[1])**2)**0.5
            rect = QRectF(c[0]-r, c[1]-r, 2*r, 2*r)
            self.preview_item = self.scene.addEllipse(rect, pen)
        elif self.mode == "line":
            p1 = self.temp_points[0]
            p2 = [scene_pos.x(), scene_pos.y()]
            self.preview_item = self.scene.addLine(p1[0], p1[1], p2[0], p2[1], pen)
        elif self.mode in ("polygon", "polyline"):
            path = QPainterPath()
            pts = [QPointF(p[0], p[1]) for p in self.temp_points]
            if pts:
                path.moveTo(pts[0])
                for p in pts[1:]:
                    path.lineTo(p)
                path.lineTo(QPointF(scene_pos.x(), scene_pos.y()))
                self.preview_item = self.scene.addPath(path, pen)

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() != Qt.LeftButton:
            super().mouseReleaseEvent(e)
            return
        if not self.temp_points:
            super().mouseReleaseEvent(e)
            return

        scene_pos = self.mapToScene(e.pos())

        if self.preview_item:
            self.scene.removeItem(self.preview_item)
            self.preview_item = None

        sh = None
        if self.mode == "rect":
            p1 = self.temp_points[0]
            p2 = [scene_pos.x(), scene_pos.y()]
            if abs(p2[0]-p1[0])>2 and abs(p2[1]-p1[1])>2:
                sh = Shape(str(uuid.uuid4()), "", "rect", [p1,p2], {})
        elif self.mode == "circle":
            c = self.temp_points[0]
            edge = [scene_pos.x(), scene_pos.y()]
            sh = Shape(str(uuid.uuid4()), "", "circle", [c,edge], {})
        elif self.mode == "line":
            p1 = self.temp_points[0]
            p2 = [scene_pos.x(), scene_pos.y()]
            sh = Shape(str(uuid.uuid4()), "", "line", [p1,p2], {})

        if sh:
            self._store_shape_with_class(sh)
            self._create_visual_from_shape(sh)

        self.temp_points.clear()


    def mouseDoubleClickEvent(self, e: QMouseEvent):
        if self.mode in ("polygon", "polyline") and len(self.temp_points) >= 2:
            sh = Shape(str(uuid.uuid4()), "", self.mode, self.temp_points[:], {})
            self._store_shape_with_class(sh)
            self._create_visual_from_shape(sh)
            self.temp_points.clear()
        else:
            super().mouseDoubleClickEvent(e)

    def _store_shape_with_class(self, sh):
        cls = self._choose_class()
        if cls:
            sh.cls = cls
            if cls not in self.state.classes:
                self.state.classes.append(cls)
        # append to project ann
        path = self.state.images[self.state.index]
        ann = self.state.anns.get(path)
        ann.shapes.append(sh)


    def _draw_shape(self, sh):
        pen = QPen(class_color(getattr(sh, "cls", "")), 3)
        pen.setCosmetic(True)
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
            r = 4.0
            self.scene.addEllipse(QRectF(x - r, y - r, 2 * r, 2 * r), pen)

    def _create_visual_from_shape(self, sh):
        # For now, just call the existing drawing method
        self._draw_shape(sh)


        # ---------------- Edit mode toggle ----------------
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        # show/hide handles for all rect items
        for sid, ritem in self.rect_items.items():
            if self.edit_mode:
                ritem.show_handles(self.scene)
            else:
                ritem.hide_handles(self.scene)
8
