from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Pessoas (líder)
    path('pessoas/', views.lista_pessoas, name='lista_pessoas'),
    path('pessoas/nova/', views.criar_pessoa, name='criar_pessoa'),

    # Bairros (supervisor)
    path('bairros/', views.lista_bairros, name='lista_bairros'),
    path('bairros/novo/', views.criar_bairro, name='criar_bairro'),

    # Líderes
    path('lideres/', views.lista_lideres, name='lista_lideres'),
    path('lideres/novo/', views.criar_lider, name='criar_lider'),
]