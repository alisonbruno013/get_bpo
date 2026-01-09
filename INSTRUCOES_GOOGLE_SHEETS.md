# Instruções para Configurar o Google Sheets

## 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 2. Criar um projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Sheets:
   - Vá em "APIs e Serviços" > "Biblioteca"
   - Procure por "Google Sheets API" e ative
   - Procure por "Google Drive API" e ative

## 3. Criar uma conta de serviço

1. Vá em "APIs e Serviços" > "Credenciais"
2. Clique em "Criar credenciais" > "Conta de serviço"
3. Preencha os dados (nome, ID, etc.)
4. Clique em "Criar e continuar"
5. Na etapa de "Conceder acesso a este projeto", você pode pular
6. Clique em "Concluído"

## 4. Baixar a chave JSON

1. Na lista de contas de serviço, clique na que você acabou de criar
2. Vá na aba "Chaves"
3. Clique em "Adicionar chave" > "Criar nova chave"
4. Selecione "JSON" e clique em "Criar"
5. O arquivo será baixado automaticamente

## 5. Configurar o arquivo de credenciais

1. Renomeie o arquivo JSON baixado para `credentials.json`
2. Coloque o arquivo `credentials.json` na mesma pasta do script (`get_BPO/`)

## 6. Compartilhar a planilha com a conta de serviço

1. Abra ou crie uma planilha no Google Sheets
2. Clique em "Compartilhar" (botão no canto superior direito)
3. Copie o email da conta de serviço (está no arquivo `credentials.json`, campo `client_email`)
4. Cole o email no campo de compartilhamento e dê permissão de "Editor"
5. Clique em "Enviar"

## 7. Configurar o nome da planilha no script

No arquivo `scriptMain.py`, altere a variável `SPREADSHEET_NAME` para o nome exato da sua planilha:

```python
SPREADSHEET_NAME = "Nome da Sua Planilha"  # Altere aqui
```

## Estrutura do arquivo credentials.json

O arquivo deve ter esta estrutura (exemplo):

```json
{
  "type": "service_account",
  "project_id": "seu-projeto",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "sua-conta@seu-projeto.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

## Teste

Após configurar tudo, execute o script:

```bash
python scriptMain.py
```

O script irá:
1. Baixar o CSV do site
2. Ler os dados com pandas
3. Fazer upload para o Google Sheets automaticamente
4. Criar uma nova aba com a data atual
