from __future__ import annotations

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


def get_config_padrao():
    return 1  # pk da config padrão


class Unidade(models.Model):
    nome = models.CharField("Nome", max_length=50)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    ativo = models.BooleanField(default=True)
    todas_salas: models.Manager[Sala]

    def get_absolute_url(self):
        return reverse("reservas:unidade", kwargs={"slug": self.slug})

    def get_salas_ativas(self):
        return self.todas_salas.filter(ativo=True)

    def __str__(self):
        return self.nome


def get_path_sala_imagem(instance, filename):
    return f"unidades/{instance.unidade.slug}/salas/{instance.slug}.{filename.split('.')[-1]}"


class Sala(models.Model):
    nome = models.CharField("Nome", max_length=50)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    imagem = models.ImageField("Imagem", upload_to=get_path_sala_imagem)
    ativo = models.BooleanField("Ativo", default=True)
    config = models.ForeignKey(
        "reservas.ConfigAgendaSala", on_delete=models.SET(get_config_padrao),
    )
    unidade = models.ForeignKey("reservas.Unidade", on_delete=models.PROTECT, related_name='todas_salas')
    todas_reservas: models.Manager[Reserva]

    def __str__(self):
        return self.nome

    def get_config_horario_abertura(self):
        return self.config.horario_abertura

    def get_config_horario_encerramento(self):
        return self.config.horario_encerramento

    def get_reservas_no_dia(self, data: datetime.date):
        # retorna todas as reservas da sala no dia do parametro
        reservas = self.todas_reservas.filter(horario_inicio__date=data)
        return reservas

    def get_horario_inicial(self, data: datetime.date):
        reservas = self.get_reservas_no_dia(data)
        if reservas.exists():
            reservas_anteriores = reservas.filter(horario_inicio__time__lte=self.config.horario_abertura)
            if reservas_anteriores.exists():
                return reservas_anteriores.first().horario_inicio

        return self.config.horario_abertura



class Reserva(models.Model):
    titulo = models.CharField("Título", max_length=50)
    horario_inicio = models.DateTimeField("Horário Início")
    horario_termino = models.DateTimeField("Horário Término")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name='todas_reservas')

    class Meta:
        ordering = ["sala", "horario_inicio"]

    def __str__(self):
        reservada = (
            f"Reservada - {self.user.get_full_name()}" if self.user else "Disponível"
        )
        return f"{self.sala.nome} - {self.horario_inicio.strftime('%d/%m/%Y %H:%M')}" \
               f" - {self.horario_termino.strftime('%d/%m/%Y %H:%M')} - {reservada}"


class ConfigAgendaSala(models.Model):
    nome = models.CharField("Nome", max_length=20)
    horario_abertura = models.TimeField("Horário Abertura da Sala")
    horario_encerramento = models.TimeField("Horário Encerramento da Sala")
    duracao_minima_reserva = models.PositiveSmallIntegerField(
        "Duração em minutos miníma pra reserva"
    )

    def __str__(self):
        return self.nome
