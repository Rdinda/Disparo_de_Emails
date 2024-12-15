import flet as ft
import asyncio
import threading
from utils import show_notification, logger
from whatsapp_browser import WhatsAppBrowser

class WhatsAppTab:
    def __init__(self, page, numeros_compartilhados):
        self.page = page
        self.numeros_compartilhados = numeros_compartilhados
        self.whatsapp = WhatsAppBrowser()
        
        self.whatsapp_mensagem = ft.TextField(
            label="Mensagem do WhatsApp",
            multiline=True,
            min_lines=3,
            max_lines=10,
            width=400
        )

        self.status_conexao = ft.Text("Desconectado", color=ft.colors.ERROR)
        self.progress_ring = ft.ProgressRing(visible=False)
        self.progress_envio = ft.ProgressBar(visible=False)
        self.status_envio = ft.Text("")

        # Campo para número de teste
        self.numero_teste = ft.TextField(
            label="Número para teste",
            hint_text="Ex: 5511999999999",
            width=200
        )

    async def fechar_navegador(self):
        """Fecha o navegador de forma segura"""
        try:
            if self.whatsapp and self.whatsapp.is_ready:
                await self.whatsapp.fechar_sessao()
                self.status_conexao.value = "Desconectado"
                self.status_conexao.color = ft.colors.ERROR
                self.page.update()
        except Exception as e:
            logger.error(f"Erro ao fechar navegador: {str(e)}")

    def iniciar_whatsapp(self, e):
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def start():
                try:
                    self.progress_ring.visible = True
                    self.status_conexao.value = "Iniciando..."
                    self.page.update()
                    
                    success = await self.whatsapp.iniciar_sessao()
                    if success:
                        self.status_conexao.value = "Conectado"
                        self.status_conexao.color = ft.colors.GREEN
                        show_notification(self.page, "WhatsApp Web conectado com sucesso!")
                    else:
                        self.status_conexao.value = "Erro na conexão"
                        self.status_conexao.color = ft.colors.ERROR
                        show_notification(self.page, "Erro ao conectar ao WhatsApp Web", color="error")
                finally:
                    self.progress_ring.visible = False
                    self.page.update()

            try:
                loop.run_until_complete(start())
            except Exception as e:
                logger.error(f"Erro na thread do WhatsApp: {str(e)}")
                self.status_conexao.value = "Erro"
                self.status_conexao.color = ft.colors.ERROR
                self.page.update()
            finally:
                loop.close()

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

    def enviar_mensagens(self, e):
        if not self.whatsapp.is_ready:
            show_notification(self.page, "Conecte ao WhatsApp primeiro!", color="error")
            return

        if not self.numeros_compartilhados:
            show_notification(self.page, "Nenhum número para enviar!", color="error")
            return

        if not self.whatsapp_mensagem.value:
            show_notification(self.page, "Digite uma mensagem!", color="error")
            return

        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def send():
                self.progress_envio.visible = True
                total = len(self.numeros_compartilhados)
                enviados = 0
                
                for numero in self.numeros_compartilhados:
                    try:
                        if await self.whatsapp.enviar_mensagem(numero, self.whatsapp_mensagem.value):
                            enviados += 1
                        self.progress_envio.value = enviados / total
                        self.status_envio.value = f"Enviando: {enviados}/{total}"
                        self.page.update()
                    except Exception as e:
                        logger.error(f"Erro ao enviar para {numero}: {str(e)}")

                self.progress_envio.visible = False
                self.status_envio.value = f"Concluído! Enviados: {enviados}/{total}"
                self.page.update()

            loop.run_until_complete(send())
            loop.close()

        threading.Thread(target=run_async, daemon=True).start()

    def enviar_mensagem_teste(self, e):
        """Wrapper síncrono para enviar_mensagem_teste_async"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def send():
                if not self.whatsapp.is_ready:
                    show_notification(self.page, "Conecte ao WhatsApp primeiro!", color="error")
                    return

                if not self.numero_teste.value:
                    show_notification(self.page, "Digite um número para teste!", color="error")
                    return

                if not self.whatsapp_mensagem.value:
                    show_notification(self.page, "Digite uma mensagem!", color="error")
                    return

                try:
                    self.progress_envio.visible = True
                    self.status_envio.value = "Enviando mensagem de teste..."
                    self.page.update()

                    # Cria uma nova instância do navegador para o envio
                    browser = WhatsAppBrowser()
                    browser.browser_manager = self.whatsapp.browser_manager
                    browser.is_ready = self.whatsapp.is_ready

                    success = await browser.enviar_mensagem(
                        self.numero_teste.value,
                        self.whatsapp_mensagem.value
                    )
                    
                    if success:
                        show_notification(self.page, "Mensagem de teste enviada com sucesso!")
                        self.status_envio.value = "Mensagem de teste enviada!"
                    else:
                        show_notification(self.page, "Erro ao enviar mensagem de teste", color="error")
                        self.status_envio.value = "Erro ao enviar mensagem de teste"

                except Exception as e:
                    logger.error(f"Erro ao enviar mensagem de teste: {str(e)}")
                    show_notification(self.page, "Erro ao enviar mensagem de teste", color="error")
                    self.status_envio.value = "Erro ao enviar mensagem de teste"
                finally:
                    self.progress_envio.visible = False
                    self.page.update()

            try:
                loop.run_until_complete(send())
            except Exception as e:
                logger.error(f"Erro ao executar envio de teste: {str(e)}")
            finally:
                loop.close()

        # Inicia em uma nova thread
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

    def build(self):
        btn_conectar = ft.ElevatedButton(
            text="Conectar WhatsApp",
            icon=ft.icons.PHONE_ANDROID,
            on_click=self.iniciar_whatsapp
        )

        btn_teste = ft.ElevatedButton(
            text="Enviar Teste",
            icon=ft.icons.SEND,
            on_click=self.enviar_mensagem_teste
        )

        btn_enviar_whatsapp = ft.ElevatedButton(
            text="Enviar Mensagens",
            icon=ft.icons.SEND,
            width=200,
            on_click=self.enviar_mensagens
        )

        return ft.Column(
            controls=[
                ft.Text("Envio de Mensagens WhatsApp", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text("Status:", size=16),
                                            self.status_conexao,
                                        ]
                                    ),
                                    self.progress_ring,
                                    btn_conectar
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(),
                            ft.Text("Teste de Envio:", size=16),
                            ft.Row(
                                controls=[
                                    self.numero_teste,
                                    btn_teste
                                ]
                            ),
                            ft.Divider(),
                            ft.Text(f"Números selecionados: {len(self.numeros_compartilhados)}", size=16),
                            self.whatsapp_mensagem,
                            btn_enviar_whatsapp,
                            self.progress_envio,
                            self.status_envio
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