from django.shortcuts import render, redirect

from .models import Pessoa, Bairro, Lider, Perfil
from .utils import is_supervisor

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .utils import is_admin, is_supervisor

from django.contrib.auth.models import User

def dashboard(request):
    total_pessoas = Pessoa.objects.count()
    total_bairros = Bairro.objects.count()
    total_lideres = Lider.objects.count()

    return render(request, 'campanha/dashboard.html', {
        'total_pessoas': total_pessoas,
        'total_bairros': total_bairros,
        'total_lideres': total_lideres,
    })

def lista_pessoas(request):
    pessoas = Pessoa.objects.select_related('bairro', 'lider').all()

    return render(request, 'campanha/pessoas.html', {
        'pessoas': pessoas
    })


def criar_pessoa(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        bairro_id = request.POST.get('bairro')
        lider_id = request.POST.get('lider')

        Pessoa.objects.create(
            nome=nome,
            telefone=telefone,
            bairro_id=bairro_id,
            lider_id=lider_id
        )

        return redirect('lista_pessoas')

    bairros = Bairro.objects.all()
    lideres = Lider.objects.all()

    return render(request, 'campanha/criar_pessoa.html', {
        'bairros': bairros,
        'lideres': lideres
    })

def lista_bairros(request):
    return HttpResponse("Lista de Bairros")

@login_required


# 📋 LISTAR BAIRROS
@login_required
def lista_bairros(request):
    if is_admin(request.user):
        bairros = Bairro.objects.all()

    elif is_supervisor(request.user):
        bairros = request.user.supervisor.bairros.all()

    else:
        return HttpResponseForbidden("Acesso negado")

    return render(request, 'campanha/bairros.html', {
        'bairros': bairros
    })


# ➕ CRIAR BAIRRO
@login_required
def criar_bairro(request):
    if not (is_admin(request.user) or is_supervisor(request.user)):
        return HttpResponseForbidden("Acesso negado")

    if request.method == 'POST':
        nome = request.POST.get('nome')

        if nome:
            Bairro.objects.get_or_create(nome=nome.strip())

        return redirect('lista_bairros')

    return render(request, 'campanha/criar_bairro.html')

@login_required
def lista_lideres(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Acesso negado")

    lideres = Lider.objects.select_related('user', 'bairro')

    return render(request, 'campanha/lideres.html', {
        'lideres': lideres
    })



@login_required
def criar_lider(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Acesso negado")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        bairro_id = request.POST.get('bairro')

        # evita usuário duplicado
        if User.objects.filter(username=username).exists():
            return render(request, 'campanha/criar_lider.html', {
                'erro': 'Usuário já existe',
                'bairros': Bairro.objects.all()
            })

        # cria usuário
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # cria perfil
        Perfil.objects.create(
            user=user,
            tipo='lider'
        )

        # cria líder
        Lider.objects.create(
            user=user,
            bairro_id=bairro_id
        )

        return redirect('lista_lideres')

    return render(request, 'campanha/criar_lider.html', {
        'bairros': Bairro.objects.all()
    })