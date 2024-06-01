import datetime
from functools import cached_property

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from reservas.forms import ReservaForm
from reservas.mixins import SalasAtivasMixin, ReservasSalaMixin, MixinTrocarSalaMixin
from reservas.models import Unidade, Sala, Reserva
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin


# UNIDADES CLASS VIEW
class UnidadesListView(LoginRequiredMixin, ListView):
    queryset = Unidade.objects.filter(ativo=True, todas_salas__isnull=False).distinct()
    template_name = "reservas/unidades/index.html"
    context_object_name = "unidades"


class SalaView(
    LoginRequiredMixin,
    SalasAtivasMixin,
    ReservasSalaMixin,
    MixinTrocarSalaMixin,
    DetailView,
):
    object: Sala
    template_name = "reservas/sala/index.html"

    def get_reservas_queryset(self):
        return self.object.get_reservas_no_dia(self.get_data_selecionada)

    def get_context_data(self, **kwargs):
        data_selecionada = self.get_data_selecionada
        return {
            **super().get_context_data(**kwargs),
            "data_selecionada": data_selecionada,
            "reservas": self.get_reservas(),
            "slotMinTime": self.object.get_horario_inicial_dia(
                data_selecionada
            ).strftime("%H:%M:%S"),
            "slotMaxTime": self.object.get_horario_termino_dia(
                data_selecionada
            ).strftime("%H:%M:%S"),
        }


class CalendarioView(
    LoginRequiredMixin,
    SalasAtivasMixin,
    ReservasSalaMixin,
    MixinTrocarSalaMixin,
    DetailView,
):
    object: Sala
    template_name = "reservas/sala/calendario.html"
    slug_url_kwarg = "sala_slug"

    def get_reservas_queryset(self):
        return self.object.get_reservas_na_semana(
            int(self.kwargs["ano"]), self.get_semana_selecionada
        )

    @cached_property
    def get_semana_selecionada(self):
        if self.request.GET.get("data_selecionada", None):
            return super().get_semana_selecionada
        return int(self.kwargs["semana"])

    @staticmethod
    def get_data_initial(ano, semana):
        dia_1_ano = datetime.date(ano, 1, 1)
        return dia_1_ano + datetime.timedelta(days=7 * (semana - 1))

    def get_next_week(self):
        ano = int(self.kwargs["ano"])
        semana = int(self.kwargs["semana"]) + 1
        return {
            "ano": ano,
            "semana": semana,
        }

    def get_previous_week(self):
        ano = int(self.kwargs["ano"])
        semana = int(self.kwargs["semana"]) - 1
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
            "data_inicial": self.get_data_initial(
                int(self.kwargs["ano"]), int(self.kwargs["semana"])
            ),
            "slotMinTime": self.object.get_horario_inicial_semana(
                int(self.kwargs["ano"]), self.get_semana_selecionada
            ).strftime("%H:%M:%S"),
            "slotMaxTime": self.object.get_horario_termino_semana(
                int(self.kwargs["ano"]), self.get_semana_selecionada
            ).strftime("%H:%M:%S"),
        }


class ReservaFormView(LoginRequiredMixin, ReservasSalaMixin, FormView):
    object: Sala | None
    form_class = ReservaForm
    template_name = "reservas/sala/reserva_form.html"

    def get_object(self):
        return Sala.objects.get(slug=self.kwargs["slug"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ano = None
        self.semana = None
        self.object = None

    def get_initial(self):
        return self.request.GET

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance: Reserva = form.save()
        messages.success(self.request, "Reserva criada com sucesso")
        self.ano = instance.horario_inicio.year
        self.semana = instance.horario_inicio.isocalendar()[1]
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        sala_slug = self.kwargs["slug"]
        return reverse(
            "reservas:calendario_com_semana",
            kwargs={"sala_slug": sala_slug, "ano": self.ano, "semana": self.semana},
        )

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        return {
            **super().get_form_kwargs(),
            "request": self.request,
            "sala": self.object,
        }
