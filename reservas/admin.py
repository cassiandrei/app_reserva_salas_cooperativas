from django.contrib import admin

from reservas.models import Sala, Reserva, ConfigAgendaSala, Unidade

# Register your models here.
admin.site.register(Unidade)
admin.site.register(Reserva)


@admin.register(ConfigAgendaSala)
class ConfigAgendaSalaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'horario_abertura', 'horario_encerramento', 'duracao_minima_reserva']


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'unidade']
    list_filter = ['ativo', 'config', 'unidade']
    search_fields = ['nome', 'unidade__nome']
