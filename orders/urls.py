from . import views
from django.urls import path

app_name = 'orders'
urlpatterns = [
    path('place_order/', views.PlaceOrderView.as_view(), name='place_order'),
    path('payments/', views.PaymentsView.as_view(), name='payments'),
]