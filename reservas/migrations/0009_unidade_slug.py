# Generated by Django 4.2.1 on 2023-07-22 14:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reservas", "0008_alter_sala_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="unidade",
            name="slug",
            field=models.SlugField(null=True, unique=True),
        ),
    ]
