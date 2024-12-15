"""
Módulo de Gerenciamento de Emails
Desenvolvido por Roberto Dinda
GitHub: https://github.com/robertodinda
Copyright (c) 2024 Roberto Dinda
Licença: MIT
"""

import flet as ft
import pandas as pd
from utils import show_notification
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

class GerenciarEmailsTab:
    def __init__(self, page, emails_compartilhados):
        self.page = page
        # Compartilha a lista de emails entre as abas
        self.emails_compartilhados = emails_compartilhados  # Agora será um dicionário
        
        # Lista visual de emails
        self.emails_list = ft.ListView(
            expand=True,
            spacing=10,
            height=400,
            auto_scroll=True
        )
        
        self.email_input = ft.TextField(
            label="Digite um email",
            width=300,
            hint_text="exemplo@email.com"
        )

        self.nome_input = ft.TextField(
            label="Nome",
            width=200,
            hint_text="Nome do destinatário"
        )
        
        self.file_picker = ft.FilePicker(
            on_result=self.processa_arquivo_excel
        )
        self.page.overlay.append(self.file_picker)

        self.status_text = ft.Text(f"Total de emails: 0")

    def adicionar_email(self, e):
        if self.email_input.value:
            self.adicionar_email_lista(self.email_input.value, self.nome_input.value)
            self.email_input.value = ""
            self.nome_input.value = ""
            self.page.update()

    def adicionar_email_lista(self, email, nome=""):
        if email not in self.emails_compartilhados:
            self.emails_compartilhados[email] = nome
            email_row = ft.Row(
                controls=[
                    ft.Text(f"{nome} <{email}>" if nome else email),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        on_click=lambda e, email=email: self.remover_email(e, email)
                    )
                ]
            )
            self.emails_list.controls.append(email_row)
            self.atualizar_status()

    def remover_email(self, e, email):
        self.emails_compartilhados.pop(email, None)
        for control in self.emails_list.controls:
            if email in control.controls[0].value:
                self.emails_list.controls.remove(control)
                break
        self.atualizar_status()
        self.page.update()

    def limpar_lista(self, e):
        self.emails_compartilhados.clear()
        self.emails_list.controls.clear()
        self.atualizar_status()
        self.page.update()

    def atualizar_status(self):
        self.status_text.value = f"Total de emails: {len(self.emails_compartilhados)}"

    def processa_arquivo_excel(self, e):
        if not e.files:
            return

        try:
            arquivo = e.files[0]
            
            if not arquivo.path:
                show_notification(self.page, "Erro: Arquivo não encontrado!", color="error")
                return

            try:
                df = pd.read_excel(arquivo.path, engine='openpyxl')
            except Exception as excel_erro:
                show_notification(
                    self.page, 
                    f"Erro ao ler arquivo Excel: {str(excel_erro)}", 
                    color="error"
                )
                return

            if df.empty:
                show_notification(self.page, "O arquivo Excel está vazio!", color="error")
                return

            # Procura colunas de email e nome
            colunas_email = ['email', 'e-mail', 'e_mail', 'email_address', 'endereco_email']
            colunas_nome = ['nome', 'name', 'nome_completo', 'full_name']
            
            coluna_email = None
            coluna_nome = None

            # Procura coluna de email
            for col in df.columns:
                col_normalizada = str(col).lower().replace('-', '').replace('_', '').strip()
                if col_normalizada in [c.replace('-', '').replace('_', '') for c in colunas_email]:
                    coluna_email = col
                    break

            # Procura coluna de nome
            for col in df.columns:
                col_normalizada = str(col).lower().replace('-', '').replace('_', '').strip()
                if col_normalizada in [c.replace('-', '').replace('_', '') for c in colunas_nome]:
                    coluna_nome = col
                    break

            if coluna_email:
                emails_adicionados = 0
                
                for idx, row in df.iterrows():
                    email = str(row[coluna_email]).strip()
                    nome = str(row[coluna_nome]).strip() if coluna_nome else ""
                    
                    if isinstance(email, str) and '@' in email:
                        self.adicionar_email_lista(email, nome)
                        emails_adicionados += 1

                if emails_adicionados > 0:
                    show_notification(
                        self.page,
                        f"{emails_adicionados} emails importados com sucesso!"
                    )
                else:
                    show_notification(
                        self.page,
                        "Nenhum email válido encontrado no arquivo!",
                        color="error"
                    )
            else:
                colunas_disponiveis = ", ".join(df.columns.tolist())
                show_notification(
                    self.page,
                    f"Não foi possível encontrar uma coluna de email! "
                    f"Colunas disponíveis: {colunas_disponiveis}",
                    color="error"
                )

        except Exception as erro:
            show_notification(
                self.page,
                f"Erro ao processar arquivo: {str(erro)}",
                color="error"
            )
        finally:
            self.page.update()

    def mostrar_detalhes(self, e):
        detalhes = f"""
        Detalhes da Lista de Emails:
        - Total de emails: {len(self.emails_compartilhados)}
        - Emails únicos: {len(self.emails_compartilhados)}
        """
        show_notification(self.page, detalhes)

    def build(self):
        return ft.Column(
            controls=[
                ft.Text("Gerenciamento de Emails", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Adicionar Email Manualmente:", size=16),
                            ft.Row(
                                controls=[
                                    self.email_input,
                                    self.nome_input,
                                    ft.ElevatedButton(
                                        text="Adicionar",
                                        on_click=self.adicionar_email
                                    ),
                                ]
                            ),
                            ft.Divider(),
                            ft.Text("Importar Emails:", size=16),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        text="Importar do Excel",
                                        on_click=lambda _: self.file_picker.pick_files(
                                            allowed_extensions=["xlsx", "xls"]
                                        )
                                    ),
                                    ft.ElevatedButton(
                                        text="Limpar Lista",
                                        on_click=self.limpar_lista
                                    ),
                                ]
                            ),
                            self.status_text,
                            self.emails_list,
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