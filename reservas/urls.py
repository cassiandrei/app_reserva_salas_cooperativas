from django.urls import path

from reservas.views import UnidadesListView, SalaView, CalendarioView, ReservaFormView

app_name = 'reservas'
urlpatterns = [
    path('', UnidadesListView.as_view(), name='unidades'),
    path('unidade/sala/<slug>/', SalaView.as_view(), name='sala'),
    path('unidade/sala/<slug>/reservar/', ReservaFormView.as_view(), name='adicionar_reserva'),
    path('calendario/sala/<sala_slug>/<ano>/<semana>/', CalendarioView.as_view(), name='calendario_com_semana'),
]
