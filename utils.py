"""
Módulo de Utilitários
Desenvolvido por Roberto Dinda
GitHub: https://github.com/robertodinda
Copyright (c) 2024 Roberto Dinda
Licença: MIT
"""

import flet as ft
import logging
import os
from datetime import datetime

# Configuração do logger
def setup_logger():
    # Cria o diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nome do arquivo de log com data
    log_filename = f'logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Configuração do logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Para mostrar logs no console também
        ]
    )
    return logging.getLogger('AutomacaoApp')

# Logger global
logger = setup_logger()

def show_notification(page: ft.Page, message: str, color="surface"):
    """Mostra uma notificação usando o novo método recomendado"""
    notification = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color
    )
    page.show_snack_bar = None  # Remove o método depreciado
    page.snack_bar = notification
    page.open = notification
    
    # Registra a notificação no log
    log_level = logging.ERROR if color == "error" else logging.INFO
    logger.log(log_level, f"Notification: {message}")