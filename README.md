# Checkpoint 5 – Pré-processador de Transcrições TOTVS com Programação Dinâmica

Disciplina: **Dynamic Programming / Data Science and Statistical Computing** (FIAP, Engenharia de Software, 2º ano)

| Integrante | RM |
|---|---|
| Bernardo Moreira | 564103 |
| Pedro Batista | 563220 |
| Larissa Shiba | 560462 |
| Renan Jordão | 560618 |

---

## 1. Objetivo

Pipeline único e reproduzível que lê o corpus `transcricoes_atividade.csv` (420 registros, 30 reuniões, 8 locutores), limpa o texto, gera a frequência de palavras, constrói o catálogo canônico a partir do próprio corpus, separa termos `EXATO` de `PENDENTE_DP` e corrige os pendentes com distância de edição implementada por Programação Dinâmica, comparando `LIMITE_DISTANCIA = 1` e `LIMITE_DISTANCIA = 2`.

```text
CSV → Limpeza → Frequência → Catálogo → Triagem exata → DP → Regra de aceitação → CSVs + estatísticas
```

Nas atividades anteriores o trabalho foi feito em notebook. Neste checkpoint a solução foi reorganizada em módulos Python (`src/`, `tests/`, `main.py`), executável do início ao fim sem edição manual dos CSVs.

---

## 2. Estrutura do projeto

```text
cp5_transcricoes/
├── saida/                               (gerada pelo programa)
│   ├── catalogo.csv
│   ├── correcoes_realizadas.csv
│   ├── estatisticas_resumo.csv
│   ├── frequencia_palavras.csv
│   ├── transcricoes_processadas_L1.csv
│   └── transcricoes_processadas_L2.csv
├── src/
│   ├── limpeza.py      limpar_texto, tokenizar_texto, limpar_corpus
│   ├── corpus.py       carregar_corpus, gerar_frequencia, construir_e_carregar_catalogo
│   ├── triagem.py      comparar_exato, classificar_termos
│   ├── dp.py           construir_matriz_dp, distancia_edicao
│   ├── aceitacao.py    avaliar_termo_pendente (melhor candidato, empate, limite)
│   └── pipeline.py     orquestração das 8 etapas e exportação dos CSVs
├── tests/
│   └── test_checkpoint5.py   7 testes mínimos de aceitação
├── main.py              executa os testes e depois o pipeline completo
├── requirements.txt     pandas e pytest
└── transcricoes_atividade.csv
```

Nenhuma biblioteca de similaridade (`fuzzywuzzy`, `rapidfuzz`, `difflib`, `python-Levenshtein`) ou corretor ortográfico foi usada. O `pandas` é usado apenas para ler e gravar CSVs.

### Etapas do pipeline

| # | Etapa | Implementação | Resultado |
|---|---|---|---|
| 1 | Ler o corpus | `carregar_corpus()` | valida as colunas `id`, `meeting_id`, `locutor`, `texto`; mostra 420 registros, 30 reuniões e 8 locutores |
| 2 | Limpar texto | `limpar_corpus()` → `limpar_texto()` | `lower()`, `strip()`, remoção de pontuação e colapso de espaços; a limpeza é feita uma única vez e mantém os campos de identificação |
| 3 | Gerar frequência | `gerar_frequencia()` | `frequencia_palavras.csv` (507 palavras distintas) |
| 4 | Carregar catálogo | `construir_e_carregar_catalogo()` | `catalogo.csv` (147 termos, com a frequência de cada um) |
| 5 | Triar igualdade exata | `classificar_termos()` + `comparar_exato()` | 3.837 `EXATO` e 362 `PENDENTE_DP` |
| 6 | Executar DP | `distancia_edicao()` | distância de cada pendente para cada termo do catálogo |
| 7 | Aplicar regra | `avaliar_termo_pendente()` | `CORRIGIDO` / `AMBIGUO` / `MANTIDO` |
| 8 | Gerar saídas | `executar_pipeline_completo()` | 6 CSVs na pasta `saida/` |

**Limpeza:** além de `lower()` e `strip()`, a função troca pontuação por espaço e junta espaços repetidos. Letras acentuadas e dígitos são preservados. O corpus tem frases com espaço duplo (ex.: `"sobre  a clusterização"`) e frases iniciadas por maiúscula (`"A validação..."`, `"O novo..."`); são esses os pares "antes → depois" exibidos no terminal.

**Triagem:** um token é `EXATO` quando `comparar_exato()` confirma a igualdade com um termo do catálogo ou com uma palavra funcional (artigos, preposições e conectivos como `de`, `no`, `não`, `para`). As palavras funcionais não entram no catálogo, porque não são termos de domínio, mas precisam ser reconhecidas como corretas. Sem isso, `de` (250 ocorrências) virava `rede` e `no` (107) virava `novo` no Limite 2.

