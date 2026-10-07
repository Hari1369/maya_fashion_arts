from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("userdetails/", views.user_details, name="userdetails"),
    path("userdetails/", views.user_details, name="user_detail"),
    path("register/", views.register, name="register"),
]