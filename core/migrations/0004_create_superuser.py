from django.db import migrations

# Esta função irá criar o super-utilizador
def create_superuser(apps, schema_editor):
    # Importamos o modelo de User aqui dentro para evitar problemas
    User = apps.get_model('core', 'User')

    # ATENÇÃO: Defina seu nome de utilizador, email e senha aqui!
    # É seguro, pois isto só roda uma vez durante o deploy.
    username = Linkon
    password = Marilyn1@
    email = milincommarcelino@gmail.com

    # Cria o super-utilizador apenas se ele não existir
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        print(f"Super-utilizador '{username}' criado com sucesso.")

# Esta função permite reverter a migração (opcional, mas boa prática)
def remove_superuser(apps, schema_editor):
    User = apps.get_model('core', 'User')
    username = "seu_nome_de_usuario"
    if User.objects.filter(username=username).exists():
        User.objects.get(username=username).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'), # Depende da migração inicial que criou o modelo User
    ]

    operations = [
        # Diz ao Django para executar nossa função durante o migrate
        migrations.RunPython(create_superuser, reverse_code=remove_superuser),
    ]