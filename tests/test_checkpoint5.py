import os
import sys

# Garante que o diretorio raiz do projeto esteja no sys.path em qualquer execucao
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.limpeza import limpar_texto
from src.triagem import comparar_exato
from src.dp import distancia_edicao
from src.aceitacao import avaliar_termo_pendente


def test_limpar_texto_basico():
    """Teste 1: limpar_texto(' TOTOS ') deve produzir 'totos'."""
    assert limpar_texto(" TOTOS ") == "totos"


def test_comparar_exato_verdadeiro():
    """Teste 2: comparar_exato('TOTVS', ' totvs ') deve produzir True."""
    assert comparar_exato("TOTVS", " totvs ") is True


def test_comparar_exato_falso():
    """Teste 3: comparar_exato('Totos', 'totvs') deve produzir False."""
    assert comparar_exato("Totos", "totvs") is False


def test_distancia_edicao_insercao():
    """Teste 4: distancia_edicao('protheu', 'protheus') deve produzir 1."""
    assert distancia_edicao("protheu", "protheus") == 1


def test_distancia_edicao_remocao():
    """Teste 5: distancia_edicao('totvss', 'totvs') deve produzir 1."""
    assert distancia_edicao("totvss", "totvs") == 1


def test_matriz_totos_totvs_dimensao_e_casos_base():
    """Teste 6: matriz para 'totos' x 'totvs' deve ser 6x6 com casos-base corretos."""
    dist, matriz = distancia_edicao("totos", "totvs", retornar_matriz=True)

    assert len(matriz) == 6
    assert all(len(linha) == 6 for linha in matriz)
    assert matriz[0] == [0, 1, 2, 3, 4, 5]
    assert [matriz[i][0] for i in range(6)] == [0, 1, 2, 3, 4, 5]
    assert dist == 1


def test_empate_entre_melhores_candidatos_marca_ambiguo():
    """Teste 7: empate na menor distancia deve marcar AMBIGUO e manter original."""
    catalogo_teste = ["teste", "trste"]
    resultado = avaliar_termo_pendente("tste", catalogo_teste, limite_distancia=1)

    assert resultado["status"] == "AMBIGUO"
    assert resultado["termo_final"] == "tste"
    assert resultado["distancia"] == 1


def executar_todos_os_testes():
    """Executa sequencialmente todos os testes minimos de aceitacao da Etapa 9."""
    print("=== EXECUTANDO TESTES MINIMOS DE ACEITACAO (ETAPA 9) ===")
    test_limpar_texto_basico()
    test_comparar_exato_verdadeiro()
    test_comparar_exato_falso()
    test_distancia_edicao_insercao()
    test_distancia_edicao_remocao()
    test_matriz_totos_totvs_dimensao_e_casos_base()
    test_empate_entre_melhores_candidatos_marca_ambiguo()
    print("[OK] Todos os 7 testes unitarios obrigatorios passaram com sucesso!\n")


if __name__ == "__main__":
    executar_todos_os_testes()