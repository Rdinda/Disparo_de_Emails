"""
Módulo de Gerenciamento de Números
Desenvolvido por Roberto Dinda
GitHub: https://github.com/robertodinda
Copyright (c) 2024 Roberto Dinda
Licença: MIT
"""

import flet as ft
import pandas as pd

class GerenciarNumerosTab:
    def __init__(self, page, numeros_compartilhados):
        self.page = page
        self.numeros_compartilhados = numeros_compartilhados
        
        self.numeros_list = ft.ListView(
            expand=True,
            spacing=10,
            height=400,
            auto_scroll=True
        )
        
        self.numero_input = ft.TextField(
            label="Digite um número",
            width=400,
            hint_text="Ex: 5511999999999"
        )
        
        self.file_picker = ft.FilePicker(
            on_result=self.processa_arquivo_excel
        )
        self.page.overlay.append(self.file_picker)

        self.status_text = ft.Text(f"Total de números: 0")

    def adicionar_numero(self, e):
        if self.numero_input.value:
            self.adicionar_numero_lista(self.numero_input.value)
            self.numero_input.value = ""
            self.page.update()

    def adicionar_numero_lista(self, numero):
        # Remove caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        if numero_limpo not in self.numeros_compartilhados:
            self.numeros_compartilhados.add(numero_limpo)
            numero_row = ft.Row(
                controls=[
                    ft.Text(numero_limpo),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        on_click=lambda e, num=numero_limpo: self.remover_numero(e, num)
                    )
                ]
            )
            self.numeros_list.controls.append(numero_row)
            self.atualizar_status()

    def remover_numero(self, e, numero):
        self.numeros_compartilhados.remove(numero)
        for control in self.numeros_list.controls:
            if control.controls[0].value == numero:
                self.numeros_list.controls.remove(control)
                break
        self.atualizar_status()
        self.page.update()

    def limpar_lista(self, e):
        self.numeros_compartilhados.clear()
        self.numeros_list.controls.clear()
        self.atualizar_status()
        self.page.update()

    def atualizar_status(self):
        self.status_text.value = f"Total de números: {len(self.numeros_compartilhados)}"

    def processa_arquivo_excel(self, e):
        if not e.files:
            return

        try:
            arquivo = e.files[0]
            
            if not arquivo.path:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro: Arquivo não encontrado!"))
                )
                return

            try:
                df = pd.read_excel(
                    arquivo.path,
                    engine='openpyxl'
                )
            except Exception as excel_erro:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Erro ao ler arquivo Excel: {str(excel_erro)}"))
                )
                return

            if df.empty:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("O arquivo Excel está vazio!"))
                )
                return

            colunas_possiveis = ['telefone', 'celular', 'whatsapp', 'numero', 'phone']
            coluna_numero = None

            print("Colunas encontradas no arquivo:", df.columns.tolist())
            
            for col in df.columns:
                col_normalizada = str(col).lower().replace('-', '').replace('_', '').strip()
                if col_normalizada in [c.replace('-', '').replace('_', '') for c in colunas_possiveis]:
                    coluna_numero = col
                    break

            if coluna_numero:
                novos_numeros = df[coluna_numero].dropna().unique()
                numeros_adicionados = 0
                
                for numero in novos_numeros:
                    numero_str = str(numero)
                    numero_limpo = ''.join(filter(str.isdigit, numero_str))
                    if numero_limpo:
                        self.adicionar_numero_lista(numero_limpo)
                        numeros_adicionados += 1

                if numeros_adicionados > 0:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"{numeros_adicionados} números importados com sucesso!")
                        )
                    )
                else:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("Nenhum número válido encontrado no arquivo!")
                        )
                    )
            else:
                colunas_disponiveis = ", ".join(df.columns.tolist())
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(
                            f"Não foi possível encontrar uma coluna de telefone! "
                            f"Colunas disponíveis: {colunas_disponiveis}"
                        )
                    )
                )

        except Exception as erro:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao processar arquivo: {str(erro)}")
                )
            )
        finally:
            self.page.update()

    def mostrar_detalhes(self, e):
        detalhes = f"""
        Detalhes da Lista de Números:
        - Total de números: {len(self.numeros_compartilhados)}
        - Números únicos: {len(self.numeros_compartilhados)}
        """
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(detalhes))
        )

    def build(self):
        btn_adicionar_numero = ft.ElevatedButton(
            text="Adicionar Número",
            on_click=self.adicionar_numero
        )

        btn_selecionar_excel = ft.ElevatedButton(
            text="Importar do Excel",
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["xlsx", "xls"]
            )
        )

        btn_limpar_lista = ft.ElevatedButton(
            text="Limpar Lista",
            on_click=self.limpar_lista
        )

        btn_detalhes = ft.ElevatedButton(
            text="Mostrar Detalhes",
            on_click=self.mostrar_detalhes
        )

        return ft.Column(
            controls=[
                ft.Text("Gerenciamento de Números", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Adicionar Número Manualmente:", size=16),
                            ft.Row(
                                controls=[
                                    self.numero_input,
                                    btn_adicionar_numero,
                                ]
                            ),
                            ft.Divider(),
                            ft.Text("Importar Números:", size=16),
                            ft.Row(
                                controls=[
                                    btn_selecionar_excel,
                                    btn_limpar_lista,
                                    btn_detalhes,
                                ]
                            ),
                            self.status_text,
                            self.numeros_list,
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