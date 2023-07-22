from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from reservas.models import Unidade


class ReservasTest(TestCase):
    fixtures = ["users.yaml", "configsalas.yaml", "unidades.yaml", "salas.yaml"]

    def test_contatem_unidades(self):
        """
        Tela de unidades deve exibir todas unidades cadastradas
        """

        # get a URL das unidades
        index_unidades_url = reverse("reservas:unidades")

        # get a URL de login
        login_url = reverse("user:login")

        # realizando o acesso na url unidades
        response = self.client.get(index_unidades_url)

        # testando se o usuario não autenticado está sendo redirecionado
        self.assertRedirects(response, login_url)

        # get usuário pk=1 (cassiano)
        self.user = User.objects.first()
        self.client.force_login(self.user)

        # realizando o acesso na url unidades
        response = self.client.get(index_unidades_url)

        for unidade in Unidade.objects.filter(ativo=True):
            # Testando se o nome da unidade  sendo exibido
            self.assertContains(
                response,
                unidade.nome,
                msg_prefix=f"Unidade {unidade.nome} deve estar sendo exibida na tela",
            )

            # testando se o link está sendo exibido
            link = reverse('reservas:unidade', kwargs={'slug': unidade.slug})
            self.assertContains(response, f'href="{link}"')
