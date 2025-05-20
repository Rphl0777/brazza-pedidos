import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from ttkthemes import ThemedTk
from datetime import datetime
import os

class PedidoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pedidos Brazza")
        self.pedidos = []
        self.total_vendido = 0.0
        self.totais_por_pagamento = {}
        self.historico_salvo = True

        self.historico_dir = os.path.join(os.getcwd(), "historicos")
        if not os.path.exists(self.historico_dir):
            os.makedirs(self.historico_dir)

        self.data_selecionada = datetime.now().date()

        frame_data = ttk.Frame(root, padding=10)
        frame_data.pack(padx=10, pady=(10, 0), fill="x")

        ttk.Label(frame_data, text="Data:").pack(side="left", padx=(0, 5))
        self.calendario = DateEntry(frame_data, width=12, background="darkred", foreground="white", date_pattern="yyyy-mm-dd")
        self.calendario.set_date(self.data_selecionada)
        self.calendario.pack(side="left")
        self.calendario.bind("<<DateEntrySelected>>", self.carregar_pedidos)

        frame_entrada = ttk.Frame(root, padding=10)
        frame_entrada.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_entrada, text="Produto:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_produto = ttk.Entry(frame_entrada, width=25)
        self.entry_produto.grid(row=0, column=1, sticky="w")

        ttk.Label(frame_entrada, text="Horário:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_horario = ttk.Entry(frame_entrada, width=25)
        self.entry_horario.grid(row=1, column=1, sticky="w")

        ttk.Label(frame_entrada, text="Nome / iFood:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome = ttk.Entry(frame_entrada, width=25)
        self.entry_nome.grid(row=2, column=1, sticky="w")

        ttk.Label(frame_entrada, text="Endereço:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_endereco = ttk.Entry(frame_entrada, width=25)
        self.entry_endereco.grid(row=3, column=1, sticky="w")

        ttk.Label(frame_entrada, text="Valor (R$):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_valor = ttk.Entry(frame_entrada, width=15)
        self.entry_valor.grid(row=4, column=1, sticky="w")

        ttk.Label(frame_entrada, text="Forma de pagamento:").grid(row=4, column=2, sticky="e", padx=5, pady=5)
        self.combo_pagamento = ttk.Combobox(frame_entrada, values=[
            "Pago para a loja",
            "Pago pelo iFood",
            "Débito",
            "Crédito"
        ], state="readonly", width=18)
        self.combo_pagamento.current(0)
        self.combo_pagamento.grid(row=4, column=3, sticky="w")

        frame_botoes = ttk.Frame(root, padding=10)
        frame_botoes.pack(padx=10, pady=5, fill="x")

        btn_adicionar = ttk.Button(frame_botoes, text="Adicionar Pedido", command=self.adicionar_pedido)
        btn_adicionar.pack(side="left", padx=5)

        btn_editar = ttk.Button(frame_botoes, text="Editar Pedido", command=self.editar_pedido)
        btn_editar.pack(side="left", padx=5)

        btn_excluir = ttk.Button(frame_botoes, text="Excluir Pedido", command=self.excluir_pedido)
        btn_excluir.pack(side="left", padx=5)

        btn_finalizar = ttk.Button(frame_botoes, text="Finalizar Pedido", command=self.finalizar_pedido)
        btn_finalizar.pack(side="left", padx=5)

        self.btn_salvar = ttk.Button(frame_botoes, text="Salvar Histórico", command=self.salvar_historico)
        self.btn_salvar.pack(side="left", padx=5)

        frame_lista = ttk.Frame(root, padding=10)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(frame_lista, columns=("Produto", "Horário", "Nome", "Endereço", "Valor", "Pagamento", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.column("Produto", width=120)
        self.tree.column("Horário", width=80)
        self.tree.column("Nome", width=120)
        self.tree.column("Endereço", width=180)
        self.tree.column("Valor", width=80, anchor="e")
        self.tree.column("Pagamento", width=120)
        self.tree.column("Status", width=100)
        self.tree.pack(fill="both", expand=True)

        frame_total = ttk.Frame(root)
        frame_total.pack(pady=(0, 10))

        self.combo_filtro_total = ttk.Combobox(frame_total, values=[
            "Todos",
            "Pago para a loja",
            "Pago pelo iFood",
            "Débito",
            "Crédito"
        ], state="readonly", width=25)
        self.combo_filtro_total.current(0)
        self.combo_filtro_total.pack()
        self.combo_filtro_total.bind("<<ComboboxSelected>>", self.atualizar_total)

        self.label_total = ttk.Label(root, text="Total vendido no dia: R$ 0.00", font=("Arial", 14, "bold"))
        self.label_total.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.confirmar_saida)
        self.carregar_pedidos()

    def adicionar_pedido(self):
        produto = self.entry_produto.get().strip()
        horario = self.entry_horario.get().strip()
        nome = self.entry_nome.get().strip()
        endereco = self.entry_endereco.get().strip()
        valor_texto = self.entry_valor.get().strip()
        pagamento = self.combo_pagamento.get()

        if not produto or not horario or not nome or not endereco or not valor_texto:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
            return

        try:
            valor = float(valor_texto.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Use apenas números.")
            return

        pedido = {
            "produto": produto,
            "horario": horario,
            "nome": nome,
            "endereco": endereco,
            "valor": valor,
            "pagamento": pagamento,
            "status": "Aberto"
        }
        self.pedidos.append(pedido)

        self.tree.insert("", "end", values=(
            produto, horario, nome, endereco, f"R$ {valor:.2f}", pagamento, pedido["status"]
        ))
        self.atualizar_totais()
        self.historico_salvo = False
        self.btn_salvar.config(style="Unsaved.TButton")

        for entry in [self.entry_produto, self.entry_horario, self.entry_nome, self.entry_endereco, self.entry_valor]:
            entry.delete(0, tk.END)
        self.combo_pagamento.current(0)

    def salvar_historico(self):
        if not self.pedidos:
            messagebox.showwarning("Aviso", "Nenhum pedido para salvar.")
            return

        data_str = self.data_selecionada.strftime("%Y-%m-%d")
        nome_arquivo = f"historico_vendas_{data_str}.txt"
        caminho_arquivo = os.path.join(self.historico_dir, nome_arquivo)

        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(f"Histórico de Vendas Brazza - {data_str}\n\n")
                for p in self.pedidos:
                    f.write(f"Produto: {p['produto']}\n")
                    f.write(f"Horário: {p['horario']}\n")
                    f.write(f"Nome / iFood: {p['nome']}\n")
                    f.write(f"Endereço: {p['endereco']}\n")
                    f.write(f"Valor: R$ {p['valor']:.2f}\n")
                    f.write(f"Pagamento: {p['pagamento']}\n")
                    f.write(f"Status: {p.get('status', 'Aberto')}\n")
                    f.write("-" * 40 + "\n")
                f.write(f"\nTotal vendido no dia: R$ {self.total_vendido:.2f}\n")
            messagebox.showinfo("Sucesso", f"Histórico salvo em:\n{caminho_arquivo}")
            self.historico_salvo = True
            self.btn_salvar.config(style="TButton")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}")

    def carregar_pedidos(self, event=None):
        self.pedidos.clear()
        self.tree.delete(*self.tree.get_children())
        self.data_selecionada = self.calendario.get_date()
        data_str = self.data_selecionada.strftime("%Y-%m-%d")
        nome_arquivo = os.path.join(self.historico_dir, f"historico_vendas_{data_str}.txt")

        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                bloco = []
                for linha in f:
                    linha = linha.strip()
                    if linha.startswith("Total vendido no dia:"):
                        break
                    if not linha:
                        continue
                    if linha == "-" * 40:
                        pedido = self._parse_bloco(bloco)
                        if pedido:
                            self.pedidos.append(pedido)
                            self.tree.insert("", "end", values=(
                                pedido["produto"],
                                pedido["horario"],
                                pedido["nome"],
                                pedido["endereco"],
                                f"R$ {pedido['valor']:.2f}",
                                pedido.get("pagamento", ""),
                                pedido.get("status", "Aberto")
                            ))
                        bloco = []
                    else:
                        bloco.append(linha)
        self.atualizar_totais()
        self.historico_salvo = True
        self.btn_salvar.config(style="TButton")

    def _parse_bloco(self, bloco):
        try:
            produto = next((l.split(": ", 1)[1] for l in bloco if l.startswith("Produto:")), "")
            horario = next((l.split(": ", 1)[1] for l in bloco if l.startswith("Horário:")), "")
            nome = next((l.split(": ", 1)[1] for l in bloco if l.startswith("Nome / iFood:")), "")
            endereco = next((l.split(": ", 1)[1] for l in bloco if l.startswith("Endereço:")), "")
            valor_str = next((l.split("R$ ")[1] for l in bloco if l.startswith("Valor:")), "0")
            valor = float(valor_str.replace(",", "."))
            pagamento = next((l.split(": ", 1)[1] for l in bloco if l.startswith("Pagamento:")), "Não informado")
            status = next((l.split(": ", 1)[1] for l in bloco if l.startswith("Status:")), "Aberto")
            return {
                "produto": produto,
                "horario": horario,
                "nome": nome,
                "endereco": endereco,
                "valor": valor,
                "pagamento": pagamento,
                "status": status
            }
        except Exception as e:
            print("Erro ao ler bloco:", bloco, "\nErro:", e)
            return None

    def atualizar_totais(self):
        # Somar só pedidos "abertos" e "finalizados"? Para não afetar total, vamos somar todos, ok?
        self.total_vendido = sum(p["valor"] for p in self.pedidos)
        self.totais_por_pagamento.clear()
        for p in self.pedidos:
            forma = p["pagamento"]
            self.totais_por_pagamento[forma] = self.totais_por_pagamento.get(forma, 0.0) + p["valor"]
        self.atualizar_total()

    def atualizar_total(self, event=None):
        tipo = self.combo_filtro_total.get()
        if tipo == "Todos":
            self.label_total.config(text=f"Total vendido no dia: R$ {self.total_vendido:.2f}")
        else:
            valor = self.totais_por_pagamento.get(tipo, 0.0)
            self.label_total.config(text=f"Total vendido no {tipo.lower()}: R$ {valor:.2f}")

    def confirmar_saida(self):
        if not self.historico_salvo:
            if not messagebox.askyesno("Sair sem salvar?", "Você não salvou o histórico de hoje. Deseja sair mesmo assim?"):
                return
        self.root.destroy()

    def _get_pedido_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um pedido na lista.")
            return None, None
        item_id = selecionado[0]
        index = self.tree.index(item_id)
        return item_id, index

    def editar_pedido(self):
        item_id, index = self._get_pedido_selecionado()
        if item_id is None:
            return
        
        pedido = self.pedidos[index]

        def salvar_edicao():
            produto = entry_produto.get().strip()
            horario = entry_horario.get().strip()
            nome = entry_nome.get().strip()
            endereco = entry_endereco.get().strip()
            valor_texto = entry_valor.get().strip()
            pagamento = combo_pagamento.get()
            status = combo_status.get()

            if not produto or not horario or not nome or not endereco or not valor_texto:
                messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
                return

            try:
                valor = float(valor_texto.replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido. Use apenas números.")
                return

            # Atualizar o pedido
            pedido.update({
                "produto": produto,
                "horario": horario,
                "nome": nome,
                "endereco": endereco,
                "valor": valor,
                "pagamento": pagamento,
                "status": status
            })

            self.tree.item(item_id, values=(
                produto, horario, nome, endereco, f"R$ {valor:.2f}", pagamento, status
            ))
            self.atualizar_totais()
            self.historico_salvo = False
            self.btn_salvar.config(style="Unsaved.TButton")
            janela_editar.destroy()

        janela_editar = tk.Toplevel(self.root)
        janela_editar.title("Editar Pedido")

        ttk.Label(janela_editar, text="Produto:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_produto = ttk.Entry(janela_editar, width=30)
        entry_produto.grid(row=0, column=1)
        entry_produto.insert(0, pedido["produto"])

        ttk.Label(janela_editar, text="Horário:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entry_horario = ttk.Entry(janela_editar, width=30)
        entry_horario.grid(row=1, column=1)
        entry_horario.insert(0, pedido["horario"])

        ttk.Label(janela_editar, text="Nome / iFood:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        entry_nome = ttk.Entry(janela_editar, width=30)
        entry_nome.grid(row=2, column=1)
        entry_nome.insert(0, pedido["nome"])

        ttk.Label(janela_editar, text="Endereço:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        entry_endereco = ttk.Entry(janela_editar, width=30)
        entry_endereco.grid(row=3, column=1)
        entry_endereco.insert(0, pedido["endereco"])

        ttk.Label(janela_editar, text="Valor (R$):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        entry_valor = ttk.Entry(janela_editar, width=20)
        entry_valor.grid(row=4, column=1)
        entry_valor.insert(0, f"{pedido['valor']:.2f}")

        ttk.Label(janela_editar, text="Forma de pagamento:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        combo_pagamento = ttk.Combobox(janela_editar, values=[
            "Pago para a loja",
            "Pago pelo iFood",
            "Débito",
            "Crédito"
        ], state="readonly", width=18)
        combo_pagamento.grid(row=5, column=1)
        try:
            idx = combo_pagamento["values"].index(pedido["pagamento"])
        except ValueError:
            idx = 0
        combo_pagamento.current(idx)

        ttk.Label(janela_editar, text="Status:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        combo_status = ttk.Combobox(janela_editar, values=["Aberto", "Finalizado"], state="readonly", width=18)
        combo_status.grid(row=6, column=1)
        combo_status.set(pedido.get("status", "Aberto"))

        btn_salvar = ttk.Button(janela_editar, text="Salvar", command=salvar_edicao)
        btn_salvar.grid(row=7, column=0, columnspan=2, pady=10)

    def excluir_pedido(self):
        item_id, index = self._get_pedido_selecionado()
        if item_id is None:
            return
        if messagebox.askyesno("Confirmar exclusão", "Deseja realmente excluir o pedido selecionado?"):
            self.tree.delete(item_id)
            del self.pedidos[index]
            self.atualizar_totais()
            self.historico_salvo = False
            self.btn_salvar.config(style="Unsaved.TButton")

    def finalizar_pedido(self):
        item_id, index = self._get_pedido_selecionado()
        if item_id is None:
            return
        pedido = self.pedidos[index]
        if pedido.get("status") == "Finalizado":
            messagebox.showinfo("Informação", "Pedido já está finalizado.")
            return
        pedido["status"] = "Finalizado"
        self.tree.item(item_id, values=(
            pedido["produto"],
            pedido["horario"],
            pedido["nome"],
            pedido["endereco"],
            f"R$ {pedido['valor']:.2f}",
            pedido["pagamento"],
            pedido["status"]
        ))
        self.historico_salvo = False
        self.btn_salvar.config(style="Unsaved.TButton")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    style = ttk.Style()
    style.configure("Unsaved.TButton", foreground="red")
    app = PedidoApp(root)
    root.mainloop()
