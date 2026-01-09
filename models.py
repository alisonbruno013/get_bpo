"""
Modelos de dados para o projeto BPO
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Credentials:
    """Modelo para credenciais de login"""
    email: str
    password: str


@dataclass
class ChromeConfig:
    """Modelo para configurações do Chrome"""
    headless: bool = True
    disable_gpu: bool = True
    disable_dev_shm_usage: bool = True
    no_sandbox: bool = True
    disable_extensions: bool = True
    disable_browser_side_navigation: bool = True
    disable_web_security: bool = True


@dataclass
class FilterConfig:
    """Modelo para configurações de filtro"""
    operation_column_index: int = 11
    filter_values: list = None
    
    def __post_init__(self):
        if self.filter_values is None:
            self.filter_values = ["FMH", "OF", "LHM"]