**Regra de aceitação:**

| Situação | Ação |
|---|---|
| igualdade exata | `EXATO` – mantém o termo |
| melhor distância única e ≤ limite | `CORRIGIDO` – substitui pelo candidato |
| empate na menor distância (dentro do limite) | `AMBIGUO` – mantém o original |
| menor distância > limite | `MANTIDO` – mantém o original |

O status de cada registro em `transcricoes_processadas_L*.csv` segue a prioridade `CORRIGIDO` > `AMBIGUO` > `MANTIDO` > `EXATO` entre os tokens da frase. `correcoes_realizadas.csv` guarda, para cada `CORRIGIDO` ou `AMBIGUO`, o `id`, `meeting_id`, `locutor`, original, candidato(s), distância, limite e status.

---

## 3. Como executar

Pré-requisito: Python 3.13 (ou 3.10+), com o terminal aberto na pasta raiz do projeto.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # cmd: .venv\Scripts\activate.bat | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python -m pytest -v                    # 7 passed
python main.py                         # testes + pipeline completo
```

Se o PowerShell bloquear a ativação, rode antes `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
Se aparecer `FileNotFoundError: transcricoes_atividade.csv`, o terminal não está na pasta raiz do projeto.

---

## 4. Testes (Etapa 9)

| # | Teste | Esperado | Resultado |
|---|---|---|---|
| 1 | `limpar_texto(" TOTOS ")` | `"totos"` | passou |
| 2 | `comparar_exato("TOTVS", " totvs ")` | `True` | passou |
| 3 | `comparar_exato("Totos", "totvs")` | `False` | passou |
| 4 | `distancia_edicao("protheu", "protheus")` | `1` | passou |
| 5 | `distancia_edicao("totvss", "totvs")` | `1` | passou |
| 6 | matriz `"totos"` × `"totvs"` | 6 × 6, bordas `0..5`, distância 1 | passou |
| 7 | `"tste"` contra `["teste", "trste"]`, limite 1 | `AMBIGUO`, mantém `"tste"` | passou |

---

## 5. Análise (Etapa 10)

### 5.1 Quantos termos existem no catálogo e qual critério foi usado?

O catálogo tem **147 termos**, e a regra fica no código (`construir_e_carregar_catalogo`):

1. palavras de `frequencia_palavras.csv` com **frequência ≥ 3** (170 palavras). Os erros de transcrição do corpus quase sempre aparecem uma ou duas vezes, enquanto as formas corretas se repetem;
2. remoção das **22 palavras funcionais** (`o`, `a`, `de`, `no`, `para`, `não`, `sobre`, `depois`…), que vão para a triagem exata, mas não são termos de domínio;
3. remoção de **formas sem acento** quando a forma acentuada também foi selecionada. Assim `previsao` (3 ocorrências) saiu e `previsão` ficou.

O código confere se o resultado está na faixa de 80 a 150 termos. Entram termos técnicos (`kubernetes`, `deploy`, `pipeline`, `token`, `versão`, `prazo`, `unitário`…) e verbos e substantivos frequentes das reuniões (`revisar`, `discutiu`, `equipe`, `reunião`).

### 5.2 O que mudou numericamente entre `LIMITE_DISTANCIA = 1` e `= 2`?

| Métrica | Limite 1 | Limite 2 |
|---|---|---|
| termos analisados | 4.199 | 4.199 |
| EXATO | 3.837 | 3.837 |
| PENDENTE_DP | 362 | 362 |
| CORRIGIDO | 276 | 290 |
| AMBIGUO | 0 | 2 |
| MANTIDO | 86 | 70 |
| % correções sobre todos os termos | 6,57% | 6,91% |
| % correções sobre os pendentes | 76,24% | 80,11% |

O Limite 2 fez **14 correções a mais** e gerou **2 casos ambíguos**, saindo de 16 tokens que no Limite 1 eram `MANTIDO`. Por registro, o Limite 1 deixou 224 frases `CORRIGIDO`, 144 `EXATO` e 52 `MANTIDO`. O Limite 2 deixou 235 `CORRIGIDO`, 144 `EXATO`, 40 `MANTIDO` e 1 `AMBIGUO`.

### 5.3 Qual limite é mais seguro? Exemplos reais

O **Limite 1** é o mais seguro para esta base. Das 276 correções que ele faz, praticamente todas são erros de uma letra:

- `serviçoi → serviço` (letra a mais no final);
- `ckassificação → classificação` (`k` no lugar de `l`, teclas vizinhas);
- `prao → prazo` e `ersão → versão` (letra faltando);
- `usuario → usuário` e `analise → análise` (acento faltando).

