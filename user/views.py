from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from user.forms import LoginForm


# Create your views here.
def login_view(request):
    form = LoginForm()
    status = None
    if request.method == 'POST':
        form = LoginForm(request.POST)

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            index_url = reverse('core:index')
            next = request.GET.get('next', index_url)
            return redirect(next)
        else:
            # mensagem erro
            status = 401

    context = {
        'form': form,
    }
    return render(request, 'user/login.html', context=context, status=status)
