import os
import unicodedata
from collections import Counter
import pandas as pd


COLUNAS_OBRIGATORIAS = ["id", "meeting_id", "locutor", "texto"]

FREQUENCIA_MINIMA_CATALOGO = 3
TAMANHO_MINIMO_CATALOGO = 80
TAMANHO_MAXIMO_CATALOGO = 150

PALAVRAS_FUNCIONAIS = {
    "o", "a", "e", "de", "do", "da", "no", "na", "ao", "em", "um", "uma",
    "para", "entre", "sobre", "antes", "depois", "ainda", "porque", "após",
    "durante", "não"
}


def carregar_corpus(caminho_csv: str = "transcricoes_atividade.csv") -> list[dict]:
    """
    Carrega o CSV principal, confirma as colunas esperadas, exibe a quantidade
    total de registros, reunioes e locutores e retorna uma estrutura preservando
    id + meeting_id + locutor + texto.
    """
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_csv}")

    df = pd.read_csv(caminho_csv)
    colunas_faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if colunas_faltantes:
        raise ValueError(f"Colunas obrigatorias ausentes no CSV: {colunas_faltantes}")

    total_registros = len(df)
    total_reunioes = df["meeting_id"].nunique()
    total_locutores = df["locutor"].nunique()

    print("=== ESTRUTURACAO DO CORPUS (ETAPA 1) ===")
    print(f"Total de registros : {total_registros}")
    print(f"Total de reunioes  : {total_reunioes}")
    print(f"Total de locutores : {total_locutores}\n")

    return df[COLUNAS_OBRIGATORIAS].to_dict(orient="records")


def gerar_frequencia(
    registros_limpos: list[dict],
    caminho_saida: str = os.path.join("saida", "frequencia_palavras.csv")
) -> pd.DataFrame:
    """
    Conta as ocorrencias de todas as palavras limpas do corpus e gera o arquivo
    frequencia_palavras.csv para apoiar a construcao do catalogo.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    contador = Counter()

    for reg in registros_limpos:
        contador.update(reg["tokens"])

    df_freq = pd.DataFrame(
        contador.most_common(),
        columns=["palavra", "frequencia"]
    )
    df_freq.to_csv(caminho_saida, index=False, encoding="utf-8")
    print(f"[ARQUIVO GERADO] {caminho_saida} ({len(df_freq)} termos unicos)")
    return df_freq


def remover_acentos(palavra: str) -> str:
    """
    Retorna a palavra sem diacriticos (ex.: 'previsão' -> 'previsao').
    """
    decomposta = unicodedata.normalize("NFD", palavra)
    return "".join(c for c in decomposta if unicodedata.category(c) != "Mn")


def construir_e_carregar_catalogo(
    df_frequencia: pd.DataFrame,
    caminho_saida: str = os.path.join("saida", "catalogo.csv"),
    frequencia_minima: int = FREQUENCIA_MINIMA_CATALOGO
) -> list[str]:
    """
    Recebe o DataFrame gerado por gerar_frequencia() e seleciona os termos
    canonicos a partir do proprio corpus:
      1. palavras com frequencia >= frequencia_minima;
      2. exclusao das palavras funcionais (artigos, preposicoes, conectivos);
      3. exclusao de formas sem acento quando a forma acentuada correspondente
         tambem foi selecionada (ex.: 'previsao' descartada por 'previsão').
    Exporta catalogo.csv e retorna a lista final carregada do arquivo.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    if df_frequencia is None or df_frequencia.empty:
        raise ValueError("A tabela de frequencia do corpus nao pode estar vazia.")

    df_candidatos = df_frequencia[
        (df_frequencia["frequencia"] >= frequencia_minima)
        & (~df_frequencia["palavra"].isin(PALAVRAS_FUNCIONAIS))
    ].copy()

    candidatos = set(df_candidatos["palavra"])
    formas_acentuadas = {
        remover_acentos(p) for p in candidatos if remover_acentos(p) != p
    }
    df_catalogo = df_candidatos[
        ~df_candidatos["palavra"].isin(formas_acentuadas)
    ].rename(columns={"palavra": "termo"})

    total = len(df_catalogo)
    if not TAMANHO_MINIMO_CATALOGO <= total <= TAMANHO_MAXIMO_CATALOGO:
        raise ValueError(
            f"Catalogo com {total} termos, fora da faixa "
            f"{TAMANHO_MINIMO_CATALOGO}-{TAMANHO_MAXIMO_CATALOGO}."
        )

    df_catalogo.to_csv(caminho_saida, index=False, encoding="utf-8")

    df_carregado = pd.read_csv(caminho_saida, encoding="utf-8")
    catalogo_final = df_carregado["termo"].dropna().astype(str).tolist()

    print(f"[ARQUIVO GERADO] {caminho_saida} ({len(catalogo_final)} termos canonicos)\n")
    return catalogo_final