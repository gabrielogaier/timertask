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


## CSV de auditoria

A exclusão lógica não modifica o CSV mensal. A ação é gravada em:

```text
<pasta-base>\registros\<usuario>\auditoria\AAAA-MM.csv
```

| Coluna | Descrição |
|---|---|
| `acao_id` | UUID permanente da ação e chave de deduplicação |
| `registro_id` | UUID do registro original |
| `acao` | Atualmente `EXCLUIR` |
| `data_hora_acao` | Data e hora da exclusão |
| `usuario_acao` | Usuário que realizou a exclusão |
| `usuario_registro` | Proprietário do registro original |
| `motivo` | Justificativa obrigatória |
| `computador` | Computador que criou a ação |
| `projeto` | Cópia do projeto para auditoria |
| `tipo_atividade` | Cópia do tipo de atividade |
| `descricao` | Cópia da descrição |
| `inicio` | Início do registro original |
| `fim` | Fim do registro original |
| `duracao_segundos` | Duração original em segundos |
| `duracao_formatada` | Duração original em `HH:MM:SS` |
| `origem_registro` | `TIMER` ou `MANUAL` |
| `observacao` | Observação original |
| `data_registro` | Data em que o registro original foi concluído |

O `acao_id` impede duplicações em reenvios. O registro original permanece disponível para auditoria, mas deixa de ser contabilizado enquanto a ação mais recente for `EXCLUIR`.
