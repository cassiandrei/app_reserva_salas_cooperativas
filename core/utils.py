from django.utils import timezone
import pytz
from datetime import datetime


def get_time_astimezone(meu_horario: datetime.time, tzinfo=None):
    # Suponha que meu_horario é um objeto time representando um horário UTC
    # Crie um objeto datetime usando uma data qualquer, já que você só precisa do horário
    data_atual = timezone.localdate()  # A data pode ser qualquer uma
    datetime_utc = datetime.combine(data_atual, meu_horario)

    # Definir o fuso horário UTC para o datetime criado
    utc_zone = pytz.timezone('UTC')
    datetime_utc = utc_zone.localize(datetime_utc)

    # Definir o fuso horário desejado
    if not tzinfo:
        tzinfo = timezone.get_default_timezone()  # pega a timezone local
    datetime_astimezone = datetime_utc.astimezone(tzinfo)  # converte para timezone local

    # Retorna apenas o horário, sem a data
    return datetime_astimezone.timetz()