Das 14 correções que só o **Limite 2** faz, 9 estão certas, todas palavras sem dois sinais gráficos (`solucao → solução`, `funcao → função`, `normalizacao → normalização`, `clusterizacao → clusterização`). As **outras 5 estão erradas**, porque trocam palavras corretas que não estão no catálogo por outro termo:

- `banco → branch` (2×, registros 29 e 259: "ajuste de banco");
- `modelo → módulo` (2×, registros 77 e 255);
- `fila → falha` (registro 389: "processamento associado ao fila").

Ou seja, o Limite 2 acerta cerca de 64% do que acrescenta, enquanto o Limite 1 quase não erra.

### 5.4 Dois casos em que a distância de edição não bastou

1. **`producao` (registros 8 e 17), Limite 2:** está a distância 2 de `produção` e também de `produto`. A regra marcou `AMBIGUO` e manteve o original. Só o contexto ("a producao do fluxo") mostra que o certo é `produção`.
2. **`fiea` e `filf` (registros 25 e 241):** pelo contexto ("na etapa de fiea", "o processo de filf") devem ser `fila`. Mas `fila` só aparece uma vez no corpus e por isso não entrou no catálogo, e os dois tokens ficaram `MANTIDO`. A distância não ajuda quando o termo correto está fora do catálogo. Com o catálogo atual, `fila` virou `falha` no Limite 2.

### 5.5 Correção automática inadequada ou arriscada

- **Limite 2, `modelo → módulo` (distância 2):** `modelo` está escrito certo ("validar a modelo", "impacto do modelo"), mas aparece só 2 vezes e não entrou no catálogo. O termo mais próximo era `módulo` (troca `o→ó` e `e→u`) e não houve empate, então a regra substituiu. A frase mudou de sentido. O mesmo aconteceu com `banco → branch`.
- **Limite 1, `ede → rede` (registro 280, "revisar token e ede"):** é arriscada porque o token tem só 3 letras. Uma operação muda 33% da palavra, e `ede` também está a distância 1 de `de`. Como palavras funcionais não entram no catálogo, só existia um candidato e a correção foi automática.

### 5.6 Significado de `dp[i][j]`, casos-base e transição

- **Estado:** `dp[i][j]` = menor número de operações para transformar os `i` primeiros caracteres de `a` nos `j` primeiros de `b`.
- **Casos-base:** `dp[i][0] = i` (remover `i` caracteres) e `dp[0][j] = j` (inserir `j` caracteres).
- **Transição:** se `a[i-1] == b[j-1]`, `dp[i][j] = dp[i-1][j-1]`. Senão, `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])` (remover, inserir, substituir).
- **Ordem:** bottom-up, linha a linha a partir das bordas. A resposta fica em `dp[m][n]`.

### 5.7 Complexidade

Uma comparação entre palavras de tamanho `m` e `n` custa **O(m·n)** de tempo e **O(m·n)** de memória (matriz `(m+1)×(n+1)`). Cada pendente é comparado com todos os `C` termos do catálogo, então o custo total é O(P·C·m·n), com `P` pendentes únicos. O custo cresce linearmente com o catálogo: dobrar `C` dobra o tempo da etapa de DP. A triagem exata reduz bastante o trabalho, já que só 362 dos 4.199 tokens chegam à DP. O cache por palavra em `processar_limite_dp` evita recalcular tokens repetidos.

### 5.8 Otimização possível e trade-off

- **Memória – duas linhas:** como `dp[i]` só depende de `dp[i-1]`, dá para guardar apenas dois vetores e cair para O(n) de memória. O custo é a legibilidade: o código fica menos didático e deixa de ser possível inspecionar a matriz inteira (usada no teste 6) ou reconstruir as operações.
- **Busca – poda por tamanho:** se `abs(len(a) - len(b)) > limite`, a distância com certeza passa do limite e a matriz nem precisa ser montada. É uma linha a mais e reduz muito o número de matrizes. Em catálogos grandes, uma BK-tree consulta só os vizinhos dentro do raio, mas aumenta a complexidade de implementação e de manutenção quando o catálogo muda.

---

## 6. Limitações

- O catálogo depende da frequência: termos corretos que aparecem uma ou duas vezes (`banco`, `modelo`, `fila`, `cache`, `commit`) ficam fora e podem ser trocados por engano no Limite 2.
- A distância de Levenshtein dá o mesmo peso a trocar um acento (`c/ç`) e a trocar uma letra qualquer. Um custo menor para acentos permitiria corrigir `producao` sem aceitar `modelo → módulo`.
- Cada token é avaliado isoladamente, sem o contexto da frase, o que impede desempatar casos como `producao`.