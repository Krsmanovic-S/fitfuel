from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('menu', views.menu, name='menu'),
    path('checkout/update-cart', views.update_session_cart, name='update_session_cart'),
    path('checkout', views.checkout_page, name='checkout_page'),
]