from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('menu', views.menu, name='menu'),
    path('contact', views.contact, name='contact'),
    path('checkout/update-cart', views.update_session_cart, name='update_session_cart'),
    path('checkout', views.checkout_page, name='checkout_page'),
    path('api/checkout-session', views.create_checkout_session, name='api_checkout_session'),
    path('success', views.payment_success_view, name='success'),
    path('failed', views.payment_failed_view, name='failed'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]