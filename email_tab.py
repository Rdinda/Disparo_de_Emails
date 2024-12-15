"""
Módulo de Envio de Emails
Desenvolvido por Roberto Dinda
GitHub: https://github.com/robertodinda
Copyright (c) 2024 Roberto Dinda
Licença: MIT
"""

import flet as ft
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_config import EmailConfig, ConfiguracaoEmailDialog
from utils import show_notification, logger

class EmailTab:
    def __init__(self, page, emails_compartilhados):
        logger.info("Inicializando EmailTab")
        self.page = page
        self.emails_compartilhados = emails_compartilhados
        self.email_config = EmailConfig()
        self.config_dialog = ConfiguracaoEmailDialog(page)
        
        self.email_assunto = ft.TextField(
            label="Assunto do Email (Use {nome} para personalizar)",
            width=400,
            hint_text="Ex: Olá {nome}, temos uma proposta para você"
        )
        
        self.email_mensagem = ft.TextField(
            label="Mensagem do Email (Use {nome} para personalizar)",
            multiline=True,
            min_lines=3,
            max_lines=10,
            width=400,
            hint_text="Ex: Prezado(a) {nome},\nTemos uma proposta especial..."
        )

        # Progresso do envio
        self.progress_bar = ft.ProgressBar(width=400, visible=False)
        self.status_envio = ft.Text("")

    def verificar_configuracoes(self):
        """Verifica se as configurações de email estão válidas"""
        # Força recarregar as configurações
        self.email_config.load_config()
        
        if not self.email_config.is_configured():
            show_notification(
                self.page,
                "Configure o email e senha primeiro!",
                color="error"
            )
            # Abre automaticamente o dialog de configuração
            self.config_dialog.show_dialog()
            return False
        return True

    def enviar_emails(self, e):
        if not self.verificar_configuracoes():
            return

        if not self.emails_compartilhados:
            logger.warning("Tentativa de envio sem emails na lista")
            show_notification(self.page, "Nenhum email para enviar!")
            return

        if not self.email_assunto.value or not self.email_mensagem.value:
            logger.warning("Tentativa de envio sem assunto ou mensagem")
            show_notification(self.page, "Preencha o assunto e a mensagem!")
            return

        try:
            logger.info(f"Iniciando envio para {len(self.emails_compartilhados)} destinatários")
            # Configuração do servidor SMTP
            server = smtplib.SMTP(
                self.email_config.config["smtp_server"],
                self.email_config.config["smtp_port"]
            )
            
            if self.email_config.config["use_tls"]:
                logger.debug("Iniciando TLS")
                server.starttls()
            
            logger.info("Realizando login no servidor SMTP")
            server.login(
                self.email_config.config["email"],
                self.email_config.config["password"]
            )

            total_emails = len(self.emails_compartilhados)
            enviados = 0
            falhas = 0

            self.progress_bar.visible = True
            self.status_envio.value = "Enviando emails..."
            self.page.update()

            for email, nome in self.emails_compartilhados.items():
                try:
                    # Personaliza assunto e mensagem
                    assunto = self.email_assunto.value.replace("{nome}", nome) if nome else self.email_assunto.value
                    mensagem = self.email_mensagem.value.replace("{nome}", nome) if nome else self.email_mensagem.value

                    msg = MIMEMultipart()
                    msg['From'] = self.email_config.config["email"]
                    msg['To'] = email
                    msg['Subject'] = assunto
                    msg.attach(MIMEText(mensagem, 'plain'))

                    server.send_message(msg)
                    enviados += 1
                    logger.info(f"Email enviado com sucesso para: {email}")
                    self.progress_bar.value = enviados / total_emails
                    self.status_envio.value = f"Progresso: {enviados}/{total_emails}"
                    self.page.update()
                except Exception as erro:
                    falhas += 1
                    logger.error(f"Erro ao enviar para {email}: {str(erro)}")

            server.quit()
            logger.info(f"Envio concluído. Enviados: {enviados}, Falhas: {falhas}")
            self.progress_bar.visible = False
            self.status_envio.value = f"Concluído! Enviados: {enviados}, Falhas: {falhas}"
            self.page.update()

        except Exception as erro:
            logger.error(f"Erro ao conectar ao servidor: {str(erro)}")
            show_notification(
                self.page,
                f"Erro ao conectar ao servidor: {str(erro)}",
                color="error"
            )
            self.progress_bar.visible = False
            self.status_envio.value = "Erro no envio"
            self.page.update()

    def build(self):
        btn_configurar = ft.ElevatedButton(
            text="Configurar Email",
            icon=ft.icons.SETTINGS,
            on_click=lambda _: self.config_dialog.show_dialog()
        )

        btn_enviar_email = ft.ElevatedButton(
            text="Enviar Emails",
            icon=ft.icons.SEND,
            on_click=self.enviar_emails,
            width=200
        )

        return ft.Column(
            controls=[
                ft.Text("Envio de Emails em Massa", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(f"Emails selecionados: {len(self.emails_compartilhados)}", size=16),
                                    btn_configurar
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            self.email_assunto,
                            self.email_mensagem,
                            self.progress_bar,
                            self.status_envio,
                            btn_enviar_email
                        ],
                        spacing=20
                    ),
                    padding=20,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                )
            ],
            spacing=20
        ) 