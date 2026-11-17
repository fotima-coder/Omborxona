# users/urls.py

from django.urls import path
from .views import LoginView, logout_view, ViewSentEmailView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('view-email/', ViewSentEmailView.as_view(), name='view_sent_email'),
]