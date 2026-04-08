from django.urls import path
from .views import *

urlpatterns = [
    path('', SectionsView.as_view(), name='sections'),

    path('products/', ProductsView.as_view(), name='products'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    path('clients/', ClientsView.as_view(), name='clients'),

    path('sales/', SalesView.as_view(), name='sales'),
    path('sales/create/', SaleCreateView.as_view(), name='sales-create'),

    path('payment/create/', PayDebtCreateView.as_view(), name='payment-create'),

    path('imports/', ImportsView.as_view(), name='imports'),
    path('payments/', PaymentsView.as_view(), name='payments'),
]
