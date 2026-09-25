"""Monta Aí com interface gráfica (Tkinter, já vem com o Python).

Uso:  python app.py
"""

import tkinter as tk
from tkinter import font as tkfont

from monta_ai.base_conhecimento import REGRAS
from monta_ai.catalogo import formatar_valor
from monta_ai.sistema import perguntas_aplicaveis, recomendar

FUNDO = "#F4F6FB"
CARTAO = "#FFFFFF"
PRIMARIA = "#4F46E5"
PRIMARIA_ESCURA = "#3730A3"
TEXTO = "#1F2937"
SUAVE = "#6B7280"
BORDA = "#E5E7EB"
ALERTA_FUNDO = "#FEF3C7"
ALERTA_TEXTO = "#92400E"


def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Botao(tk.Label):
    """Botão plano com cor, feito com Label para ter a mesma aparência em todo Windows."""

    def __init__(self, pai, texto, comando, primario=True, **kw):
        cor, cor_texto = (PRIMARIA, "white") if primario else (CARTAO, PRIMARIA)
        super().__init__(pai, text=texto, bg=cor, fg=cor_texto, cursor="hand2",
                         padx=18, pady=8, font=("Segoe UI", 10, "bold"),
                         highlightthickness=1, highlightbackground=PRIMARIA, **kw)
        self._cor = cor
        self.bind("<Button-1>", lambda _: comando())
        self.bind("<Enter>", lambda _: self.config(bg=PRIMARIA_ESCURA if primario else "#EEF2FF"))
        self.bind("<Leave>", lambda _: self.config(bg=self._cor))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monta Aí: recomendação de computadores")
        self.geometry("760x640")
        self.minsize(640, 540)
        self.configure(bg=FUNDO)
        tkfont.nametofont("TkDefaultFont").configure(family="Segoe UI", size=10)
        self.respostas = {}
        self.historico = []  # perguntas já respondidas, para o botão Voltar
        self.conteudo = None
        self.tela_inicial()

    # ------------------------------------------------------------------
    def limpar(self):
        if self.conteudo is not None:
            self.conteudo.destroy()
        self.conteudo = tk.Frame(self, bg=FUNDO)
        self.conteudo.pack(fill="both", expand=True, padx=32, pady=24)
        return self.conteudo

    def cabecalho(self, pai, titulo, subtitulo=""):
        tk.Label(pai, text="🖥  MONTA AÍ", bg=FUNDO, fg=PRIMARIA,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(pai, text=titulo, bg=FUNDO, fg=TEXTO, font=("Segoe UI", 18, "bold"),
                 wraplength=680, justify="left").pack(anchor="w", pady=(8, 0))
        if subtitulo:
            tk.Label(pai, text=subtitulo, bg=FUNDO, fg=SUAVE, font=("Segoe UI", 10),
                     wraplength=680, justify="left").pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------------
    def tela_inicial(self):
        pai = self.limpar()
        self.respostas, self.historico = {}, []
        self.cabecalho(pai, "Descubra o computador ideal para você",
                       "Responda algumas perguntas rápidas. O sistema especialista analisa "
                       f"suas respostas com {len(REGRAS)} regras e indica a configuração, os alertas e "
                       "o porquê de cada escolha.")
        caixa = tk.Frame(pai, bg=CARTAO, highlightthickness=1, highlightbackground=BORDA)
        caixa.pack(fill="x", pady=24)
        for icone, texto in [("💰", "Seu orçamento"), ("🎮", "Para que você vai usar"),
                             ("🖥", "Resolução do monitor"), ("🔧", "Planos de upgrade")]:
            linha = tk.Frame(caixa, bg=CARTAO)
            linha.pack(fill="x", padx=18, pady=6)
            tk.Label(linha, text=icone, bg=CARTAO, font=("Segoe UI Emoji", 14)).pack(side="left")
            tk.Label(linha, text=texto, bg=CARTAO, fg=TEXTO, font=("Segoe UI", 11)).pack(side="left", padx=10)
        Botao(pai, "Começar  →", self.proxima_pergunta).pack(anchor="w")

    # ------------------------------------------------------------------
    def proxima_pergunta(self):
        pendentes = [p for p in perguntas_aplicaveis(self.respostas) if p.atributo not in self.respostas]
        if not pendentes:
            self.tela_resultado()
            return
        self.tela_pergunta(pendentes[0])

    def voltar(self):
        if not self.historico:
            self.tela_inicial()
            return
        ultimo = self.historico.pop()
        # Apaga a resposta e as que dependiam dela.
        self.respostas.pop(ultimo, None)
        if ultimo == "uso":
            self.respostas.pop("tipo_jogo", None)
        self.proxima_pergunta()

    def tela_pergunta(self, pergunta):
        pai = self.limpar()
        total = len(list(perguntas_aplicaveis(self.respostas)))
        numero = len(self.historico) + 1
        self.cabecalho(pai, pergunta.texto, f"Pergunta {numero} de {total}")

        barra = tk.Frame(pai, bg=BORDA, height=6)
        barra.pack(fill="x", pady=(12, 18))
        barra.update_idletasks()
        tk.Frame(barra, bg=PRIMARIA, height=6).place(relwidth=numero / total, relheight=1)

        erro = tk.Label(pai, text="", bg=FUNDO, fg="#B91C1C")

        if pergunta.opcoes:
            escolha = tk.StringVar(value=self.respostas.get(pergunta.atributo, ""))
            for valor, rotulo in pergunta.opcoes:
                tk.Radiobutton(pai, text=rotulo, value=valor, variable=escolha, anchor="w",
                               bg=CARTAO, fg=TEXTO, selectcolor="#EEF2FF", indicatoron=False,
                               font=("Segoe UI", 11), padx=16, pady=10, relief="flat", bd=0, offrelief="flat",
                               highlightthickness=1, highlightbackground=BORDA,
                               activebackground="#EEF2FF", cursor="hand2",
                               ).pack(fill="x", pady=4)
            obter = escolha.get
        else:
            campo = tk.Frame(pai, bg=CARTAO, highlightthickness=1, highlightbackground=BORDA)
            campo.pack(fill="x", pady=4)
            tk.Label(campo, text="R$", bg=CARTAO, fg=SUAVE, font=("Segoe UI", 14)).pack(side="left", padx=(14, 4))
            entrada = tk.Entry(campo, font=("Segoe UI", 16), relief="flat", bg=CARTAO)
            entrada.pack(side="left", fill="x", expand=True, pady=10)
            entrada.focus_set()

            def obter():
                bruto = entrada.get().strip().replace(".", "").replace(",", ".")
                try:
                    valor = float(bruto)
                except ValueError:
                    return ""
                return valor if valor > 0 else ""

        def avancar():
            valor = obter()
            if valor == "":
                erro.config(text="Responda para continuar.")
                return
            self.respostas[pergunta.atributo] = valor
            self.historico.append(pergunta.atributo)
            self.proxima_pergunta()

        erro.pack(anchor="w", pady=(6, 0))
        botoes = tk.Frame(pai, bg=FUNDO)
        botoes.pack(fill="x", pady=12)
        Botao(botoes, "←  Voltar", self.voltar, primario=False).pack(side="left")
        Botao(botoes, "Próximo  →", avancar).pack(side="right")
        self.bind("<Return>", lambda _: avancar())

    # ------------------------------------------------------------------
    def tela_resultado(self):
        self.unbind("<Return>")
        resultado = recomendar(self.respostas)
        pai = self.limpar()

        # Área com rolagem.
        tela = tk.Canvas(pai, bg=FUNDO, highlightthickness=0)
        rolagem = tk.Scrollbar(pai, orient="vertical", command=tela.yview)
        corpo = tk.Frame(tela, bg=FUNDO)
        corpo.bind("<Configure>", lambda _: tela.configure(scrollregion=tela.bbox("all")))
        janela = tela.create_window((0, 0), window=corpo, anchor="nw")
        tela.bind("<Configure>", lambda e: tela.itemconfig(janela, width=e.width))
        tela.configure(yscrollcommand=rolagem.set)
        tela.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")
        self.bind_all("<MouseWheel>", lambda e: tela.yview_scroll(-e.delta // 120, "units"))

        f = resultado.fatos
        self.cabecalho(corpo, "Sua configuração recomendada",
                       f"Perfil: {formatar_valor('perfil', f['perfil'])}   •   "
                       f"Orçamento {formatar_valor('faixa_orcamento', f['faixa_orcamento'])}")

        grade = tk.Frame(corpo, bg=FUNDO)
        grade.pack(fill="x", pady=(16, 0))
        grade.columnconfigure((0, 1), weight=1, uniform="c")
        for i, (fato, peca, nome, detalhe) in enumerate(resultado.pecas()):
            cartao = tk.Frame(grade, bg=CARTAO, highlightthickness=1, highlightbackground=BORDA)
            cartao.grid(row=i // 2, column=i % 2, sticky="nsew", padx=4, pady=4)
            tk.Label(cartao, text=peca.upper(), bg=CARTAO, fg=SUAVE,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
            tk.Label(cartao, text=nome, bg=CARTAO, fg=TEXTO, font=("Segoe UI", 11, "bold"),
                     wraplength=300, justify="left").pack(anchor="w", padx=12)
            if detalhe:
                tk.Label(cartao, text=detalhe, bg=CARTAO, fg=SUAVE, font=("Segoe UI", 9),
                         wraplength=300, justify="left").pack(anchor="w", padx=12)
            link = tk.Label(cartao, text="Por quê?", bg=CARTAO, fg=PRIMARIA, cursor="hand2",
                            font=("Segoe UI", 9, "underline"))
            link.pack(anchor="w", padx=12, pady=(4, 10))
            link.bind("<Button-1>", lambda _, fa=fato, t=f"Por que {peca.lower()}: {nome}?":
                      self.janela_explicacao(t, resultado.explicar(fa)))

        if resultado.alertas:
            tk.Label(corpo, text="Alertas", bg=FUNDO, fg=TEXTO,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(18, 4))
            for alerta in resultado.alertas:
                caixa = tk.Frame(corpo, bg=ALERTA_FUNDO)
                caixa.pack(fill="x", pady=3)
                tk.Label(caixa, text="⚠  " + alerta, bg=ALERTA_FUNDO, fg=ALERTA_TEXTO,
                         wraplength=640, justify="left").pack(side="left", anchor="w", padx=12, pady=8)
                link = tk.Label(caixa, text="Por quê?", bg=ALERTA_FUNDO, fg=ALERTA_TEXTO,
                                cursor="hand2", font=("Segoe UI", 9, "underline"))
                link.pack(side="right", padx=12)
                link.bind("<Button-1>", lambda _, a=alerta:
                          self.janela_explicacao("Por que este alerta?", resultado.explicar_alerta(a)))

        distribuicao = resultado.distribuicao_em_reais()
        if distribuicao:
            tk.Label(corpo, text=f"Como dividir {moeda(f['orcamento'])}", bg=FUNDO, fg=TEXTO,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(18, 4))
            tabela = tk.Frame(corpo, bg=CARTAO, highlightthickness=1, highlightbackground=BORDA)
            tabela.pack(fill="x")
            for peca, pct, valor in distribuicao:
                linha = tk.Frame(tabela, bg=CARTAO)
                linha.pack(fill="x", padx=12, pady=3)
                tk.Label(linha, text=peca, bg=CARTAO, fg=TEXTO, width=16, anchor="w").pack(side="left")
                fundo_barra = tk.Frame(linha, bg=BORDA, height=10, width=240)
                fundo_barra.pack(side="left", padx=8)
                fundo_barra.pack_propagate(False)
                tk.Frame(fundo_barra, bg=PRIMARIA, height=10, width=int(240 * pct / 40)
                         if pct < 40 else 240).pack(side="left")
                tk.Label(linha, text=f"{pct}%  ≈ {moeda(valor)}", bg=CARTAO, fg=SUAVE).pack(side="left")

        botoes = tk.Frame(corpo, bg=FUNDO)
        botoes.pack(fill="x", pady=18)
        Botao(botoes, "Ver regras disparadas", lambda: self.janela_explicacao(
            "Regras disparadas (encadeamento para frente)",
            [f"{rid}: {desc}" for rid, desc in resultado.rastro()]), primario=False).pack(side="left")
        Botao(botoes, "Nova consulta", self.nova_consulta).pack(side="right")

    def nova_consulta(self):
        self.unbind_all("<MouseWheel>")
        self.tela_inicial()

    # ------------------------------------------------------------------
    def janela_explicacao(self, titulo, linhas):
        janela = tk.Toplevel(self, bg=CARTAO)
        janela.title("Explicação")
        janela.geometry("680x420")
        janela.transient(self)
        tk.Label(janela, text=titulo, bg=CARTAO, fg=TEXTO, font=("Segoe UI", 12, "bold"),
                 wraplength=640, justify="left").pack(anchor="w", padx=16, pady=(14, 6))
        texto = tk.Text(janela, wrap="word", relief="flat", bg=CARTAO, fg=TEXTO,
                        font=("Segoe UI", 10), padx=16, pady=4)
        texto.tag_configure("regra", font=("Segoe UI", 10, "bold"), foreground=PRIMARIA)
        for linha in linhas:
            if linha.startswith("      "):
                texto.insert("end", linha.strip() + "\n\n")
            else:
                texto.insert("end", linha + "\n", "regra")
        texto.configure(state="disabled")
        texto.pack(fill="both", expand=True)
        Botao(janela, "Fechar", janela.destroy).pack(pady=10)


if __name__ == "__main__":
    App().mainloop()
