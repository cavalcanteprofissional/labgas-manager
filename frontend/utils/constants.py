# Constants for the application
import os

ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))

LITROS_EQUIVALENTES_KG = float(os.getenv("LITROS_EQUIVALENTES_KG", "956.0"))
GAS_KG_DEFAULT = float(os.getenv("GAS_KG_DEFAULT", "1.0"))
CUSTO_DEFAULT = float(os.getenv("CUSTO_DEFAULT", "290.00"))

CILINDRO_STATUS = ["ativo", "esgotado"]

# Sistema de cores - Rainbow por dependencia
# Ordem do espectro: Vermelho → Laranja → Verde → Azul → Violeta
# Entidades dependentes compartilham matiz proximo
ICON_TIPO = {
    "cilindro": "box-seam",
    "pressao": "activity",
    "elemento": "droplet",
    "leitura": "eye",
    "amostra": "collection",
    "historico": "clock-history",
    "perfil": "person",
    "admin": "gear",
    "dashboard": "speedometer2",
    "ativos": "check-circle",
}

COR_TIPO = {
    "cilindro": {
        "class": "red",
        "hex": "#e63946",
        "var": "var(--cilindro)",
        "bg": "danger",
        "gradient": "linear-gradient(135deg, #c1121f, #e63946)",
    },
    "pressao": {
        "class": "orange",
        "hex": "#f77f00",
        "var": "var(--pressao)",
        "bg": "warning",
        "gradient": "linear-gradient(135deg, #e85d04, #fca311)",
    },
    "elemento": {
        "class": "green",
        "hex": "#2a9d8f",
        "var": "var(--elemento)",
        "bg": "success",
        "gradient": "linear-gradient(135deg, #1b4332, #52b788)",
    },
    "leitura": {
        "class": "blue",
        "hex": "#457b9d",
        "var": "var(--leitura)",
        "bg": "primary",
        "gradient": "linear-gradient(135deg, #1d3557, #a8dadc)",
    },
    "amostra": {
        "class": "purple",
        "hex": "#6a1b9a",
        "var": "var(--amostra)",
        "bg": "secondary",
        "gradient": "linear-gradient(135deg, #4a0072, #bb8fce)",
    },
    "historico": {
        "class": "gray",
        "hex": "#6c757d",
        "var": "var(--historico)",
        "bg": "secondary",
        "gradient": "linear-gradient(135deg, #343a40, #adb5bd)",
    },
    "perfil": {
        "class": "info",
        "hex": "#0070b8",
        "var": "var(--primary)",
        "bg": "info",
        "gradient": "linear-gradient(135deg, #003a5e, #4da3e8)",
    },
    "dashboard": {
        "class": "blue",
        "hex": "#0070b8",
        "var": "var(--primary)",
        "bg": "primary",
        "gradient": "linear-gradient(135deg, var(--primary), var(--primary-light))",
    },
    "ativos": {
        "class": "green",
        "hex": "#1b4332",
        "var": "var(--green-dark)",
        "bg": "success",
        "gradient": "linear-gradient(135deg, #081c15, #2d6a4f)",
    },
    "admin": {
        "class": "dark",
        "hex": "#002a47",
        "var": "var(--primary-darkest)",
        "bg": "dark",
        "gradient": "linear-gradient(135deg, #001a2f, #004475)",
    },
}

# Paletas ordenadas do mais CLARO (valor baixo) → mais ESCURO (valor alto)
# para uso em graficos Chart.js com getColorByIntensity()
PALETA_CILINDRO = ["#f4a261", "#e76f51", "#d62828", "#c1121f", "#780000"]
PALETA_PRESSAO  = ["#ffd166", "#fca311", "#f77f00", "#e85d04", "#9d0208"]
PALETA_ELEMENTO = ["#b7e4c7", "#52b788", "#2d6a4f", "#1b4332", "#081c15"]
PALETA_LEITURA  = ["#a8dadc", "#457b9d", "#1d3557", "#0b1a2a", "#050d14"]
PALETA_AMOSTRA  = ["#e8daef", "#bb8fce", "#8e44ad", "#6a1b9a", "#4a0072"]

# Aliases para compatibilidade com codigo existente
ELEMENTO_CORES = PALETA_ELEMENTO
ELEMENTO_CORES_LEITURAS = PALETA_LEITURA

ELEMENTOS_PADRAO = [
    {"nome": "Antimônio", "consumo_lpm": 1.5},
    {"nome": "Alumínio", "consumo_lpm": 4.5},
    {"nome": "Arsênio", "consumo_lpm": 1.5},
    {"nome": "Bário", "consumo_lpm": 4.5},
    {"nome": "Cádmio", "consumo_lpm": 1.5},
    {"nome": "Chumbo", "consumo_lpm": 2.0},
    {"nome": "Cobalto", "consumo_lpm": 1.5},
    {"nome": "Cobre", "consumo_lpm": 1.5},
    {"nome": "Cromo", "consumo_lpm": 4.5},
    {"nome": "Estanho FAAS", "consumo_lpm": 4.5},
    {"nome": "Estanho HG", "consumo_lpm": 1.5},
    {"nome": "Ferro", "consumo_lpm": 2.0},
    {"nome": "Manganês", "consumo_lpm": 1.5},
    {"nome": "Mercúrio", "consumo_lpm": 0},
    {"nome": "Molibdênio", "consumo_lpm": 4.5},
    {"nome": "Níquel", "consumo_lpm": 1.5},
    {"nome": "Prata", "consumo_lpm": 1.5},
    {"nome": "Selênio", "consumo_lpm": 2.0},
    {"nome": "Zinco", "consumo_lpm": 1.5},
    {"nome": "Tálio", "consumo_lpm": 1.5},
]
