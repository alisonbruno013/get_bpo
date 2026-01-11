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
    wait_for_clickable_js,
    wait_for_clickable_multiple,
    wait_for_send_keys,
    wait_for_send_keys_js,
    wait_for_download_complete,
    get_latest_csv_file,
    filter_dataframe_by_operation,
    filter_dataframe_by_region,
    upload_to_google_sheets,
    clean_downloads_folder,
    send_error_email
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
    
    # Configura as opções do Chrome para melhor compatibilidade headless
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Novo modo headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--window-size=1920,1080")  # Tamanho de janela fixo
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
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
        # Carrega configurações de email
        Config.load_email_config()
        
        # Carrega credenciais
        email, password = Config.get_credentials()
        print(f"✅ Credenciais carregadas para: {email}")
        
        # Configura o Chrome
        driver, download_dir = setup_chrome_driver()
        print("✅ Chrome WebDriver configurado")
        
        # Acessa o site
        driver.get("https://dwmanagement.spx.com.br/")
        print("✅ Site acessado")
        
        # Faz login usando JavaScript (mais confiável)
        print("Fazendo login via JavaScript...")
        try:
            wait_for_send_keys_js(driver, "data.email", email, timeout=20, by_type='id')
            wait_for_send_keys_js(driver, "data.password", password, timeout=20, by_type='id')
            wait_for_clickable_js(driver, "//*[@id='form']/div[2]/div/button", timeout=20, by_type='xpath')
            print("✅ Login realizado via JavaScript")
        except Exception as e:
            print(f"⚠️ Login via JS falhou, tentando método tradicional: {e}")
            # Fallback para método tradicional
            wait_for_send_keys(driver, "//*[@id='data.email']", email, timeout=20)
            wait_for_send_keys(driver, "//*[@id='data.password']", password, timeout=20)
            wait_for_clickable(driver, "//*[@id='form']/div[2]/div/button", timeout=20)
            print("✅ Login realizado via método tradicional")
        
        # Aguarda a página carregar após o login
        print("Aguardando página carregar após login...")
        time.sleep(5)  # Espera inicial maior
        
        # Aguarda a URL mudar ou algum elemento da página principal aparecer
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        try:
            # Aguarda até que não esteja mais na página de login
            WebDriverWait(driver, 30).until(
                lambda d: "login" not in d.current_url.lower() or d.find_elements(By.XPATH, "//aside//nav")
            )
            print("✅ Página principal carregada")
        except Exception as e:
            error_msg = f"⚠️ Aviso ao aguardar página principal: {e}"
            print(error_msg)
            # Envia screenshot por email
            try:
                send_error_email(driver, str(e))
            except Exception as email_error:
                print(f"⚠️ Erro ao enviar email: {email_error}")
        
        # Aguarda o menu aparecer
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//aside//nav"))
            )
            print("✅ Menu carregado")
            time.sleep(3)  # Espera adicional para menu renderizar
        except Exception as e:
            error_msg = f"⚠️ Aviso: Menu pode não ter carregado completamente: {e}"
            print(error_msg)
            # Envia screenshot por email
            try:
                send_error_email(driver, str(e))
            except Exception as email_error:
                print(f"⚠️ Erro ao enviar email: {email_error}")
            # Tenta aguardar mais
            time.sleep(5)
        
        # Tenta acessar diretamente a URL de relatórios se o menu não funcionar
        print("Tentando navegar para relatórios...")
        
        # Primeiro tenta pelo menu (com múltiplos tipos de seletores)
        selectors_relatorios = [
            ("/html/body/div[1]/aside/nav/ul/li[1]/ul/li[2]/a", "xpath"),
            ("//aside//nav//ul//li[1]//ul//li[2]//a", "xpath"),
            ("//a[contains(@href, 'daily') or contains(text(), 'Daily')]", "xpath"),
            ("//nav//a[contains(text(), 'Daily')]", "xpath"),
            ("//a[contains(@href, 'daily-worker')]", "xpath"),
            ("a[href*='daily-worker']", "css"),
            ("nav a:contains('Daily')", "css")
        ]
        
        navegacao_sucesso = False
        try:
            wait_for_clickable_multiple(driver, selectors_relatorios, timeout=20)
            print("✅ Navegação para relatórios via menu")
            navegacao_sucesso = True
        except Exception as e:
            print(f"⚠️ Erro ao navegar pelo menu: {e}")
            # Tenta acessar diretamente a URL
            try:
                print("Tentando acessar URL diretamente...")
                driver.get("https://dwmanagement.spx.com.br/daily-worker-requests")
                
                # Aguarda a página carregar completamente
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                
                print("Aguardando página de relatórios carregar...")
                # Aguarda até que algum elemento da página apareça
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)  # Espera adicional para JavaScript carregar
                
                # Tenta encontrar qualquer campo de formulário para confirmar que carregou
                try:
                    WebDriverWait(driver, 20).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.ID, "data.fromDate")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#data\\.fromDate")),
                            EC.presence_of_element_located((By.NAME, "data.fromDate"))
                        )
                    )
                    print("✅ Página de relatórios carregada")
                except:
                    print("⚠️ Campos podem não ter carregado completamente")
                
                navegacao_sucesso = True
            except Exception as e2:
                print(f"⚠️ Erro ao acessar URL diretamente: {e2}")
        
        if not navegacao_sucesso:
            print("⚠️ Continuando mesmo com erro de navegação...")
            time.sleep(5)
        
        # Configura as datas
        data_inicial = (datetime.datetime.now() - timedelta(days=Config.DAYS_BEFORE)).strftime("%d/%m/%Y")
        data_final = (datetime.datetime.now() + timedelta(days=Config.DAYS_AFTER)).strftime("%d/%m/%Y")
        
        print(f"Data Inicial: {data_inicial}")
        print(f"Data Final: {data_final}")
        
        # Preenche as datas usando JavaScript (mais confiável)
        print("Preenchendo campo de data inicial via JavaScript...")
        selectors_from_date = [
            ("data.fromDate", "id"),
            ("#data\\.fromDate", "css"),
            ("//*[@id='data.fromDate']", "xpath"),
            ("data.fromDate", "name")
        ]
        
        data_preenchida = False
        for selector, by_type in selectors_from_date:
            try:
                wait_for_send_keys_js(driver, selector, data_inicial, timeout=15, by_type=by_type)
                print(f"✅ Data inicial preenchida via JS usando {by_type}: {selector}")
                data_preenchida = True
                break
            except Exception as e:
                print(f"⚠️ Falhou JS com {by_type} {selector}: {str(e)[:80]}")
                # Tenta método tradicional como fallback
                try:
                    wait_for_send_keys(driver, selector, data_inicial, timeout=10, by_type=by_type)
                    print(f"✅ Data inicial preenchida via método tradicional: {selector}")
                    data_preenchida = True
                    break
                except:
                    continue
        
        if not data_preenchida:
            raise Exception("Não foi possível preencher campo de data inicial")
        
        time.sleep(1)  # Pequena pausa entre campos
        
        print("Preenchendo campo de data final via JavaScript...")
        selectors_to_date = [
            ("data.toDate", "id"),
            ("#data\\.toDate", "css"),
            ("//*[@id='data.toDate']", "xpath"),
            ("data.toDate", "name")
        ]
        
        data_preenchida = False
        for selector, by_type in selectors_to_date:
            try:
                wait_for_send_keys_js(driver, selector, data_final, timeout=15, by_type=by_type)
                print(f"✅ Data final preenchida via JS usando {by_type}: {selector}")
                data_preenchida = True
                break
            except Exception as e:
                print(f"⚠️ Falhou JS com {by_type} {selector}: {str(e)[:80]}")
                # Tenta método tradicional como fallback
                try:
                    wait_for_send_keys(driver, selector, data_final, timeout=10, by_type=by_type)
                    print(f"✅ Data final preenchida via método tradicional: {selector}")
                    data_preenchida = True
                    break
                except:
                    continue
        
        if not data_preenchida:
            raise Exception("Não foi possível preencher campo de data final")
        
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
