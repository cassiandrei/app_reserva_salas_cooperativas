import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.utils import get_time_astimezone
from reservas.models import Unidade, Sala
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now


# Create your views here.

# UNIDADES FUNCTION VIEW
@login_required
def unidades(request):
    unidades = Unidade.objects.filter(ativo=True)
    context = {"unidades": unidades}
    return render(request, 'reservas/unidades/index.html', context=context)


# UNIDADES CLASS VIEW
class UnidadesListView(LoginRequiredMixin, ListView):
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
        sala: Sala = get_object_or_404(Sala, unidade=unidade, slug=sala_selecionada)
    else:
        sala: Sala = unidade.get_salas_ativas().first()

    # data selecionada do datepicker
    # todo implementar get do datepicker
    data_selecionada = now().date()

    reservas = sala.get_reservas_no_dia(data_selecionada)

    context = {
        "unidade": unidade,
        "sala": sala,
        "data_selecionada": data_selecionada,
        "slotMinTime":  sala.get_horario_inicial(data_selecionada).strftime('%H:%M:%S'),
        "slotMaxTime":  sala.get_horario_termino(data_selecionada).strftime('%H:%M:%S')
    }
    return render(request, 'reservas/unidade/index.html', context=context)


def calendario(request, sala_slug, ano=None, semana=None):
    # obtem a sala
    sala = get_object_or_404(Sala, slug=sala_slug)
    data_atual = now().date()

    # pre definição do ano e semana
    if not ano and not semana:
        ano = data_atual.isocalendar()[0]  # year
        semana = data_atual.isocalendar()[1]  # weeknumber

    reservas = sala.get_reservas_na_semana(int(ano), int(semana))

    context = {
        reservas: reservas
    }
    return render(request, 'reservas/unidade/calendario.html', context)
