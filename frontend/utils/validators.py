# Validation utility functions
import re


def safe_int(value, default=None):
    """Converte valor para int com fallback seguro."""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=None):
    """Converte valor para float com fallback seguro."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def validar_codigo_cilindro(codigo):
    """Valida se o código segue o formato CIL-XXX."""
    return bool(re.match(r'^CIL-\d{3}$', codigo.upper()))


def formatar_tempo_chama(tempo_str):
    """Formata tempo de chama para HH:MM:SS.
    Aceita string 'HH:MM:SS' ou 'HH:MM' e retorna 'HH:MM:SS'.
    """
    if not tempo_str:
        return "00:00:00"
    partes = tempo_str.strip().split(":")
    if len(partes) == 3:
        h, m, s = partes
    elif len(partes) == 2:
        h, m = partes
        s = "00"
    else:
        raise ValueError("Formato de tempo inválido. Use HH:MM:SS ou HH:MM")
    return f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}"


def remover_duplicatas_por_campo(items, campo):
    """Remove itens duplicados baseado em um campo específico."""
    unicos = []
    vistos = set()
    for item in items:
        valor = item.get(campo, "").lower()
        if valor not in vistos:
            vistos.add(valor)
            unicos.append(item)
    return unicos
