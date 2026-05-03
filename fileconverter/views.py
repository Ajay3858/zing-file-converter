from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings

from PIL import Image
from pdf2image import convert_from_path
from pdf2docx import Converter

import subprocess
import os
import platform


OUTPUT_DIR = os.path.join(settings.BASE_DIR, "converted_files")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def is_large(file):
    return file.size > MAX_FILE_SIZE


def index(request):
    return render(request, "index.html")


# ================= JPG TO PDF =================
def jpg_to_pdf(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")

        if not image_file:
            return render(request, "jpg_to_pdf.html", {"message": "Upload image ❌"})

        if is_large(image_file):
            return render(request, "jpg_to_pdf.html", {"message": "Max 5MB allowed ❌"})

        try:
            image = Image.open(image_file)

            if image.mode != "RGB":
                image = image.convert("RGB")

            name = os.path.splitext(image_file.name)[0]
            filename = f"{name}.pdf"
            path = os.path.join(OUTPUT_DIR, filename)

            image.save(path, "PDF")

            return render(request, "jpg_to_pdf.html", {
                "message": "Success ✅",
                "file": filename
            })

        except Exception as e:
            return render(request, "jpg_to_pdf.html", {"message": str(e)})

    return render(request, "jpg_to_pdf.html")


# ================= PDF TO JPG =================
def pdf_to_jpg(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "pdf_to_jpg.html", {"message": "Upload PDF ❌"})

        if is_large(pdf_file):
            return render(request, "pdf_to_jpg.html", {"message": "Max 5MB allowed ❌"})

        try:
            name = os.path.splitext(pdf_file.name)[0]
            temp_pdf = os.path.join(OUTPUT_DIR, f"{name}.pdf")

            with open(temp_pdf, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            pages = convert_from_path(temp_pdf, first_page=1, last_page=1)

            filename = f"{name}.jpg"
            path = os.path.join(OUTPUT_DIR, filename)

            pages[0].save(path, "JPEG", quality=85)

            return render(request, "pdf_to_jpg.html", {
                "message": "Success ✅",
                "file": filename
            })

        except Exception as e:
            return render(request, "pdf_to_jpg.html", {"message": str(e)})

    return render(request, "pdf_to_jpg.html")


# ================= PDF TO WORD =================
def pdf_to_word(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "pdf_to_word.html", {"message": "Upload PDF ❌"})

        try:
            name = os.path.splitext(pdf_file.name)[0]
            pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
            word_filename = f"{name}.docx"
            word_path = os.path.join(OUTPUT_DIR, word_filename)

            with open(pdf_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            cv = Converter(pdf_path)
            cv.convert(word_path, start=0, end=5)
            cv.close()

            return render(request, "pdf_to_word.html", {
                "message": "Success ✅",
                "file": word_filename
            })

        except Exception as e:
            return render(request, "pdf_to_word.html", {"message": str(e)})

    return render(request, "pdf_to_word.html")


# ================= WORD TO PDF =================
def word_to_pdf(request):
    if request.method == "POST":
        word_file = request.FILES.get("doc")

        if not word_file:
            return render(request, "word_to_pdf.html", {"message": "Upload Word ❌"})

        try:
            name = os.path.splitext(word_file.name)[0]
            word_path = os.path.join(OUTPUT_DIR, word_file.name)

            with open(word_path, "wb") as f:
                for chunk in word_file.chunks():
                    f.write(chunk)

            subprocess.run([
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", OUTPUT_DIR,
                word_path
            ], check=True, timeout=20)

            return render(request, "word_to_pdf.html", {
                "message": "Success ✅",
                "file": f"{name}.pdf"
            })

        except Exception as e:
            return render(request, "word_to_pdf.html", {"message": str(e)})

    return render(request, "word_to_pdf.html")


# ================= COMPRESS JPG (FIXED) =================
def compress_jpg(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        quality = int(request.POST.get("quality", 35))

        if not image_file:
            return render(request, "compress_jpg.html", {"message": "Upload JPG ❌"})

        try:
            image = Image.open(image_file)

            if image.mode != "RGB":
                image = image.convert("RGB")

            name = os.path.splitext(image_file.name)[0]
            final_path = os.path.join(OUTPUT_DIR, f"{name}_compressed.jpg")
            temp_path = os.path.join(OUTPUT_DIR, f"{name}_temp.jpg")

            # Save compressed
            # Resize image (IMPORTANT)
            width, height = image.size
            image = image.resize((int(width * 0.7), int(height * 0.7)))

            # Save with strong compression
            image.save(
                temp_path,
                "JPEG",
                quality=quality,
                optimize=True,
                subsampling=2
            )

            # Compare sizes
            if os.path.getsize(temp_path) < image_file.size:
                os.rename(temp_path, final_path)
                message = "Compressed Successfully ✅"
            else:
                with open(final_path, "wb") as f:
                    for chunk in image_file.chunks():
                        f.write(chunk)
                os.remove(temp_path)
                message = "Already optimized. Original returned ✅"

            return render(request, "compress_jpg.html", {
                "message": message,
                "file": f"{name}_compressed.jpg"
            })

        except Exception as e:
            return render(request, "compress_jpg.html", {"message": str(e)})

    return render(request, "compress_jpg.html")


# ================= COMPRESS PDF =================
def compress_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "compress_pdf.html", {"message": "Upload PDF ❌"})

        try:
            name = os.path.splitext(pdf_file.name)[0]
            input_path = os.path.join(OUTPUT_DIR, pdf_file.name)
            output_path = os.path.join(OUTPUT_DIR, f"{name}_compressed.pdf")

            with open(input_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            gs = "gswin64c" if platform.system() == "Windows" else "gs"

            subprocess.run([
                gs,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/screen",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                input_path
            ], check=True)

            return render(request, "compress_pdf.html", {
                "message": "Compressed Successfully ✅",
                "file": f"{name}_compressed.pdf"
            })

        except Exception as e:
            return render(request, "compress_pdf.html", {"message": str(e)})

    return render(request, "compress_pdf.html")


# ================= DOWNLOAD =================
def download(request):
    file = request.GET.get("file")

    path = os.path.join(OUTPUT_DIR, file)

    if not os.path.exists(path):
        raise Http404("File not found")

    return FileResponse(open(path, "rb"), as_attachment=True)