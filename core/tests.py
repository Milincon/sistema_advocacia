from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Client as AdvocaciaClient, LawCase

# --- TESTES PARA A FUNCIONALIDADE DE LOGIN ---
class LoginTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = '12345!@#$Abc'
        self.user = User.objects.create_user(username=self.username, password=self.password, email='test@test.com')
        self.client = Client()
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')

    def test_login_success(self):
        """ Teste de login com credenciais corretas """
        print("Executando teste de login com sucesso...")
        response = self.client.post(self.login_url, {'username': self.username, 'password': self.password})
        self.assertRedirects(response, self.dashboard_url)
        print("Teste de login com sucesso... OK")

    def test_login_failure_wrong_password(self):
        """ Teste de login com senha incorreta """
        print("Executando teste de login com senha errada...")
        response = self.client.post(self.login_url, {'username': self.username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nome de usuário ou senha inválidos.')
        print("Teste de login com senha errada... OK")

    def test_authenticated_user_access_dashboard(self):
        """ Teste se um usuário já logado consegue acessar o dashboard """
        print("Executando teste de acesso ao dashboard...")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        print("Teste de acesso ao dashboard... OK")

# --- TESTES PARA O CRUD DE PROCESSOS ---
class LawCaseCRUDTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='casetester', password='password123')
        self.advocacia_client = AdvocaciaClient.objects.create(user=self.user, name='Cliente de Teste para Casos')
        self.client = Client()
        self.client.login(username='casetester', password='password123')

    def test_create_law_case(self):
        """ Teste para garantir que um novo processo pode ser criado """
        print("Executando teste de CRIAÇÃO de processo...")
        create_url = reverse('processo_create')
        form_data = {
            'title': 'Novo Caso de Teste', 'case_number': '12345-67.2025.8.05.0001',
            'status': 'ACTIVE', 'client': self.advocacia_client.id
        }
        self.client.post(create_url, form_data)
        self.assertTrue(LawCase.objects.filter(title='Novo Caso de Teste').exists())
        print("Teste de CRIAÇÃO de processo... OK")

    def test_read_law_case_detail(self):
        """ Teste para garantir que a página de detalhes de um processo pode ser acessada """
        print("Executando teste de LEITURA de processo...")
        case = LawCase.objects.create(user=self.user, client=self.advocacia_client, title='Caso para Leitura')
        detail_url = reverse('processo_detalhe', args=[case.pk])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Caso para Leitura')
        print("Teste de LEITURA de processo... OK")

    def test_update_law_case(self):
        """ Teste para garantir que um processo pode ser editado """
        print("Executando teste de ATUALIZAÇÃO de processo...")
        case = LawCase.objects.create(user=self.user, client=self.advocacia_client, title='Caso Original')
        edit_url = reverse('processo_edit', args=[case.pk])

        form_data = {
            'title': 'Caso com Título Atualizado',
            # AQUI ESTÁ A CORREÇÃO: se case.case_number for None, usamos uma string vazia ''
            'case_number': case.case_number or '',
            'status': case.status,
            'client': case.client.id
        }

        self.client.post(edit_url, form_data)
        case.refresh_from_db()
        self.assertEqual(case.title, 'Caso com Título Atualizado')
        print("Teste de ATUALIZAÇÃO de processo... OK")

    def test_delete_law_case(self):
        """ Teste para garantir que um processo pode ser apagado """
        print("Executando teste de EXCLUSÃO de processo...")
        case = LawCase.objects.create(user=self.user, client=self.advocacia_client, title='Caso para Apagar')
        case_id = case.pk
        delete_url = reverse('processo_delete', args=[case.pk])
        self.client.post(delete_url)
        self.assertFalse(LawCase.objects.filter(pk=case_id).exists())
        print("Teste de EXCLUSÃO de processo... OK")