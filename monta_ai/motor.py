"""Motor de inferência com encadeamento para frente (forward chaining).

O motor não sabe nada sobre hardware: ele só recebe uma lista de regras
(a base de conhecimento) e um conjunto de fatos iniciais (as respostas do
usuário) e vai disparando regras até que nenhuma nova regra possa ser
aplicada. Cada disparo fica registrado para que o sistema consiga explicar
como chegou em cada conclusão.
"""

from dataclasses import dataclass, field

# Atributo especial que acumula uma lista de avisos em vez de um valor único.
ALERTAS = "alertas"

OPERADORES = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
}


@dataclass
class Regra:
    """Uma regra de produção no formato SE <condições> ENTÃO <conclusões>.

    condicoes: lista de (atributo, operador, valor). O valor pode ser uma
        referência a outro fato, escrita como "?nome_do_fato".
    conclusoes: lista de (atributo, valor). O valor pode ser uma referência
        "?fato" ou uma expressão ("min", a, b) / ("soma", a, b).
    prioridade: usada para resolver conflitos quando mais de uma regra
        pode disparar ao mesmo tempo (a maior dispara primeiro).
    """

    id: str
    grupo: str
    descricao: str
    condicoes: list
    conclusoes: list
    prioridade: int = 0


@dataclass
class Disparo:
    """Registro de uma regra que foi disparada durante a inferência."""

    regra: Regra
    fatos_usados: dict
    fatos_gerados: dict = field(default_factory=dict)


class MotorInferencia:
    def __init__(self, regras):
        self.regras = list(regras)
        self.fatos = {}
        self.historico = []
        # Guarda qual disparo produziu cada fato, para montar a explicação.
        self._origem = {}

    # ------------------------------------------------------------------
    # Avaliação de condições e conclusões
    # ------------------------------------------------------------------
    def _resolver(self, valor):
        """Troca referências "?fato" pelo valor do fato e calcula expressões."""
        if isinstance(valor, str) and valor.startswith("?"):
            return self.fatos[valor[1:]]
        if isinstance(valor, tuple) and valor and valor[0] in ("min", "soma"):
            a, b = (self._resolver(v) for v in valor[1:])
            return min(a, b) if valor[0] == "min" else a + b
        return valor

    def _referencias(self, valor):
        """Lista os fatos que um valor usa (para saber se já estão definidos)."""
        if isinstance(valor, str) and valor.startswith("?"):
            return [valor[1:]]
        if isinstance(valor, tuple) and valor and valor[0] in ("min", "soma"):
            return [r for v in valor[1:] for r in self._referencias(v)]
        return []

    def _satisfeita(self, regra):
        for atributo, operador, valor in regra.condicoes:
            necessarios = [atributo] + self._referencias(valor)
            if any(n not in self.fatos for n in necessarios):
                return False
            if not OPERADORES[operador](self.fatos[atributo], self._resolver(valor)):
                return False
        # Todas as conclusões precisam conseguir ser calculadas.
        for _, valor in regra.conclusoes:
            if any(r not in self.fatos for r in self._referencias(valor)):
                return False
        return True

    def _acrescenta_algo(self, regra):
        """Evita disparar uma regra cujas conclusões já são todas conhecidas."""
        return any(atr == ALERTAS or atr not in self.fatos for atr, _ in regra.conclusoes)

    # ------------------------------------------------------------------
    # Ciclo de inferência
    # ------------------------------------------------------------------
    def conjunto_conflito(self, ja_disparadas):
        return [
            r for r in self.regras
            if r.id not in ja_disparadas and self._satisfeita(r) and self._acrescenta_algo(r)
        ]

    def executar(self, fatos_iniciais):
        """Roda o encadeamento para frente e devolve a base de fatos final."""
        self.fatos = dict(fatos_iniciais)
        self.fatos.setdefault(ALERTAS, [])
        self.historico = []
        self._origem = {}
        disparadas = set()

        while True:
            candidatas = self.conjunto_conflito(disparadas)
            if not candidatas:
                break
            # Resolução de conflito: maior prioridade; empate -> ordem na base.
            regra = max(candidatas, key=lambda r: (r.prioridade, -self.regras.index(r)))
            self._disparar(regra)
            disparadas.add(regra.id)

        return self.fatos

    def _disparar(self, regra):
        usados = {}
        for atributo, _, valor in regra.condicoes:
            for nome in [atributo] + self._referencias(valor):
                usados[nome] = self.fatos[nome]
        disparo = Disparo(regra, usados)

        for atributo, valor in regra.conclusoes:
            if atributo == ALERTAS:
                self.fatos[ALERTAS].append(valor)
                disparo.fatos_gerados.setdefault(ALERTAS, []).append(valor)
                self._origem.setdefault(("alerta", valor), disparo)
                continue
            if atributo in self.fatos:
                # Fatos não são sobrescritos: quem disparou antes (maior prioridade) vence.
                continue
            self.fatos[atributo] = self._resolver(valor)
            disparo.fatos_gerados[atributo] = self.fatos[atributo]
            self._origem[atributo] = disparo

        self.historico.append(disparo)

    # ------------------------------------------------------------------
    # Módulo de explicação
    # ------------------------------------------------------------------
    def origem(self, fato):
        """Disparo que gerou o fato, ou None se o fato veio do usuário."""
        return self._origem.get(fato)

    def origem_alerta(self, texto):
        return self._origem.get(("alerta", texto))

    def cadeia(self, fato):
        """Lista de disparos (do mais básico ao final) que levaram até o fato."""
        visitados, ordem = set(), []

        def visitar(nome):
            disparo = self._origem.get(nome)
            if disparo is None or id(disparo) in visitados:
                return
            visitados.add(id(disparo))
            for usado in disparo.fatos_usados:
                visitar(usado)
            ordem.append(disparo)

        visitar(fato)
        return ordem

    def cadeia_alerta(self, texto):
        disparo = self.origem_alerta(texto)
        if disparo is None:
            return []
        anteriores = []
        for usado in disparo.fatos_usados:
            for d in self.cadeia(usado):
                if d not in anteriores:
                    anteriores.append(d)
        return anteriores + [disparo]
