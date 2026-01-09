# Script BPO - Automação de Relatórios

Script automatizado para baixar relatórios BPO, filtrar dados e enviar para Google Sheets.

## Estrutura do Projeto

```
get_BPO/
├── scriptMain.py          # Script principal
├── config.py              # Configurações e gerenciamento de credenciais
├── utils.py               # Funções utilitárias
├── models.py              # Modelos de dados
├── save_credentials.py    # Script para salvar credenciais
├── credentials.pkl        # Arquivo com credenciais (gerado após primeiro uso)
├── credentials.json       # Credenciais do Google Sheets API
├── requirements.txt       # Dependências do projeto
└── downloads/             # Diretório de downloads (criado automaticamente)
```

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure suas credenciais de login:
```bash
python save_credentials.py
```
Digite seu email e senha quando solicitado. As credenciais serão salvas em `credentials.pkl`.

3. Configure as credenciais do Google Sheets (se ainda não fez):
   - Siga as instruções em `INSTRUCOES_GOOGLE_SHEETS.md`
   - Coloque o arquivo `credentials.json` na pasta do projeto

## Uso

Execute o script principal:
```bash
python scriptMain.py
```

## Configurações

As configurações podem ser alteradas no arquivo `config.py`:

- `SPREADSHEET_NAME`: Nome da planilha do Google Sheets
- `WORKSHEET_NAME`: Nome da aba
- `FILTER_VALUES`: Valores para filtrar na coluna de operação
- `DAYS_BEFORE`: Dias antes da data atual para buscar dados
- `DAYS_AFTER`: Dias depois da data atual para buscar dados

## Módulos

### config.py
Gerencia configurações e credenciais:
- `Config.save_credentials(email, password)`: Salva credenciais
- `Config.get_credentials()`: Retorna (email, password)
- `Config.load_credentials()`: Carrega credenciais do arquivo

### utils.py
Funções utilitárias:
- `wait_for_clickable()`: Aguarda e clica em elemento
- `wait_for_send_keys()`: Aguarda e envia texto
- `wait_for_download_complete()`: Aguarda download completar
- `get_latest_csv_file()`: Retorna arquivo CSV mais recente
- `filter_dataframe_by_operation()`: Filtra DataFrame
- `upload_to_google_sheets()`: Envia dados para Google Sheets

### models.py
Modelos de dados (dataclasses):
- `Credentials`: Modelo para credenciais
- `ChromeConfig`: Configurações do Chrome
- `FilterConfig`: Configurações de filtro

## Segurança

⚠️ **Importante**: 
- O arquivo `credentials.pkl` contém suas credenciais em texto. 
- Não compartilhe este arquivo ou faça commit no Git.
- Adicione `credentials.pkl` ao `.gitignore` se usar controle de versão.

## Troubleshooting

### Erro: "Arquivo de credenciais não encontrado"
Execute `python save_credentials.py` para criar o arquivo de credenciais.

### Erro: "Planilha não encontrada"
Verifique se:
1. O nome da planilha em `config.py` está correto
2. A conta de serviço tem acesso à planilha
3. A planilha foi compartilhada com o email da conta de serviço

### Erro: "Download não foi concluído"
Aumente o timeout em `utils.py` na função `wait_for_download_complete()`.

## Execução Agendada

### Opção 1: GitHub Actions (Recomendado)

O projeto inclui um workflow do GitHub Actions configurado para executar automaticamente às **09h, 15h, 18h e 00h** (horário de Brasília).

**Configuração:**
1. Siga as instruções em `GITHUB_SETUP.md`
2. Configure os secrets no GitHub:
   - `BPO_EMAIL`: Seu email de login
   - `BPO_PASSWORD`: Sua senha
   - `GOOGLE_CREDENTIALS_JSON`: Conteúdo do arquivo `credentials.json`
3. O workflow executará automaticamente nos horários configurados

**Vantagens:**
- ✅ Não precisa manter computador ligado
- ✅ Execução na nuvem
- ✅ Logs disponíveis no GitHub
- ✅ Execução manual disponível

### Opção 2: Cron Jobs (Local)

Para executar localmente usando cron:

**macOS/Linux:**
```bash
# Execute o script de configuração automática
bash setup_cron.sh

# Ou configure manualmente
crontab -e
```

**Windows:**
Use o Agendador de Tarefas do Windows ou WSL com cron.

**Ver logs:**
```bash
tail -f logs/cron.log
```

Para mais detalhes, consulte `GITHUB_SETUP.md`.
