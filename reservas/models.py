from django.db import models
from django.contrib.auth.models import User


def get_config_padrao():
    return 1  # pk da config padrão


# Create your models here.
class Sala(models.Model):
    nome = models.CharField("Nome", max_length=50)
    imagem = models.ImageField("Imagem", upload_to="salas")
    ativo = models.BooleanField("Ativo", default=True)
    config = models.ForeignKey('reservas.ConfigAgendaSala', on_delete=models.SET(get_config_padrao), null=True)

    def __str__(self):
        return self.nome


class Reserva(models.Model):
    horario_inicio = models.DateTimeField("Horário Início")
    horario_termino = models.DateTimeField("Horário Término")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)

    def __str__(self):
        reservada = (
            f"Reservada - {self.user.get_full_name()}" if self.user else "Disponível"
        )
        return f"{self.sala.nome} - {self.horario_inicio.strftime('%d/%m/%Y %H:%M')} - {self.horario_termino.strftime('%d/%m/%Y %H:%M')} - {reservada}"


class ConfigAgendaSala(models.Model):
    nome = models.CharField("Nome", max_length=20)
    horario_abertura = models.TimeField("Horário Abertura da Sala")
    horario_encerramento = models.TimeField("Horário Encerramento da Sala")
    duracao_minima_reserva = models.PositiveSmallIntegerField("Duração em minutos miníma pra reserva")

    def __str__(self):
        return self.nome
