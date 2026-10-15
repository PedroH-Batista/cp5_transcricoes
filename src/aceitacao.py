from src.dp import distancia_edicao


def avaliar_termo_pendente(
    palavra: str,
    catalogo: list[str],
    limite_distancia: int
) -> dict:
    """
    Calcula a distancia de edicao de um termo PENDENTE_DP para todos os termos
    do catalogo e aplica os criterios de aceitacao (CORRIGIDO, AMBIGUO, MANTIDO).
    """
    menor_distancia = float("inf")
    melhores_candidatos = []

    for termo_canonico in catalogo:
        dist = distancia_edicao(palavra, termo_canonico)
        if dist < menor_distancia:
            menor_distancia = dist
            melhores_candidatos = [termo_canonico]
        elif dist == menor_distancia:
            melhores_candidatos.append(termo_canonico)

    if menor_distancia <= limite_distancia:
        if len(melhores_candidatos) == 1:
            candidato_eleito = melhores_candidatos[0]
            return {
                "original": palavra,
                "termo_final": candidato_eleito,
                "candidato": candidato_eleito,
                "distancia": menor_distancia,
                "limite": limite_distancia,
                "status": "CORRIGIDO"
            }
        else:
            # Empate na menor distancia: marca AMBIGUO e preserva o original
            return {
                "original": palavra,
                "termo_final": palavra,
                "candidato": "|".join(melhores_candidatos),
                "distancia": menor_distancia,
                "limite": limite_distancia,
                "status": "AMBIGUO"
            }

    # Menor distancia acima do limite permitido: mantem o original
    return {
        "original": palavra,
        "termo_final": palavra,
        "candidato": (
            melhores_candidatos[0]
            if len(melhores_candidatos) == 1
            else "|".join(melhores_candidatos)
        ),
        "distancia": menor_distancia,
        "limite": limite_distancia,
        "status": "MANTIDO"
    }