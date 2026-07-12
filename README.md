# Timer Task

Aplicativo Windows simples para registrar tempo por projeto e tipo de atividade, com armazenamento local em SQLite e exportação dos registros concluídos para arquivos CSV em uma pasta escolhida pelo usuário.

## Principais recursos

- timer com início, finalização e cancelamento;
- registro manual com identificação de origem para auditoria;
- projetos e tipos de atividade armazenados localmente;
- recuperação do timer após fechamento ou reinicialização;
- registros pendentes mantidos no SQLite em caso de falha de rede;
- botão **Registrar Tasks** para reenviar pendências manualmente;
- UUID permanente para impedir linhas duplicadas no CSV;
- histórico diário e total de tempo;
- ícone na bandeja do Windows;
- geração de executável e instalador por arquivos `.bat`.

## Arquitetura

```text
Timer Task
├── SQLite local
│   ├── configurações
│   ├── projetos
│   ├── tipos de atividade
│   ├── timer ativo
│   └── registros pendentes
└── Pasta definida pelo usuário
    └── registros\<usuario>\AAAA-MM.csv
```

O SQLite não deve ser colocado em pasta de rede. Apenas os CSVs concluídos ficam no local compartilhado.

## Origem dos registros

A coluna `origem_registro` permite distinguir:

- `TIMER`: atividade iniciada e finalizada pelo cronômetro;
- `MANUAL`: atividade inserida pela tela de registro manual.

A estrutura completa está em [docs/CSV_SCHEMA.md](docs/CSV_SCHEMA.md).

## Executar o código-fonte

Requisitos:

- Windows 10 ou Windows 11;
- Python 3.10 ou superior.

Scripts disponíveis:

- `run_timertask.bat`: prepara as dependências e abre o aplicativo sem terminal;
- `run_debug.bat`: abre o aplicativo mantendo o terminal visível;
- `finalizar_timertask.bat`: encerra somente a execução iniciada por esta pasta.

## Criar o executável

Execute:

```text
build_executavel.bat
```

Resultado:

```text
dist\Timer Task.exe
```

## Criar o instalador

Execute:

```text
build_installer.bat
```

O script:

1. chama `build_executavel.bat`;
2. localiza ou instala o Inno Setup 6 pelo `winget`;
3. cria `dist\installer\TimerTask-Setup.exe`.

O computador de compilação precisa ter Python 3. O computador do usuário final não precisa ter Python instalado.

## Ícone

Mantenha um único arquivo `.ico` dentro de `icons\`. O nome é livre. O primeiro `.ico` em ordem alfabética é usado na janela, bandeja, executável, atalhos e instalador.

O arquivo deve conter, preferencialmente, as resoluções 16, 32, 48 e 256 pixels.

## Dados locais

Os dados ficam em:

```text
%LOCALAPPDATA%\TimerTask
```

O repositório não contém nem deve receber bancos, logs ou CSVs reais. Esses formatos estão bloqueados no `.gitignore`.

## Testes

```powershell
python -m unittest discover -s tests -v
python -m compileall app.py database.py csv_store.py
```

## Privacidade

O aplicativo não possui telemetria, serviço em nuvem ou envio automático de dados para terceiros. O usuário define onde os CSVs serão armazenados.

## Autoria

Desenvolvido por **gabrielogaier**.
## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
