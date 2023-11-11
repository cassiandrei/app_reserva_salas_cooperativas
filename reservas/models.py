from __future__ import annotations

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.timezone import now

from core.utils import get_time_astimezone


def get_config_padrao():
    return 1  # pk da config padrão


class Unidade(models.Model):
    nome = models.CharField("Nome", max_length=50)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    ativo = models.BooleanField(default=True)
    todas_salas: models.Manager[Sala]

    def get_primeira_sala(self):
        return self.todas_salas.first()

    def get_absolute_url(self):
        primeira_sala = self.get_primeira_sala()
        if primeira_sala:
            return reverse("reservas:sala", args=(self.get_primeira_sala().slug,))
        return '#'

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
        "reservas.ConfigAgendaSala",
        on_delete=models.SET(get_config_padrao),
    )
    unidade = models.ForeignKey(
        "reservas.Unidade", on_delete=models.PROTECT, related_name="todas_salas"
    )
    todas_reservas: models.Manager[Reserva]

    class Meta:
        ordering = ['unidade', 'slug']

    def __str__(self):
        return self.nome

    def get_config_horario_abertura(self):
        return self.config.horario_abertura

    def get_config_horario_encerramento(self):
        return self.config.horario_encerramento

    def get_reservas_no_dia(self, data: datetime.date) -> models.QuerySet[Reserva]:
        # retorna todas as reservas da sala no dia do parametro
        reservas = self.todas_reservas.filter(horario_inicio__date=data)
        return reservas

    def get_reservas_na_semana(self, ano, semana):
        primeiro_dia_do_ano = datetime.date(ano, 1, 1)
        primeiro_dia_semana_1 = primeiro_dia_do_ano - datetime.timedelta(
            days=primeiro_dia_do_ano.weekday() + 1
        )
        data_inicio = primeiro_dia_semana_1 + datetime.timedelta(weeks=semana)
        data_fim = data_inicio + datetime.timedelta(days=6)
        reservas = self.todas_reservas.filter(
            horario_inicio__date__gte=data_inicio, horario_inicio__date__lte=data_fim
        )
        return reservas

    def get_horario_inicial(self, data: datetime.date) -> datetime.time:
        reservas = self.get_reservas_no_dia(data)
        if reservas_anteriores := reservas.filter(
                horario_inicio__time__lte=self.config.horario_abertura
        ):
            return reservas_anteriores.first().horario_inicio.astimezone().time()
        return self.config.horario_abertura

    def get_horario_termino(self, data: datetime.date) -> datetime.time:
        reservas = self.get_reservas_no_dia(data)
        if reservas_superiores := reservas.filter(
                horario_termino__time__gte=self.config.horario_encerramento
        ):
            return reservas_superiores.last().horario_termino.astimezone().time()
        return self.config.horario_encerramento

    def get_absolute_url(self):
        return reverse("reservas:sala", args=(self.slug,))


class Reserva(models.Model):
    titulo = models.CharField("Título", max_length=50)
    horario_inicio = models.DateTimeField("Horário Início")
    horario_termino = models.DateTimeField("Horário Término")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    sala = models.ForeignKey(
        Sala, on_delete=models.PROTECT, related_name="todas_reservas"
    )

    class Meta:
        ordering = ["sala", "horario_inicio"]

    def __str__(self):
        reservada = (
            f"Reservada - {self.user.get_full_name()}" if self.user else "Disponível"
        )
        return (
            f"{self.sala.nome} - {timezone.localtime(self.horario_inicio).strftime('%d/%m/%Y %H:%M')}"
            f" - {timezone.localtime(self.horario_termino).strftime('%d/%m/%Y %H:%M')} - {reservada}"
        )

    def get_reserva_class(self):
        now = now()
        if self.horario_termino < now:
            return "reserva_encerrada"
        elif self.horario_inicio <= now <= self.horario_termino:
            return "reserva_andamento"
        else:
            return "reserva_reservada"

    def serialize(self):
        return {
            "title": self.titulo,
            "start": self.horario_inicio.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": self.horario_termino.strftime("%Y-%m-%dT%H:%M:%S"),
            "class": self.get_reserva_class(),
        }


class ConfigAgendaSala(models.Model):
    nome = models.CharField("Nome", max_length=20)
    horario_abertura = models.TimeField("Horário Abertura da Sala")
    horario_encerramento = models.TimeField("Horário Encerramento da Sala")
    duracao_minima_reserva = models.PositiveSmallIntegerField(
        "Duração em minutos miníma pra reserva"
    )

    def __str__(self):
        return self.nome
