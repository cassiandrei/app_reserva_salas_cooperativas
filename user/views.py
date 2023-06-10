from django.shortcuts import render
from django.contrib.auth import login, authenticate
from user.forms import LoginForm


# Create your views here.
def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            # mensagem erro
            pass

    context = {
        'form': form,
    }
    return render(request, 'user/login.html', context=context)
