import re
import pandas as pd


def limpar_texto(texto: str) -> str:
    """
    Normaliza a entrada aplicando lower() e strip(), removendo pontuacoes
    sem eliminar informacao relevante (preserva letras acentuadas e digitos) e
    colapsando multiplos espacos em um unico espaco.
    """
    if texto is None or pd.isna(texto):
        return ""

    texto_base = str(texto).lower().strip()
    texto_sem_pontuacao = re.sub(r"[^a-z0-9à-öø-ÿ\s]", " ", texto_base)
    return re.sub(r"\s+", " ", texto_sem_pontuacao).strip()


def tokenizar_texto(texto: str) -> list[str]:
    """
    Recebe um texto bruto, aplica limpar_texto() e retorna a lista de tokens.
    """
    texto_limpo = limpar_texto(texto)
    if not texto_limpo:
        return []
    return texto_limpo.split()


def limpar_corpus(registros: list[dict]) -> list[dict]:
    """
    Aplica limpar_texto() e tokenizar_texto() uma unica vez em cada registro,
    preservando id, meeting_id, locutor e o texto original.
    """
    registros_limpos = []
    for reg in registros:
        texto_original = "" if pd.isna(reg["texto"]) else str(reg["texto"])
        texto_limpo = limpar_texto(texto_original)
        registros_limpos.append({
            "id": reg["id"],
            "meeting_id": reg["meeting_id"],
            "locutor": reg["locutor"],
            "texto": texto_original,
            "texto_limpo": texto_limpo,
            "tokens": texto_limpo.split() if texto_limpo else []
        })
    return registros_limpos