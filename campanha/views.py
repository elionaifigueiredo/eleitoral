from django.db.models import Count
from django.shortcuts import render, redirect
import requests

from campanha.utils_bonus import calcular_bonus, progresso_meta

from .models import Pessoa, Bairro, Lider, Perfil

# Create your views here.

from django.contrib.auth.models import User

from .utils import is_admin, is_supervisor, is_lider
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden

@login_required
def dashboard(request):

    # 🧑 ADMIN → tudo
    if is_admin(request.user):
        total_pessoas = Pessoa.objects.count()
        total_bairros = Bairro.objects.count()
        total_lideres = Lider.objects.count()

    # 🧑‍💼 SUPERVISOR → só bairros dele
    elif is_supervisor(request.user):
        bairros = request.user.supervisor.bairros.all()

        total_pessoas = Pessoa.objects.filter(bairro__in=bairros).count()
        total_bairros = bairros.count()
        total_lideres = Lider.objects.filter(bairro__in=bairros).count()

    # 👤 LÍDER → só dele
    elif is_lider(request.user):
        lider = request.user.lider

        total_pessoas = Pessoa.objects.filter(lider=lider).count()

        return render(request, 'campanha/dashboard.html', {
            'total_pessoas': total_pessoas,
            'total_bairros': 1,
            'total_lideres': 1,
            'bairro': lider.bairro.nome,  # ✅ AQUI SIM
        })

    else:
        return HttpResponseForbidden("Acesso negado")

    return render(request, 'campanha/dashboard.html', {
        'total_pessoas': total_pessoas,
        'total_bairros': total_bairros,
        'total_lideres': total_lideres,
    })


@login_required
def lista_pessoas(request):

    # 🧑 ADMIN → vê tudo
    if is_admin(request.user):
        pessoas = Pessoa.objects.select_related('bairro', 'lider').all()

    # 🧑‍💼 SUPERVISOR → só bairros dele
    elif is_supervisor(request.user) and hasattr(request.user, 'supervisor'):
        bairros = request.user.supervisor.bairros.all()
        pessoas = Pessoa.objects.select_related('bairro', 'lider').filter(bairro__in=bairros)

    # 👤 LÍDER → só as dele
    elif is_lider(request.user) and hasattr(request.user, 'lider'):
        pessoas = Pessoa.objects.filter(lider=request.user.lider)

    else:
        return HttpResponseForbidden("Acesso negado")

    return render(request, 'campanha/pessoas.html', {
        'pessoas': pessoas
    })


