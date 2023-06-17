from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    context = {
        'tela_name': 'Tela inicial',
    }
    return render(request, 'core/index.html', context=context)
