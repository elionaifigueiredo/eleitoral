from django.db import models
from django.contrib.auth.models import User


# 🏘️ Bairro
class Bairro(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


# 🔐 Perfil de acesso
class Perfil(models.Model):
    TIPOS = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('lider', 'Líder'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=20, choices=TIPOS)

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"


# 🧑‍💼 Supervisor
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor')
    bairros = models.ManyToManyField(Bairro, related_name='supervisores')

    def __str__(self):
        return self.user.username


# 🧑 Líder
class Lider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lider')
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, related_name='lideres')

    def __str__(self):
        return f"{self.user.username} - {self.bairro.nome}"


# 👥 Pessoas (eleitores)
class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, related_name='pessoas')
    lider = models.ForeignKey(Lider, on_delete=models.CASCADE, related_name='pessoas')

    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


# 💰 Bônus (já preparado)
class Bonus(models.Model):
    lider = models.ForeignKey(Lider, on_delete=models.CASCADE, related_name='bonus')
    quantidade = models.IntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lider.user.username} - R$ {self.valor}"