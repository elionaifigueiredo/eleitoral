from django.shortcuts import render, redirect
import requests

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

from .utils import is_admin, is_supervisor, is_lider

@login_required
def lista_pessoas(request):

    if is_admin(request.user):
        pessoas = Pessoa.objects.select_related('bairro', 'lider').all()

    elif is_supervisor(request.user):
        bairros = request.user.supervisor.bairros.all()
        pessoas = Pessoa.objects.select_related('bairro', 'lider').filter(bairro__in=bairros)

    elif is_lider(request.user):
        pessoas = Pessoa.objects.filter(lider=request.user.lider)

    else:
        return HttpResponseForbidden("Acesso negado")

    return render(request, 'campanha/pessoas.html', {
        'pessoas': pessoas
    })



from .utils import is_admin, is_supervisor, is_lider

@login_required
def criar_pessoa(request):

    # 🔐 PERMISSÃO
    if not (is_admin(request.user) or is_lider(request.user)):
        return HttpResponseForbidden("Acesso negado")

    # 👤 SE FOR LÍDER (automático)
    if is_lider(request.user):
        lider = request.user.lider

        if request.method == 'POST':
            nome = request.POST.get('nome')
            telefone = request.POST.get('telefone')

            Pessoa.objects.create(
                nome=nome,
                telefone=telefone,
                bairro=lider.bairro,
                lider=lider
            )

            return redirect('lista_pessoas')

        return render(request, 'campanha/criar_pessoa.html')

    # 🧑 ADMIN (pode escolher)
    if is_admin(request.user):
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

        return render(request, 'campanha/criar_pessoa_admin.html', {
            'bairros': Bairro.objects.all(),
            'lideres': Lider.objects.all()
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

from .models import Lider
from .utils import is_admin, is_supervisor


@login_required
def ranking_lideres(request):

    # 🧑 ADMIN → vê todos
    if is_admin(request.user):
        ranking = (
            Lider.objects
            .annotate(total_pessoas=Count('pessoas'))
            .order_by('-total_pessoas')
        )

    # 🧑‍💼 SUPERVISOR → só bairros dele
    elif is_supervisor(request.user):
        bairros = request.user.supervisor.bairros.all()

        ranking = (
            Lider.objects
            .filter(bairro__in=bairros)
            .annotate(total_pessoas=Count('pessoas'))
            .order_by('-total_pessoas')
        )

    else:
        return HttpResponseForbidden("Acesso negado")

    return render(request, 'campanha/ranking.html', {
        'ranking': ranking
    })