from django.db import models
from django.contrib.auth.models import User


# 🏘️ Bairro
class Bairro(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)


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



# 👥 Pessoas (eleitores)
class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, blank=True, null=True)

    titulo_eleitor = models.CharField(max_length=20, blank=True, null=True)
    zona = models.CharField(max_length=10, blank=True, null=True)
    secao = models.CharField(max_length=10, blank=True, null=True)

    # bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    bairro = models.ForeignKey('Bairro', on_delete=models.CASCADE)
    # lider = models.ForeignKey('Lider', on_delete=models.CASCADE)
    lider = models.ForeignKey(
        'Lider',
        on_delete=models.CASCADE,
        related_name='pessoas'
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    

# 🧑 Líder
class Lider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nome_completo = models.CharField(max_length=150)
    titulo_eleitor = models.CharField(max_length=20)
    zona = models.CharField(max_length=10)
    secao = models.CharField(max_length=10)
    meta = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.nome_completo} - {self.bairro.nome}"


# 💰 Bônus (já preparado)
class Bonus(models.Model):
    lider = models.ForeignKey(
    Lider,
    on_delete=models.CASCADE,
    related_name='bonificacoes'
)
    quantidade = models.IntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lider.user.username} - R$ {self.valor}"