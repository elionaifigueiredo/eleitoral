from django.shortcuts import render, redirect
from .models import Pessoa, Bairro, Lider
from .utils import is_supervisor

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

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
def criar_bairro(request):
    if not is_supervisor(request.user):
        return HttpResponseForbidden("Acesso negado")

def lista_lideres(request):
    return HttpResponse("Lista de Líderes")

def criar_lider(request):
    return HttpResponse("Criar Líder")