from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from reservas.models import Unidade, Sala
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
    # pega a Unidade
    unidade = get_object_or_404(Unidade, slug=slug)

    # seleciona a sala atraves do argumento sala ou pega a primeira
    sala_selecionada = request.GET.get('sala', None)
    if sala_selecionada:
        sala = get_object_or_404(Sala, unidade=unidade, slug=sala_selecionada)
    else:
        sala = unidade.get_salas_ativas().first()

    context = {
        "unidade": unidade,
        "sala": sala,
    }
    return render(request, 'reservas/unidade/index.html', context=context)
