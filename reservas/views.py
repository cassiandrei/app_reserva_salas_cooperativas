import datetime
from functools import cached_property

from reservas.mixins import SalasAtivasMixin, ReservasSalaMixin, MixinTrocarSalaMixin
from reservas.models import Unidade, Sala
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


# UNIDADES CLASS VIEW
class UnidadesListView(LoginRequiredMixin, ListView):
    queryset = Unidade.objects.filter(ativo=True, todas_salas__isnull=False).distinct()
    template_name = 'reservas/unidades/index.html'
    context_object_name = "unidades"


class SalaView(LoginRequiredMixin, SalasAtivasMixin, ReservasSalaMixin, MixinTrocarSalaMixin, DetailView):
    object: Sala
    template_name = 'reservas/sala/index.html'

    def get_reservas_queryset(self):
        return self.object.get_reservas_no_dia(self.get_data_selecionada)

    def get_context_data(self, **kwargs):
        data_selecionada = self.get_data_selecionada
        return {
            **super().get_context_data(**kwargs),
            "data_selecionada": data_selecionada,
            "reservas": self.get_reservas(),
            "slotMinTime": self.object.get_horario_inicial_dia(data_selecionada).strftime('%H:%M:%S'),
            "slotMaxTime": self.object.get_horario_termino_dia(data_selecionada).strftime('%H:%M:%S')
        }


class CalendarioView(LoginRequiredMixin, SalasAtivasMixin, ReservasSalaMixin, MixinTrocarSalaMixin, DetailView):
    object: Sala
    template_name = "reservas/sala/calendario.html"
    slug_url_kwarg = "sala_slug"

    def get_reservas_queryset(self):
        return self.object.get_reservas_na_semana(int(self.kwargs['ano']), self.get_semana_selecionada)

    @cached_property
    def get_semana_selecionada(self):
        if self.request.GET.get('data_selecionada', None):
            return super().get_semana_selecionada
        return int(self.kwargs['semana'])

    @staticmethod
    def get_data_initial(ano, semana):
        dia_1_ano = datetime.date(ano, 1, 1)
        return dia_1_ano + datetime.timedelta(days=7 * (semana - 1))

    def get_next_week(self):
        ano = int(self.kwargs['ano'])
        semana = int(self.kwargs['semana']) + 1
        return {
            "ano": ano,
            "semana": semana,
        }

    def get_previous_week(self):
        ano = int(self.kwargs['ano'])
        semana = int(self.kwargs['semana']) - 1
        if semana == 0:
            ano = ano - 1
            semana = 52
        return {
            "ano": ano,
            "semana": semana,
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "reservas": self.get_reservas(),
            "data_inicial": self.get_data_initial(int(self.kwargs['ano']), int(self.kwargs['semana'])),
            "slotMinTime": self.object.get_horario_inicial_semana(int(self.kwargs['ano']),
                                                                  self.get_semana_selecionada).strftime('%H:%M:%S'),
            "slotMaxTime": self.object.get_horario_termino_semana(int(self.kwargs['ano']),
                                                                  self.get_semana_selecionada).strftime('%H:%M:%S')
        }
