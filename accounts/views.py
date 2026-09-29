from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils import timezone

from .email import send_otp_email
from .forms import (
    SignupForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
)
from .models import UserProfile
from .utils import generate_otp








from datetime import datetime


# ==================================================
# HOME
# ==================================================

def home(request):

    return render(
        request,
        "accounts/home.html"
    )


# ==================================================
# SIGNUP
# ==================================================

def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.is_active = False

            user.save()

            # Create/Get profile
            profile, created = UserProfile.objects.get_or_create(
                user=user
            )

            # Generate OTP
            otp = generate_otp()

            profile.otp = otp
            profile.otp_created_at = timezone.now()
            profile.is_verified = False

            profile.save()

            # Send OTP to registered email
            send_otp_email(
                user.email,
                otp
            )

            # Store user ID in session
            request.session["user_id"] = user.id

            return redirect("verify_otp")

    else:

        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {
            "form": form
        }
    )


# ==================================================
# LOGIN
# ==================================================

def login_view(request):

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            profile, created = UserProfile.objects.get_or_create(
                user=user
            )

            if not profile.is_verified:

                messages.error(
                    request,
                    "Please verify your email first."
                )

                return redirect("verify_otp")

            login(
                request,
                user
            )

            return redirect("dashboard")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    else:

        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


# ==================================================
# DASHBOARD
# ==================================================

@login_required
def dashboard(request):

    return render(
        request,
        "accounts/dashboard.html"
    )


# ==================================================
# LOGOUT
# ==================================================

def logout_view(request):

    logout(request)

    return redirect("home")


# ==================================================
# VERIFY OTP
# ==================================================

def verify_otp(request):

    if request.method == "POST":

        otp = request.POST.get("otp")

        user_id = request.session.get("user_id")

        if not user_id:

            return redirect("signup")

        profile = UserProfile.objects.get(
            user_id=user_id
        )

        # Check OTP exists
        if profile.otp_created_at is None:

            messages.error(
                request,
                "OTP not found."
            )

            return redirect("signup")

        # OTP expiry - 5 minutes
        if timezone.now() > (
            profile.otp_created_at +
            timedelta(minutes=5)
        ):

            messages.error(
                request,
                "OTP Expired. Please request a new OTP."
            )

            return redirect("verify_otp")

        # OTP match
        if profile.otp == otp:

            profile.is_verified = True
            profile.otp = None
            profile.otp_created_at = None

            profile.save()

            user = profile.user

            user.is_active = True

            user.save()

            messages.success(
                request,
                "Email Verified Successfully."
            )

            return redirect("login")

        else:

            messages.error(
                request,
                "Invalid OTP"
            )

    return render(
        request,
        "accounts/verify_otp.html"
    )


# ==================================================
# RESEND OTP
# ==================================================

def resend_otp(request):

    user_id = request.session.get("user_id")

    if not user_id:

        return redirect("signup")

    profile = UserProfile.objects.get(
        user_id=user_id
    )

    otp = generate_otp()

    profile.otp = otp
    profile.otp_created_at = timezone.now()

    profile.save()

    send_otp_email(
        profile.user.email,
        otp
    )

    messages.success(
        request,
        "New OTP sent successfully."
    )

    return redirect("verify_otp")


# ==================================================
# FORGOT PASSWORD
# ==================================================

def forgot_password(request):

    if request.method == "POST":

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:

                user = User.objects.get(
                    email=email
                )

                profile, created = UserProfile.objects.get_or_create(
                    user=user
                )

                otp = generate_otp()

                profile.otp = otp
                profile.otp_created_at = timezone.now()

                profile.save()

                send_otp_email(
                    email,
                    otp
                )

                request.session["reset_user"] = user.id

                messages.success(
                    request,
                    "OTP sent successfully."
                )

                return redirect("reset_password")

            except User.DoesNotExist:

                messages.error(
                    request,
                    "Email not found."
                )

    else:

        form = ForgotPasswordForm()

    return render(
        request,
        "accounts/forgot_password.html",
        {
            "form": form
        }
    )


