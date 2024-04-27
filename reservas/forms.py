from django import forms

from reservas.models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['titulo', 'horario_inicio', 'horario_termino']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'horario_termino': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.sala = kwargs.pop('sala')
        super().__init__(*args, **kwargs)

    def clean(self):
        self.instance.user = self.request.user
        self.instance.sala = self.sala
        return super().clean()
