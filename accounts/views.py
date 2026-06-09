from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout


def register(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('/accounts/login/')

    return render(
        request,
        'register.html'
    )


def user_login(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('/')

    return render(
        request,
        'login.html'
    )


def user_logout(request):

    logout(request)

    return redirect('/')