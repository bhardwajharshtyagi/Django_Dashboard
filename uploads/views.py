from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UploadFileForm
from .models import UploadedFile


from django.http import FileResponse, Http404
import os

import csv
import openpyxl


from django.db.models import Q



import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

import io
import base64


from django.db.models import Count, Sum

from django.db.models import Sum
from uploads.models import UploadedFile


from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UploadFileForm
from .models import UploadedFile


@login_required
def upload_file(request):

    if request.method == "POST":

        form = UploadFileForm(
            request.POST,
            request.FILES
        )

        uploaded_files = request.FILES.getlist("files")

        if len(uploaded_files) > 10:

            messages.error(
                request,
                "You can upload a maximum of 10 files at once."
            )

            return redirect("upload_file")

        if form.is_valid():

            uploaded_count = 0

            for uploaded_file in uploaded_files:

                extension = Path(
                    uploaded_file.name
                ).suffix.lower()

                if extension in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif"
                ]:

                    file_type = "image"

                elif extension == ".pdf":

                    file_type = "pdf"

                elif extension in [
                    ".xls",
                    ".xlsx"
                ]:

                    file_type = "excel"

                elif extension == ".csv":

                    file_type = "csv"

                else:

                    file_type = "other"

                UploadedFile.objects.create(

                    user=request.user,

                    file=uploaded_file,

                    original_name=uploaded_file.name,

                    file_size=uploaded_file.size,

                    file_type=file_type,
                )

                uploaded_count += 1

            messages.success(
                request,
                f"{uploaded_count} file(s) uploaded successfully."
            )

            return redirect("upload_file")

    else:

        form = UploadFileForm()

    files = UploadedFile.objects.filter(
        user=request.user
    ).order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "uploads/upload.html",
        {
            "form": form,
            "files": files,
        },
    )

#delete file 


@login_required
def delete_file(request, file_id):

    try:

        file = s.get(
            id=file_id,
            user=request.user
        )

    except UploadedFile.DoesNotExist:

        messages.error(request, "File not found.")

        return redirect("upload_file")

    if file.file:

        if os.path.isfile(file.file.path):

            os.remove(file.file.path)

    file.delete()

    messages.success(request, "File deleted successfully.")

    return redirect("upload_file")


@login_required
def download_file(request, file_id):

    try:

        file = UploadedFile.objects.get(
            id=file_id,
            user=request.user
        )

    except UploadedFile.DoesNotExist:

        raise Http404()

    return FileResponse(

        open(file.file.path, "rb"),

        as_attachment=True,

        filename=file.original_name,

    )





@login_required
def preview_file(request, file_id):

    try:

        uploaded_file = UploadedFile.objects.get(
            id=file_id,
            user=request.user
        )

    except UploadedFile.DoesNotExist:

        raise Http404()

    # Image aur PDF browser me open honge
    if uploaded_file.file_type in ["image", "pdf"]:

        return redirect(uploaded_file.file.url)

    # CSV Preview
    if uploaded_file.file_type == "csv":

        rows = []

        with open(
            uploaded_file.file.path,
            "r",
            encoding="utf-8-sig"
        ) as csv_file:

            reader = csv.reader(csv_file)

            for row in reader:
                rows.append(row)

        return render(
            request,
            "uploads/preview.html",
            {
                "file": uploaded_file,
                "rows": rows,
            }
        )

    # Excel Preview
    if uploaded_file.file_type == "excel":

        workbook = openpyxl.load_workbook(
            uploaded_file.file.path,
            read_only=True,
            data_only=True
        )

        sheet = workbook.active

        rows = []

        for row in sheet.iter_rows(
            values_only=True
        ):

            rows.append([
                "" if cell is None else cell
                for cell in row
            ])

        workbook.close()

        return render(
            request,
            "uploads/preview.html",
            {
                "file": uploaded_file,
                "rows": rows,
            }
        )

    # Other files
    messages.info(
        request,
        "Preview is not available for this file type."
    )

    return redirect("upload_file")








from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import UploadedFile


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

from .models import UploadedFile






