"""
Script para configurar credenciais de email para alertas
Execute este script para salvar suas credenciais de email
"""
from config import Config
import pickle
import os

if __name__ == "__main__":
    print("=" * 50)
    print("Configuração de Email para Alertas")
    print("=" * 50)
    
    email_from = input("Digite seu email (remetente): ")
    email_password = input("Digite a senha do email (ou app password): ")
    email_to = input("Digite o email de destino (onde receber alertas): ")
    
    # Salva as configurações de email
    email_config = {
        "email_from": email_from,
        "email_password": email_password,
        "email_to": email_to
    }
    
    email_config_file = "email_config.pkl"
    with open(email_config_file, "wb") as f:
        pickle.dump(email_config, f)
    
    # Atualiza o Config
    Config.EMAIL_FROM = email_from
    Config.EMAIL_TO = email_to
    Config.EMAIL_PASSWORD = email_password
    
    print(f"\n✅ Configurações de email salvas em {email_config_file}")
    print(f"Email remetente: {email_from}")
    print(f"Email destino: {email_to}")
