from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('confirm/<uidb64>/<token>/', views.ActivateView.as_view(), name='activate'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', views.DashboardView.as_view(), name='dashboard'),
]