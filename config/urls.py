from django.contrib import admin
from django.urls import path, include  # 1. Adicione a palavra 'include' aqui

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # 2. Adicione esta linha inteira
]