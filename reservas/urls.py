from django.urls import path

from reservas.views import UnidadesListView, SalaView, CalendarioView

app_name = 'reservas'
urlpatterns = [
    path('', UnidadesListView.as_view(), name='unidades'),
    path('unidade/sala/<slug>', SalaView.as_view(), name='sala'),
    path('calendario/sala/<sala_slug>/<ano>/<semana>', CalendarioView.as_view(), name='calendario_com_semana'),
    path('calendario/sala/<sala_slug>', CalendarioView.as_view(), name='calendario_sem_semana'),
]
