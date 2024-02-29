from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('<slug:category_slug>', views.StoreView.as_view(), name='products_by_category'),
]