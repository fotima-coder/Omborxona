# core/urls.py

from django.contrib import admin
from django.urls import path, include
from users.views import CustomPasswordResetView, CustomPasswordResetDoneView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('auth/', include('users.urls')),

    # Custom password reset URL'lari - ALLAUTH'DAN OLDIN
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/password/reset/done/', CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),


    # Boshqa allauth URL'lari (login, signup, va h.k.)
    path('accounts/', include('allauth.urls')),
]