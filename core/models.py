from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    oab_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nº da OAB")
    def __str__(self):
        return self.get_full_name() or self.username

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Advogado Responsável")
    name = models.CharField(max_length=255, verbose_name="Nome do Cliente")
    document_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    def __str__(self):
        return self.name

class LawCase(models.Model):
    STATUS_CHOICES = [('ACTIVE', 'Ativo'), ('ARCHIVED', 'Arquivado'), ('SUSPENDED', 'Suspenso')]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='law_cases', verbose_name="Cliente")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Advogado Responsável")
    title = models.CharField(max_length=255, verbose_name="Título do Caso")
    case_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número do Processo")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="Status")
    def __str__(self):
        return f"{self.title} ({self.client.name})"

class CaseUpdate(models.Model):
    law_case = models.ForeignKey(LawCase, on_delete=models.CASCADE, related_name='updates', verbose_name="Processo")
    description = models.TextField(verbose_name="Descrição do Andamento/Prazo")
    due_date = models.DateField(blank=True, null=True, verbose_name="Data Fatal do Prazo")
    is_deadline = models.BooleanField(default=False, verbose_name="É um prazo fatal?")
    completed = models.BooleanField(default=False, verbose_name="Concluído")
    class Meta:
        ordering = ['-due_date']
    def __str__(self):
        return f"Andamento em {self.law_case.title} para {self.due_date or 'sem data'}"

class FinancialTransaction(models.Model):
    TYPE_CHOICES = [('INCOME', 'Receita (Honorários)'), ('EXPENSE', 'Despesa (Custas)')]
    STATUS_CHOICES = [('PENDING', 'Pendente'), ('PAID', 'Pago'), ('OVERDUE', 'Atrasado')]
    law_case = models.ForeignKey(
        LawCase, 
        on_delete=models.CASCADE, 
        related_name='transactions', 
        verbose_name="Processo",
        null=True, 
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Advogado")
    description = models.CharField(max_length=255, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor R$")
    transaction_type = models.CharField(max_length=7, choices=TYPE_CHOICES, verbose_name="Tipo")
    due_date = models.DateField(verbose_name="Data de Vencimento/Pagamento")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="Status")
    def __str__(self):
        return f"{self.get_transaction_type_display()} de R${self.amount} em {self.law_case.title if self.law_case else 'Transação do Escritório'}"

class PersonalTransaction(models.Model):
    CATEGORY_CHOICES = [
        ('MORADIA', 'Moradia'), ('TRANSPORTE', 'Transporte'), ('ALIMENTACAO', 'Alimentação'),
        ('SAUDE', 'Saúde'), ('LAZER', 'Lazer'), ('EDUCACAO', 'Educação'), ('PESSOAIS', 'Despesas Pessoais'),
        ('OUTRAS_DESPESAS', 'Outras Despesas'), ('SALARIO', 'Salário / Pró-labore'),
        ('INVESTIMENTOS', 'Rendimentos'), ('OUTRAS_RECEITAS', 'Outras Receitas'),
    ]
    TRANSACTION_TYPE_CHOICES = [('INCOME', 'Receita'), ('EXPENSE', 'Despesa')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_transactions')
    description = models.CharField(max_length=255, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES, verbose_name="Tipo")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Categoria")
    date = models.DateField(verbose_name="Data da Transação")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_category_display()} - R${self.amount}"