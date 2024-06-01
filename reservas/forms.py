import datetime

from crispy_forms.helper import FormHelper
from django import forms

from reservas.models import Reserva


class ReservaForm(forms.ModelForm):
    data = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    horario_inicio = forms.TimeField(
        label="Horário de início",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )
    horario_termino = forms.TimeField(
        label="Horário de término",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )

    class Meta:
        model = Reserva
        fields = ["titulo", "data", "horario_inicio", "horario_termino"]
        widgets = {"titulo": forms.TextInput(attrs={"class": "form-control"})}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.sala = kwargs.pop("sala")
        super().__init__(*args, **kwargs)

        # Configurações do Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.initial = self.request.GET

    def clean_horario_inicio(self):
        data = self.cleaned_data["data"]
        horario_inicio = self.cleaned_data["horario_inicio"]
        string_datetime = f"{data.isoformat()} {horario_inicio.isoformat()}"
        horario_inicio = datetime.datetime.strptime(
            string_datetime, "%Y-%m-%d %H:%M:%S"
        )
        return horario_inicio

    def clean_horario_termino(self):
        data = self.cleaned_data["data"]
        horario_termino = self.cleaned_data["horario_termino"]
        string_datetime = f"{data.isoformat()} {horario_termino.isoformat()}"
        horario_termino = datetime.datetime.strptime(
            string_datetime, "%Y-%m-%d %H:%M:%S"
        )
        return horario_termino

    def clean(self):
        self.instance.user = self.request.user
        self.instance.sala = self.sala
        return super().clean()
