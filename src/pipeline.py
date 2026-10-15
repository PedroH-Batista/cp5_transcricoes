import os
import pandas as pd
from src.corpus import (
    PALAVRAS_FUNCIONAIS,
    carregar_corpus,
    gerar_frequencia,
    construir_e_carregar_catalogo
)
from src.limpeza import limpar_corpus
from src.triagem import classificar_termos
from src.aceitacao import avaliar_termo_pendente


def processar_limite_dp(
    registros_triados: list[dict],
    catalogo: list[str],
    limite_distancia: int
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Recebe os registros vindos da etapa de triagem (EXATO vs PENDENTE_DP),
    aciona a Programacao Dinamica apenas para os termos PENDENTE_DP e consolida
    os resultados, logs de rastreabilidade e estatisticas para o limite ativo.
    """
    cache_avaliacoes = {}
    linhas_processadas = []
    log_correcoes = []

    contagem = {
        "limite": f"Limite {limite_distancia}",
        "termos_analisados": 0,
        "EXATO": 0,
        "PENDENTE_DP": 0,
        "CORRIGIDO": 0,
        "AMBIGUO": 0,
        "MANTIDO": 0
    }

    for reg in registros_triados:
        id_reg = reg["id"]
        meeting_id = reg["meeting_id"]
        locutor = reg["locutor"]
        texto_original = reg["texto"]

        tokens_finais = []
        status_presentes_na_linha = set()

        for item in reg["tokens_triados"]:
            token = item["token"]
            status_triagem = item["status_triagem"]
            contagem["termos_analisados"] += 1

            # 1. Se a triagem ja resolveu como EXATO, nao chama a DP
            if status_triagem == "EXATO":
                tokens_finais.append(token)
                contagem["EXATO"] += 1
                status_presentes_na_linha.add("EXATO")
                continue

            # 2. Termo PENDENTE_DP: avalia via DP contra o catalogo
            contagem["PENDENTE_DP"] += 1
            if token not in cache_avaliacoes:
                cache_avaliacoes[token] = avaliar_termo_pendente(
                    palavra=token,
                    catalogo=catalogo,
                    limite_distancia=limite_distancia
                )

            decisao = cache_avaliacoes[token]
            status_dp = decisao["status"]
            termo_final = decisao["termo_final"]

            tokens_finais.append(termo_final)
            contagem[status_dp] += 1
            status_presentes_na_linha.add(status_dp)

            # Registra a rastreabilidade de todas as decisoes de correcao/ambiguidade
            if status_dp in ("CORRIGIDO", "AMBIGUO"):
                log_correcoes.append({
                    "id": id_reg,
                    "meeting_id": meeting_id,
                    "locutor": locutor,
                    "original": decisao["original"],
                    "candidato": decisao["candidato"],
                    "distancia": decisao["distancia"],
                    "limite": limite_distancia,
                    "status": status_dp
                })

        # Define o status consolidado do registro
        if "CORRIGIDO" in status_presentes_na_linha:
            status_registro = "CORRIGIDO"
        elif "AMBIGUO" in status_presentes_na_linha:
            status_registro = "AMBIGUO"
        elif "MANTIDO" in status_presentes_na_linha:
            status_registro = "MANTIDO"
        else:
            status_registro = "EXATO"

        linhas_processadas.append({
            "id": id_reg,
            "meeting_id": meeting_id,
            "locutor": locutor,
            "texto_original": texto_original,
            "texto_tratado": " ".join(tokens_finais),
            "status": status_registro
        })

    total = contagem["termos_analisados"]
    pendentes = contagem["PENDENTE_DP"]
    contagem["percentual_correcoes_automaticas"] = (
        round((contagem["CORRIGIDO"] / total) * 100, 2) if total > 0 else 0.0
    )
    contagem["percentual_correcoes_sobre_pendentes"] = (
        round((contagem["CORRIGIDO"] / pendentes) * 100, 2) if pendentes > 0 else 0.0
    )

    df_processado = pd.DataFrame(linhas_processadas)
    df_correcoes = pd.DataFrame(
        log_correcoes,
        columns=["id", "meeting_id", "locutor", "original", "candidato",
                 "distancia", "limite", "status"]
    )
    return df_processado, df_correcoes, contagem


def executar_pipeline_completo(
    caminho_entrada: str = "transcricoes_atividade.csv",
    pasta_saida: str = "saida"
) -> dict:
    """
    Executa as 8 etapas do pipeline sequencialmente sem intervencao manual
    e salva todos os CSVs obrigatorios na pasta 'saida/'.
    """
    os.makedirs(pasta_saida, exist_ok=True)

    # Etapa 1: Ler e validar o corpus preservando id, meeting_id, locutor e texto
    registros = carregar_corpus(caminho_entrada)

    # Etapa 2: Limpar o texto uma unica vez preservando os campos de identificacao
    registros_limpos = limpar_corpus(registros)

    # Etapa 3: Gerar frequencia de palavras a partir do corpus limpo
    caminho_freq = os.path.join(pasta_saida, "frequencia_palavras.csv")
    df_freq = gerar_frequencia(registros_limpos, caminho_saida=caminho_freq)

    # Etapa 4: Construir e carregar o catalogo canonico a partir da frequencia
    caminho_cat = os.path.join(pasta_saida, "catalogo.csv")
    catalogo = construir_e_carregar_catalogo(df_freq, caminho_saida=caminho_cat)

    # Etapa 5: Triar igualdade exata antes da DP (separa EXATO de PENDENTE_DP)
    registros_triados, resumo_triagem = classificar_termos(
        registros_limpos=registros_limpos,
        catalogo=catalogo,
        palavras_funcionais=PALAVRAS_FUNCIONAIS,
        exibir_evidencias=True
    )

    # Etapa 6 e 7: Executar DP e aplicar regra para Limite 1 e Limite 2
    print("[PIPELINE] Executando Programacao Dinamica para LIMITE_DISTANCIA = 1...")
    df_l1, df_corr_l1, stats_l1 = processar_limite_dp(
        registros_triados=registros_triados,
        catalogo=catalogo,
        limite_distancia=1
    )

    print("[PIPELINE] Executando Programacao Dinamica para LIMITE_DISTANCIA = 2...")
    df_l2, df_corr_l2, stats_l2 = processar_limite_dp(
        registros_triados=registros_triados,
        catalogo=catalogo,
        limite_distancia=2
    )

    # Etapa 8: Gerar todos os arquivos CSV de saida
    caminho_proc_l1 = os.path.join(pasta_saida, "transcricoes_processadas_L1.csv")
    caminho_proc_l2 = os.path.join(pasta_saida, "transcricoes_processadas_L2.csv")
    caminho_correcoes = os.path.join(pasta_saida, "correcoes_realizadas.csv")
    caminho_stats = os.path.join(pasta_saida, "estatisticas_resumo.csv")

    df_l1.to_csv(caminho_proc_l1, index=False, encoding="utf-8")
    df_l2.to_csv(caminho_proc_l2, index=False, encoding="utf-8")

    df_correcoes_total = pd.concat([df_corr_l1, df_corr_l2], ignore_index=True)
    df_correcoes_total.to_csv(caminho_correcoes, index=False, encoding="utf-8")

    df_stats = pd.DataFrame([stats_l1, stats_l2])
    df_stats.to_csv(caminho_stats, index=False, encoding="utf-8")

    print("\n=== ESTATISTICAS COMPARATIVAS (ETAPA 8) ===")
    print(df_stats.to_string(index=False))
    print(f"\n[SUCESSO] Todos os 6 arquivos CSV foram exportados em '{pasta_saida}/'.\n")

    return {
        "df_l1": df_l1,
        "df_l2": df_l2,
        "df_correcoes": df_correcoes_total,
        "df_stats": df_stats,
        "resumo_triagem": resumo_triagem
    }