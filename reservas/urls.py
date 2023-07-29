from django.urls import path

from reservas.views import unidades

app_name = 'reservas'
urlpatterns = [
    path('', unidades, name='unidades')
]