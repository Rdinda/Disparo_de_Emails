import flet as ft
import json
import os
from utils import show_notification, logger

class EmailConfig:
    def __init__(self):
        logger.info("Inicializando configurações de email")
        self.config_file = "email_config.json"
        self.default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "",
            "password": "",
            "use_tls": True
        }
        self.config = self.default_config.copy()
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Atualiza apenas os valores que existem no arquivo
                    self.config.update(saved_config)
                    logger.info(f"Configurações carregadas: servidor={self.config['smtp_server']}, email={self.config['email']}")
                    return True
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {str(e)}")
        return False

    def save_config(self):
        try:
            # Verifica se as configurações essenciais estão presentes
            if not self.config["email"] or not self.config["password"]:
                logger.error("Tentativa de salvar configurações sem email ou senha")
                return False

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                logger.info(f"Configurações salvas para o email: {self.config['email']}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {str(e)}")
            return False

    def is_configured(self):
        """Verifica se as configurações básicas estão presentes"""
        return bool(self.config.get("email")) and bool(self.config.get("password"))

class ConfiguracaoEmailDialog(ft.UserControl):
    def __init__(self, page: ft.Page):
        logger.info("Inicializando dialog de configuração")
        super().__init__()
        self.page = page
        self.email_config = EmailConfig()
        
        # Campos do formulário
        self.smtp_server = ft.TextField(
            label="Servidor SMTP",
            value=self.email_config.config["smtp_server"],
            width=400
        )
        
        self.smtp_port = ft.TextField(
            label="Porta SMTP",
            value=str(self.email_config.config["smtp_port"]),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.email = ft.TextField(
            label="Email",
            value=self.email_config.config["email"],
            width=400
        )
        
        self.password = ft.TextField(
            label="Senha",
            value=self.email_config.config["password"],
            width=400,
            password=True
        )
        
        self.use_tls = ft.Checkbox(
            label="Usar TLS",
            value=self.email_config.config["use_tls"]
        )

        # Dialog de configuração
        self.dialog = ft.AlertDialog(
            title=ft.Text("Configurações de Email"),
            content=self.build_dialog_content()
        )

    def build_dialog_content(self):
        return ft.Column(
            controls=[
                ft.Text("Configurações do Servidor SMTP", size=16, weight="bold"),
                self.smtp_server,
                ft.Row(
                    controls=[
                        self.smtp_port,
                        self.use_tls
                    ]
                ),
                ft.Divider(),
                ft.Text("Credenciais", size=16, weight="bold"),
                self.email,
                self.password,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Para Gmail:", size=14, weight="bold"),
                        ft.Text("1. Ative a verificação em duas etapas", size=12),
                        ft.Text("2. Gere uma Senha de App em:", size=12),
                        ft.TextButton(
                            text="https://myaccount.google.com/security",
                            url="https://myaccount.google.com/security"
                        ),
                        ft.Text("3. Use esta senha gerada aqui", size=12),
                    ]),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=10,
                    border_radius=5
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="Salvar",
                            on_click=self.save_settings
                        ),
                        ft.OutlinedButton(
                            text="Testar Conexão",
                            on_click=self.test_connection
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            width=500,
            height=600,
            scroll=ft.ScrollMode.AUTO
        )

    def save_settings(self, e):
        try:
            # Validações básicas
            if not self.email.value or not self.password.value:
                raise ValueError("Email e senha são obrigatórios")
            
            port = int(self.smtp_port.value)
            if port <= 0:
                raise ValueError("Porta inválida")

            # Primeiro testa a conexão
            logger.info(f"Testando conexão antes de salvar - Email: {self.email.value}")
            if not self.test_connection_silent():
                raise ValueError("Falha no teste de conexão. Verifique as credenciais.")

            # Se o teste passou, salva as configurações
            self.email_config.config.update({
                "smtp_server": self.smtp_server.value,
                "smtp_port": port,
                "email": self.email.value,
                "password": self.password.value,
                "use_tls": self.use_tls.value
            })

            if self.email_config.save_config():
                show_notification(self.page, "Configurações salvas com sucesso!")
                self.dialog.open = False
                self.page.update()
            else:
                raise ValueError("Erro ao salvar as configurações")

        except ValueError as ve:
            logger.error(f"Erro de validação: {str(ve)}")
            show_notification(self.page, f"Erro: {str(ve)}", color="error")
        except Exception as erro:
            logger.error(f"Erro ao salvar configurações: {str(erro)}")
            show_notification(self.page, f"Erro ao salvar: {str(erro)}", color="error")

    def test_connection_silent(self):
        """Testa a conexão sem mostrar notificações"""
        import smtplib
        try:
            with smtplib.SMTP(self.smtp_server.value, int(self.smtp_port.value)) as server:
                if self.use_tls.value:
                    server.starttls()
                server.login(self.email.value, self.password.value)
                return True
        except Exception as erro:
            logger.error(f"Erro no teste silencioso: {str(erro)}")
            return False

    def test_connection(self, e):
        import smtplib
        try:
            logger.info(f"Testando conexão com {self.smtp_server.value}:{self.smtp_port.value}")
            with smtplib.SMTP(self.smtp_server.value, int(self.smtp_port.value)) as server:
                if self.use_tls.value:
                    logger.debug("Iniciando TLS")
                    server.starttls()
                logger.info("Realizando login de teste")
                server.login(self.email.value, self.password.value)
                logger.info("Teste de conexão bem sucedido")
                show_notification(self.page, "Conexão estabelecida com sucesso!")
        except Exception as erro:
            logger.error(f"Erro no teste de conexão: {str(erro)}")
            show_notification(self.page, f"Erro na conexão: {str(erro)}", color="error")

    def enviar_email_teste(self, e):
        if not self.email_teste.value:
            show_notification(self.page, "Digite um email para teste!")
            return

        try:
            # ... (código de envio mantido)
            show_notification(self.page, "Email de teste enviado com sucesso!")

        except Exception as erro:
            show_notification(
                self.page,
                f"Erro ao enviar email de teste: {str(erro)}",
                color="error"
            )

    def show_dialog(self):
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update() 