from __future__ import annotations

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone


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
        return "#"

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
        ordering = ["unidade", "slug"]

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

        if primeiro_dia_do_ano.weekday() != 6:
            # recuperar o domingo da semana 1
            domingo_semana_1 = primeiro_dia_do_ano - datetime.timedelta(
                days=primeiro_dia_do_ano.weekday() + 1
            )
        else:
            # domingo é ele proprio
            domingo_semana_1 = primeiro_dia_do_ano

        data_inicio = domingo_semana_1 + datetime.timedelta(weeks=semana - 1)
        data_fim = data_inicio + datetime.timedelta(days=6)
        reservas = self.todas_reservas.filter(
            horario_inicio__date__gte=data_inicio, horario_inicio__date__lte=data_fim
        )
        return reservas

    def get_horario_inicial_dia(self, data: datetime.date) -> datetime.time:
        reservas = self.get_reservas_no_dia(data)
        if reservas_anteriores := reservas.filter(
            horario_inicio__time__lte=self.config.horario_abertura
        ):
            return reservas_anteriores.first().horario_inicio.astimezone().time()
        return self.config.horario_abertura

    def get_horario_termino_dia(self, data: datetime.date) -> datetime.time:
        reservas = self.get_reservas_no_dia(data)
        if reservas_superiores := reservas.filter(
            horario_termino__time__gte=self.config.horario_encerramento
        ):
            return reservas_superiores.last().horario_termino.astimezone().time()
        return self.config.horario_encerramento

    def get_horario_inicial_semana(self, ano: int, semana: int) -> datetime.time:
        reservas = self.get_reservas_na_semana(ano, semana)
        if reservas_anteriores := reservas.filter(
            horario_inicio__time__lte=self.config.horario_abertura
        ):
            return reservas_anteriores.first().horario_inicio.astimezone().time()
        return self.config.horario_abertura

    def get_horario_termino_semana(self, ano: int, semana: int) -> datetime.time:
        reservas = self.get_reservas_na_semana(ano, semana)
        if reservas_superiores := reservas.filter(
            horario_termino__time__gte=self.config.horario_encerramento
        ):
            return reservas_superiores.last().horario_termino.astimezone().time()
        return self.config.horario_encerramento

    def get_absolute_url(self):
        return reverse("reservas:sala", args=(self.slug,))

    def get_calendario_url(self):
        return reverse("reservas:calendario_com_semana", args=(self.slug,))


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

    def duracao_reserva(self) -> int:
        return int((self.horario_termino - self.horario_inicio).seconds / 60)

    def has_conflito_horario(self) -> bool:
        return self.sala.todas_reservas.filter(
            models.Q(
                horario_inicio__lte=self.horario_inicio,
                horario_termino__gte=self.horario_inicio,
            )
            | models.Q(
                horario_inicio__gte=self.horario_termino,
                horario_termino__lte=self.horario_termino,
            )
        ).exists()

    def has_datas_diferentes_na_reserva(self) -> bool:
        return self.horario_inicio.date() != self.horario_termino.date()

    def clean(self):
        if self.horario_termino <= self.horario_inicio:
            raise ValidationError(
                {"horario_termino": "Horário término deve ser maior que horário Início"}
            )

        if self.duracao_reserva() < self.sala.config.duracao_minima_reserva:
            raise ValidationError(
                {
                    "horario_termino": f"A duração da reserva deve ser no minímo {self.sala.config.duracao_minima_reserva} minutos."
                }
            )

        if self.has_conflito_horario():
            raise ValidationError(
                "Já existe outra reserva conflitando com esse período."
            )

        if self.has_datas_diferentes_na_reserva():
            raise ValidationError(
                "Horário de início deve ser no mesmo dia do horário de término"
            )

    def get_reserva_status(self):
        now = timezone.now()
        if self.horario_termino < now:
            return "reserva_encerrada"
        elif self.horario_inicio <= now <= self.horario_termino:
            return "reserva_andamento"
        else:
            return "reserva_reservada"

    def get_evento_cor(self):
        status_cores = {
            "reserva_encerrada": {
                "backgroundColor": "grey",
                "borderColor": "grey",
                "textColor": "000000",
            },
            "reserva_andamento": {
                "backgroundColor": "#3788d8",
                "borderColor": "#000000",
                "textColor": "#FFFFFF",
            },
            "reserva_reservada": {
                "backgroundColor": "#FCF442",
                "borderColor": "#000000",
                "textColor": "red",
            },
        }

        if self.get_reserva_status() in status_cores:
            return status_cores[self.get_reserva_status()]
        return status_cores["reserva_andamento"]

    def serialize(self):
        return {
            "title": f"{self.titulo} ({self.user.get_full_name()})",
            "start": timezone.localtime(self.horario_inicio).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "end": timezone.localtime(self.horario_termino).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "class": self.get_reserva_status(),
            **self.get_evento_cor(),
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
