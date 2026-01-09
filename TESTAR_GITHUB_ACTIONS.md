# Como Testar a Execução pelo GitHub Actions

## Passo 1: Configurar Secrets no GitHub

Antes de testar, você precisa configurar os secrets (credenciais) no GitHub:

1. Acesse seu repositório no GitHub
2. Vá em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret** e adicione:

### Secret 1: BPO_EMAIL
- **Name**: `BPO_EMAIL`
- **Secret**: Seu email de login (ex: `alison.bruno@shopee.com`)

### Secret 2: BPO_PASSWORD
- **Name**: `BPO_PASSWORD`
- **Secret**: Sua senha

### Secret 3: GOOGLE_CREDENTIALS_JSON
- **Name**: `GOOGLE_CREDENTIALS_JSON`
- **Secret**: Cole TODO o conteúdo do arquivo `credentials.json` do Google Sheets
  - Abra o arquivo `credentials.json` no seu computador
  - Copie TODO o conteúdo (todo o JSON)
  - Cole no campo Secret

## Passo 2: Fazer Push do Código

Certifique-se de que o código está no GitHub:

```bash
# Verificar se o repositório remoto está configurado
git remote -v

# Se não estiver, adicione:
git remote add origin https://github.com/alisonbruno013/get_BPO.git

# Fazer push
git push -u origin main
```

## Passo 3: Testar Execução Manual

### Opção A: Via Interface do GitHub (Mais Fácil)

1. Acesse seu repositório no GitHub
2. Clique na aba **Actions** (no topo)
3. No menu lateral, clique em **Execução Agendada BPO**
4. Clique no botão **Run workflow** (no lado direito)
5. Selecione a branch **main**
6. Clique em **Run workflow** (botão verde)

### Opção B: Via URL Direta

Acesse diretamente:
```
https://github.com/alisonbruno013/get_BPO/actions/workflows/scheduled_run.yml
```

Depois clique em **Run workflow**.

## Passo 4: Verificar Execução

1. Na aba **Actions**, você verá a execução em andamento (amarelo)
2. Clique na execução para ver os detalhes
3. Clique em **run-bpo-script** para ver os logs
4. Expanda cada step para ver o que está acontecendo

### Status:
- 🟡 **Amarelo**: Em execução
- ✅ **Verde**: Sucesso
- ❌ **Vermelho**: Erro

## Passo 5: Verificar Logs

Nos logs você verá:
- ✅ Checkout código
- ✅ Configurar Python
- ✅ Instalar dependências
- ✅ Configurar credenciais
- ✅ Executar script BPO
- ✅ Resultados do script

## Troubleshooting

### Erro: "Secret not found"
- Verifique se todos os 3 secrets estão configurados
- Nomes devem ser exatamente: `BPO_EMAIL`, `BPO_PASSWORD`, `GOOGLE_CREDENTIALS_JSON`

### Erro: "Chrome/ChromeDriver not found"
- O workflow já instala automaticamente
- Se falhar, pode ser problema temporário do GitHub Actions

### Erro: "Planilha não encontrada"
- Verifique se o nome da planilha em `config.py` está correto
- Verifique se a conta de serviço tem acesso à planilha

### Erro: "Credentials JSON inválido"
- Certifique-se de copiar TODO o conteúdo do `credentials.json`
- Não deve ter quebras de linha extras
- Deve ser um JSON válido

### Workflow não aparece
- Certifique-se de que fez push do arquivo `.github/workflows/scheduled_run.yml`
- Verifique se está na branch `main`

## Testar Localmente Antes

Para testar localmente antes de enviar para o GitHub:

```bash
# Executar o script localmente
python scriptMain.py
```

Se funcionar localmente, deve funcionar no GitHub Actions também.

## Dica: Testar com Workflow Simplificado

Se quiser testar apenas a configuração básica primeiro, você pode criar um workflow de teste:

1. Crie `.github/workflows/test.yml`:
```yaml
name: Teste Simples

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Teste
      run: echo "Funcionou!"
```

2. Faça commit e push
3. Execute manualmente para ver se o GitHub Actions está funcionando

## Próximos Passos

Depois que testar e funcionar:
- O workflow executará automaticamente nos horários agendados (09h, 15h, 18h, 00h)
- Você pode ver todas as execuções na aba **Actions**
- Os logs ficam disponíveis por 90 dias
