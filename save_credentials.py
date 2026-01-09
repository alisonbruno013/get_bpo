"""
Script para salvar credenciais de login em arquivo pickle
Execute este script uma vez para salvar suas credenciais
"""
from config import Config

if __name__ == "__main__":
    print("=" * 50)
    print("Configuração de Credenciais")
    print("=" * 50)
    
    email = input("Digite seu email: ")
    password = input("Digite sua senha: ")
    
    Config.save_credentials(email, password)
    print("\n✅ Credenciais salvas com sucesso!")
    print(f"Arquivo criado: {Config.CREDENTIALS_FILE}")
