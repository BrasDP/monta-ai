"""Junta motor, base de conhecimento e catálogo numa interface simples,
usada tanto pela versão de terminal quanto pela versão com janelas."""

from .base_conhecimento import REGRAS
from .catalogo import (ATRIBUTOS, NIVEIS_ARMAZ, NIVEIS_CPU, NIVEIS_GPU, NIVEIS_RAM,
                       PERGUNTAS, formatar_valor)
from .motor import ALERTAS, MotorInferencia

SIMBOLOS = {"==": "=", "!=": "≠", "<": "<", "<=": "≤", ">": ">", ">=": "≥",
            "in": "∈", "not in": "∉"}


def _texto_valor(atributo, valor):
    if isinstance(valor, str) and valor.startswith("?"):
        return ATRIBUTOS.get(valor[1:], valor[1:])
    if isinstance(valor, tuple) and valor and valor[0] == "min":
        return f"menor entre ({_texto_valor(atributo, valor[1])}) e ({_texto_valor(atributo, valor[2])})"
    if isinstance(valor, tuple) and valor and valor[0] == "soma":
        b = valor[2]
        if isinstance(b, int) and b < 0:
            return f"{_texto_valor(atributo, valor[1])} − {-b}"
        return f"{_texto_valor(atributo, valor[1])} + {_texto_valor(atributo, b)}"
    if isinstance(valor, tuple) and valor and isinstance(valor[0], str):
        return "{" + ", ".join(formatar_valor("perfil", v) for v in valor) + "}"
    if isinstance(valor, tuple):
        return ", ".join(f"{peca} {pct}%" for peca, pct in valor)
    if isinstance(valor, int) and atributo not in ("orcamento",):
        return str(valor)
    return formatar_valor(atributo, valor)


def condicao_texto(condicao):
    atributo, operador, valor = condicao
    nome = ATRIBUTOS.get(atributo, atributo)
    if operador == "!=" and valor is None:
        return f"há um valor para {nome}"
    if atributo == "orcamento":
        return f"{nome} {SIMBOLOS[operador]} R$ {valor:,}".replace(",", ".")
    return f"{nome} {SIMBOLOS[operador]} {_texto_valor(atributo, valor)}"


def conclusao_texto(conclusao):
    atributo, valor = conclusao
    if atributo == ALERTAS:
        return f'alerta: "{valor}"'
    return f"{ATRIBUTOS.get(atributo, atributo)} = {_texto_valor(atributo, valor)}"


def regra_texto(regra):
    """Regra no formato SE ... ENTÃO ..., gerada a partir da própria regra."""
    se = " E ".join(condicao_texto(c) for c in regra.condicoes)
    entao = " E ".join(conclusao_texto(c) for c in regra.conclusoes)
    return f"SE {se} ENTÃO {entao}"


class Resultado:
    def __init__(self, motor, respostas):
        self.motor = motor
        self.respostas = respostas
        self.fatos = motor.fatos

    @property
    def completa(self):
        return self.fatos.get("recomendacao") == "completa"

    @property
    def alertas(self):
        return list(self.fatos.get(ALERTAS, []))

    def pecas(self):
        """Lista de (fato, nome da peça, recomendação, detalhe)."""
        f = self.fatos
        itens = []
        if "cpu_rec" in f:
            itens.append(("cpu_rec", "Processador", *NIVEIS_CPU[f["cpu_rec"]]))
        if "gpu_rec" in f:
            nome, detalhe = NIVEIS_GPU[f["gpu_rec"]]
            if "gpu_marca" in f and f["gpu_rec"] >= 1:
                detalhe += f" Marca: {f['gpu_marca']}."
            itens.append(("gpu_rec", "Placa de vídeo", nome, detalhe))
        if "ram_rec" in f:
            itens.append(("ram_rec", "Memória RAM", *NIVEIS_RAM[f["ram_rec"]]))
        if "armaz_rec" in f:
            itens.append(("armaz_rec", "Armazenamento", *NIVEIS_ARMAZ[f["armaz_rec"]]))
        if "placa_mae" in f:
            itens.append(("placa_mae", "Placa-mãe", f["placa_mae"], ""))
        if "fonte" in f:
            itens.append(("fonte", "Fonte", f["fonte"], ""))
        return itens

    def distribuicao_em_reais(self):
        dist = self.fatos.get("distribuicao")
        if not dist:
            return []
        total = self.fatos["orcamento"]
        return [(peca, pct, total * pct / 100) for peca, pct in dist]

    def explicar(self, fato):
        """Explicação do porquê de um fato: a cadeia de regras que levou a ele."""
        return self._explicar_cadeia(self.motor.cadeia(fato))

    def explicar_alerta(self, texto):
        return self._explicar_cadeia(self.motor.cadeia_alerta(texto))

    def _explicar_cadeia(self, cadeia):
        linhas = []
        for disparo in cadeia:
            regra = disparo.regra
            usados = ", ".join(f"{ATRIBUTOS.get(k, k)} = {formatar_valor(k, v)}"
                               for k, v in disparo.fatos_usados.items())
            gerados = ", ".join(
                f"{ATRIBUTOS.get(k, k)} = {formatar_valor(k, v)}"
                for k, v in disparo.fatos_gerados.items() if k != ALERTAS)
            linhas.append(f"{regra.id}: {regra.descricao}")
            linhas.append(f"      porque {usados}" + (f"  →  {gerados}" if gerados else ""))
        return linhas

    def rastro(self):
        """Todas as regras disparadas, na ordem em que o motor as aplicou."""
        return [(d.regra.id, d.regra.descricao) for d in self.motor.historico]


def perguntas_aplicaveis(respostas):
    """Perguntas que ainda devem ser feitas, considerando as respostas dadas."""
    for pergunta in PERGUNTAS:
        if pergunta.mostrar_se:
            atributo, valor = pergunta.mostrar_se
            if respostas.get(atributo) != valor:
                continue
        yield pergunta


def recomendar(respostas):
    motor = MotorInferencia(REGRAS)
    motor.executar(respostas)
    return Resultado(motor, respostas)
