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


# JPG TO PDF
def jpg_to_pdf(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")

        if not image_file:
            return render(request, "jpg_to_pdf.html", {"message": "Please upload an image ❌"})

        if is_large(image_file):
            return render(request, "jpg_to_pdf.html", {"message": "File too large. Max 5MB allowed ❌"})

        try:
            image = Image.open(image_file)

            if image.mode != "RGB":
                image = image.convert("RGB")

            name = os.path.splitext(image_file.name)[0]
            filename = f"{name}.pdf"
            path = os.path.join(OUTPUT_DIR, filename)

            image.save(path, "PDF")

            return render(request, "jpg_to_pdf.html", {
                "message": "Converted Successfully ✅",
                "file": filename
            })

        except Exception as e:
            return render(request, "jpg_to_pdf.html", {"message": f"Error: {e}"})

    return render(request, "jpg_to_pdf.html")


# PDF TO JPG
def pdf_to_jpg(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "pdf_to_jpg.html", {"message": "Please upload a PDF ❌"})

        if is_large(pdf_file):
            return render(request, "pdf_to_jpg.html", {"message": "File too large. Max 5MB allowed ❌"})

        if not pdf_file.name.lower().endswith(".pdf"):
            return render(request, "pdf_to_jpg.html", {"message": "Only PDF files allowed ❌"})

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
                "message": "Converted Successfully ✅",
                "file": filename
            })

        except Exception as e:
            return render(request, "pdf_to_jpg.html", {"message": f"Error: {e}"})

    return render(request, "pdf_to_jpg.html")


# PDF TO WORD
def pdf_to_word(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "pdf_to_word.html", {"message": "Please upload a PDF ❌"})

        if is_large(pdf_file):
            return render(request, "pdf_to_word.html", {"message": "File too large. Max 5MB allowed ❌"})

        if not pdf_file.name.lower().endswith(".pdf"):
            return render(request, "pdf_to_word.html", {"message": "Only PDF files allowed ❌"})

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
                "message": "Converted Successfully ✅",
                "file": word_filename
            })

        except Exception as e:
            return render(request, "pdf_to_word.html", {"message": f"Error: {e}"})

    return render(request, "pdf_to_word.html")


# WORD TO PDF
def word_to_pdf(request):
    if request.method == "POST":
        word_file = request.FILES.get("doc")

        if not word_file:
            return render(request, "word_to_pdf.html", {"message": "Please upload a Word file ❌"})

        if is_large(word_file):
            return render(request, "word_to_pdf.html", {"message": "File too large. Max 5MB allowed ❌"})

        if not word_file.name.lower().endswith((".doc", ".docx")):
            return render(request, "word_to_pdf.html", {"message": "Only Word files allowed ❌"})

        try:
            name = os.path.splitext(word_file.name)[0]
            word_path = os.path.join(OUTPUT_DIR, word_file.name)
            pdf_filename = f"{name}.pdf"

            with open(word_path, "wb") as f:
                for chunk in word_file.chunks():
                    f.write(chunk)

            subprocess.run([
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", OUTPUT_DIR,
                word_path
            ], check=True, timeout=25)

            return render(request, "word_to_pdf.html", {
                "message": "Converted Successfully ✅",
                "file": pdf_filename
            })

        except subprocess.TimeoutExpired:
            return render(request, "word_to_pdf.html", {
                "message": "Conversion took too long. Try a smaller file ❌"
            })

        except Exception as e:
            return render(request, "word_to_pdf.html", {"message": f"Error: {e}"})

    return render(request, "word_to_pdf.html")


# COMPRESS JPG
def compress_jpg(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        quality = int(request.POST.get("quality", 50))

        if not image_file:
            return render(request, "compress_jpg.html", {"message": "Upload JPG image ❌"})

        if is_large(image_file):
            return render(request, "compress_jpg.html", {"message": "File too large. Max 5MB allowed ❌"})

        if not image_file.name.lower().endswith((".jpg", ".jpeg")):
            return render(request, "compress_jpg.html", {"message": "Only JPG/JPEG files allowed ❌"})

        try:
            image = Image.open(image_file)

            if image.mode != "RGB":
                image = image.convert("RGB")

            name = os.path.splitext(image_file.name)[0]
            filename = f"{name}_compressed.jpg"
            path = os.path.join(OUTPUT_DIR, filename)

            image.save(path, "JPEG", optimize=True, quality=quality)

            return render(request, "compress_jpg.html", {
                "message": "JPG Compressed Successfully ✅",
                "file": filename
            })

        except Exception as e:
            return render(request, "compress_jpg.html", {"message": f"Error: {e}"})

    return render(request, "compress_jpg.html")


# COMPRESS PDF
def compress_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")
        level = request.POST.get("level", "/ebook")

        if not pdf_file:
            return render(request, "compress_pdf.html", {"message": "Upload PDF ❌"})

        if is_large(pdf_file):
            return render(request, "compress_pdf.html", {"message": "File too large. Max 5MB allowed ❌"})

        if not pdf_file.name.lower().endswith(".pdf"):
            return render(request, "compress_pdf.html", {"message": "Only PDF files allowed ❌"})

        try:
            name = os.path.splitext(pdf_file.name)[0]
            input_path = os.path.join(OUTPUT_DIR, pdf_file.name)
            output_filename = f"{name}_compressed.pdf"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            with open(input_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            gs_command = "gswin64c" if platform.system() == "Windows" else "gs"

            subprocess.run([
                gs_command,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={level}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                input_path
            ], check=True, timeout=25)

            return render(request, "compress_pdf.html", {
                "message": "PDF Compressed Successfully ✅",
                "file": output_filename
            })

        except subprocess.TimeoutExpired:
            return render(request, "compress_pdf.html", {
                "message": "Compression took too long. Try a smaller PDF ❌"
            })

        except Exception as e:
            return render(request, "compress_pdf.html", {"message": f"Error: {e}"})

    return render(request, "compress_pdf.html")


# DOWNLOAD
def download(request):
    file = request.GET.get("file")

    if not file:
        return HttpResponse("No file ❌")

    path = os.path.join(OUTPUT_DIR, file)

    if not os.path.exists(path):
        raise Http404("File not found")

    return FileResponse(open(path, "rb"), as_attachment=True, filename=file)