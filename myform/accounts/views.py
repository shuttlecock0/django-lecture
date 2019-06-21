from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash, get_user_model
from .forms import CustomUserChangeForm, CustomUserCreationForm
from boards.models import Board
# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # form이 저장되고 user session을 create한다.
            user = form.save()
            auth_login(request, user)
            return redirect('boards:index')
    else:
        form = CustomUserCreationForm()
    context = {'form': form,}
    return render(request, 'accounts/auth_form.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('boards:index')
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user()) # user session create
            return redirect(request.GET.get('next') or 'boards:index')
    else:
        form = AuthenticationForm()
    context = {'form':form}
    return render(request, 'accounts/login.html', context)
    
def logout(request):
    auth_logout(request)
    return redirect('boards:index')

def delete(request):
    if request.method == 'POST':
        request.user.delete()
    return redirect('boards:index')

def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('boards:index')
    else:
        form = CustomUserChangeForm(instance = request.user)
    context = {'form':form}
    return render(request, 'accounts/auth_form.html', context)

def change_password(request):
    if request.method=='POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            #현재 사용자의 session이 무효화 되는 것을 막고 session을 그대로 유지함
            update_session_auth_hash(request, user)
            return redirect('boards:index')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form':form}
    return render(request, 'accounts/auth_form.html', context)

def profile(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    context = {'person': person,}
    return render(request, 'accounts/profile.html', context)