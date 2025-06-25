from django import forms
from .models import CaseUpdate, LawCase, FinancialTransaction, PersonalTransaction, Client

# --- Formulário de Andamentos ---
class CaseUpdateForm(forms.ModelForm):
    class Meta:
        model = CaseUpdate
        fields = ['description', 'due_date', 'is_deadline']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_deadline': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'description': 'Descrição do Andamento ou Prazo',
            'due_date': 'Data do Prazo (deixe em branco se for apenas um andamento)',
            'is_deadline': 'É um prazo fatal?',
        }

# --- Formulário de Processos ---
class LawCaseForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        empty_label="-- Selecione um Cliente --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = LawCase
        fields = ['title', 'case_number', 'status', 'client']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'case_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Título do Caso',
            'case_number': 'Número do Processo',
            'status': 'Status do Processo',
            'client': 'Cliente Associado',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LawCaseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['client'].queryset = Client.objects.filter(user=user)

# --- Formulário Financeiro do Escritório ---
class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['description', 'amount', 'transaction_type', 'due_date', 'status']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 150.50'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'description': 'Descrição da Transação',
            'amount': 'Valor (R$)',
            'transaction_type': 'Tipo',
            'due_date': 'Data de Vencimento/Pagamento',
            'status': 'Status do Pagamento',
        }

# --- Formulário de Finanças Pessoais ---
class PersonalTransactionForm(forms.ModelForm):
    class Meta:
        model = PersonalTransaction
        fields = ['description', 'amount', 'transaction_type', 'category', 'date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
            'transaction_type': 'Tipo',
            'category': 'Categoria',
            'date': 'Data',
        }

# --- Formulário da Agenda/Calendário ---
class CalendarEventForm(forms.ModelForm):
    law_case = forms.ModelChoiceField(
        queryset=LawCase.objects.none(),
        label="Processo Associado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = CaseUpdate
        fields = ['law_case', 'description', 'due_date', 'is_deadline']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': True}),
            'is_deadline': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'description': 'Descrição da Tarefa/Prazo',
            'due_date': 'Data',
            'is_deadline': 'É um prazo fatal?',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['law_case'].queryset = LawCase.objects.filter(user=user, status='ACTIVE')