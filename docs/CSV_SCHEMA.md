# Estrutura do CSV

Cada usuário possui um arquivo mensal em:

```text
<pasta-base>\registros\<usuario>\AAAA-MM.csv
```

O delimitador utilizado é ponto e vírgula (`;`) e o arquivo é gravado em UTF-8 com BOM para facilitar a abertura no Excel.

| Coluna | Descrição |
|---|---|
| `registro_id` | UUID permanente do registro e chave de deduplicação |
| `usuario` | Nome configurado pelo usuário |
| `origem_registro` | `TIMER` ou `MANUAL` |
| `projeto` | Projeto selecionado no momento do registro |
| `tipo_atividade` | Tipo de atividade selecionado |
| `descricao` | Descrição informada pelo usuário |
| `inicio` | Data e hora inicial |
| `fim` | Data e hora final |
| `duracao_segundos` | Duração numérica em segundos |
| `duracao_formatada` | Duração em `HH:MM:SS` |
| `observacao` | Observação final opcional |
| `computador` | Nome do computador que criou o registro |
| `data_registro` | Data e hora em que o registro foi concluído |

Antes de acrescentar uma linha, o aplicativo verifica `registro_id`. Uma nova tentativa do mesmo registro não cria duplicação.
