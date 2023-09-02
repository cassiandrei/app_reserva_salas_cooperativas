import datetime
import os

import requests
from django.shortcuts import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

from reservas.models import Unidade, Sala


class ReservasTest(TestCase):
    fixtures = ["users.yaml", "configsalas.yaml", "unidades.yaml", "salas.yaml"]

    def setUp(self) -> None:
        # get usuário pk=1 (cassiano)
        self.user = User.objects.first()
        self.user.set_password('teste1234')
        self.user.save()

        self.client_autenticado = Client()
        self.client_autenticado.force_login(self.user)


class TelaInicialUnidades(ReservasTest):
    '''
        Tela da lista das unidades
    '''

    def test_tela_inicial_redirect(self):
        """
        Tela de unidades deve exibir todas unidades cadastradas
        """

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

        # testando se o usuario está sendo redirecionado para unidades url
        self.assertEqual(response.url, rota_inicial)

        # realizando o acesso na url da rota inicial
        response = self.client.get(response.url)

        # teste de redirecionamento
        # get a URL das unidades
        index_unidades_url = reverse("reservas:unidades")
        self.assertRedirects(response, index_unidades_url)

    def test_contagem_unidades(self):
        """
        Tela de unidades deve exibir todas unidades cadastradas
        """

        # get usuário pk=1 (cassiano)
        self.user = User.objects.first()
        self.user.set_password('teste1234')
        self.user.save()

        # get a URL de login
        login_url = reverse("user:login")

        # get a URL das unidades
        index_unidades_url = reverse("reservas:unidades")

        # fazendo um GET na url
        response = self.client.get(index_unidades_url)

        # testando se o usuario não autenticado está sendo redirecionado
        self.assertRedirects(response, f"{login_url}?next={index_unidades_url}")

        # fazer um POST na tela de login
        response = self.client.post(
            response.url, {"username": self.user.username, "password": "teste1234"}
        )

        # testando se o usuario está sendo redirecionado para unidades url
        self.assertEqual(response.url, index_unidades_url)

        # realizando o acesso na url unidades
        response = self.client.get(response.url)

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


class TelaCarroselUnidade(ReservasTest):
    '''
        Tela Carrosel Unidade
    '''

    def test_usuario_logado(self):
        # get a URL de login
        login_url = reverse("user:login")

        sala = Sala.objects.first()

        # rota da sala
        url_sala = reverse('reservas:unidade', kwargs={"slug": sala.slug})

        # fazendo um GET na URL
        response = self.client.get(url_sala)

        # testando se o usuario não autenticado está sendo redirecionado para tela login
        self.assertRedirects(response, f"{login_url}?next={url_sala}")

    def test_componentes_basicos_carrosel(self):
        # consulta todas unidades ativas
        unidades = Unidade.objects.filter(ativo=True)

        for unidade in unidades:
            # acessando a tela da sala (carrosel)
            url_unidade = reverse('reservas:unidade', kwargs={"slug": unidade.slug})
            response = self.client_autenticado.get(url_unidade)

            # Teste para verificar componente de selecionar data
            self.assertContains(response, 'id="componente_selecionar_data"',
                                msg_prefix="Componente de selecionar data não está sendo exibida")

            # Teste para verificar se a imagem está exibida
            self.assertContains(response, 'id="imagem_sala"',
                                msg_prefix="Componente de selecionar sala não está sendo exibida")

            # Teste para verificar se a tabela de hoŕarios está sendo exibida
            self.assertContains(response, 'id="lista_horarios"',
                                msg_prefix="Componente de lista horários não está sendo exibida")

    def test_imagem_nome_sala_correspondente(self):
        # consulta todas unidades ativas
        unidades = Unidade.objects.filter(ativo=True)

        for unidade in unidades:
            # acessando a tela da sala (carrosel)
            url_unidade = reverse('reservas:unidade', kwargs={"slug": unidade.slug})

            for sala in unidade.todas_salas.filter(ativo=True):
                
                url_sala = url_unidade + f'?sala={sala.slug}'

                # teste para verificar o nome do arquivo correspondente a sala
                nome_arquivo_image_sala = os.path.basename(sala.imagem.name)
                self.assertEqual(str(sala.slug), nome_arquivo_image_sala.split('.')[0])

                # testando se o caminho da imagem está sendo exibida na tela
                url_imagem = sala.imagem.url
                response = self.client_autenticado.get(url_sala)
                self.assertContains(response, f'src="{url_imagem}"')

                # testando se o nome da sala está sendo exibido na tela
                self.assertContains(response, f'<span>{sala.nome}</span>')

                # todo Verificar o motivo do self.client.get(url_arquivo) sempre retornar 404
                # teste pra verificar se o arquivo está carregando (sendo exibida)
                response = requests.get("http://127.0.0.1:8000" + url_imagem)
                self.assertEqual(response.status_code, 200)

                # verificar o content-type do response
                self.assertTrue(response.headers['Content-Type'].startswith('image/'))

    def test_sala_sem_reservas_no_dia(self):
        # get no dia atual
        dia_hoje = datetime.date.today()

        # consideramos o horário inicial do dia (5 da manhã)
        data_horario_inicial = datetime.datetime(dia_hoje.year, dia_hoje.month, dia_hoje.day, 5, 0, 0)

        # get a primeira sala disponível
        sala = Sala.objects.filter(ativo=True).first()
        url_unidade = reverse('reservas:unidade', kwargs={"slug": sala.unidade.slug})
        url_sala = url_unidade + f'?sala={sala.slug}'

        # pega a configuração da sala
        config = sala.config
        horario_abertura = config.horario_abertura
        horario_encerramento = config.horario_encerramento

        # teste se está retornando nenhuma sala
        reservas = sala.get_reservas_no_dia(dia_hoje)
        self.assertEqual(reservas.count(), 0)

        # tem que exibir o horário inicial da sala no componente
        response = self.client_autenticado.get(url_sala)
        horario_inicial_sala = sala.get_horario_inicial(dia_hoje)

        # todo continuamores no sabado (09/07/2023)
        self.assertContains(response, "")

