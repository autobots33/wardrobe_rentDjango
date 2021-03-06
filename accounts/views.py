from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from validate_email import validate_email
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
#from decorators import auth_user_should_not_access
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_activation_email(user,request):
    current_site = get_current_site(request)
    email_subject = 'Active your Account'
    email_body = render_to_string('authentication/activate.html',
          {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
                                   }
                                   )
        
    email=EmailMessage(
    subject=email_subject,
            body=email_body,
            from_emali=settings.EMAIL_FROM_USER,
            to=[user.emali]
           
    )    
    EmailThread(email).start()   


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        context = {

            'data': request.POST,
            'has_error': False
        }

        email = request.POST.get('email')
        username = request.POST.get('username')
        full_name = request.POST.get('name')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'Passwords should be atleast 6 characters long')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 "Passwords does not match")
            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please provide a valid email')
            context['has_error'] = True

        try:
            if User.objects.get(email=email):
                messages.add_message(request, messages.ERROR, 'Email is taken')
                context['has_error'] = True

        except Exception as e:
            pass

        try:
            if User.objects.get(username=username):
                messages.add_message(
                    request, messages.ERROR, 'Username is taken')
                context['has_error'] = True

        except Exception as e:
            pass

        if context['has_error']:
            return render(request, 'authentication/register.html', context)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.first_name = full_name
        user.last_name = full_name
        user.is_active = False
        user.save()
        
        send_activation_email(user, request)
       
        messages.add_message(request, messages.SUCCESS,
                             'We have sent you link to verify your account')

        return redirect('login')
    


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'has_error': False
        }
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == '':
            messages.add_message(request, messages.ERROR,
                                 'Username is required')
            context['has_error'] = True
        if password == '':
            messages.add_message(request, messages.ERROR,
                                 'Password is required')
            context['has_error'] = True
        user = authenticate(request, username=username, password=password)

        if not user and not context['has_error']:
            messages.add_message(request, messages.ERROR, 'Invalid Credentials')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'authentication/login.html', status=401, context=context)
        login(request, user)
        messages.add_message(request, messages.SUCCESS,
                                 f'Welcome {user.username}')
        return redirect('home')


class activate_user(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as e:
            user = None
        if user and generate_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Email verified successfully, you can now login ')
            return redirect('login')
        return render(request, 'authentication/activate-failed.html', {'user':user})


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Logout successfully')
        return redirect('login')


class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'authentication/request-reset-email.html')

    def post(self, request):
        email = request.POST['email']

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')
            return render(request, 'authentication/request-reset-email.html')

        user = User.objects.filter(email=email)

        if user.exists():
            current_site = get_current_site(request)
            email_subject = '[Reset your Password]'
            message = render_to_string('authentication/reset-user-password.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )

            EmailThread(email_message).start()

        messages.success(
            request, 'We have sent you an email with instructions on how to reset your password')
        return render(request, 'authentication/request-reset-email.html')


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password reset link, is invalid, please request a new one')
                return render(request, 'auth/request-reset-email.html')

        except DjangoUnicodeDecodeError as e:
            messages.success(
                request, 'Invalid link')
            return render(request, 'authentication/request-reset-email.html')

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'passwords should be at least 6 characters long')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'passwords don`t match')
            context['has_error'] = True

        if context['has_error'] == True:
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(
                request, 'Password reset success, you can login with new password')

            return redirect('login')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'Something went wrong')
            return render(request, 'authentication/set-new-password.html', context)

       