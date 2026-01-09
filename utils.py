"""
Funções utilitárias para o script BPO
"""
import os
import glob
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials
from config import Config


def wait_for_clickable(driver, xpath, timeout=30):
    """
    Aguarda um elemento estar clicável e clica nele
    
    Args:
        driver: Instância do WebDriver
        xpath: XPath do elemento
        timeout: Tempo máximo de espera em segundos
    """
    import time
    wait = WebDriverWait(driver, timeout)
    
    try:
        # Primeiro tenta encontrar o elemento
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        # Depois aguarda estar clicável
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        # Pequena espera antes de clicar
        time.sleep(0.5)
        element.click()
    except Exception as e:
        print(f"❌ Erro ao clicar no elemento {xpath}: {e}")
        # Tenta scroll até o elemento
        try:
            element = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            element.click()
        except Exception as e2:
            raise Exception(f"Não foi possível clicar no elemento {xpath}. Erro original: {e}, Erro no scroll: {e2}")


def wait_for_clickable_multiple(driver, xpaths, timeout=30):
    """
    Tenta clicar em um dos múltiplos XPaths fornecidos
    
    Args:
        driver: Instância do WebDriver
        xpaths: Lista de XPaths para tentar
        timeout: Tempo máximo de espera em segundos para cada tentativa
    """
    for i, xpath in enumerate(xpaths):
        try:
            print(f"Tentativa {i+1}/{len(xpaths)}: {xpath[:50]}...")
            wait_for_clickable(driver, xpath, timeout=timeout)
            print(f"✅ Sucesso com XPath {i+1}")
            return True
        except Exception as e:
            print(f"⚠️ XPath {i+1} falhou: {str(e)[:100]}")
            if i == len(xpaths) - 1:
                raise Exception(f"Todos os XPaths falharam. Último erro: {e}")
    return False


def wait_for_send_keys(driver, xpath, keys, timeout=10):
    """
    Aguarda um elemento estar clicável e envia texto
    
    Args:
        driver: Instância do WebDriver
        xpath: XPath do elemento
        keys: Texto a ser enviado
        timeout: Tempo máximo de espera em segundos
    """
    wait = WebDriverWait(driver, timeout)
    input_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    input_element.send_keys(keys)


def wait_for_download_complete(download_dir, timeout=60):
    """
    Aguarda o download completar verificando se não há arquivos .crdownload
    
    Args:
        download_dir: Diretório de downloads
        timeout: Tempo máximo de espera em segundos
    
    Returns:
        bool: True se o download foi concluído, False se timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Verifica se há arquivos .crdownload (download em andamento)
        crdownload_files = glob.glob(os.path.join(download_dir, "*.crdownload"))
        if not crdownload_files:
            # Verifica se há arquivos CSV
            csv_files = glob.glob(os.path.join(download_dir, "*.csv"))
            if csv_files:
                return True
        time.sleep(0.5)
    return False


def get_latest_csv_file(download_dir):
    """
    Retorna o arquivo CSV mais recente no diretório de downloads
    
    Args:
        download_dir: Diretório de downloads
    
    Returns:
        str: Caminho do arquivo CSV mais recente
    """
    csv_files = glob.glob(os.path.join(download_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado no diretório de downloads")
    # Retorna o arquivo mais recente baseado na data de modificação
    latest_file = max(csv_files, key=os.path.getmtime)
    return latest_file


def filter_dataframe_by_operation(df, operation_column=None):
    """
    Filtra o DataFrame mantendo apenas valores específicos na coluna de operação
    
    Args:
        df: DataFrame do pandas
        operation_column: Nome da coluna de operação (se None, tenta encontrar automaticamente)
    
    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    # Tenta encontrar a coluna de operação
    if operation_column is None:
        for col in df.columns:
            if 'oper' in col.lower() or 'operação' in col.lower():
                operation_column = col
                break
        
        # Se não encontrou pelo nome, tenta pela posição
        if operation_column is None and len(df.columns) > Config.OPERATION_COLUMN_INDEX:
            operation_column = df.columns[Config.OPERATION_COLUMN_INDEX]
            print(f"Usando coluna na posição {Config.OPERATION_COLUMN_INDEX + 1}: {operation_column}")
    
    if operation_column is None:
        print("⚠️ Aviso: Coluna 'Operação' não encontrada. Retornando DataFrame original.")
        print(f"Colunas disponíveis: {list(df.columns)}")
        return df
    
    print(f"Filtrando pela coluna: '{operation_column}'")
    valores_antes = len(df)
    
    # Mostra valores únicos antes do filtro
    valores_unicos_antes = df[operation_column].unique()
    print(f"Valores únicos antes do filtro: {valores_unicos_antes}")
    
    # Remove espaços em branco e converte para string para garantir comparação correta
    df[operation_column] = df[operation_column].astype(str).str.strip()
    
    # Filtra mantendo apenas os valores configurados (case-insensitive)
    df_filtered = df[df[operation_column].str.upper().isin([v.upper() for v in Config.FILTER_VALUES])]
    
    valores_depois = len(df_filtered)
    print(f"✅ Filtro aplicado: {valores_antes} -> {valores_depois} linhas")
    
    if valores_depois > 0:
        print(f"Valores únicos após filtro: {df_filtered[operation_column].unique()}")
    else:
        print(f"⚠️ Nenhuma linha corresponde aos filtros {Config.FILTER_VALUES}")
    
    return df_filtered


