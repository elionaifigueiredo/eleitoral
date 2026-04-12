# campanha/utils_bonus.py

def calcular_bonus(total):
    if total >= 100:
        return 800
    elif total >= 50:
        return 300
    elif total >= 10:
        return 50
    return 0


def progresso_meta(total, meta):
    if meta == 0:
        return 0
    return int((total / meta) * 100) if total < meta else 100