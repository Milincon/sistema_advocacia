from django.contrib import admin
from .models import User, Client, LawCase, CaseUpdate, FinancialTransaction

admin.site.register(User)
admin.site.register(Client)
admin.site.register(LawCase)
admin.site.register(CaseUpdate)
admin.site.register(FinancialTransaction)