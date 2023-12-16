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

    def get_reservas_queryset(self):
        raise ImproperlyConfigured("Função get_reservas_queryset não implementada")

    def get_reservas(self):
        item: Reserva
        return [
            item.serialize() for item in self.get_reservas_queryset().iterator()
        ]
