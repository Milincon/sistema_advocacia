from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings
from django.urls import reverse
import google.generativeai as genai
from datetime import date, datetime
import calendar
from .models import LawCase, CaseUpdate, FinancialTransaction, Client, PersonalTransaction
from .forms import CaseUpdateForm, LawCaseForm, FinancialTransactionForm, PersonalTransactionForm, CalendarEventForm

# --- View de Login ---
def login_view(request):
    if request.method == 'POST':
        username_form = request.POST.get('username')
        password_form = request.POST.get('password')
        user = authenticate(request, username=username_form, password=password_form)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            context = {'error_message': 'Nome de usuário ou senha inválidos.'}
            return render(request, 'login.html', context)
    return render(request, 'login.html')

# --- View de Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- View do Dashboard Principal ---
@login_required(login_url='login')
def dashboard_view(request):
    processos = LawCase.objects.filter(user=request.user)
    context = { 'lista_de_processos': processos }
    return render(request, 'dashboard.html', context)

# --- View de Detalhes do Processo ---
@login_required(login_url='login')
def processo_detalhe_view(request, pk):
    context = {}
    try:
        processo = LawCase.objects.get(pk=pk, user=request.user)
        if request.method == 'POST' and 'submit_andamento' in request.POST:
            update_form = CaseUpdateForm(request.POST)
            if update_form.is_valid():
                new_update = update_form.save(commit=False)
                new_update.law_case = processo
                new_update.save()
                return redirect('processo_detalhe', pk=processo.pk)
        else:
            update_form = CaseUpdateForm()
        if request.method == 'POST' and 'submit_transacao' in request.POST:
            transaction_form = FinancialTransactionForm(request.POST)
            if transaction_form.is_valid():
                new_transaction = transaction_form.save(commit=False)
                new_transaction.law_case = processo
                new_transaction.user = request.user
                new_transaction.save()
                return redirect('processo_detalhe', pk=processo.pk)
        else:
            transaction_form = FinancialTransactionForm()
        updates = processo.updates.all()
        transacoes = processo.transactions.all().order_by('-due_date')
        context = {
            'processo': processo, 'updates': updates, 'transacoes': transacoes,
            'update_form': update_form, 'transaction_form': transaction_form,
        }
        return render(request, 'processo_detalhe.html', context)
    except LawCase.DoesNotExist:
        return redirect('dashboard')

