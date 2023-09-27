from django.db import models


# Create your models here.
class SiteConfig(models.Model):
    termos_de_uso = models.TextField(default="Termos de uso")

    class Meta:
        verbose_name = 'Configurações do site'
        verbose_name_plural = 'Configurações do site'

    def __str__(self):
        return 'Configurações do site'
