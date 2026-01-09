"""
Arquivo de configuração para gerenciar credenciais e configurações
"""
import pickle
import os


class Config:
    """Classe para gerenciar configurações e credenciais"""
    
    CREDENTIALS_FILE = "credentials.pkl"
    GOOGLE_CREDENTIALS_FILE = "credentials.json"
    DOWNLOAD_DIR = "downloads"
    SPREADSHEET_NAME = "GET_BPO"
    WORKSHEET_NAME = "Base"
    
    # Configurações do Chrome
    CHROME_OPTIONS = {
        "headless": True,
        "disable_gpu": True,
        "disable_dev_shm_usage": True,
        "no_sandbox": True,
        "disable_extensions": True,
        "disable_browser_side_navigation": True,
        "disable_web_security": True
    }
    
    # Filtros do DataFrame
    FILTER_VALUES = ["FMH", "OF", "LMH"]
    OPERATION_COLUMN_INDEX = 12 # Coluna 13 (índice 12)
    REGION_FILTER_VALUES = ["SPM", "SPI"]
    REGION_COLUMN_INDEX = 8  # Coluna 9 (índice 8)
    
    # Datas
    DAYS_BEFORE = 5
    DAYS_AFTER = 5
    
    @staticmethod
    def save_credentials(email: str, password: str):
        """
        Salva as credenciais em um arquivo pickle
        
        Args:
            email: Email de login
            password: Senha
        """
        credentials = {
            "email": email,
            "password": password
        }
        with open(Config.CREDENTIALS_FILE, "wb") as f:
            pickle.dump(credentials, f)
        print(f"✅ Credenciais salvas em {Config.CREDENTIALS_FILE}")
    
    @staticmethod
    def load_credentials():
        """
        Carrega as credenciais do arquivo pickle
        
        Returns:
            dict: Dicionário com 'email' e 'password'
        """
        if not os.path.exists(Config.CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Arquivo de credenciais não encontrado: {Config.CREDENTIALS_FILE}\n"
                "Use Config.save_credentials() para criar o arquivo."
            )
        
        with open(Config.CREDENTIALS_FILE, "rb") as f:
            credentials = pickle.load(f)
        
        return credentials
    
    @staticmethod
    def get_credentials():
        """
        Retorna email e senha separadamente
        
        Returns:
            tuple: (email, password)
        """
        creds = Config.load_credentials()
        return creds["email"], creds["password"]
