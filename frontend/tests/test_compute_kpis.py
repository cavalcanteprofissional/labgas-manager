import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

from app import _compute_kpis


def _cilindro(id_, codigo, status="ativo", litros=956.0, custo=290.0):
    return {"id": id_, "codigo": codigo, "status": status, "litros_equivalentes": litros, "custo": custo}


def _elemento(id_, nome, consumo_lpm):
    return {"id": id_, "nome": nome, "consumo_lpm": consumo_lpm}


def _leitura(id_, cilindro_id, elemento_id, data, quantidade=1, tempo_chama="00:30"):
    return {"id": id_, "cilindro_id": cilindro_id, "elemento_id": elemento_id, "data": data,
            "quantidade": quantidade, "tempo_chama": tempo_chama}


def _pressao(id_, cilindro_id, data, pressao):
    return {"id": id_, "cilindro_id": cilindro_id, "data": data, "pressao": pressao}


def test_compute_kpis_nao_estoura_valores_com_dados():
    cilindro = [_cilindro(1, "CIL-001"), _cilindro(2, "CIL-002", status="esgotado")]
    elementos = [_elemento(10, "Ar", 15.0)]
    leituras = [
        _leitura(1, 1, 10, "2026-07-01", tempo_chama="00:30"),
        _leitura(2, 1, 10, "2026-07-02", quantidade=2, tempo_chama="01:00"),
    ]

    kpis = _compute_kpis(leituras, cilindro, elementos, [], [], [])

    assert kpis["cilindros_ativos"] == 1
    assert kpis["total_quantidade"] == 3
    assert kpis["total_gas_consumido"] == round(7.5 + 15.0, 1)
    assert kpis["cilindro_leituras_values"] == [3]
    assert kpis["leituras_mes_values"] == [3]


def test_compute_kpis_labels_cilindro_usam_numero_nao_codigo():
    cilindro = [_cilindro(1, "CIL-001"), _cilindro(2, "CIL-002")]
    elementos = [_elemento(10, "Ar", 15.0)]
    leituras = [
        _leitura(1, 1, 10, "2026-07-01"),
        _leitura(2, 2, 10, "2026-07-01"),
    ]

    kpis = _compute_kpis(leituras, cilindro, elementos, [], [], [])

    labels = [str(x) for x in kpis["cilindro_leituras_labels"]]
    assert labels == ["1", "2"]
    assert not any("CIL-" in l for l in labels)
    assert kpis["cilindro_dict"][1] == 1
    assert kpis["cilindro_dict"][2] == 2


def test_compute_kpis_gas_restante_somente_cilindros_ativos():
    cilindro = [
        _cilindro(1, "CIL-001", status="ativo", litros=1000.0),
        _cilindro(2, "CIL-002", status="esgotado", litros=1000.0),
    ]
    elementos = [_elemento(10, "Ar", 60.0)]
    leituras = [_leitura(1, 1, 10, "2026-07-01", tempo_chama="00:30")]

    kpis = _compute_kpis(leituras, cilindro, elementos, [], [], [])

    gas = 30 / 60 * 60.0
    assert kpis["total_gas_consumido"] == round(gas, 1)
    assert kpis["gas_restante"] == round(1000.0 - gas, 1)
    assert kpis["gas_pct"] == round((1000.0 - gas) / 1000.0 * 100, 1)


def test_compute_kpis_sem_dados_nao_quebra():
    kpis = _compute_kpis([], [], [], [], [], [])
    assert kpis["cilindros_ativos"] == 0
    assert kpis["total_quantidade"] == 0
    assert kpis["total_gas_consumido"] == 0.0
    assert kpis["cilindro_leituras_labels"] == []
    assert kpis["pressao_chart"] == {}


def test_compute_kpis_pressao_chart_agrupa_por_cilindro_numero():
    cilindro = [_cilindro(1, "CIL-001")]
    pressoes = [
        _pressao(1, 1, "2026-07-01", 150.0),
        _pressao(2, 1, "2026-07-02", 145.0),
    ]

    kpis = _compute_kpis([], cilindro, [], [], [], pressoes)

    assert list(kpis["pressao_chart"].keys()) == [1]
    assert kpis["pressao_chart"][1]["values"] == [150.0, 145.0]
    assert kpis["pressao_chart_labels"] == ["01/07/2026", "02/07/2026"]
