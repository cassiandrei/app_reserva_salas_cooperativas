from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


def get_config_padrao():
    return 1  # pk da config padrão


class Unidade(models.Model):
    nome = models.CharField("Nome", max_length=50)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    ativo = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("reservas:unidade", kwargs={"slug": self.slug})

    def __str__(self):
        return self.nome


class Sala(models.Model):
    nome = models.CharField("Nome", max_length=50)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    imagem = models.ImageField("Imagem", upload_to="salas")
    ativo = models.BooleanField("Ativo", default=True)
    config = models.ForeignKey(
        "reservas.ConfigAgendaSala", on_delete=models.SET(get_config_padrao),
    )
    unidade = models.ForeignKey("reservas.Unidade", on_delete=models.PROTECT)

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
    duracao_minima_reserva = models.PositiveSmallIntegerField(
        "Duração em minutos miníma pra reserva"
    )

    def __str__(self):
        return self.nome
