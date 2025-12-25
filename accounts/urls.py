from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('otp/', views.otp_view, name='otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),  
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]