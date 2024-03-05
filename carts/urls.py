from django.urls import path
from . import views
app_name = 'carts'
urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add_cart/<int:product_id>/', views.AddCartView.as_view(), name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.RemoveCartView.as_view(), name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.RemoveCartItemView.as_view(), name='remove_cart_item'),
]