def analytics_view(request):

    # =========================
    # USER KE FILES
    # =========================

    files = UploadedFile.objects.filter(
        user=request.user
    )


    # =========================
    # TOTAL FILES
    # =========================

    total_files = files.count()


    # =========================
    # FILE TYPE COUNTS
    # =========================

    total_images = files.filter(
        file_type="image"
    ).count()


    total_pdfs = files.filter(
        file_type="pdf"
    ).count()


    total_excel = files.filter(
        file_type="excel"
    ).count()


    total_csv = files.filter(
        file_type="csv"
    ).count()


    total_other = (
        total_files
        - total_images
        - total_pdfs
        - total_excel
        - total_csv
    )


    # =========================
    # STORAGE CALCULATION
    # =========================

    total_storage_bytes = sum(
        file.file_size
        for file in files
    )


    storage_mb = round(
        total_storage_bytes / (1024 * 1024),
        2
    )


    # =========================
    # CHART DATA
    # =========================

    labels = [
        "Images",
        "PDF",
        "Excel",
        "CSV"
    ]


    counts = [
        total_images,
        total_pdfs,
        total_excel,
        total_csv
    ]


    # =========================
    # SEABORN BAR CHART
    # =========================

    plt.figure(
        figsize=(7, 4)
    )


    sns.barplot(
        x=labels,
        y=counts
    )


    plt.title(
        "Uploaded Files by Type"
    )


    plt.xlabel(
        "File Type"
    )


    plt.ylabel(
        "Number of Files"
    )


    plt.tight_layout()


    buffer = io.BytesIO()


    plt.savefig(
        buffer,
        format="png"
    )


    buffer.seek(0)


    bar_chart = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


    buffer.close()


    plt.close()


    # =========================
    # MATPLOTLIB PIE CHART
    # =========================

    pie_labels = []
    pie_counts = []


    for label, count in zip(
        labels,
        counts
    ):

        if count > 0:

            pie_labels.append(
                label
            )

            pie_counts.append(
                count
            )


    pie_chart = None


    if pie_counts:

        plt.figure(
            figsize=(6, 5)
        )


        plt.pie(
            pie_counts,
            labels=pie_labels,
            autopct="%1.1f%%",
            startangle=90
        )


        plt.title(
            "File Distribution"
        )


        plt.tight_layout()


        buffer = io.BytesIO()


        plt.savefig(
            buffer,
            format="png"
        )


        buffer.seek(0)


        pie_chart = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")


        buffer.close()


        plt.close()


    # =========================
    # STORAGE DONUT CHART
    # =========================

    storage_chart = None


    if storage_mb > 0:

        storage_limit_mb = 100


        remaining_storage = max(
            storage_limit_mb - storage_mb,
            0
        )


        plt.figure(
            figsize=(6, 5)
        )


        plt.pie(
            [
                storage_mb,
                remaining_storage
            ],
            labels=[
                "Used",
                "Remaining"
            ],
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={
                "width": 0.45
            }
        )


        plt.text(
            0,
            0,
            f"{storage_mb} MB\nUsed",
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold"
        )


        plt.title(
            "Storage Usage"
        )


        plt.tight_layout()


        buffer = io.BytesIO()


        plt.savefig(
            buffer,
            format="png"
        )


        buffer.seek(0)


        storage_chart = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")


        buffer.close()


        plt.close()


    # =========================
    # SEND DATA TO HTML
    # =========================

    context = {

        "total_files": total_files,

        "total_images": total_images,

        "total_pdfs": total_pdfs,

        "total_excel": total_excel,

        "total_csv": total_csv,

        "total_other": total_other,

        "storage_mb": storage_mb,

        "bar_chart": bar_chart,

        "pie_chart": pie_chart,

        "storage_chart": storage_chart,

    }


    return render(
        request,
        "uploads/analytics.html",
        context
    )







from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def chatbot_user_context(request):

    files = UploadedFile.objects.filter(
        user=request.user
    )

    total_files = files.count()

    total_images = files.filter(
        file_type="image"
    ).count()

    total_pdfs = files.filter(
        file_type="pdf"
    ).count()

    total_excel = files.filter(
        file_type="excel"
    ).count()

    total_csv = files.filter(
        file_type="csv"
    ).count()

    total_other = files.filter(
        file_type="other"
    ).count()

    return JsonResponse({

        "username": request.user.username,

        "email": request.user.email,

        "total_files": total_files,

        "images": total_images,

        "pdfs": total_pdfs,

        "excel": total_excel,

        "csv": total_csv,

        "other": total_other

    })





from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import UploadedFile


@login_required
def chatbot_user_context(request):

    uploaded_files = UploadedFile.objects.filter(
        user=request.user
    )


    total_files = uploaded_files.count()


    file_breakdown = {

        "image": uploaded_files.filter(
            file_type="image"
        ).count(),

        "pdf": uploaded_files.filter(
            file_type="pdf"
        ).count(),

        "excel": uploaded_files.filter(
            file_type="excel"
        ).count(),

        "csv": uploaded_files.filter(
            file_type="csv"
        ).count(),

        "other": uploaded_files.filter(
            file_type="other"
        ).count(),

    }


    return JsonResponse({

        "username": request.user.username,

        "uploaded_file_count": total_files,

        "file_breakdown": file_breakdown,

    })