def filter_dataframe_by_region(df, region_column=None):
    """
    Filtra o DataFrame mantendo apenas valores específicos na coluna de região
    
    Args:
        df: DataFrame do pandas
        region_column: Nome da coluna de região (se None, tenta encontrar automaticamente)
    
    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    # Tenta encontrar a coluna de região
    if region_column is None:
        for col in df.columns:
            if 'regi' in col.lower() or 'região' in col.lower():
                region_column = col
                break
        
        # Se não encontrou pelo nome, tenta pela posição
        if region_column is None and len(df.columns) > Config.REGION_COLUMN_INDEX:
            region_column = df.columns[Config.REGION_COLUMN_INDEX]
            print(f"Usando coluna na posição {Config.REGION_COLUMN_INDEX + 1}: {region_column}")
    
    if region_column is None:
        print("⚠️ Aviso: Coluna 'Região' não encontrada. Retornando DataFrame original.")
        print(f"Colunas disponíveis: {list(df.columns)}")
        return df
    
    print(f"Filtrando pela coluna de Região: '{region_column}'")
    valores_antes = len(df)
    
    # Mostra valores únicos antes do filtro
    valores_unicos_antes = df[region_column].unique()
    print(f"Valores únicos antes do filtro de região: {valores_unicos_antes}")
    
    # Remove espaços em branco e converte para string para garantir comparação correta
    df[region_column] = df[region_column].astype(str).str.strip()
    
    # Filtra mantendo apenas os valores configurados (case-insensitive)
    df_filtered = df[df[region_column].str.upper().isin([v.upper() for v in Config.REGION_FILTER_VALUES])]
    
    valores_depois = len(df_filtered)
    print(f"✅ Filtro de região aplicado: {valores_antes} -> {valores_depois} linhas")
    
    if valores_depois > 0:
        print(f"Valores únicos após filtro de região: {df_filtered[region_column].unique()}")
    else:
        print(f"⚠️ Nenhuma linha corresponde aos filtros de região {Config.REGION_FILTER_VALUES}")
    
    return df_filtered


def upload_to_google_sheets(df, spreadsheet_name=None, worksheet_name=None, credentials_path=None):
    """
    Faz upload de um DataFrame para o Google Sheets
    
    Args:
        df: DataFrame do pandas com os dados
        spreadsheet_name: Nome da planilha do Google Sheets
        worksheet_name: Nome da aba (se None, usa a primeira aba)
        credentials_path: Caminho para o arquivo JSON de credenciais
    
    Returns:
        str: URL da planilha
    """
    if spreadsheet_name is None:
        spreadsheet_name = Config.SPREADSHEET_NAME
    if worksheet_name is None:
        worksheet_name = Config.WORKSHEET_NAME
    if credentials_path is None:
        credentials_path = os.path.join(os.getcwd(), Config.GOOGLE_CREDENTIALS_FILE)
    
    # Configura o escopo necessário
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Arquivo de credenciais não encontrado: {credentials_path}\n"
            "Por favor, baixe o arquivo JSON de credenciais do Google Cloud Console"
        )
    
    # Autentica usando service account
    creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValueError(f"Planilha '{spreadsheet_name}' não encontrada. Verifique o nome e se a conta de serviço tem acesso.")
    
    # Seleciona a aba (worksheet)
    if worksheet_name:
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Cria a aba se não existir
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=len(df)+1, cols=len(df.columns))
    else:
        worksheet = spreadsheet.sheet1
    
    # Limpa a aba existente
    worksheet.clear()
    
    # Prepara os dados: substitui NaN por strings vazias
    df_clean = df.fillna('')
    
    # Converte DataFrame para lista de listas
    # Primeiro adiciona os cabeçalhos
    values = [df_clean.columns.tolist()]
    # Depois adiciona os dados, convertendo tudo para string para evitar problemas
    for row in df_clean.values.tolist():
        values.append([str(val) if val is not None else '' for val in row])
    
    print(f"Preparando para enviar {len(values)} linhas (incluindo cabeçalho) e {len(values[0])} colunas...")
    
    # Faz upload dos dados usando batch_update para melhor performance
    batch_size = 10000
    total_rows = len(values)
    
    if total_rows <= batch_size:
        # Se couber em um lote, envia tudo de uma vez
        worksheet.update('A1', values, value_input_option='USER_ENTERED')
        print(f"Dados enviados em 1 lote")
    else:
        # Divide em múltiplos lotes
        print(f"Dividindo em lotes de {batch_size} linhas...")
        # Envia cabeçalho primeiro
        worksheet.update('A1', [values[0]], value_input_option='USER_ENTERED')
        
        # Envia os dados em lotes
        for i in range(1, total_rows, batch_size):
            batch = values[i:i+batch_size]
            start_row = i + 1  # +1 porque a linha 1 é o cabeçalho
            range_name = f'A{start_row}'
            worksheet.update(range_name, batch, value_input_option='USER_ENTERED')
            print(f"Lote enviado: linhas {start_row} a {start_row + len(batch) - 1}")
    
    print(f"Dados enviados para o Google Sheets com sucesso!")
    print(f"Planilha: {spreadsheet_name}")
    print(f"Aba: {worksheet.title}")
    print(f"Total de linhas enviadas: {len(df_clean)}")
    print(f"Total de colunas: {len(df_clean.columns)}")
    print(f"URL: {spreadsheet.url}")
    
    return spreadsheet.url
