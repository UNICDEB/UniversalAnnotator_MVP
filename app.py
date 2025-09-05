# import os, sys, json

# from PySide6.QtWidgets import (
#     QApplication,
#     QMainWindow,
#     QLabel,
#     QPushButton,
#     QFileDialog,
#     QMessageBox,
#     QGraphicsScene,
#     QGraphicsView,
#     QVBoxLayout,
#     QHBoxLayout,
#     QWidget,
#     QComboBox,
#     QListWidget,
#     QListWidgetItem,
#     QMenuBar,   # ✅ added
#     QMenu       # ✅ usually used with QMenuBar
# )

# from PySide6.QtGui import (
#     QAction,
# )

# from PySide6.QtCore import (
#     Qt,
#     QDir,
# )

# from canvas import AnnotCanvas
# from models import ProjectState
# from exporters.yolo import export_yolo_folder
# from exporters.voc import export_voc_folder
# from exporters.coco import export_coco_folder



# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Universal Annotator (MVP)")
#         self.resize(1200, 800)

#         self.state = ProjectState()
#         self._build_ui()
#         self._wire_events()

#     def _build_ui(self):
#         central = QWidget(self)
#         root = QVBoxLayout(central)

#         # Top bar
#         top = QHBoxLayout()
#         self.open_btn = QPushButton("Open Folder")
#         self.class_label = QLabel("Class:")
#         self.class_combo = QComboBox()
#         self.class_combo.setEditable(True)
#         self.prev_btn = QPushButton("⟨ Prev")
#         self.next_btn = QPushButton("Next ⟩")
#         self.save_btn = QPushButton("Save (Ctrl+S)")

#         top.addWidget(self.open_btn)
#         top.addStretch(1)
#         top.addWidget(self.class_label)
#         top.addWidget(self.class_combo, 2)
#         top.addStretch(1)
#         top.addWidget(self.prev_btn)
#         top.addWidget(self.next_btn)
#         top.addWidget(self.save_btn)

#         # Canvas
#         mid = QHBoxLayout()
#         self.canvas = AnnotCanvas(self.state)
#         self.list = QListWidget()
#         self.list.setMaximumWidth(260)
#         mid.addWidget(self.canvas, 1)
#         mid.addWidget(self.list)

#         root.addLayout(top)
#         root.addLayout(mid, 1)

#         self.setCentralWidget(central)

#         # Menu
#         menubar = self.menuBar() if isinstance(self.menuBar(), QMenuBar) else QMenuBar(self)
#         file_menu = menubar.addMenu("&File")
#         self.export_menu = menubar.addMenu("&Export")

#         act_open = QAction("Open Folder...", self); act_open.triggered.connect(self._open_folder)
#         act_save = QAction("Save", self); act_save.setShortcut("Ctrl+S"); act_save.triggered.connect(self._save_current)
#         file_menu.addAction(act_open)
#         file_menu.addAction(act_save)

#         act_yolo = QAction("Export YOLO (txt)", self); act_yolo.triggered.connect(self._export_yolo)
#         act_voc = QAction("Export Pascal VOC (xml)", self); act_voc.triggered.connect(self._export_voc)
#         act_coco = QAction("Export COCO (json)", self); act_coco.triggered.connect(self._export_coco)
#         self.export_menu.addAction(act_yolo)
#         self.export_menu.addAction(act_voc)
#         self.export_menu.addAction(act_coco)

#     def _wire_events(self):
#         self.open_btn.clicked.connect(self._open_folder)
#         self.prev_btn.clicked.connect(lambda: self._move_image(-1))
#         self.next_btn.clicked.connect(lambda: self._move_image(1))
#         self.save_btn.clicked.connect(self._save_current)
#         self.list.itemSelectionChanged.connect(self._on_select_image)
#         self.class_combo.currentTextChanged.connect(self._on_class_change)

#     def _open_folder(self):
#         folder = QFileDialog.getExistingDirectory(self, "Select Image Folder", QDir.homePath())
#         if not folder: return
#         self.state.load_folder(folder)
#         self._refresh_list()
#         self.class_combo.clear()
#         self.class_combo.addItems(self.state.classes or [])
#         if self.state.images:
#             self.list.setCurrentRow(0)

#     def _refresh_list(self):
#         self.list.clear()
#         for p in self.state.images:
#             item = QListWidgetItem(os.path.basename(p))
#             item.setData(Qt.UserRole, p)
#             self.list.addItem(item)

#     def _on_select_image(self):
#         items = self.list.selectedItems()
#         if not items: return
#         path = items[0].data(Qt.UserRole)
#         self.state.open_image(path)
#         self.canvas.load_image(path)

#     def _move_image(self, delta):
#         row = self.list.currentRow()
#         if row < 0: return
#         new_row = max(0, min(self.list.count()-1, row + delta))
#         self.list.setCurrentRow(new_row)

#     def _save_current(self):
#         try:
#             self.state.save_current()
#             QMessageBox.information(self, "Saved", "Annotations saved.")
#         except Exception as e:
#             QMessageBox.critical(self, "Save Failed", str(e))