# ==================================================
# RESET PASSWORD
# ==================================================

def reset_password(request):

    user_id = request.session.get("reset_user")

    if not user_id:

        return redirect("forgot_password")

    user = User.objects.get(
        id=user_id
    )

    profile = UserProfile.objects.get(
        user=user
    )

    if request.method == "POST":

        form = ResetPasswordForm(request.POST)

        if form.is_valid():

            otp = form.cleaned_data["otp"]

            password = form.cleaned_data["password"]

            confirm = form.cleaned_data["confirm_password"]

            # OTP check
            if profile.otp_created_at is None:

                messages.error(
                    request,
                    "OTP not found."
                )

                return redirect("forgot_password")

            # OTP expiry
            if timezone.now() > (
                profile.otp_created_at +
                timedelta(minutes=5)
            ):

                messages.error(
                    request,
                    "OTP expired."
                )

                return redirect("forgot_password")

            # OTP match
            if otp != profile.otp:

                messages.error(
                    request,
                    "Invalid OTP"
                )

                return redirect("reset_password")

            # Password match
            if password != confirm:

                messages.error(
                    request,
                    "Passwords do not match"
                )

                return redirect("reset_password")

            # Update password
            user.set_password(password)

            user.save()

            # Clear OTP
            profile.otp = None
            profile.otp_created_at = None

            profile.save()

            del request.session["reset_user"]

            messages.success(
                request,
                "Password reset successful."
            )

            return redirect("login")

    else:

        form = ResetPasswordForm()

    return render(
        request,
        "accounts/reset_password.html",
        {
            "form": form
        }
    )


# ==================================================
# CHANGE PASSWORD
# ==================================================

@login_required
def change_password(request):

    if request.method == "POST":

        form = ChangePasswordForm(request.POST)

        if form.is_valid():

            old_password = form.cleaned_data["old_password"]

            new_password = form.cleaned_data["new_password"]

            confirm_password = form.cleaned_data["confirm_password"]

            # Check current password
            if not request.user.check_password(
                old_password
            ):

                messages.error(
                    request,
                    "Current password is incorrect."
                )

                return redirect("change_password")

            # Check passwords match
            if new_password != confirm_password:

                messages.error(
                    request,
                    "Passwords do not match."
                )

                return redirect("change_password")

            # Update password
            request.user.set_password(
                new_password
            )

            request.user.save()

            # Logout user after password change
            logout(request)

            messages.success(
                request,
                "Password changed successfully. Please login again."
            )

            return redirect("login")

    else:

        form = ChangePasswordForm()

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form
        }
    )


# ==================================================
# PROFILE
# ==================================================

@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # ==========================
        # REMOVE PROFILE PHOTO
        # ==========================

        if request.POST.get("remove_profile_image") == "true":

            if profile.profile_image:

                profile.profile_image.delete(
                    save=False
                )

                profile.profile_image = None

                profile.save()

                messages.success(
                    request,
                    "Profile photo removed successfully."
                )

            return redirect("profile")


        # ==========================
        # PHOTO UPLOAD FLAG
        # ==========================

        photo_uploaded = False


        # ==========================
        # DATE OF BIRTH
        # ==========================

        date_of_birth = request.POST.get(
            "date_of_birth"
        )

        if date_of_birth:

            try:

                profile.date_of_birth = datetime.strptime(
                    date_of_birth,
                    "%d-%m-%Y"
                ).date()

            except ValueError:

                messages.error(
                    request,
                    "Please enter DOB in DD-MM-YYYY format."
                )

                return redirect("profile")


        # ==========================
        # UPDATE PROFILE PHOTO
        # ==========================

        if "profile_image" in request.FILES:

            image = request.FILES[
                "profile_image"
            ]

            if not image.name.lower().endswith(
                (".jpg", ".jpeg")
            ):

                messages.error(
                    request,
                    "Only JPG or JPEG images are allowed."
                )

                return redirect("profile")


            # DELETE OLD PHOTO

            if profile.profile_image:

                profile.profile_image.delete(
                    save=False
                )


            # SAVE NEW PHOTO

            profile.profile_image = image

            photo_uploaded = True


        # ==========================
        # SAVE PROFILE
        # ==========================

        profile.save()


        # ==========================
        # SUCCESS MESSAGE
        # ==========================

        if photo_uploaded:

            messages.success(
                request,
                "Profile photo uploaded successfully."
            )

        else:

            messages.success(
                request,
                "Profile updated successfully."
            )


        return redirect("profile")


    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
        }
    )









