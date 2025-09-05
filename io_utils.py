
import os, json
from models import ProjectState, Shape

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def image_stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]
