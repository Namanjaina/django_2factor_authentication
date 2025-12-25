
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
import random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create and save user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)  # important
            )

            messages.success(request, "Account created successfully!")
            return redirect('login')   # redirect to login page

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

# Login View with OTP

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check username + password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login user temporarily BEFORE OTP
            login(request, user)

            # Generate OTP
            otp = random.randint(100000, 999999)

            # Save OTP and email in session
            request.session['otp'] = otp
            request.session['email'] = user.email

            # Send OTP Email
            send_mail(
                'Your Login OTP',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return redirect('otp')   # go to OTP verification page

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')



def otp_view(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')          # OTP user typed
        session_otp = request.session.get('otp')    # OTP stored in session

        if int(user_otp) == int(session_otp):
            # OTP correct → allow access
            request.session['is_verified'] = True
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'accounts/otp_verify.html')

@login_required
def dashboard(request):
    # Check if OTP is verified
    if not request.session.get('is_verified'):
        return redirect('login')

    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    logout(request)
    request.session.flush()   # clear OTP + session
    return redirect('login')

def resend_otp(request):
    email = request.session.get('email')

    if not email:
        messages.error(request, "Session expired. Please login again.")
        return redirect('login')

    # Generate new OTP
    otp = random.randint(100000, 999999)
    request.session['otp'] = otp

    # Send email
    send_mail(
        'Your New OTP',
        f'Your new OTP is {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('otp')