from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

from uploads.models import UploadedFile


@login_required
def dashboard(request):

    # Sirf current logged-in user ki files
    files = UploadedFile.objects.filter(
        user=request.user
    )

    # Total files
    total_files = files.count()

    # Total images
    total_images = files.filter(
        file_type="image"
    ).count()

    # Total PDFs
    total_pdfs = files.filter(
        file_type="pdf"
    ).count()

    # Total Excel files
    total_excel = files.filter(
        file_type="excel"
    ).count()

    # Total CSV files
    total_csv = files.filter(
        file_type="csv"
    ).count()

    # Total storage in bytes
    total_storage = files.aggregate(
        total=Sum("file_size")
    )["total"] or 0

    # Bytes -> MB
    storage_mb = round(
        total_storage / (1024 * 1024),
        2
    )

    context = {
        "total_files": total_files,
        "total_images": total_images,
        "total_pdfs": total_pdfs,
        "total_excel": total_excel,
        "total_csv": total_csv,
        "storage_mb": storage_mb,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context
    )




from .forms import SupportTicketForm
from .models import SupportTicket




@login_required
def support(request):

    if request.method == "POST":

        form = SupportTicketForm(request.POST)

        if form.is_valid():

            ticket = form.save(commit=False)

            ticket.user = request.user

            ticket.save()

            messages.success(
                request,
                "Your support request has been submitted successfully."
            )

            return redirect("support")

    else:

        form = SupportTicketForm()


    tickets = SupportTicket.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )


    return render(
        request,
        "support.html",
        {
            "form": form,
            "tickets": tickets,
        }
    )




# ==================================================
# PDF GENERATOR
# ==================================================

from io import BytesIO

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from xml.sax.saxutils import escape


@login_required
def pdf_generator(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "Generated Document"
        ).strip()

        text = request.POST.get(
            "text",
            ""
        ).strip()

        if not text:

            messages.error(
                request,
                "Please enter some text before generating the PDF."
            )

            return redirect("pdf_generator")

        # ==========================================
        # CREATE PDF IN MEMORY
        # ==========================================

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title=title,
            author=request.user.username,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "PDFTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        body_style = ParagraphStyle(
            "PDFBody",
            parent=styles["BodyText"],
            fontSize=11,
            leading=17,
            spaceAfter=10,
        )

        story = []

        # ==========================================
        # TITLE
        # ==========================================

        story.append(
            Paragraph(
                escape(title),
                title_style
            )
        )

        story.append(
            Spacer(1, 10)
        )

        # ==========================================
        # TEXT PROCESSING
        # ==========================================

        paragraphs = text.split("\n")

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if paragraph:

                paragraph = escape(paragraph)

                story.append(
                    Paragraph(
                        paragraph,
                        body_style
                    )
                )

            else:

                story.append(
                    Spacer(1, 8)
                )

        # ==========================================
        # MINIMUM 3 PAGES
        # ==========================================

        story.append(PageBreak())
        story.append(
            Paragraph(
                " ",
                body_style
            )
        )

        story.append(PageBreak())
        story.append(
            Paragraph(
                " ",
                body_style
            )
        )

        # ==========================================
        # BUILD PDF
        # ==========================================

        document.build(story)

        buffer.seek(0)

        filename = "generated_document.pdf"

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf"
        )

    return render(
        request,
        "accounts/pdf_generator.html"
    )





