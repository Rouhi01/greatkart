from django.urls import path
from . import views
app_name = 'carts'
urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('addcart/<slug:product_slug>', views.CartView.as_view(), name='cart'),
]