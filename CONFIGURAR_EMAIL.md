# Configuração de Email para Alertas

O script pode enviar automaticamente emails com screenshots quando ocorrem erros críticos.

## Configuração Local

### 1. Execute o script de configuração:

```bash
python save_email_config.py
```

Digite:
- **Email remetente**: Seu email (ex: seu-email@gmail.com)
- **Senha**: Senha do email ou App Password (para Gmail)
- **Email destino**: Email onde você quer receber os alertas

### 2. Para Gmail - Criar App Password:

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione "Mail" e "Other (Custom name)"
3. Digite "BPO Script" e clique em "Generate"
4. Copie a senha gerada (16 caracteres)
5. Use essa senha no script (não use sua senha normal)

## Configuração no GitHub Actions

### 1. Adicione os secrets no GitHub:

Vá em **Settings** → **Secrets and variables** → **Actions** e adicione:

- **EMAIL_FROM**: Seu email remetente
- **EMAIL_TO**: Email onde receber alertas
- **EMAIL_PASSWORD**: Senha do email ou App Password

### 2. O workflow já está configurado

O arquivo `.github/workflows/scheduled_run.yml` já está configurado para usar esses secrets.

## Quando os Emails são Enviados

Os emails são enviados automaticamente quando ocorrem estes erros:

1. ⚠️ **Aviso ao aguardar página principal**: Quando a página não carrega após login
2. ⚠️ **Menu pode não ter carregado completamente**: Quando o menu não aparece

## Conteúdo do Email

O email inclui:
- Data e hora do erro
- Mensagem de erro completa
- Screenshot da tela no momento do erro (anexado)

## Desabilitar Alertas

Para desabilitar os alertas, edite `config.py`:

```python
EMAIL_ALERT_ENABLED = False
```

## Troubleshooting

### Erro: "Email não configurado"
- Execute `python save_email_config.py` localmente
- Ou configure os secrets no GitHub Actions

### Erro: "Authentication failed"
- Para Gmail, use App Password (não a senha normal)
- Verifique se habilitou "Less secure app access" (não recomendado)
- Ou use App Password (recomendado)

### Screenshot não aparece
- O screenshot é salvo localmente mesmo se o email falhar
- Verifique a pasta do projeto por arquivos `screenshot_error_*.png`
