from django.urls import path

from reservas.views import unidades, unidade, UnidadesListView, calendario

app_name = 'reservas'
urlpatterns = [
    path('', UnidadesListView.as_view(), name='unidades'),
    path('unidade/<slug>', unidade, name='unidade'),
    path('calendario/<sala_slug>/<ano>/<semana>', calendario, name='calendario'),
    path('calendario/<sala_slug>', calendario, name='calendario'),
]
