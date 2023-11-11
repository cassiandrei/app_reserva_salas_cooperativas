import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.utils import get_time_astimezone
from reservas.models import Unidade, Sala
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now


# UNIDADES CLASS VIEW
class UnidadesListView(LoginRequiredMixin, ListView):
    queryset = Unidade.objects.filter(ativo=True, todas_salas__isnull=False).distinct()
    template_name = 'reservas/unidades/index.html'
    context_object_name = "unidades"


class SalaView(DetailView):
    object: Sala
    model = Sala
    template_name = 'reservas/sala/index.html'

    def get_lista_salas(self):
        return self.object.unidade.todas_salas.order_by('slug')

    def get_proxima_sala(self):
        sala = self.get_lista_salas().filter(slug__gt=self.object.slug).exclude(pk=self.object.pk).first()
        if not sala:
            return self.get_lista_salas().first()
        return sala

    def get_sala_anterior(self):
        sala = self.get_lista_salas().filter(slug__lt=self.object.slug).exclude(pk=self.object.pk).last()
        if not sala:
            return self.get_lista_salas().last()
        return sala

    def get_data_selecionada(self):
        return now().date()

    def get_context_data(self, **kwargs):
        data_selecionada = self.get_data_selecionada()
        return {
            **super().get_context_data(**kwargs),
            "data_selecionada": data_selecionada,
            "slotMinTime": self.object.get_horario_inicial(data_selecionada).strftime('%H:%M:%S'),
            "slotMaxTime": self.object.get_horario_termino(data_selecionada).strftime('%H:%M:%S')
        }


@login_required
def unidade(request, slug):
    # pega a Unidade
    unidade = get_object_or_404(Unidade, slug=slug)

    # data selecionada do datepicker
    # todo implementar get do datepicker
    data_selecionada = now().date()

    reservas = sala.get_reservas_no_dia(data_selecionada)

    context = {
        "unidade": unidade,
        "sala": sala,
        "data_selecionada": data_selecionada,
        "slotMinTime": sala.get_horario_inicial(data_selecionada).strftime('%H:%M:%S'),
        "slotMaxTime": sala.get_horario_termino(data_selecionada).strftime('%H:%M:%S')
    }
    return render(request, 'reservas/sala/index.html', context=context)


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
    return render(request, 'reservas/sala/calendario.html', context)
