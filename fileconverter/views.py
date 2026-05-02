from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings

from PIL import Image
from pdf2image import convert_from_path
from pdf2docx import Converter
from docx2pdf import convert

import os


OUTPUT_DIR = os.path.join(settings.BASE_DIR, "converted_files")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def index(request):
    return render(request, "index.html")


# JPG TO PDF
def jpg_to_pdf(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")

        if not image_file:
            return render(request, "jpg_to_pdf.html", {
                "message": "Please upload an image ❌"
            })

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
            return render(request, "jpg_to_pdf.html", {
                "message": f"Error: {e}"
            })

    return render(request, "jpg_to_pdf.html")


# PDF TO JPG
def pdf_to_jpg(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "pdf_to_jpg.html", {
                "message": "Please upload a PDF ❌"
            })

        try:
            name = os.path.splitext(pdf_file.name)[0]

            temp_pdf = os.path.join(OUTPUT_DIR, f"{name}.pdf")

            with open(temp_pdf, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            pages = convert_from_path(
                temp_pdf,
                poppler_path=r"C:\poppler-25.12.0\Library\bin"
            )

            filename = f"{name}.jpg"
            path = os.path.join(OUTPUT_DIR, filename)

            pages[0].save(path, "JPEG")

            return render(request, "pdf_to_jpg.html", {
                "message": "Converted Successfully ✅",
                "file": filename
            })

        except Exception as e:
            return render(request, "pdf_to_jpg.html", {
                "message": f"Error: {e}"
            })

    return render(request, "pdf_to_jpg.html")


# PDF TO WORD
def pdf_to_word(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "pdf_to_word.html", {
                "message": "Please upload a PDF ❌"
            })

        try:
            name = os.path.splitext(pdf_file.name)[0]
            pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
            word_filename = f"{name}.docx"
            word_path = os.path.join(OUTPUT_DIR, word_filename)

            with open(pdf_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            cv = Converter(pdf_path)

            # convert only first 5 pages to avoid infinite loading
            cv.convert(word_path, start=0, end=5)

            cv.close()

            return render(request, "pdf_to_word.html", {
                "message": "Converted Successfully ✅",
                "file": word_filename
            })

        except Exception as e:
            return render(request, "pdf_to_word.html", {
                "message": f"Error: {e}"
            })

    return render(request, "pdf_to_word.html")

# WORD TO PDF
def word_to_pdf(request):
    if request.method == "POST":
        word_file = request.FILES.get("doc")

        if not word_file:
            return render(request, "word_to_pdf.html", {
                "message": "Please upload a Word file ❌"
            })

        try:
            name = os.path.splitext(word_file.name)[0]

            word_path = os.path.join(OUTPUT_DIR, word_file.name)
            pdf_filename = f"{name}.pdf"
            pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

            with open(word_path, "wb") as f:
                for chunk in word_file.chunks():
                    f.write(chunk)

            convert(word_path, pdf_path)

            return render(request, "word_to_pdf.html", {
                "message": "Converted Successfully ✅",
                "file": pdf_filename
            })

        except Exception as e:
            return render(request, "word_to_pdf.html", {
                "message": f"Error: {e}"
            })

    return render(request, "word_to_pdf.html")


# DOWNLOAD
def download(request):
    file = request.GET.get("file")

    if not file:
        return HttpResponse("No file ❌")

    path = os.path.join(OUTPUT_DIR, file)

    if not os.path.exists(path):
        raise Http404("File not found")

    return FileResponse(open(path, "rb"), as_attachment=True, filename=file)