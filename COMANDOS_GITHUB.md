# Comandos para Publicar no GitHub

## Passo a Passo Rápido

### 1. Criar repositório no GitHub (faça isso primeiro no navegador)

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `get_BPO`
   - **Description**: "Automação BPO - Download de relatórios e upload para Google Sheets"
   - **Visibility**: ⚠️ **Private** (importante para proteger credenciais)
   - **NÃO marque** "Add a README file" (já temos)
3. Clique em **"Create repository"**

### 2. Executar os comandos abaixo no terminal

```bash
# 1. Inicializar Git
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Fazer primeiro commit
git commit -m "Initial commit: Script BPO com automação"

# 4. Renomear branch para main
git branch -M main

# 5. Adicionar repositório remoto (SUBSTITUA SEU_USUARIO pelo seu usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/get_BPO.git

# 6. Enviar para o GitHub
git push -u origin main
```

### 3. Se pedir autenticação

Se pedir usuário e senha, você pode:
- Usar um **Personal Access Token** (recomendado)
- Ou usar SSH (mais seguro)

**Criar Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Marque: `repo` (acesso completo a repositórios)
4. Copie o token e use como senha

## Verificar se funcionou

Após executar os comandos, acesse:
`https://github.com/SEU_USUARIO/get_BPO`

Você deve ver todos os arquivos lá!

## Próximos Passos

Depois de publicar, configure a execução agendada:
- Veja `GITHUB_SETUP.md` para configurar GitHub Actions
- Ou veja `setup_cron.sh` para execução local
