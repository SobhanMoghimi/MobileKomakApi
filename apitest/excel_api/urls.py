from django.urls import path
from excel_api import views

urlpatterns = [
    path("hello-view/", views.HelloApiView.as_view()),
    path("excel-view/", views.ExcelApiView.as_view()),
    ]