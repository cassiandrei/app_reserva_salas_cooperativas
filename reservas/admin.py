from django.contrib import admin

from reservas.models import Sala, Reserva, ConfigAgendaSala

# Register your models here.
admin.site.register(Sala)
admin.site.register(Reserva)


@admin.register(ConfigAgendaSala)
class ConfigAgendaSalaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'horario_abertura', 'horario_encerramento', 'duracao_minima_reserva']


