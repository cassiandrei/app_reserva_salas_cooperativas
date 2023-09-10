import datetime
import os
from django.test import TestCase
from django.utils import timezone
import requests
from django.shortcuts import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

from reservas.models import Unidade, Sala


class ReservasTest(TestCase):
    fixtures = ["users.yaml", "configsalas.yaml", "unidades.yaml", "salas.yaml", "reservas.yaml"]

    def setUp(self) -> None:
        # get usuário pk=1 (cassiano)
        self.user = User.objects.first()
        self.user.set_password("teste1234")
        self.user.save()

        self.client_autenticado = Client()
        self.client_autenticado.force_login(self.user)

        # consulta todas unidades ativas
        self.unidades = Unidade.objects.filter(ativo=True)


class TelaInicialUnidades(ReservasTest):
    """
    Tela da lista das unidades
    """

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
        self.user.set_password("teste1234")
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
            link = unidade.get_absolute_url()
            self.assertContains(response, f'href="{link}"')


class TelaCarroselUnidade(ReservasTest):
    """
    Tela Carrosel Unidade
    """

    def test_usuario_logado(self):
        # get a URL de login
        login_url = reverse("user:login")

        sala = Sala.objects.first()

        # rota da sala
        url_sala = sala.get_absolute_url()

        # fazendo um GET na URL
        response = self.client.get(url_sala)

        # testando se o usuario não autenticado está sendo redirecionado para tela login
        self.assertRedirects(response, f"{login_url}?next={url_sala}")

    def test_componentes_basicos_carrosel(self):
        for unidade in self.unidades:
            # acessando a tela da sala (carrosel)
            url_unidade = unidade.get_absolute_url()
            response = self.client_autenticado.get(url_unidade)

            # Teste para verificar componente de selecionar data
            self.assertContains(
                response,
                'id="componente_selecionar_data"',
                msg_prefix="Componente de selecionar data não está sendo exibida",
            )

            # Teste para verificar se a imagem está exibida
            self.assertContains(
                response,
                'id="imagem_sala"',
                msg_prefix="Componente de selecionar sala não está sendo exibida",
            )

            # Teste para verificar se a tabela de hoŕarios está sendo exibida
            self.assertContains(
                response,
                'id="lista_horarios"',
                msg_prefix="Componente de lista horários não está sendo exibida",
            )

    def test_imagem_nome_sala_correspondente(self):
        for unidade in self.unidades:
            for sala in unidade.todas_salas.filter(ativo=True):
                url_sala = sala.get_absolute_url()

                # teste para verificar o nome do arquivo correspondente a sala
                nome_arquivo_image_sala = os.path.basename(sala.imagem.name)
                self.assertEqual(str(sala.slug), nome_arquivo_image_sala.split(".")[0])

                # testando se o caminho da imagem está sendo exibida na tela
                url_imagem = sala.imagem.url
                response = self.client_autenticado.get(url_sala)
                self.assertContains(response, f'src="{url_imagem}"')

                # testando se o nome da sala está sendo exibido na tela
                self.assertContains(response, f"<span>{sala.nome}</span>")

                # todo Verificar o motivo do self.client.get(url_arquivo) sempre retornar 404
                # teste pra verificar se o arquivo está carregando (sendo exibida)
                response = requests.get("http://127.0.0.1:8000" + url_imagem)
                self.assertEqual(response.status_code, 200)

                # verificar o content-type do response
                self.assertTrue(response.headers["Content-Type"].startswith("image/"))

    def test_sala_sem_reservas_no_dia(self):
        # get no dia atual
        dia_hoje = datetime.date.today()

        # consideramos o horário inicial do dia (5 da manhã)
        data_horario_inicial = datetime.datetime(
            dia_hoje.year, dia_hoje.month, dia_hoje.day, 5, 0, 0
        )

        # get a primeira sala disponível
        sala = Sala.objects.filter(ativo=True).first()
        url_sala = sala.get_absolute_url()

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

    def teste_sala_abertura_encerramento(self):
        """
        Testar se os horários de abertura e encerramento estão sendo exibidos
         de acordo com a sala e a data selecionada
        """

        for unidade in self.unidades:

            # percorrer todas as salas
            for sala in unidade.todas_salas.filter(ativo=True):
                # pega a configuração da sala
                config = sala.config
                horario_abertura = config.horario_abertura.strftime("%H:%M")
                horario_encerramento = config.horario_encerramento.strftime("%H:%M")

                # acessando o link da sala
                url_sala = sala.get_absolute_url()

                # faz o request na url
                response = self.client_autenticado.get(url_sala)

                self.assertContains(
                    response, f"<span id='horario_abertura'>{horario_abertura}</span>"
                )
                self.assertContains(
                    response,
                    f"<span id='horario_encerramento'>{horario_encerramento}</span>",
                )

    def test_timegrid_reserva(self):
        '''
            Testes para exibir uma reserva dentro do Timegrid
        '''
        sala = Sala.objects.get(pk=1)

        # acessando o link da sala
        url_sala = sala.get_absolute_url()

        # resgata uma data
        data = datetime.date(2023, 9, 27)

        # resgatar todos as reservas da sala nesse dia
        reservas = sala.get_reservas_no_dia(data)

        # faz o request na url
        response = self.client_autenticado.get(url_sala)

        if reservas.exists():
            for reserva in reservas:
                # teste para verificar se está exibindo a reserva
                self.assertContains(response, f"<span for='titulo_{reserva.pk}'>{reserva.titulo}</span>")
                self.assertContains(response,
                                    f"<span for='horario_inicio_{reserva.pk}'>{reserva.horario_inicio}</span>")
                self.assertContains(response,
                                    f"<span for='horario_termino_{reserva.pk}'>{reserva.horario_termino}</span>")

        else:
            # teste para verificar se exibe nenhuma reserva
            self.fail("É necessário uma reserva registrada para continuar o teste")

    def test_reserva_andamento(self):
        '''
            Teste para mostrar ao usuário que a reserva está em andamento
        '''
        # define o horário de acesso
        horario_acesso = datetime.datetime(year=2023, month=9, day=27, hour=9, minute=0)
        # pega a saka
        sala = Sala.objects.get(pk=1)
        # acessando o link da sala
        url_sala = sala.get_absolute_url()
        # resgatar todos as reservas da sala nesse dia
        reservas = sala.get_reservas_no_dia(horario_acesso.date())

        if reservas.exists():

            # Set the desired local date and time (in this example, 9:00 AM)
            desired_datetime = timezone.make_aware(horario_acesso)

            # Override the current timezone for the duration of the test
            with timezone.override(desired_datetime.tzinfo):
                # Now, any datetime operations within this block will use the desired datetime

                # horario atual simulado no "horario_acesso"
                current_time = timezone.now()

                # faz o request na url
                response = self.client_autenticado.get(url_sala)

                for reserva in reservas:
                    self.assertContains(response, 'class="reserva_andamento"')

        else:
            # teste para verificar se exibe nenhuma reserva
            self.fail("É necessário uma reserva registrada para continuar o teste")
