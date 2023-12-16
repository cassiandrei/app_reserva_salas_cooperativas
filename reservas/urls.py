from django.urls import path

from reservas.views import UnidadesListView, calendario, SalaView, CalendarioView

app_name = 'reservas'
urlpatterns = [
    path('', UnidadesListView.as_view(), name='unidades'),
    path('unidade/sala/<slug>', SalaView.as_view(), name='sala'),
    path('calendario/<sala_slug>/<ano>/<semana>', calendario, name='calendario'),
    path('calendario/<slug>', CalendarioView.as_view(), name='calendario'),
]
