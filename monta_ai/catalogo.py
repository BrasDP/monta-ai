"""Perguntas feitas ao usuário e textos usados para exibir os fatos."""

from dataclasses import dataclass

NIVEIS_GPU = {
    0: ("Vídeo integrado", "Usa o vídeo do próprio processador. Suficiente para estudo, "
                           "escritório, vídeos e programação."),
    1: ("Placa de vídeo de entrada", "4 a 8 GB de memória de vídeo. Jogos leves e "
                                     "competitivos em 1080p."),
    2: ("Placa de vídeo intermediária", "8 GB de memória de vídeo. Jogos atuais em 1080p no "
                                        "alto e edição de vídeo."),
    3: ("Placa de vídeo intermediária-alta", "12 a 16 GB de memória de vídeo. Jogos pesados em "
                                             "1440p, edição e IA."),
    4: ("Placa de vídeo alta (topo de linha)", "16 GB ou mais de memória de vídeo. 4K e "
                                               "cargas profissionais."),
}

NIVEIS_CPU = {
    1: ("Processador de entrada", "4 a 6 núcleos. Tarefas do dia a dia."),
    2: ("Processador intermediário", "6 núcleos / 12 threads. Jogos e programação."),
    3: ("Processador intermediário-alto", "8 núcleos / 16 threads. Edição, lives e IA."),
    4: ("Processador alto", "12 núcleos ou mais. Cargas profissionais pesadas."),
}

NIVEIS_RAM = {
    1: ("8 GB de RAM", "2 pentes de 4 GB (dual channel)."),
    2: ("16 GB de RAM", "2 pentes de 8 GB (dual channel)."),
    3: ("32 GB de RAM", "2 pentes de 16 GB (dual channel)."),
    4: ("64 GB de RAM", "2 pentes de 32 GB (dual channel)."),
}

NIVEIS_ARMAZ = {
    1: ("SSD de 512 GB", "SATA ou NVMe. Sistema e programas abrem rápido."),
    2: ("SSD NVMe de 1 TB", "Espaço para jogos e projetos."),
    3: ("SSD NVMe de 2 TB", "Espaço para arquivos de vídeo pesados."),
}

FAIXAS = {1: "baixo (até R$ 3 mil)", 2: "médio (R$ 3 a 5 mil)",
          3: "alto (R$ 5 a 8 mil)", 4: "premium (acima de R$ 8 mil)"}

PERFIS = {
    "basico": "Básico",
    "desenvolvedor": "Desenvolvedor",
    "gamer_casual": "Gamer casual",
    "gamer_entusiasta": "Gamer entusiasta",
    "criador_conteudo": "Criador de conteúdo",
    "computacao_intensiva": "Computação intensiva",
}

# Nome legível de cada atributo, usado na explicação e no relatório.
ATRIBUTOS = {
    "orcamento": "orçamento",
    "uso": "uso principal",
    "tipo_jogo": "tipo de jogo",
    "resolucao": "resolução do monitor",
    "streaming": "faz lives ou grava a tela",
    "formato": "formato",
    "upgrade": "pretende fazer upgrade",
    "faixa_orcamento": "faixa de orçamento",
    "perfil": "perfil",
    "gpu_base": "nível de placa de vídeo do perfil",
    "cpu_base": "nível de processador do perfil",
    "bonus_resolucao": "ajuste pela resolução",
    "bonus_streaming": "ajuste por streaming",
    "gpu_req": "placa de vídeo necessária",
    "cpu_req": "processador necessário",
    "ram_req": "memória necessária",
    "armaz_req": "armazenamento necessário",
    "gpu_teto": "teto de placa de vídeo",
    "cpu_teto": "teto de processador",
    "ram_teto": "teto de memória",
    "gpu_rec": "placa de vídeo recomendada",
    "cpu_rec": "processador recomendado",
    "ram_rec": "memória recomendada",
    "armaz_rec": "armazenamento recomendado",
    "gpu_marca": "marca da placa de vídeo",
    "fonte": "fonte",
    "placa_mae": "placa-mãe",
    "distribuicao": "distribuição do orçamento",
    "alertas": "alerta",
    "recomendacao": "recomendação",
}


@dataclass
class Pergunta:
    atributo: str
    texto: str
    opcoes: list          # lista de (valor, rótulo); vazia = resposta numérica
    mostrar_se: tuple = None  # (atributo, valor): só pergunta se a condição valer


PERGUNTAS = [
    Pergunta("orcamento", "Quanto você pretende gastar, em reais?", []),
    Pergunta("formato", "Você quer um desktop ou um notebook?",
             [("desktop", "Desktop (PC de mesa)"), ("notebook", "Notebook")]),
    Pergunta("uso", "Para que você vai usar o computador principalmente?",
             [("escritorio", "Estudo e escritório"), ("programacao", "Programação"),
              ("jogos", "Jogos"), ("edicao_video", "Edição de vídeo"),
              ("ia_dados", "IA e ciência de dados")]),
    Pergunta("tipo_jogo", "Que tipo de jogo você joga?",
             [("leves", "Leves / competitivos (LoL, Valorant, CS2, Minecraft)"),
              ("pesados", "Pesados / lançamentos (mundo aberto, gráficos no máximo)")],
             mostrar_se=("uso", "jogos")),
    Pergunta("resolucao", "Qual a resolução do monitor (ou da tela do notebook)?",
             [("1080p", "1080p (Full HD)"), ("1440p", "1440p (2K / Quad HD)"), ("4k", "4K")]),
    Pergunta("streaming", "Você vai fazer lives ou gravar a tela enquanto usa?",
             [("sim", "Sim"), ("nao", "Não")]),
    Pergunta("upgrade", "Pretende trocar ou adicionar peças no futuro?",
             [("sim", "Sim"), ("nao", "Não")]),
]


def rotulo_opcao(atributo, valor):
    for pergunta in PERGUNTAS:
        if pergunta.atributo == atributo:
            for v, rotulo in pergunta.opcoes:
                if v == valor:
                    return rotulo
    return None


def formatar_valor(atributo, valor):
    """Transforma o valor interno de um fato num texto legível."""
    if atributo == "orcamento":
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if atributo == "faixa_orcamento":
        return f"{valor} – {FAIXAS.get(valor, valor)}"
    if atributo == "perfil":
        return PERFIS.get(valor, valor)
    niveis = {"gpu": NIVEIS_GPU, "cpu": NIVEIS_CPU, "ram": NIVEIS_RAM, "armaz": NIVEIS_ARMAZ}
    prefixo = atributo.split("_")[0]
    if prefixo in niveis and atributo.endswith(("_base", "_req", "_teto", "_rec")):
        nome = niveis[prefixo].get(max(0, valor))
        return f"{valor} ({nome[0]})" if nome else str(valor)
    if atributo == "distribuicao":
        return ", ".join(f"{peca} {pct}%" for peca, pct in valor)
    rotulo = rotulo_opcao(atributo, valor)
    return rotulo or str(valor)
