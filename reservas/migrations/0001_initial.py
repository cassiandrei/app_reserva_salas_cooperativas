# Generated by Django 4.2.1 on 2023-07-01 14:52

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Sala",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=50, verbose_name="Nome")),
                ("imagem", models.ImageField(upload_to="salas", verbose_name="Imagem")),
            ],
        ),
    ]