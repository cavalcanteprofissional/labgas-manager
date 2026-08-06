# Cilindro utility functions - exibicao do numero e normalizacao de codigo
import re

_SUFIXO_REGEX = re.compile(r"(\d+)$")


def normalizar_codigo_cilindro(codigo):
    """Extrai o sufixo numerico do codigo (CIL-001 -> 1). Retorna None se nao houver."""
    if not codigo:
        return None
    m = _SUFIXO_REGEX.search(str(codigo))
    if not m:
        return None
    try:
        return int(m.group(1))
    except (ValueError, TypeError):
        return None


def codigo_corresponde(codigo, q):
    """True se q casa com o codigo por substring ou por numero (001 == CIL-001)."""
    if not codigo or not q:
        return False
    codigo = str(codigo)
    q = str(q).strip()
    if q.lower() in codigo.lower():
        return True
    if q.isdigit():
        sufixo = normalizar_codigo_cilindro(codigo)
        if sufixo is not None:
            try:
                return int(q) == sufixo
            except (ValueError, TypeError):
                return False
    return False


def enriquecer_cilindros(cilindros):
    """Adiciona o rotulo de exibicao do cilindro: numero_exibicao.

    - Para codigos com sufixo numerico (CIL-001) mostra somente o numero (1)
    - Caso contrario (ex: CIL-PR) mantem o codigo completo
    """
    for c in cilindros:
        codigo = c.get("codigo", "")
        c["numero_exibicao"] = normalizar_codigo_cilindro(codigo) or codigo
    return cilindros
