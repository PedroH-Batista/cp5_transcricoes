def construir_matriz_dp(a: str, b: str) -> list[list[int]]:
    """
    Constroi e preenche a matriz de Programacao Dinamica (m+1) x (n+1)
    para a distancia de edicao (Levenshtein) em ordem bottom-up assim como nos vimos em aula.

    Estado: dp[i][j] = menor custo para transformar a[:i] em b[:j].
    Casos-base: dp[i][0] = i (remocoes) e dp[0][j] = j (insercoes).
    Transicao:
      - se a[i-1] == b[j-1]: dp[i][j] = dp[i-1][j-1]
      - caso contrario: 1 + min(remover, inserir, substituir)
    """
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Inicializacao dos casos-base nas suas bordas
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Preenchimento bottom-up das celulas internas
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                remocao = dp[i - 1][j]
                insercao = dp[i][j - 1]
                substituicao = dp[i - 1][j - 1]
                dp[i][j] = 1 + min(remocao, insercao, substituicao)

    return dp


def distancia_edicao(a: str, b: str, retornar_matriz: bool = False):
    """
    É o retorno da distancia minima de edicao entre as strings 'a' e 'b'.
    Se retornar_matriz=True, retorna uma tupla (distancia_final, matriz_dp).
    """
    matriz = construir_matriz_dp(a, b)
    distancia_final = matriz[len(a)][len(b)]

    if retornar_matriz:
        return distancia_final, matriz
    return distancia_final