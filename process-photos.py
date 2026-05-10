#!/usr/bin/env python3
"""
Manila House — Photo Pipeline
================================
Procesa fotos de propiedades desde tu carpeta original y las
optimiza para producción en /public/images/properties/.
Genera gallery-manifest.json con la lista completa por propiedad.

Uso:
    python process-photos.py

Requisitos:
    pip install Pillow pillow-heif
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageOps

# HEIC support (iPhone photos)
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_OK = True
except ImportError:
    HEIC_OK = False

# ============================================================
# CONFIG — ajustá estas rutas si tu estructura cambia
# ============================================================
SOURCE_BASE = Path(r"C:\Users\Usuario\Documents\ANDRES\Manila House")
REPO_BASE = Path(r"C:\Users\Usuario\Documents\ANDRES\manila-house-propiedades")

OUTPUT_DIR = REPO_BASE / "public" / "images" / "properties"
MANIFEST_PATH = REPO_BASE / "public" / "images" / "gallery-manifest.json"

TARGET_SIZE = (1600, 1067)        # 3:2 horizontal — landing standard
JPEG_QUALITY = 85                  # sweet spot calidad/peso
MAX_PHOTOS_PER_PROPERTY = 12      # ajustá si querés más/menos
MIN_FILE_SIZE_KB = 50             # filtra thumbnails y archivos rotos

# Mapeo carpeta de Manila House → ID en la landing
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


# ============================================================
# CORE
# ============================================================
def get_valid_photos(folder: Path) -> list[Path]:
    """Lista fotos válidas en orden alfabético, filtra archivos pequeños."""
    if not folder.exists():
        return []
    photos = []
    for f in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if not f.is_file():
            continue
        if f.suffix.lower() not in VALID_EXT:
            continue
        size_kb = f.stat().st_size / 1024
        if size_kb < MIN_FILE_SIZE_KB:
            continue  # skip thumbnails/corruptos
        if f.suffix.lower() in {".heic", ".heif"} and not HEIC_OK:
            continue  # skip HEIC si no hay soporte
        photos.append(f)
    return photos


def process_image(source: Path, output: Path) -> bool:
    """Abre, auto-rota por EXIF, cover-crop a target, optimiza, guarda JPG."""
    try:
        img = Image.open(source)
        img = ImageOps.exif_transpose(img)              # respeta orientación cámara
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = ImageOps.fit(                              # cover crop centered
            img,
            TARGET_SIZE,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
        img.save(
            output,
            "JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,                            # progressive load
        )
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def format_size(bytes_n: int) -> str:
    if bytes_n < 1024 * 1024:
        return f"{bytes_n / 1024:.0f} KB"
    return f"{bytes_n / (1024 * 1024):.2f} MB"


def main():
    print("=" * 60)
    print("🏠 MANILA HOUSE — PHOTO PIPELINE")
    print("=" * 60)
    print(f"📂 Fuente:  {SOURCE_BASE}")
    print(f"📁 Destino: {OUTPUT_DIR}")
    print(f"🎨 Formato: {TARGET_SIZE[0]}x{TARGET_SIZE[1]} JPEG q{JPEG_QUALITY}")
    print(f"📸 HEIC:    {'✅ activado' if HEIC_OK else '⚠️  no soportado (instalá pillow-heif)'}")
    print()

    # Verifica que las carpetas existan
    if not SOURCE_BASE.exists():
        print(f"❌ No existe la carpeta fuente: {SOURCE_BASE}")
        sys.exit(1)
    if not REPO_BASE.exists():
        print(f"❌ No existe el repo: {REPO_BASE}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}
    total_in = 0
    total_out = 0
    total_size = 0

    for folder_name, prop_id in FOLDER_MAPPING.items():
        folder_path = SOURCE_BASE / folder_name
        print(f"📦 {folder_name:20s} → {prop_id}")

        photos = get_valid_photos(folder_path)
        if not photos:
            print(f"   ⚠️  Sin fotos válidas (carpeta vacía o no existe)")
            print()
            continue

        photos = photos[:MAX_PHOTOS_PER_PROPERTY]
        total_in += len(photos)
        prop_files = []

        for i, source in enumerate(photos, start=1):
            output_name = f"{prop_id}.jpg" if i == 1 else f"{prop_id}_{i}.jpg"
            output_path = OUTPUT_DIR / output_name

            if process_image(source, output_path):
                size = output_path.stat().st_size
                total_size += size
                total_out += 1
                prop_files.append(output_name)
                print(f"   ✓ {output_name:14s} ← {source.name[:40]:40s} {format_size(size):>10s}")

        manifest[prop_id] = prop_files
        print()

    # Guardar manifest
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"✅ DONE — {total_out}/{total_in} fotos procesadas")
    print(f"📦 Peso total: {format_size(total_size)}")
    print(f"📋 Manifest: {MANIFEST_PATH}")
    print(f"📁 Fotos:    {OUTPUT_DIR}")
    print("=" * 60)
    print()
    print("Próximo paso: revisar visualmente las fotos en")
    print(f"  {OUTPUT_DIR}")
    print()
    print("Si querés cambiar alguna, simplemente:")
    print("  1. Borrá la que no te gusta")
    print("  2. Copiá manualmente la que quieras y renombrala con la convención")
    print("  3. Volvé a correr este script (sobreescribe sin problema)")
    print()


if __name__ == "__main__":
    main()
