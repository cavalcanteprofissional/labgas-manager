# Constants for the application
import os

ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))

LITROS_EQUIVALENTES_KG = float(os.getenv("LITROS_EQUIVALENTES_KG", "956.0"))
GAS_KG_DEFAULT = float(os.getenv("GAS_KG_DEFAULT", "1.0"))
CUSTO_DEFAULT = float(os.getenv("CUSTO_DEFAULT", "290.00"))

CILINDRO_STATUS = ["ativo", "esgotado"]

# Sistema de cores - Paleta baseada em #0070b8
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
        "class": "green",
        "hex": "#00897b",
        "var": "var(--green)",
        "bg": "success",
        "gradient": "linear-gradient(135deg, #005f96, #4da3e8)",
    },
    "pressao": {
        "class": "orange",
        "hex": "#f59e0b",
        "var": "var(--yellow)",
        "bg": "warning",
        "gradient": "linear-gradient(135deg, #d97706, #fbbf24)",
    },
    "elemento": {
        "class": "blue",
        "hex": "#0070b8",
        "var": "var(--primary)",
        "bg": "primary",
        "gradient": "linear-gradient(135deg, #003a5e, #4da3e8)",
    },
    "leitura": {
        "class": "pink",
        "hex": "#e91e63",
        "var": "var(--pink)",
        "bg": "danger",
        "gradient": "linear-gradient(135deg, #0070b8, #6cccff)",
    },
    "amostra": {
        "class": "purple",
        "hex": "#6a1b9a",
        "var": "var(--amostra)",
        "bg": "secondary",
        "gradient": "linear-gradient(135deg, #6a1b9a, #ce93d8)",
    },
    "historico": {
        "class": "blue",
        "hex": "#0070b8",
        "var": "var(--primary)",
        "bg": "primary",
        "gradient": "linear-gradient(135deg, #002a47, #003a5e)",
    },
    "perfil": {
        "class": "info",
        "hex": "#6cccff",
        "var": "var(--primary-lighter)",
        "bg": "info",
        "gradient": "linear-gradient(135deg, #0070b8, #4da3e8)",
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
        "hex": "#004d40",
        "var": "var(--green-darkest)",
        "bg": "success",
        "gradient": "linear-gradient(135deg, #002a47, #003a5e)",
    },
    "admin": {
        "class": "danger",
        "hex": "#0070b8",
        "var": "var(--primary)",
        "bg": "primary",
        "gradient": "linear-gradient(135deg, #002a47, #004475)",
    },
}

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

ELEMENTO_CORES = [
    "#0070b8", "#0069a3", "#005f96", "#005a8e", "#004475",
    "#003a5e", "#002a47", "#4da3e8", "#5cb8e8", "#6cccff",
    "#7ad0ff", "#88d4ff", "#94ddff", "#8bbed4", "#6a9ab8",
    "#4a7a98", "#2a5a78", "#1a4a58", "#0a3a48", "#002a38"
]

ELEMENTO_CORES_LEITURAS = [
    "#e91e63", "#c2185b", "#d81b60", "#f06292", "#f48fb1",
    "#f06292", "#ec407a", "#f8bbd0", "#f48fb1", "#f62d74",
    "#d81b60", "#c2185b", "#880e4f", "#ad1457", "#c51162",
    "#f62d74", "#ec407a", "#ea80fc", "#aa00ff", "#b388ff"
]