# --- View de Edição de Processo ---
@login_required(login_url='login')
def processo_edit_view(request, pk):
    try:
        processo = LawCase.objects.get(pk=pk, user=request.user)
    except LawCase.DoesNotExist:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LawCaseForm(request.POST, instance=processo, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('processo_detalhe', pk=processo.pk)
    else:
        form = LawCaseForm(instance=processo, user=request.user)
    context = { 'form': form, 'processo': processo, 'page_title': f'Editar Processo: {processo.title}' }
    return render(request, 'processo_form.html', context)

# --- View de Criação de Processo ---
@login_required(login_url='login')
def processo_create_view(request):
    if request.method == 'POST':
        form = LawCaseForm(request.POST, user=request.user)
        if form.is_valid():
            novo_processo = form.save(commit=False)
            novo_processo.user = request.user
            novo_processo.save()
            return redirect('dashboard')
    else:
        form = LawCaseForm(user=request.user)
    context = { 'form': form, 'page_title': 'Adicionar Novo Processo' }
    return render(request, 'processo_form.html', context)

# --- View de Deleção de Processo ---
@login_required(login_url='login')
def processo_delete_view(request, pk):
    try:
        processo = LawCase.objects.get(pk=pk, user=request.user)
    except LawCase.DoesNotExist:
        return redirect('dashboard')
    if request.method == 'POST':
        processo.delete()
        return redirect('dashboard')
    context = { 'processo': processo }
    return render(request, 'processo_delete.html', context)

# --- View do Dashboard Financeiro do Escritório ---
@login_required(login_url='login')
def financeiro_view(request):
    transacoes = FinancialTransaction.objects.filter(user=request.user)
    total_receitas = transacoes.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    total_despesas = transacoes.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    saldo = total_receitas - total_despesas
    context = {
        'total_receitas': total_receitas, 'total_despesas': total_despesas,
        'saldo': saldo, 'transacoes': transacoes.order_by('-due_date')
    }
    return render(request, 'financeiro.html', context)

# --- View de Análise com Gemini (Escritório) ---
@login_required(login_url='login')
def analise_gemini_view(request):
    context = {}
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        transacoes = FinancialTransaction.objects.filter(user=request.user)
        total_receitas = transacoes.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        total_despesas = transacoes.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        saldo = total_receitas - total_despesas
        prompt = f"..."
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        context['analise_ia'] = response.text
    except Exception as e:
        context['error_ia'] = f"Ocorreu um erro ao contatar a IA. Detalhes: {e}"
    
    transacoes = FinancialTransaction.objects.filter(user=request.user)
    context['total_receitas'] = transacoes.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    context['total_despesas'] = transacoes.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    context['saldo'] = context['total_receitas'] - context['total_despesas']
    context['transacoes'] = transacoes.order_by('-due_date')
    return render(request, 'financeiro.html', context)

# --- View de Finanças Pessoais ---
@login_required(login_url='login')
def minhas_financas_view(request):
    if request.method == 'POST':
        form = PersonalTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('minhas_financas')
    else:
        form = PersonalTransactionForm()
    transacoes_pessoais = PersonalTransaction.objects.filter(user=request.user)
    context = { 'transacoes_pessoais': transacoes_pessoais, 'form': form }
    return render(request, 'minhas_financas.html', context)

# --- View de Transferência Financeira ---
@login_required(login_url='login')
def transferencia_view(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        description = request.POST.get('description', 'Retirada de Lucro / Pró-labore')
        try:
            amount = float(amount_str.replace('.', '').replace(',', '.'))
            FinancialTransaction.objects.create(
                user=request.user, law_case=None, description=description, amount=amount,
                transaction_type='EXPENSE', due_date=request.POST.get('date'), status='PAID'
            )
            PersonalTransaction.objects.create(
                user=request.user, description=description, amount=amount,
                transaction_type='INCOME', category='SALARIO', date=request.POST.get('date')
            )
            return redirect('financeiro')
        except (ValueError, TypeError):
            pass
    return render(request, 'transferencia.html')

# --- Views de Editar e Apagar Finanças Pessoais ---
@login_required(login_url='login')
def personal_transaction_edit_view(request, pk):
    try:
        transaction = PersonalTransaction.objects.get(pk=pk, user=request.user)
    except PersonalTransaction.DoesNotExist:
        return redirect('minhas_financas')
    if request.method == 'POST':
        form = PersonalTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('minhas_financas')
    else:
        form = PersonalTransactionForm(instance=transaction)
    context = { 'form': form, 'transaction': transaction }
    return render(request, 'personal_transaction_form.html', context)

@login_required(login_url='login')
def personal_transaction_delete_view(request, pk):
    try:
        transaction = PersonalTransaction.objects.get(pk=pk, user=request.user)
    except PersonalTransaction.DoesNotExist:
        return redirect('minhas_financas')
    if request.method == 'POST':
        transaction.delete()
        return redirect('minhas_financas')
    context = { 'transaction': transaction }
    return render(request, 'personal_transaction_delete.html', context)

# --- Views de Editar e Apagar Finanças do Escritório ---
@login_required(login_url='login')
def financial_transaction_edit_view(request, pk):
    try:
        transaction = FinancialTransaction.objects.get(pk=pk, user=request.user)
    except FinancialTransaction.DoesNotExist:
        return redirect('financeiro')
    if request.method == 'POST':
        form = FinancialTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('financeiro')
    else:
        form = FinancialTransactionForm(instance=transaction)
    context = { 'form': form, 'transaction': transaction }
    return render(request, 'financial_transaction_form.html', context)

@login_required(login_url='login')
def financial_transaction_delete_view(request, pk):
    try:
        transaction = FinancialTransaction.objects.get(pk=pk, user=request.user)
    except FinancialTransaction.DoesNotExist:
        return redirect('financeiro')
    if request.method == 'POST':
        transaction.delete()
        return redirect('financeiro')
    context = { 'transaction': transaction }
    return render(request, 'financial_transaction_delete.html', context)
    
# --- View de Análise do Processo com IA ---
@login_required(login_url='login')
def analise_processo_view(request, pk):
    context = {}
    try:
        processo = LawCase.objects.get(pk=pk, user=request.user)
        updates = processo.updates.all()
        transacoes = processo.transactions.all()
        receitas_caso = transacoes.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        despesas_caso = transacoes.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        saldo_caso = receitas_caso - despesas_caso
        prompt_parts = [
            f"Você é um advogado sênior e consultor de gestão. Analise os dados do seguinte processo e gere um 'Resumo Executivo Inteligente', em 2 ou 3 parágrafos, terminando com uma 'Ação Recomendada' clara.\n\n",
            f"DADOS DO PROCESSO:\n- Título: {processo.title}\n- Cliente: {processo.client.name}\n- Status: {processo.get_status_display()}\n\n",
            "ÚLTIMOS ANDAMENTOS:\n"
        ]
        if updates:
            for update in updates[:5]: prompt_parts.append(f"- {update.description}\n")
        else:
            prompt_parts.append("- Nenhum andamento registrado.\n")
        prompt_parts.append(f"\nFINANCEIRO DO CASO:\n- Receitas: R$ {receitas_caso:.2f}\n- Despesas: R$ {despesas_caso:.2f}\n- Saldo: R$ {saldo_caso:.2f}\n\n")
        final_prompt = "".join(prompt_parts)
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(final_prompt)
        context['analise_processo_ia'] = response.text
    except LawCase.DoesNotExist:
        return redirect('dashboard')
    except Exception as e:
        context['error_processo_ia'] = f"Ocorreu um erro ao gerar a análise: {e}"
    context['processo'] = processo
    context['updates'] = updates
    context['transacoes'] = transacoes.order_by('-due_date')
    context['update_form'] = CaseUpdateForm()
    context['transaction_form'] = FinancialTransactionForm()
    return render(request, 'processo_detalhe.html', context)

# --- View do Calendário Anual ---
@login_required(login_url='login')
def calendario_view(request):
    ano = int(request.GET.get('ano', date.today().year))
    prazos = CaseUpdate.objects.filter(
        law_case__user=request.user, is_deadline=True, due_date__year=ano
    ).order_by('due_date')
    prazos_por_dia = {}
    for prazo in prazos:
        if prazo.due_date in prazos_por_dia:
            prazos_por_dia[prazo.due_date].append(prazo)
        else:
            prazos_por_dia[prazo.due_date] = [prazo]
    meses_do_ano = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    calendario_anual = []
    cal = calendar.Calendar()
    for mes in range(1, 13):
        nome_mes = meses_do_ano[mes-1]
        semanas_do_mes = cal.monthdatescalendar(ano, mes)
        calendario_do_mes = { 'nome_mes': nome_mes, 'numero_mes': mes, 'semanas': [] }
        for semana in semanas_do_mes:
            dias_da_semana = []
            for dia in semana:
                dias_da_semana.append({ 'data': dia, 'prazos': prazos_por_dia.get(dia, []) })
            calendario_do_mes['semanas'].append(dias_da_semana)
        calendario_anual.append(calendario_do_mes)
    context = {
        'ano': ano, 'calendario_anual': calendario_anual,
        'ano_anterior': ano - 1, 'proximo_ano': ano + 1,
        'today': date.today(), 'event_form': CalendarEventForm(user=request.user),
    }
    return render(request, 'calendario.html', context)

# --- View para Adicionar Evento do Calendário ---
@login_required(login_url='login')
def add_calendar_event_view(request):
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
        event_date_str = request.POST.get('due_date')
        if event_date_str:
            year = datetime.strptime(event_date_str, '%Y-%m-%d').year
            return redirect(f"{reverse('calendario')}?ano={year}")
    return redirect('calendario')