from decimal import Decimal
from django.db.models import ExpressionWrapper, F, FloatField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import *


class SectionsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, "sections.html")


class ProductsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        products = Product.objects.filter(branch=request.user.branch)
        return render(request, "products.html", {"products": products})

    def post(self, request):
        Product.objects.create(
            name=request.POST["name"],
            brand=request.POST.get("brand"),
            price=Decimal(request.POST["price"]),
            amount=Decimal(request.POST["amount"]),
            unit=request.POST["unit"],
            branch=request.user.branch,
        )
        return redirect('products')


class ProductUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get_object(self, request, pk):
        return get_object_or_404(Product, pk=pk, branch=request.user.branch)

    def get(self, request, pk):
        product = self.get_object(request, pk)
        return render(request, "product_update.html", {"product": product})

    def post(self, request, pk):
        product = self.get_object(request, pk)

        product.name = request.POST["name"]
        product.brand = request.POST.get("brand")
        product.price = Decimal(request.POST["price"])
        product.amount = Decimal(request.POST["amount"])
        product.save()

        return redirect('products')


class ProductDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def get_object(self, request, pk):
        return get_object_or_404(Product, pk=pk, branch=request.user.branch)

    def get(self, request, pk):
        product = self.get_object(request, pk)
        return render(request, "product_delete.html", {"product": product})

    def post(self, request, pk):
        product = self.get_object(request, pk)
        product.delete()
        return redirect('products')


class ClientsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        clients = Client.objects.filter(branch=request.user.branch)
        return render(request, "clients.html", {"clients": clients})

    def post(self, request):
        Client.objects.create(
            name=request.POST["name"],
            shop_name=request.POST.get("shop_name"),
            phone_number=request.POST.get("phone_number"),
            address=request.POST.get("address"),
            branch=request.user.branch,
        )
        return redirect('clients')


class SalesView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        sales = Sale.objects.filter(branch=request.user.branch).order_by('-id')
        products = Product.objects.filter(branch=request.user.branch)
        clients = Client.objects.filter(branch=request.user.branch)

        return render(request, "sales.html", {
            "sales": sales,
            "products": products,
            "clients": clients
        })


class SaleCreateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        product = Product.objects.get(id=request.POST['product_id'])
        client = Client.objects.get(id=request.POST['client_id'])

        amount = Decimal(request.POST['amount'])
        paid = Decimal(request.POST.get('paid_price', 0))

        total = product.price * amount
        debt = total - paid

        Sale.objects.create(
            product=product,
            client=client,
            amount=amount,
            total_price=total,
            paid_price=paid,
            debt_price=debt,
            user=request.user,
            branch=request.user.branch
        )

        # Ombordan kamaytirish
        product.amount -= amount
        product.save()

        return redirect('sales')


class PayDebtCreateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        client = Client.objects.get(id=request.POST['client_id'])

        PayDebt.objects.create(
            client=client,
            amount=Decimal(request.POST['amount']),
            user=request.user,
            branch=request.user.branch
        )

        return redirect('clients')


class ImportsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        imports = ImportP.objects.filter(branch=request.user.branch).order_by('-id')
        return render(request, "imports.html", {"imports": imports})


class PaymentsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        payments = PayDebt.objects.filter(branch=request.user.branch).order_by('-id')
        return render(request, "payments.html", {"payments": payments})