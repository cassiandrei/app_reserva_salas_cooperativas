from functools import cached_property

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from reservas.models import Sala, Reserva


class SalasAtivasMixin:
    queryset = Sala.objects.filter(ativo=True)


class ReservasSalaMixin:
    object: Sala

    @cached_property
    def get_data_selecionada(self):
        data_selecionada = self.request.GET.get('data_selecionada', None)
        if data_selecionada:
            data_selecionada = timezone.datetime.strptime(data_selecionada, '%Y-%m-%d').date()
        else:
            data_selecionada = timezone.now().date()
        return data_selecionada

    @cached_property
    def get_semana_selecionada(self):
        """
            python         humanos
            1 - segunda    domingo
            2 - terça      segunda
            3 - quarta     terça
            4 - quinta     quarta
            5 - sexta      quinta
            6 - sabado     sexta
            7 - domingo    sabado
        """
        isocalendar = self.get_data_selecionada.isocalendar()
        week = isocalendar[1]
        weekday_python = isocalendar[2]
        weekday_humano = (weekday_python + 1) % 7 or 7

        if weekday_humano < weekday_python:
            week += 1

        return week

    def get_reservas_queryset(self):
        raise ImproperlyConfigured("Função get_reservas_queryset não implementada")

    def get_reservas(self):
        item: Reserva
        return [
            item.serialize() for item in self.get_reservas_queryset().iterator()
        ]
