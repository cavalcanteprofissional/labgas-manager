# Cilindro utility functions - numero do cilindro (inteiro)
import re

_NUMERO_REGEX = re.compile(r"(\d+)$")


def normalizar_numero_cilindro(valor):
    """Converte o identificador do cilindro para int (1, 2, 3...).

    Aceita int, string numerica ('1', '001') ou codigo antigo com sufixo
    numerico ('CIL-015'). Retorna None se nao houver numero valido.
    """
    if valor is None or valor == "":
        return None
    if isinstance(valor, int):
        return valor
    texto = str(valor).strip()
    if texto.isdigit():
        try:
            return int(texto)
        except (ValueError, TypeError):
            return None
    m = _NUMERO_REGEX.search(texto)
    if not m:
        return None
    try:
        return int(m.group(1))
    except (ValueError, TypeError):
        return None


def numero_corresponde(numero, q):
    """True se q casa com o numero do cilindro.

    Aceita q numerico ('1', '001') ou codigo antigo ('CIL-015'); a busca por
    substring considera o numero formatado com 3 digitos (1 -> '001'), de
    forma que '5' casa com 5 e 15 (substring de '015').
    """
    if numero is None or q is None:
        return False
    q = str(q).strip()
    if not q:
        return False
    num_int = normalizar_numero_cilindro(numero)
    if num_int is None:
        return False
    formatado = f"{num_int:03d}"
    if q.isdigit():
        try:
            if int(q) == num_int:
                return True
        except (ValueError, TypeError):
            pass
        return q in formatado
    if q.lower() in formatado:
        return True
    q_num = normalizar_numero_cilindro(q)
    if q_num is not None:
        return q_num == num_int
    return False


def enriquecer_cilindros(cilindros):
    """Adiciona o rotulo de exibicao do cilindro: numero_exibicao.

    Sempre numerico quando possivel (1, 2, 3...); fallback para o valor
    original caso o registro nao tenha numero.
    """
    for c in cilindros:
        numero = normalizar_numero_cilindro(c.get("numero"))
        c["numero_exibicao"] = numero if numero is not None else c.get("numero", "")
    return cilindros


# Alias de compatibilidade para codigo existente
normalizar_codigo_cilindro = normalizar_numero_cilindro
codigo_corresponde = numero_corresponde