#     def _on_class_change(self, text):
#         self.canvas.set_active_class(text.strip())

#     def _export_yolo(self):
#         try:
#             export_yolo_folder(self.state)
#             QMessageBox.information(self, "Export", "YOLO export complete.")
#         except Exception as e:
#             QMessageBox.critical(self, "Export Failed", str(e))

#     def _export_voc(self):
#         try:
#             export_voc_folder(self.state)
#             QMessageBox.information(self, "Export", "VOC export complete.")
#         except Exception as e:
#             QMessageBox.critical(self, "Export Failed", str(e))

#     def _export_coco(self):
#         try:
#             export_coco_folder(self.state)
#             QMessageBox.information(self, "Export", "COCO export complete.")
#         except Exception as e:
#             QMessageBox.critical(self, "Export Failed", str(e))

# def run_app():
#     app = QApplication(sys.argv)
#     win = MainWindow()
#     win.show()
#     sys.exit(app.exec())


# app.py
import os
import sys
import json
import uuid
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGraphicsScene,
    QGraphicsView,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QMenu,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QDir

from canvas import AnnotCanvas
from models import ProjectState
from exporters.yolo import export_yolo_folder
from exporters.voc import export_voc_folder
from exporters.coco import export_coco_folder


class ClassSelectorDialog(QDialog):
    """
    Simple dialog that shows a combo of existing classes plus a line edit
    where user can type a new class. get_class() returns chosen/new class or None.
    """

    def __init__(self, classes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select / Add Class")
        self.setModal(True)
        self.resize(320, 120)

        self._combo = QComboBox(self)
        self._combo.setEditable(False)
        self._combo.addItems(classes or [])

        self._line = QLineEdit(self)
        self._line.setPlaceholderText("Or enter new class name...")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose existing class or type a new one:"))
        layout.addWidget(self._combo)
        layout.addWidget(self._line)
        layout.addWidget(buttons)

    def get_class(self) -> Optional[str]:
        new_name = self._line.text().strip()
        if new_name:
            return new_name
        sel = self._combo.currentText().strip()
        return sel if sel else None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Annotator (MVP)")
        self.resize(1200, 800)

        self.state = ProjectState()
        self._build_ui()
        self._wire_events()

    def _build_ui(self):
        central = QWidget(self)
        root = QVBoxLayout(central)

        # Top bar
        top = QHBoxLayout()
        self.open_btn = QPushButton("Open Folder")
        self.class_label = QLabel("Class:")
        self.class_combo = QComboBox()
        self.class_combo.setEditable(True)
        self.prev_btn = QPushButton("⟨ Prev")
        self.next_btn = QPushButton("Next ⟩")
        self.save_btn = QPushButton("Save (Ctrl+S)")

        top.addWidget(self.open_btn)
        top.addStretch(1)
        top.addWidget(self.class_label)
        top.addWidget(self.class_combo, 2)
        top.addStretch(1)
        top.addWidget(self.prev_btn)
        top.addWidget(self.next_btn)
        top.addWidget(self.save_btn)

        # Canvas + side list
        mid = QHBoxLayout()
        self.canvas = AnnotCanvas(self.state)
        # If canvas doesn't provide ask_class_name, monkey-patch it to use our dialog:
        if not hasattr(self.canvas, "ask_class_name"):
            self.canvas.ask_class_name = self._canvas_ask_class_name

        self.list = QListWidget()
        self.list.setMaximumWidth(260)
        mid.addWidget(self.canvas, 1)
        mid.addWidget(self.list)

        root.addLayout(top)
        root.addLayout(mid, 1)

        self.setCentralWidget(central)

        # Menu
        menubar = self.menuBar() if isinstance(self.menuBar(), QMenuBar) else QMenuBar(self)
        file_menu = menubar.addMenu("&File")
        self.export_menu = menubar.addMenu("&Export")

        act_open = QAction("Open Folder...", self)
        act_open.triggered.connect(self._open_folder)
        act_save = QAction("Save", self)
        act_save.setShortcut("Ctrl+S")
        act_save.triggered.connect(self._save_current)
        file_menu.addAction(act_open)
        file_menu.addAction(act_save)

        act_yolo = QAction("Export YOLO (txt)", self)
        act_yolo.triggered.connect(self._export_yolo)
        act_voc = QAction("Export Pascal VOC (xml)", self)
        act_voc.triggered.connect(self._export_voc)
        act_coco = QAction("Export COCO (json)", self)
        act_coco.triggered.connect(self._export_coco)
        self.export_menu.addAction(act_yolo)
        self.export_menu.addAction(act_voc)
        self.export_menu.addAction(act_coco)

    def _wire_events(self):
        self.open_btn.clicked.connect(self._open_folder)
        self.prev_btn.clicked.connect(lambda: self._move_image(-1))
        self.next_btn.clicked.connect(lambda: self._move_image(1))
        self.save_btn.clicked.connect(self._save_current)
        self.list.itemSelectionChanged.connect(self._on_select_image)
        self.class_combo.currentTextChanged.connect(self._on_class_change)

    # ---------- Folder / images ----------
    def _open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder", QDir.homePath())
        if not folder:
            return
        self.state.load_folder(folder)
        # populate UI lists
        self._refresh_list()
        # load saved classes into combo
        self.class_combo.clear()
        self.class_combo.addItems(self.state.classes or [])
        # If images exist, select the first
        if self.state.images:
            self.list.setCurrentRow(0)

    def _refresh_list(self):
        self.list.clear()
        for p in self.state.images:
            item = QListWidgetItem(os.path.basename(p))
            item.setData(Qt.UserRole, p)
            self.list.addItem(item)

    def _on_select_image(self):
        items = self.list.selectedItems()
        if not items:
            return
        path = items[0].data(Qt.UserRole)
        try:
            self.state.open_image(path)
            self.canvas.load_image(path)
            # update active class in canvas
            cur = self.class_combo.currentText().strip()
            if cur:
                self.canvas.set_active_class(cur)
        except Exception as e:
            QMessageBox.critical(self, "Open Failed", str(e))

    def _move_image(self, delta: int):
        row = self.list.currentRow()
        if row < 0:
            return
        new_row = max(0, min(self.list.count() - 1, row + delta))
        self.list.setCurrentRow(new_row)

    # ---------- Save / Export ----------
    def _save_current(self):
        try:
            # Save per-image project annotation (.ua.<stem>.json)
            self.state.save_current()
            QMessageBox.information(self, "Saved", "Annotations saved (project file).")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    def _on_class_change(self, text: str):
        t = text.strip()
        if t:
            # add to project classes (deduplicate)
            if t not in self.state.classes:
                self.state.classes.append(t)
                # persist classes to project file immediately
                if self.state.folder:
                    try:
                        with open(os.path.join(self.state.folder, ".ua.json"), "w", encoding="utf-8") as f:
                            json.dump({"classes": self.state.classes}, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
            # tell canvas current class
            try:
                self.canvas.set_active_class(t)
            except Exception:
                pass

    def _export_yolo(self):
        try:
            # Export to default exporter (this will create an export folder by default)
            export_yolo_folder(self.state)
            # Also save per-image annotation files beside images (optional behavior)
            self._save_annotations_same_dir(format="yolo")
            QMessageBox.information(self, "Export", "YOLO export complete.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _export_voc(self):
        try:
            export_voc_folder(self.state)
            self._save_annotations_same_dir(format="voc")
            QMessageBox.information(self, "Export", "VOC export complete.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _export_coco(self):
        try:
            export_coco_folder(self.state)
            # COCO is usually aggregated into one file; we still also write per-image JSON copies
            self._save_annotations_same_dir(format="coco")
            QMessageBox.information(self, "Export", "COCO export complete.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    # ---------- Helpers ----------
    def _canvas_ask_class_name(self) -> Optional[str]:
        """
        Fallback ask-class dialog that will be used if canvas has no own ask_class_name.
        It also stores the class into project state and updates the combo.
        """
        dlg = ClassSelectorDialog(self.state.classes or [], parent=self)
        if dlg.exec() == QDialog.Accepted:
            cls = dlg.get_class()
            if cls:
                if cls not in self.state.classes:
                    self.state.classes.append(cls)
                    # persist project classes
                    if self.state.folder:
                        try:
                            with open(os.path.join(self.state.folder, ".ua.json"), "w", encoding="utf-8") as f:
                                json.dump({"classes": self.state.classes}, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                    # update combobox (avoid duplicates)
                    if self.class_combo.findText(cls) == -1:
                        self.class_combo.addItem(cls)
                return cls
        return None

    def _save_annotations_same_dir(self, format: str = "yolo"):
        """
        Writes per-image annotation files into the same directory as each image
        using a small sidecar format depending on 'format':
         - 'yolo' writes <image>.txt with yolo lines (best effort)
         - 'voc' writes <image>.xml (calls exporter per-image is complex; we do a simple JSON sidecar)
         - 'coco' writes <image>.json with its annotations (simple sidecar)
        Note: This function is intentionally conservative — it writes sidecar JSON who holds shapes read from state.anns
        """
        if not self.state.folder:
            return

        for img in self.state.images:
            ann = self.state.anns.get(img)
            if not ann:
                continue
            base = os.path.splitext(img)[0]
            # simple JSON sidecar capturing shapes (round-trip friendly)
            out_path = base + ".annotations.json"
            payload = {
                "image": os.path.basename(img),
                "width": ann.width,
                "height": ann.height,
                "shapes": [ {
                    "id": s.id,
                    "class": s.cls,
                    "type": s.type,
                    "points": s.points,
                    "extra": s.extra
                } for s in ann.shapes ]
            }
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
            except Exception as e:
                # non-fatal; continue with other images
                print("Failed to write sidecar for", img, ":", e)

        # Note: advanced per-format exact exporters can be added here (YOLO bbox per-image, VOC per-image, etc.)

def run_app():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


