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

# ... (Mantenha todas as outras views como estão) ...

# --- VIEW DO CALENDÁRIO COM A CORREÇÃO FINAL ---
@login_required(login_url='login')
def calendario_view(request):
    ano = int(request.GET.get('ano', date.today().year))
    prazos = CaseUpdate.objects.filter(
        law_case__user=request.user,
        is_deadline=True,
        due_date__year=ano
    ).order_by('due_date')
    prazos_por_dia = {}
    for prazo in prazos:
        if prazo.due_date in prazos_por_dia:
            prazos_por_dia[prazo.due_date].append(prazo)
        else:
            prazos_por_dia[prazo.due_date] = [prazo]
            
    # Nossa própria lista de meses em português
    meses_do_ano = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    calendario_anual = []
    cal = calendar.Calendar()
    
    for mes in range(1, 13):
        # Usamos a nossa lista para pegar o nome do mês
        nome_mes = meses_do_ano[mes-1]
        semanas_do_mes = cal.monthdatescalendar(ano, mes)
        
        calendario_do_mes = {
            'nome_mes': nome_mes,
            'numero_mes': mes,
            'semanas': []
        }
        for semana in semanas_do_mes:
            dias_da_semana = []
            for dia in semana:
                dias_da_semana.append({
                    'data': dia,
                    'prazos': prazos_por_dia.get(dia, [])
                })
            calendario_do_mes['semanas'].append(dias_da_semana)
        calendario_anual.append(calendario_do_mes)
        
    event_form = CalendarEventForm(user=request.user)
    context = {
        'ano': ano,
        'calendario_anual': calendario_anual,
        'ano_anterior': ano - 1,
        'proximo_ano': ano + 1,
        'today': date.today(),
        'event_form': event_form,
    }
    return render(request, 'calendario.html', context)

# ... (Mantenha o resto das views como estão) ...