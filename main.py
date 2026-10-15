from tests.test_checkpoint5 import executar_todos_os_testes
from src.pipeline import executar_pipeline_completo


def exibir_insumos_para_readme(df_correcoes):
    """
    Exibe exemplos reais de correcoes e ambiguidades obtidos no corpus
    para fundamentar as respostas analiticas do README.md (Etapa 10).
    """
    if df_correcoes.empty:
        return

    print("=== AMOSTRAS REAIS DO CORPUS PARA O README (ETAPA 10) ===")

    corr_l1 = (
        df_correcoes[
            (df_correcoes["limite"] == 1) & (df_correcoes["status"] == "CORRIGIDO")
        ][["original", "candidato", "distancia"]]
        .drop_duplicates()
        .head(8)
    )
    print("\n-> Exemplos de Correcoes no Limite 1 (dist = 1):")
    print(corr_l1.to_string(index=False))

    corr_l2_dist2 = (
        df_correcoes[
            (df_correcoes["limite"] == 2)
            & (df_correcoes["distancia"] == 2)
            & (df_correcoes["status"] == "CORRIGIDO")
        ][["original", "candidato", "distancia"]]
        .drop_duplicates()
        .head(12)
    )
    print("\n-> Exemplos de Correcoes Exclusivas do Limite 2 (dist = 2):")
    print(corr_l2_dist2.to_string(index=False))

    ambiguos = (
        df_correcoes[df_correcoes["status"] == "AMBIGUO"][
            ["original", "candidato", "distancia", "limite"]
        ]
        .drop_duplicates()
        .head(8)
    )
    print("\n-> Exemplos de Casos AMBIGUOS detectados:")
    if ambiguos.empty:
        print("Nenhum caso de empate dentro do limite para o catalogo atual.")
    else:
        print(ambiguos.to_string(index=False))


def main():
    # 1. Validacao unitaria obrigatoria (Etapa 9)
    executar_todos_os_testes()

    # 2. Execucao do pipeline completo sobre os 420 registros (Etapas 1 a 8)
    resultados = executar_pipeline_completo(
        caminho_entrada="transcricoes_atividade.csv",
        pasta_saida="saida"
    )

    # 3. Extracao de exemplos reais do corpus para o relatorio README.md
    exibir_insumos_para_readme(resultados["df_correcoes"])


if __name__ == "__main__":
    main()