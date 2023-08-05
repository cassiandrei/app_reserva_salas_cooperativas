from django.urls import path

from reservas.views import unidades, unidade, UnidadesListView

app_name = 'reservas'
urlpatterns = [
    path('', UnidadesListView.as_view(), name='unidades'),
    path('unidade/<slug>/', unidade, name='unidade'),
]
