from src.limpeza import limpar_texto


def comparar_exato(a: str, b: str) -> bool:
    """
    Compara duas strings apos aplicar a normalizacao de limpar_texto().
    """
    return limpar_texto(a) == limpar_texto(b)


def classificar_termos(
    registros_limpos: list[dict],
    catalogo: list[str],
    palavras_funcionais: set[str] | None = None,
    exibir_evidencias: bool = True
) -> tuple[list[dict], dict]:
    """
    Recebe os registros ja limpos (id, meeting_id, locutor, texto, texto_limpo,
    tokens) e o catalogo canonico. Separa cada token em EXATO ou PENDENTE_DP
    antes da DP. Um token e EXATO quando comparar_exato() confirma a igualdade
    com um termo do catalogo ou com uma palavra funcional.
    Retorna a lista de registros triados e o dicionario de resumo da triagem.
    """
    vocabulario_exato = {limpar_texto(termo): termo for termo in catalogo}
    for palavra in palavras_funcionais or set():
        vocabulario_exato.setdefault(limpar_texto(palavra), palavra)

    registros_triados = []
    pares_alterados = []
    pares_sem_alteracao = []
    total_exatos = 0
    total_pendentes = 0

    for reg in registros_limpos:
        texto_original = reg["texto"]
        texto_normalizado = reg["texto_limpo"]

        if texto_original != texto_normalizado:
            pares_alterados.append((texto_original, texto_normalizado))
        else:
            pares_sem_alteracao.append((texto_original, texto_normalizado))

        tokens_classificados = []
        for token in reg["tokens"]:
            termo_referencia = vocabulario_exato.get(token)
            if termo_referencia is not None and comparar_exato(token, termo_referencia):
                status_triagem = "EXATO"
                total_exatos += 1
            else:
                status_triagem = "PENDENTE_DP"
                total_pendentes += 1

            tokens_classificados.append({
                "token": token,
                "status_triagem": status_triagem
            })

        registros_triados.append({
            "id": reg["id"],
            "meeting_id": reg["meeting_id"],
            "locutor": reg["locutor"],
            "texto": texto_original,
            "texto_limpo": texto_normalizado,
            "tokens_triados": tokens_classificados
        })

    pares_antes_depois = (pares_alterados + pares_sem_alteracao)[:5]

    resumo_triagem = {
        "total_termos": total_exatos + total_pendentes,
        "total_exatos": total_exatos,
        "total_pendentes_dp": total_pendentes,
        "exemplos_antes_depois": pares_antes_depois
    }

    if exibir_evidencias:
        print("=== EVIDENCIAS DE LIMPEZA E TRIAGEM EXATA (ETAPAS 2 E 5) ===")
        print("5 pares 'antes -> depois' apos limpeza:")
        for idx, (antes, depois) in enumerate(pares_antes_depois, start=1):
            print(f"  [{idx}] ANTES : {antes}")
            print(f"      DEPOIS: {depois}")
        print(f"Quantidade de termos EXATOS      : {total_exatos}")
        print(f"Quantidade de termos PENDENTE_DP : {total_pendentes}\n")

    return registros_triados, resumo_triagem