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

    # Password reset
    path('pass_reset/', views.PassResetView.as_view(), name='pass_reset'),
    path('pass_reset_done/', views.PassResetDoneView.as_view(), name='pass_reset_done'),
    path('pass_reset_confirm/<uidb64>/<token>/', views.PassResetConfirmView.as_view(), name='pass_reset_confirm'),
    path('pass_reset_complete/', views.PassResetCompleteView.as_view(), name='pass_reset_complete'),
]