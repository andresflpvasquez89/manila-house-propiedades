#!/usr/bin/env python3
"""
Manila House — Photo Pipeline v3 (always recursive)
====================================================
Busca fotos recursivamente en TODA la estructura de carpetas.
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_OK = True
except ImportError:
    HEIC_OK = False

SOURCE_BASE = Path(r"C:\Users\Usuario\Documents\ANDRES\Manila House")
REPO_BASE = Path(r"C:\Users\Usuario\Documents\ANDRES\manila-house-propiedades")
OUTPUT_DIR = REPO_BASE / "images" / "properties"
MANIFEST_PATH = REPO_BASE / "images" / "gallery-manifest.json"

TARGET_SIZE = (1600, 1067)
JPEG_QUALITY = 85
MAX_PHOTOS_PER_PROPERTY = 12
MIN_FILE_SIZE_KB = 50

FOLDER_MAPPING = {
    "Pink house":     "s1",
    "Casa envigado":  "s2",
    "Manila 5":       "s4",
    "Manila 1":       "s5",
    "Manila 3":       "s6",
    "Manila 2":       "s7",
    "Finca rionegro": "s8",
    "FINCA santa fe": "s9",
    "CASA BOGOTA":    "s10",
    "VOLCANA":        "s11",
}

VALID_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}


def find_all_photos_recursive(folder: Path) -> list:
    """Busca TODAS las fotos válidas recursivamente."""
    if not folder.exists():
        return []
    photos = []
    for f in folder.rglob("*"):
        try:
            if not f.is_file():
                continue
            if f.suffix.lower() not in VALID_EXT:
                continue
            size_kb = f.stat().st_size / 1024
            if size_kb < MIN_FILE_SIZE_KB:
                continue
            if f.suffix.lower() in {".heic", ".heif"} and not HEIC_OK:
                continue
            photos.append(f)
        except (OSError, PermissionError):
            continue
    return sorted(photos, key=lambda p: p.name.lower())


def process_image(source: Path, output: Path) -> bool:
    try:
        img = Image.open(source)
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = ImageOps.fit(img, TARGET_SIZE, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        img.save(output, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def format_size(b):
    return f"{b / 1024:.0f} KB" if b < 1024 * 1024 else f"{b / (1024*1024):.2f} MB"


def main():
    print("=" * 60)
    print("🏠 MANILA HOUSE — PHOTO PIPELINE v3 (RECURSIVE)")
    print("=" * 60)
    print(f"📁 Destino: {OUTPUT_DIR}")
    print(f"📸 HEIC: {'✅' if HEIC_OK else '⚠️'}")
    print()

    if not SOURCE_BASE.exists():
        print(f"❌ No existe: {SOURCE_BASE}"); sys.exit(1)
    if not REPO_BASE.exists():
        print(f"❌ No existe: {REPO_BASE}"); sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    total_out = 0
    total_size = 0

    for folder_name, prop_id in FOLDER_MAPPING.items():
        folder_path = SOURCE_BASE / folder_name
        print(f"📦 {folder_name:20s} → {prop_id}")
        if not folder_path.exists():
            print(f"   ❌ Carpeta NO EXISTE: {folder_path}\n")
            continue
        all_photos = find_all_photos_recursive(folder_path)
        print(f"   🔎 {len(all_photos)} fotos válidas encontradas (recursivo)")
        if not all_photos:
            print()
            continue
        photos = all_photos[:MAX_PHOTOS_PER_PROPERTY]
        prop_files = []
        for i, source in enumerate(photos, start=1):
            output_name = f"{prop_id}.jpg" if i == 1 else f"{prop_id}_{i}.jpg"
            output_path = OUTPUT_DIR / output_name
            if process_image(source, output_path):
                size = output_path.stat().st_size
                total_size += size
                total_out += 1
                prop_files.append(output_name)
                src = source.name[:35]
                print(f"   ✓ {output_name:14s} ← {src:35s} {format_size(size):>10s}")
        manifest[prop_id] = prop_files
        print()

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"✅ DONE — {total_out} fotos procesadas")
    print(f"📦 Peso total: {format_size(total_size)}")
    print(f"📋 {MANIFEST_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
