# Guia: Publicar no GitHub e Configurar Execução Agendada

## Parte 1: Publicar no GitHub

### 1. Criar repositório no GitHub

1. Acesse https://github.com
2. Clique em "New repository" (ou vá em https://github.com/new)
3. Preencha:
   - **Repository name**: `get_BPO` (ou outro nome de sua escolha)
   - **Description**: "Automação BPO - Download de relatórios e upload para Google Sheets"
   - **Visibility**: Private (recomendado, pois contém credenciais)
   - **NÃO marque** "Initialize with README" (já temos um)
4. Clique em "Create repository"

### 2. Configurar Git localmente

Abra o terminal na pasta do projeto e execute:

```bash
# Inicializar repositório Git (se ainda não foi feito)
git init

# Adicionar todos os arquivos
git add .

# Fazer primeiro commit
git commit -m "Initial commit: Script BPO com automação"

# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/get_BPO.git

# Renomear branch para main (se necessário)
git branch -M main

# Enviar para o GitHub
git push -u origin main
```

### 3. Verificar arquivos importantes

Certifique-se de que o `.gitignore` está correto e que **NÃO** está fazendo commit de:
- ❌ `credentials.pkl` (credenciais de login)
- ❌ `credentials.json` (credenciais do Google)
- ❌ Arquivos CSV em `downloads/`

## Parte 2: Execução Agendada Local (Cron Jobs)

### Opção A: Usar Cron no macOS/Linux

1. Abra o terminal e edite o crontab:
```bash
crontab -e
```

2. Adicione as seguintes linhas (ajuste o caminho do Python e do script):
```bash
# Executa o script BPO todos os dias às 09:00, 15:00, 18:00 e 00:00
0 9 * * * /usr/bin/python3 /caminho/completo/para/get_BPO/scriptMain.py >> /caminho/completo/para/get_BPO/logs/cron.log 2>&1
0 15 * * * /usr/bin/python3 /caminho/completo/para/get_BPO/scriptMain.py >> /caminho/completo/para/get_BPO/logs/cron.log 2>&1
0 18 * * * /usr/bin/python3 /caminho/completo/para/get_BPO/scriptMain.py >> /caminho/completo/para/get_BPO/logs/cron.log 2>&1
0 0 * * * /usr/bin/python3 /caminho/completo/para/get_BPO/scriptMain.py >> /caminho/completo/para/get_BPO/logs/cron.log 2>&1
```

3. Para encontrar o caminho do Python:
```bash
which python3
```

4. Para testar se o cron está funcionando:
```bash
# Listar jobs agendados
crontab -l

# Verificar logs do sistema (macOS)
log show --predicate 'process == "cron"' --last 1h
```

### Opção B: Usar GitHub Actions (Recomendado)

GitHub Actions permite executar o script na nuvem sem precisar manter seu computador ligado.

#### 1. Configurar Secrets no GitHub

1. Vá para seu repositório no GitHub
2. Clique em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret** e adicione:

   **BPO_EMAIL**:
   - Name: `BPO_EMAIL`
   - Secret: `seu-email@exemplo.com`
   
   **BPO_PASSWORD**:
   - Name: `BPO_PASSWORD`
   - Secret: `sua-senha`
   
   **GOOGLE_CREDENTIALS_JSON**:
   - Name: `GOOGLE_CREDENTIALS_JSON`
   - Secret: Cole todo o conteúdo do arquivo `credentials.json` do Google

#### 2. O arquivo de workflow já está criado

O arquivo `.github/workflows/scheduled_run.yml` já está configurado para:
- Executar às 09h, 15h, 18h e 00h (horário de Brasília)
- Instalar dependências automaticamente
- Configurar credenciais a partir dos secrets
- Executar o script

#### 3. Ajustar horários (se necessário)

Se quiser mudar os horários, edite o arquivo `.github/workflows/scheduled_run.yml`:

```yaml
- cron: '0 12,18,21,3 * * *'  # Formato: minuto hora dia mês dia-da-semana
```

**Conversão de horário (Brasil UTC-3 para UTC)**:
- 09:00 BR = 12:00 UTC
- 15:00 BR = 18:00 UTC
- 18:00 BR = 21:00 UTC
- 00:00 BR = 03:00 UTC

#### 4. Fazer commit e push

```bash
git add .github/workflows/scheduled_run.yml
git commit -m "Adiciona execução agendada via GitHub Actions"
git push
```

#### 5. Verificar execução

1. Vá para seu repositório no GitHub
2. Clique na aba **Actions**
3. Você verá as execuções agendadas e pode ver os logs

## Parte 3: Execução Manual via GitHub Actions

Você também pode executar manualmente:

1. Vá para **Actions** no seu repositório
2. Selecione o workflow "Execução Agendada BPO"
3. Clique em **Run workflow**
4. Selecione a branch e clique em **Run workflow**

## Troubleshooting

### Cron não está executando

1. Verifique se o caminho do Python está correto:
```bash
which python3
```

2. Verifique permissões do script:
```bash
chmod +x scriptMain.py
```

3. Teste manualmente o comando que está no cron

### GitHub Actions falhando

1. Verifique se todos os secrets estão configurados
2. Veja os logs na aba **Actions** para identificar o erro
3. Certifique-se de que o arquivo `requirements.txt` está atualizado

### Horários incorretos

Use uma calculadora de cron online:
- https://crontab.guru/
- Lembre-se de converter para UTC (Brasil = UTC-3)

## Recomendações

1. **Use GitHub Actions** se possível (não precisa manter computador ligado)
2. **Mantenha o repositório privado** (contém informações sensíveis)
3. **Nunca faça commit** de arquivos com credenciais
4. **Monitore os logs** regularmente para garantir que está funcionando
5. **Teste manualmente** antes de confiar na automação
