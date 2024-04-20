from django import forms

from reservas.models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['titulo', 'horario_inicio', 'horario_termino']

    def save(self, commit=True):
        instance = super().save(commit)
        return instance
