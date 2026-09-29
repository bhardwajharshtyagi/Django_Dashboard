from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path("admin/", admin.site.urls),

    # Accounts
    path("", include("accounts.urls")),

    # Uploads
    path("uploads/", include("uploads.urls")),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )