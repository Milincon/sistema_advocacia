from django.urls import path
from . import views

urlpatterns = [
    # --- Rotas Principais e de Autenticação ---
    path('login/', views.login_view, name='login'),
    path('', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('financeiro/', views.financeiro_view, name='financeiro'),
    path('financeiro/analise/', views.analise_gemini_view, name='analise_gemini'),
    path('minhas-financas/', views.minhas_financas_view, name='minhas_financas'),
    path('transferencia/', views.transferencia_view, name='transferencia'),
    path('calendario/', views.calendario_view, name='calendario'),
    path('calendario/adicionar/', views.add_calendar_event_view, name='add_calendar_event'), # NOVA ROTA

    # --- Rotas para Gerenciar Processos ---
    path('processo/novo/', views.processo_create_view, name='processo_create'),
    path('processo/<int:pk>/', views.processo_detalhe_view, name='processo_detalhe'),
    path('processo/<int:pk>/editar/', views.processo_edit_view, name='processo_edit'),
    path('processo/<int:pk>/apagar/', views.processo_delete_view, name='processo_delete'),
    path('processo/<int:pk>/analise/', views.analise_processo_view, name='analise_processo'),

    # --- Rotas para Gerenciar Finanças Pessoais ---
    path('minhas-financas/<int:pk>/editar/', views.personal_transaction_edit_view, name='personal_transaction_edit'),
    path('minhas-financas/<int:pk>/apagar/', views.personal_transaction_delete_view, name='personal_transaction_delete'),
    
    # --- Rotas para Gerenciar Finanças do Escritório ---
    path('financeiro/<int:pk>/editar/', views.financial_transaction_edit_view, name='financial_transaction_edit'),
    path('financeiro/<int:pk>/apagar/', views.financial_transaction_delete_view, name='financial_transaction_delete'),
]