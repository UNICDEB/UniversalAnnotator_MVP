
import os
from lxml import etree
from models import ProjectState
from io_utils import ensure_dir, image_stem

def export_voc_folder(state: ProjectState, out_dir=None):
    if out_dir is None: out_dir = os.path.join(state.folder, "export_voc")
    ensure_dir(out_dir)
    for img in state.images:
        ann = state.anns.get(img)
        if not ann: continue
        root = etree.Element("annotation")
        etree.SubElement(root, "folder").text = os.path.basename(state.folder or "")
        etree.SubElement(root, "filename").text = os.path.basename(img)
        size = etree.SubElement(root, "size")
        etree.SubElement(size, "width").text = str(ann.width)
        etree.SubElement(size, "height").text = str(ann.height)
        etree.SubElement(size, "depth").text = "3"

        # VOC supports boxes; write others under ua:extra
        extra = etree.SubElement(root, "ua:extra")
        for sh in ann.shapes:
            if sh.type == "rect":
                (x1,y1),(x2,y2) = sh.points
                x_min, y_min = int(min(x1,x2)), int(min(y1,y2))
                x_max, y_max = int(max(x1,x2)), int(max(y1,y2))
                obj = etree.SubElement(root, "object")
                etree.SubElement(obj, "name").text = sh.cls
                bb = etree.SubElement(obj, "bndbox")
                etree.SubElement(bb, "xmin").text = str(x_min)
                etree.SubElement(bb, "ymin").text = str(y_min)
                etree.SubElement(bb, "xmax").text = str(x_max)
                etree.SubElement(bb, "ymax").text = str(y_max)
            else:
                e = etree.SubElement(extra, sh.type, attrib={"class": sh.cls})
                pts = " ".join([f"{int(x)},{int(y)}" for x,y in sh.points])
                e.text = pts

        stem = image_stem(img)
        etree.ElementTree(root).write(os.path.join(out_dir, f"{stem}.xml"), pretty_print=True, xml_declaration=True, encoding="utf-8")
