from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reservas.models import Unidade
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

# UNIDADES FUNCTION VIEW
@login_required
def unidades(request):
    unidades = Unidade.objects.filter(ativo=True)
    context = {"unidades": unidades}
    return render(request, 'reservas/unidades/index.html', context=context)


# UNIDADES CLASS VIEW
class UnidadesListView(ListView, LoginRequiredMixin):
    queryset = Unidade.objects.filter(ativo=True)
    template_name = 'reservas/unidades/index.html'
    context_object_name = "unidades"


@login_required
def unidade(request, slug):
    context = {

    }
    return render(request, 'reservas/unidade/index.html', context=context)