@login_required
def criar_pessoa(request):

    if not (is_admin(request.user) or is_lider(request.user)):
        return HttpResponseForbidden("Acesso negado")

    lider = None

    if is_lider(request.user):
        lider = request.user.lider

    if request.method == 'POST':
        Pessoa.objects.create(
            nome=request.POST.get('nome'),
            telefone=request.POST.get('telefone'),
            cpf=request.POST.get('cpf'),
            rg=request.POST.get('rg'),
            titulo_eleitor=request.POST.get('titulo_eleitor'),
            zona=request.POST.get('zona'),
            secao=request.POST.get('secao'),
            bairro_id=request.POST.get('bairro') if is_admin(request.user) else lider.bairro.id,
            lider_id=request.POST.get('lider') if is_admin(request.user) else lider.id
        )
        return redirect('lista_pessoas')

    return render(request, 'campanha/criar_pessoa.html', {
        'bairros': Bairro.objects.all(),
        'lideres': Lider.objects.all(),
        'is_admin': is_admin(request.user)
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
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')

        endereco = None
        latitude = None
        longitude = None

        # 🔎 BUSCA CEP
        if cep:
            cep_limpo = cep.replace('-', '').replace('.', '')

            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                if not data.get('erro'):
                    endereco = f"{data.get('logradouro')}, {data.get('bairro')} - {data.get('localidade')}"

                    # 🔥 pegar lat/long com Google Maps (segunda API)
                    geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={cep}&key=YOUR_API_KEY"
                    geo_response = requests.get(geo_url)

                    if geo_response.status_code == 200:
                        geo_data = geo_response.json()

                        if geo_data['results']:
                            location = geo_data['results'][0]['geometry']['location']
                            latitude = location['lat']
                            longitude = location['lng']

        Bairro.objects.create(
            nome=nome,
            cep=cep,
            endereco=endereco,
            latitude=latitude,
            longitude=longitude
        )

        return redirect('lista_bairros')

    return render(request, 'campanha/criar_bairro.html')


from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404

@login_required
def editar_bairro(request, id):
    if not (is_admin(request.user) or is_supervisor(request.user)):
        return HttpResponseForbidden("Acesso negado")

    bairro = get_object_or_404(Bairro, id=id)

    if request.method == 'POST':
        bairro.nome = request.POST.get('nome')
        bairro.cep = request.POST.get('cep')
        bairro.endereco = request.POST.get('endereco')


    lat = request.POST.get('latitude')
    lng = request.POST.get('longitude')

    try:
        bairro.latitude = Decimal(lat) if lat else None
    except (InvalidOperation, TypeError):
        bairro.latitude = None

    try:
        bairro.longitude = Decimal(lng) if lng else None
    except (InvalidOperation, TypeError):
        bairro.longitude = None
        bairro.save()

        return redirect('lista_bairros')

    return render(request, 'campanha/editar_bairro.html', {
        'bairro': bairro
    })

from .utils import is_admin

@login_required
def excluir_bairro(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Apenas admin pode excluir")

    bairro = get_object_or_404(Bairro, id=id)

    if request.method == 'POST':
        bairro.delete()
        return redirect('lista_bairros')

    return render(request, 'campanha/confirmar_exclusao.html', {
        'objeto': bairro
    })


@login_required
def lista_lideres(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Acesso negado")

    lideres = Lider.objects.select_related('bairro', 'user').all()

    return render(request, 'campanha/lideres.html', {
        'lideres': lideres
    })



@login_required
def criar_lider(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        bairro_id = request.POST.get('bairro')

        nome_completo = request.POST.get('nome_completo')
        titulo_eleitor = request.POST.get('titulo_eleitor')
        zona = request.POST.get('zona')
        secao = request.POST.get('secao')

        # 🔐 cria usuário
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # 👤 cria perfil (AQUI ESTÁ O SEGREDO)
        Perfil.objects.create(
            user=user,
            tipo='lider'
        )

        # 🧑 cria líder
        meta = request.POST.get('meta')

        Lider.objects.create(
            user=user,
            bairro_id=bairro_id,
            nome_completo=nome_completo,
            titulo_eleitor=titulo_eleitor,
            zona=zona,
            secao=secao,
            meta=meta
        )

        return redirect('lista_lideres')

    return render(request, 'campanha/criar_lider.html', {
        'bairros': Bairro.objects.all()
    })


@login_required
def editar_lider(request, id):

    if not is_admin(request.user):
        return HttpResponseForbidden("Acesso negado")

    lider = get_object_or_404(Lider, id=id)

    if request.method == 'POST':
        lider.nome_completo = request.POST.get('nome_completo')
        lider.meta = request.POST.get('meta')
        lider.titulo_eleitor = request.POST.get('titulo_eleitor')
        lider.zona = request.POST.get('zona')
        lider.secao = request.POST.get('secao')
        lider.bairro_id = request.POST.get('bairro')

        lider.save()
        return redirect('lista_lideres')

    return render(request, 'campanha/editar_lider.html', {
        'lider': lider,
        'bairros': Bairro.objects.all()
    })


@login_required
def excluir_lider(request, id):

    if not is_admin(request.user):
        return HttpResponseForbidden("Acesso negado")

    lider = get_object_or_404(Lider, id=id)

    if request.method == 'POST':
        lider.delete()
        return redirect('lista_lideres')

    return render(request, 'campanha/confirmar_exclusao.html', {
        'obj': lider
    })


from .utils_bonus import calcular_bonus, progresso_meta
@login_required
def ranking_lideres(request):

    # 🔒 segurança extra
    if not hasattr(request.user, 'perfil'):
        return HttpResponseForbidden("Usuário sem perfil")

    # 🧑 ADMIN → vê todos
    if is_admin(request.user):
        lideres = Lider.objects.all()

    # 🧑‍💼 SUPERVISOR → só bairros dele
    elif is_supervisor(request.user):
        bairros = request.user.supervisor.bairros.all()
        lideres = Lider.objects.filter(bairro__in=bairros)

    else:
        return HttpResponseForbidden("Acesso negado")

    # 📊 ranking com total
    ranking = (
        lideres
        .annotate(total_pessoas=Count('pessoa'))
        .order_by('-total_pessoas')
    )

    # 💰 cálculo de bônus
    for l in ranking:
        l.total_pessoas = l.total_pessoas or 0

        l.progresso = progresso_meta(l.total_pessoas, l.meta)
        l.bonus_calc = calcular_bonus(l.total_pessoas)

        # 🎨 cor
        if l.progresso < 50:
            l.cor = 'bg-danger'
        elif l.progresso < 100:
            l.cor = 'bg-warning'
        else:
            l.cor = 'bg-success'

        # 🎯 faltam
        l.faltam = max(l.meta - l.total_pessoas, 0)

    return render(request, 'campanha/ranking.html', {
        'ranking': ranking
    })