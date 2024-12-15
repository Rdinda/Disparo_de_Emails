from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import logger
import os

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None

    def _get_chrome_path(self):
        """Retorna o caminho do Chrome instalado"""
        chrome_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            os.environ.get('CHROME_PATH', '')
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                logger.info(f"Chrome encontrado em: {path}")
                return path
                
        return None

    async def iniciar_navegador(self):
        try:
            logger.info("Iniciando navegador...")
            
            chrome_path = self._get_chrome_path()
            if not chrome_path:
                logger.error("Chrome não encontrado no sistema!")
                return False
            
            chrome_options = Options()
            chrome_options.binary_location = chrome_path
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Configura o user agent
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Usa o Chrome instalado
            service = Service()
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 60)  # Aumentado para 60 segundos
            
            # Configura o tamanho da janela
            self.driver.set_window_size(1366, 768)
            
            return True

        except Exception as e:
            logger.error(f"Erro ao iniciar navegador: {str(e)}")
            if self.driver:
                self.driver.quit()
            self.driver = None
            return False

    async def navegar_para(self, url):
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"Erro ao navegar para {url}: {str(e)}")
            return False

    async def fechar_navegador(self):
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            logger.error(f"Erro ao fechar navegador: {str(e)}")

    async def encontrar_elemento(self, by, value, timeout=60):
        """Encontra um elemento na página com espera"""
        try:
            # Primeiro tenta encontrar o elemento visível
            elemento = self.wait.until(
                EC.visibility_of_element_located((by, value))
            )
            return elemento
        except:
            try:
                # Se não encontrar visível, tenta encontrar presente no DOM
                elemento = self.wait.until(
                    EC.presence_of_element_located((by, value))
                )
                return elemento
            except Exception as e:
                logger.error(f"Erro ao encontrar elemento {value}: {str(e)}")
                return None

    async def encontrar_elementos(self, by, value, timeout=30):
        """Encontra múltiplos elementos na página com espera"""
        try:
            elementos = self.wait.until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elementos
        except Exception as e:
            logger.error(f"Erro ao encontrar elementos {value}: {str(e)}")
            return []

    async def clicar_elemento(self, elemento):
        """Clica em um elemento com espera"""
        try:
            self.wait.until(EC.element_to_be_clickable(elemento))
            elemento.click()
            return True
        except Exception as e:
            logger.error(f"Erro ao clicar no elemento: {str(e)}")
            return False

    async def enviar_texto(self, elemento, texto):
        """Envia texto para um elemento com espera"""
        try:
            elemento.clear()
            elemento.send_keys(texto)
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar texto: {str(e)}")
            return False 