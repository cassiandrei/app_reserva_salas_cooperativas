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

        # get usuário pk=1 (cassiano)
        self.user = User.objects.first()
        self.user.set_password('teste1234')
        self.user.save()

        # get a URL de login
        login_url = reverse("user:login")

        # rota raíz
        rota_inicial = "/"

        # fazendo um GET na rota raíz
        response = self.client.get(rota_inicial)

        # testando se o usuario não autenticado está sendo redirecionado
        self.assertRedirects(response, f"{login_url}?next={rota_inicial}")

        # fazer um POST na tela de login
        response = self.client.post(
            response.url, {"username": self.user.username, "password": "teste1234"}
        )

        # testando se o usuario está sendo redirecionado para a rota inicial
        self.assertEqual(response.url, rota_inicial)

        # fazendo o get na rota inicial
        response = self.client.get(response.url)

        # get a URL das unidades
        index_unidades_url = reverse("reservas:unidades")

        # testando se o usuario está sendo redirecionado para a tela das unidades
        self.assertRedirects(response, index_unidades_url)

        # realizando o acesso na url unidades
        response = self.client.get(response)

        for unidade in Unidade.objects.filter(ativo=True):
            # Testando se o nome da unidade  sendo exibido
            self.assertContains(
                response,
                unidade.nome,
                msg_prefix=f"Unidade {unidade.nome} deve estar sendo exibida na tela",
            )

            # testando se o link está sendo exibido
            link = reverse("reservas:unidade", kwargs={"slug": unidade.slug})
            self.assertContains(response, f'href="{link}"')
