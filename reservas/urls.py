from django.urls import path

from reservas.views import unidade, UnidadesListView, calendario, SalaView

app_name = 'reservas'
urlpatterns = [
    path('', UnidadesListView.as_view(), name='unidades'),
    path('unidade/sala/<slug>', SalaView.as_view(), name='sala'),
    path('calendario/<sala_slug>/<ano>/<semana>', calendario, name='calendario'),
    path('calendario/<sala_slug>', calendario, name='calendario'),
]
