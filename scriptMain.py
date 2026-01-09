"""
Script principal para automação BPO
Baixa dados do site, filtra e envia para Google Sheets
"""
import os
import time
import pandas as pd
import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Imports locais
from config import Config
from utils import (
    wait_for_clickable,
    wait_for_clickable_multiple,
    wait_for_send_keys,
    wait_for_download_complete,
    get_latest_csv_file,
    filter_dataframe_by_operation,
    filter_dataframe_by_region,
    upload_to_google_sheets,
    clean_downloads_folder
)


def setup_chrome_driver():
    """
    Configura e retorna uma instância do Chrome WebDriver
    
    Returns:
        webdriver.Chrome: Instância configurada do Chrome
    """
    # Configura o diretório de download
    download_dir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIR)
    os.makedirs(download_dir, exist_ok=True)
    
    # Configura as opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-web-security")
    
    # Configura preferências de download
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Cria e retorna o driver
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    return driver, download_dir


def main():
    """Função principal do script"""
    try:
        # Carrega credenciais
        email, password = Config.get_credentials()
        print(f"✅ Credenciais carregadas para: {email}")
        
        # Configura o Chrome
        driver, download_dir = setup_chrome_driver()
        print("✅ Chrome WebDriver configurado")
        
        # Acessa o site
        driver.get("https://dwmanagement.spx.com.br/")
        print("✅ Site acessado")
        
        # Faz login
        wait_for_send_keys(driver, "//*[@id='data.email']", email)
        wait_for_send_keys(driver, "//*[@id='data.password']", password)
        wait_for_clickable(driver, "//*[@id='form']/div[2]/div/button")
        print("✅ Login realizado")
        
        # Aguarda a página carregar após o login
        print("Aguardando página carregar após login...")
        time.sleep(3)  # Espera inicial
        
        # Aguarda o menu aparecer (pode demorar mais no GitHub Actions)
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        try:
            # Tenta encontrar qualquer elemento do menu para confirmar que a página carregou
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//aside//nav"))
            )
            print("✅ Menu carregado")
        except Exception as e:
            print(f"⚠️ Aviso: Menu pode não ter carregado completamente: {e}")
        
        # Aguarda mais um pouco para garantir
        time.sleep(2)
        
        # Navega para a página de relatórios (com timeout maior e múltiplos XPaths)
        print("Tentando navegar para relatórios...")
        
        # Tenta múltiplos XPaths possíveis
        xpaths_relatorios = [
            "/html/body/div[1]/aside/nav/ul/li[1]/ul/li[2]/a",
            "//aside//nav//ul//li[1]//ul//li[2]//a",
            "//a[contains(@href, 'daily') or contains(text(), 'Daily')]",
            "//nav//a[contains(text(), 'Daily')]"
        ]
        
        try:
            wait_for_clickable_multiple(driver, xpaths_relatorios, timeout=30)
            print("✅ Navegação para relatórios")
        except Exception as e:
            print(f"⚠️ Erro ao navegar: {e}")
            print("Tentando continuar...")
            # Tenta aguardar mais e continuar
            time.sleep(5)
        
        # Configura as datas
        data_inicial = (datetime.datetime.now() - timedelta(days=Config.DAYS_BEFORE)).strftime("%d/%m/%Y")
        data_final = (datetime.datetime.now() + timedelta(days=Config.DAYS_AFTER)).strftime("%d/%m/%Y")
        
        print(f"Data Inicial: {data_inicial}")
        print(f"Data Final: {data_final}")
        
        # Preenche as datas
        wait_for_send_keys(driver, "//*[@id='data.fromDate']", data_inicial)
        wait_for_send_keys(driver, "//*[@id='data.toDate']", data_final)
        
        # Gera o relatório
        wait_for_clickable(driver, "/html/body/div[1]/div[1]/main/div/section/header/div[2]/div/button")
        wait_for_clickable(driver, "/html/body/div[1]/div[1]/main/div/form[1]/div/div/div[2]/div/div/div[2]/div/button[1]/span[1]")
        time.sleep(10)
        
        # Faz download do CSV
        wait_for_clickable(driver, "/html/body/div[1]/div[1]/div/nav/div/div[1]/div[1]/button")
        wait_for_clickable(driver, "/html/body/div[1]/div[1]/div/nav/div/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/div/div/div[2]/a[1]/span")
        print("✅ Download iniciado")
        
        # Aguarda o download completar
        print("Aguardando download do CSV...")
        if wait_for_download_complete(download_dir):
            print("Download concluído!")
            
            # Encontra o arquivo CSV mais recente
            csv_file = get_latest_csv_file(download_dir)
            print(f"Arquivo encontrado: {csv_file}")
            
            # Lê o CSV com pandas
            df = pd.read_csv(csv_file)
            print(f"\nDados carregados com sucesso!")
            print(f"Total de linhas antes do filtro: {len(df)}")
            print(f"Colunas: {list(df.columns)}")
            
            # Filtra o DataFrame por Operação
            df = filter_dataframe_by_operation(df)
            
            # Filtra o DataFrame por Região (SPM e SPI)
            df = filter_dataframe_by_region(df)
            
            print(f"\nTotal de linhas após todos os filtros: {len(df)}")
            print(f"\nPrimeiras linhas:")
            print(df.head())
            
            # Faz upload para o Google Sheets
            try:
                print(f"\n{'='*50}")
                print(f"Fazendo upload para o Google Sheets...")
                print(f"Planilha: {Config.SPREADSHEET_NAME}")
                print(f"Aba: {Config.WORKSHEET_NAME}")
                print(f"DataFrame shape: {df.shape} (linhas x colunas)")
                print(f"{'='*50}")
                
                sheet_url = upload_to_google_sheets(df)
                print(f"\n✅ Upload concluído com sucesso!")
                print(f"URL da planilha: {sheet_url}")
                
                # Limpa a pasta de downloads após upload bem-sucedido
                print(f"\n{'='*50}")
                print("Limpando pasta de downloads...")
                clean_downloads_folder(download_dir)
                print(f"{'='*50}")
            except FileNotFoundError as e:
                print(f"❌ Erro: {e}")
            except ValueError as e:
                print(f"❌ Erro: {e}")
            except Exception as e:
                import traceback
                print(f"❌ Erro ao fazer upload para o Google Sheets: {e}")
                print(f"\nDetalhes do erro:")
                traceback.print_exc()
                print("\nVerifique se:")
                print(f"1. O arquivo '{Config.GOOGLE_CREDENTIALS_FILE}' está no diretório do projeto")
                print("2. O nome da planilha está correto")
                print("3. A conta de serviço tem permissão para acessar a planilha")
        else:
            print("Timeout: Download não foi concluído no tempo esperado")
    
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Dica: Execute 'python save_credentials.py' para salvar suas credenciais")
    except Exception as e:
        import traceback
        print(f"❌ Erro inesperado: {e}")
        traceback.print_exc()
    finally:
        if 'driver' in locals():
            driver.quit()
            print("✅ Driver finalizado")


if __name__ == "__main__":
    main()
