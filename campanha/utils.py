def is_admin(user):
    return hasattr(user, 'perfil') and user.perfil.tipo == 'admin'

def is_supervisor(user):
    return hasattr(user, 'perfil') and user.perfil.tipo == 'supervisor'

def is_lider(user):
    return hasattr(user, 'perfil') and user.perfil.tipo == 'lider'