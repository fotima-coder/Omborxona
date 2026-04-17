# users/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from allauth.account.views import PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import os
import re
import glob
from pathlib import Path


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

        messages.error(request, "Foydalanuvchi nomi yoki parol noto'g'ri")
        return self.get(request)


def logout_view(request):
    logout(request)
    return redirect('login')


class CustomPasswordResetView(PasswordResetView):
    template_name = "account/password_reset.html"
    success_url = reverse_lazy("account_reset_password_done")

    def form_valid(self, form):
        # Email manzilini session'ga saqlash
        email = form.cleaned_data["email"]
        self.request.session['reset_email'] = email
        self.request.session['email_sent_time'] = str(timezone.now())
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "account/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Session'dan email'ni olish
        reset_email = self.request.session.get('reset_email', '')
        if not reset_email:
            reset_email = self.request.GET.get('email', '')

        context['reset_email'] = reset_email

        # Email fayli mavjudligini tekshirish
        context['has_email_file'] = self.check_email_file_exists()

        return context

    def check_email_file_exists(self):
        """Email fayli mavjudligini tekshirish"""
        if hasattr(settings, 'EMAIL_FILE_PATH'):
            email_path = Path(settings.EMAIL_FILE_PATH)
            if email_path.exists():
                files = list(email_path.glob('*.log'))
                return len(files) > 0
        return False


class ViewSentEmailView(View):
    """Yuborilgan email'ni to'g'ri ko'rsatish"""

    def get(self, request):
        # Eng oxirgi email faylini o'qish
        email_content = self.get_latest_email()

        if email_content:
            # Email'dan reset link'ini ajratib olish
            reset_url = self.extract_reset_url(email_content)

            # Foydalanuvchi ma'lumotlarini olish
            user_email = self.extract_email(email_content)
            username = self.extract_username(email_content)

            # Context yaratish
            context = {
                'reset_url': reset_url,
                'user_email': user_email,
                'username': username,
                'site_name': getattr(settings, 'SITE_NAME', 'Munavvar'),
                'domain': get_current_site(request).domain,
                'protocol': 'https' if request.is_secure() else 'http',
            }

            # Agar reset_url topilgan bo'lsa, uni ko'rsatish
            if reset_url:
                context.update({
                    'user': {'get_username': lambda: context.get('username', 'Foydalanuvchi')},
                    'site_name': context.get('site_name', 'Munavvar'),
                    'site_url': settings.DEFAULT_FROM_EMAIL,
                })
                return render(request, 'account/email/password_reset_key_message.html', context)
            else:
                # Agar URL topilmasa, xatolik xabari
                return HttpResponse(self.get_error_html(email_content))
        else:
            return HttpResponse(
                "<h2>📭 Email topilmadi</h2>"
                "<p>Hali email yuborilmagan yoki fayl topilmadi.</p>"
                "<p>Iltimos, avval parolni tiklash so'rovini yuboring.</p>"
                "<a href='/accounts/password/reset/'>Parolni tiklash</a>"
            )

    def get_latest_email(self):
        """Eng oxirgi email faylini o'qish"""
        if hasattr(settings, 'EMAIL_FILE_PATH'):
            email_path = Path(settings.EMAIL_FILE_PATH)
            if email_path.exists():
                files = sorted(email_path.glob('*.log'), key=os.path.getmtime, reverse=True)
                if files:
                    try:
                        with open(files[0], 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        print(f"Email o'qishda xatolik: {e}")
                        return None
        return None

    def extract_reset_url(self, content):
        """Email kontentidan reset URL'ini ajratib olish"""
        # Quoted-printable formatdagi URL'ni tozalash
        # 1. = belgisini va keyingi newline'ni olib tashlash
        content = re.sub(r'=\s*\n\s*', '', content)

        # 2. URL pattern'larini qidirish
        patterns = [
            r'http://[^\s<>"]+/accounts/password/reset/key/[^\s<>"]+/',  # Standard URL
            r'http://[^\s<>"]+/password/reset/key/[^\s<>"]+/',  # Qisqa URL
            r'/accounts/password/reset/key/[^\s<>"]+/',  # Nisbiy URL
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                url = match.group(0)
                # = belgilarini tozalash
                url = url.replace('=\n', '').replace('=', '')
                # Agar nisbiy URL bo'lsa, to'liq URL'ga aylantirish
                if url.startswith('/'):
                    url = f"http://127.0.0.1:8000{url}"
                return url

        return None

    def extract_email(self, content):
        """Email manzilini ajratib olish"""
        match = re.search(r'To:\s*([^\s\n]+@[^\s\n]+)', content)
        return match.group(1) if match else "email@example.com"

    def extract_username(self, content):
        """Foydalanuvchi nomini ajratib olish"""
        match = re.search(r'foydalanuvchi nomingiz:\s*([^\s\n]+)', content, re.IGNORECASE)
        if match:
            return match.group(1)

        # Email'dan username ajratish
        email = self.extract_email(content)
        if '@' in email:
            return email.split('@')[0]

        return "Foydalanuvchi"

    def get_error_html(self, email_content):
        """Xatolik HTML'ini qaytarish"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Email Preview - Xatolik</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .error-box {{
                    background: white;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h2 {{ color: #d32f2f; }}
                pre {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                    font-size: 12px;
                }}
                .notice {{
                    background: #fff3cd;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>⚠️ Havola topilmadi</h2>
                <div class="notice">
                    <p>Email kontentidan parolni tiklash havolasini ajratib olib bo'lmadi.</p>
                    <p>Iltimos, quyidagi email kontentidan URL'ni qo'lda nusxalang.</p>
                </div>
                <h3>Email kontenti:</h3>
                <pre>{email_content}</pre>
                <p style="margin-top: 20px;">
                    <a href="/accounts/password/reset/" style="color: #667eea;">
                        ← Qayta urinib ko'rish
                    </a>
                </p>
            </div>
        </body>
        </html>
        """