from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.upload_file,
        name="upload_file",
    ),

    path(
        "delete/<int:file_id>/",
        views.delete_file,
        name="delete_file",
    ),

    path(
        "download/<int:file_id>/",
        views.download_file,
        name="download_file",
    ),

    path(
        "preview/<int:file_id>/",
        views.preview_file,
        name="preview_file",
    ),

    path(
        "analytics/",
        views.analytics_view,
        name="analytics"
    ),

    path(
        "chatbot-user-context/",
        views.chatbot_user_context,
        name="chatbot_user_context"
    ),

]