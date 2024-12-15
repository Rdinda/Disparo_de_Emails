"""
Automação de Mensagens
Desenvolvido por Roberto Dinda
GitHub: https://github.com/robertodinda
Copyright (c) 2024 Roberto Dinda
Licença: MIT
"""

import flet as ft
from email_tab import EmailTab
from whatsapp_tab import WhatsAppTab
from gerenciar_emails_tab import GerenciarEmailsTab
from gerenciar_numeros_tab import GerenciarNumerosTab
import asyncio
import logging

logger = logging.getLogger(__name__)

async def main(page: ft.Page):
    page.title = "Automação de Emails"
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    page.padding = 20

    # Rodapé com informações do desenvolvedor (mais compacto)
    footer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    "Desenvolvido por Rdinda",
                    size=12,
                    color=ft.colors.GREY_700,
                    weight=ft.FontWeight.BOLD
                ),
                ft.TextButton(
                    "GitHub",
                    url="https://github.com/Rdinda",
                    tooltip="Visite meu GitHub",
                    icon=ft.icons.CODE,
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(5)
                    )
                ),
                ft.Text(
                    "© 2024",
                    size=12,
                    color=ft.colors.GREY_700
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            tight=True
        ),
        padding=ft.padding.only(top=10),
        height=40  # Altura fixa para o rodapé
    )

    # Estruturas compartilhadas
    emails_compartilhados = {}
    numeros_compartilhados = set()

    # Criando as instâncias das abas
    gerenciar_emails_tab = GerenciarEmailsTab(page, emails_compartilhados)
    email_tab = EmailTab(page, emails_compartilhados)
    gerenciar_numeros_tab = GerenciarNumerosTab(page, numeros_compartilhados)
    whatsapp_tab = WhatsAppTab(page, numeros_compartilhados)

    async def handle_window_event(e):
        if e.data == "close":
            try:
                # Fecha o navegador antes de fechar o app
                await whatsapp_tab.fechar_navegador()
                # Força o fechamento da janela
                page.window_destroy()
            except Exception as err:
                logger.error(f"Erro ao fechar aplicativo: {str(err)}")
                # Força o fechamento mesmo com erro
                page.window_destroy()

    def on_window_close(e):
        """Handler síncrono para o evento de fechamento"""
        # Cria uma task para executar o handler assíncrono
        page.window_destroy()

    # Configura o evento de fechamento da janela
    page.window.on_close = on_window_close

    # Criando as abas
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Gerenciar Emails",
                icon=ft.icons.EMAIL_OUTLINED,
                content=gerenciar_emails_tab.build()
            ),
            ft.Tab(
                text="Enviar Emails",
                icon=ft.icons.SEND,
                content=email_tab.build()
            ),
            ft.Tab(
                text="Gerenciar Números",
                icon=ft.icons.PHONE,
                content=gerenciar_numeros_tab.build()
            ),
            ft.Tab(
                text="WhatsApp",
                icon=ft.icons.SEND_ROUNDED,
                content=whatsapp_tab.build()
            )
        ]
    )

    # Criando o layout principal
    main_content = ft.Column(
        controls=[
            ft.Container(
                content=tabs,
                expand=True  # Faz as abas ocuparem o espaço disponível
            ),
            ft.Divider(height=1),  # Linha divisória fina
            footer  # Rodapé compacto
        ],
        spacing=0,
        expand=True
    )

    page.add(main_content)
    await page.update_async()

if __name__ == "__main__":
    ft.app(target=main) 