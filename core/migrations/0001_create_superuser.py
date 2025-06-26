from django.db import migrations
import os

# Esta função irá criar o super-utilizador
def create_superuser(apps, schema_editor):
    # Importamos o modelo de User aqui dentro para evitar problemas
    User = apps.get_model('core', 'User')

    # Pega as credenciais das Variáveis de Ambiente que vamos criar na Render
    # Isso é mais seguro do que colocar a senha diretamente no código
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

    # Cria o super-utilizador apenas se ele não existir
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        print(f"Super-utilizador de produção '{username}' criado com sucesso.")

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'), # Depende da migração inicial que criou o modelo User
    ]

    operations = [
        # Diz ao Django para executar nossa função durante o comando 'migrate'
        migrations.RunPython(create_superuser),
    ]