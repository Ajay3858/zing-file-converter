import subprocess
from PIL import Image


def compress_image(input_path, output_path, quality=50):
    img = Image.open(input_path)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.save(output_path, optimize=True, quality=quality)


def compress_pdf(input_path, output_path):
    subprocess.run([
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ], check=True)