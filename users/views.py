from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout

class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    def post(self, request):
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            login(request, user)
            return redirect('sections')
        return self.get(request)

def logout_view(request):
    logout(request)
    return redirect('login')