# =============================================================================
#  MONTA AÍ - Sistema Especialista que recomenda computadores
#  Disciplina: Programação de Sistemas Especialistas - UVA (Campus Tijuca)
#  Grupo: Lucas Pires da Costa, Ruan da Silva Marques e Lucas Santos Garcia
#
#  Como rodar:  python monta_ai.py
# =============================================================================
#
#  MINIMUNDO
#  ---------
#  Muita gente precisa comprar um computador e não sabe quais peças escolher.
#  Normalmente essa pessoa pede ajuda a um amigo que entende do assunto: um
#  especialista. O Monta Aí faz o papel desse especialista.
#
#  O usuário responde 3 perguntas no terminal:
#    1. Para que vai usar o computador (estudo, programação, jogos ou edição de vídeo)
#    2. Quanto pode gastar (orçamento baixo, médio ou alto)
#    3. Se quer um desktop ou um notebook
#
#  Com essas respostas, o sistema aplica as regras da base de conhecimento e
#  recomenda: processador, memória RAM, placa de vídeo e armazenamento, além de
#  avisos e dicas. No final, mostra quais regras usou para chegar à resposta.
#
#  Partes de um sistema especialista neste arquivo:
#    - Base de conhecimento  -> lista REGRAS (as regras SE ... ENTÃO ...)
#    - Base de fatos         -> dicionário "fatos" (respostas + o que foi deduzido)
#    - Motor de inferência   -> função motor_de_inferencia (encadeamento para frente)
#    - Explicação            -> função mostrar_explicacao (mostra as regras usadas)
#    - Interface             -> funções que fazem as perguntas e mostram o resultado
# =============================================================================


# -----------------------------------------------------------------------------
# 1. BASE DE CONHECIMENTO
# -----------------------------------------------------------------------------
# Cada regra tem:
#   "id"    -> o nome da regra (R1, R2, ...)
#   "se"    -> as condições: TODAS precisam ser verdadeiras para a regra valer
#   "entao" -> os novos fatos que a regra acrescenta na base de fatos
#
# Exemplo: a regra R3 diz "SE uso = jogos ENTÃO perfil = gamer".
# Repare que algumas regras usam fatos criados por outras regras (por exemplo,
# a R7 usa o "perfil" criado pela R3). Isso é o ENCADEAMENTO de regras.

REGRAS = [
    # --- Grupo 1: descobrir o perfil do usuário pelo uso ---
    {"id": "R1", "se": {"uso": "estudo"},          "entao": {"perfil": "básico"}},
    {"id": "R2", "se": {"uso": "programação"},     "entao": {"perfil": "desenvolvedor"}},
    {"id": "R3", "se": {"uso": "jogos"},           "entao": {"perfil": "gamer"}},
    {"id": "R4", "se": {"uso": "edição de vídeo"}, "entao": {"perfil": "criador de conteúdo"}},

    # --- Grupo 2: peças que cada perfil precisa ---
    {"id": "R5", "se": {"perfil": "básico"},
     "entao": {"processador": "de entrada (4 núcleos)", "memoria": "8 GB", "video": "integrado"}},
    {"id": "R6", "se": {"perfil": "desenvolvedor"},
     "entao": {"processador": "intermediário (6 núcleos)", "memoria": "16 GB", "video": "integrado"}},
    {"id": "R7", "se": {"perfil": "gamer"},
     "entao": {"processador": "intermediário (6 núcleos)", "memoria": "16 GB", "video": "dedicado"}},
    {"id": "R8", "se": {"perfil": "criador de conteúdo"},
     "entao": {"processador": "avançado (8 núcleos ou mais)", "memoria": "32 GB", "video": "dedicado"}},

    # --- Grupo 3: armazenamento de acordo com o orçamento ---
    {"id": "R9",  "se": {"orcamento": "baixo"}, "entao": {"armazenamento": "SSD de 256 GB"}},
    {"id": "R10", "se": {"orcamento": "médio"}, "entao": {"armazenamento": "SSD de 512 GB"}},
    {"id": "R11", "se": {"orcamento": "alto"},  "entao": {"armazenamento": "SSD de 1 TB"}},

    # --- Grupo 4: placa de vídeo (depende do tipo de vídeo E do orçamento) ---
    {"id": "R12", "se": {"video": "integrado"},
     "entao": {"placa_de_video": "não precisa (usa o vídeo do processador)"}},
    {"id": "R13", "se": {"video": "dedicado", "orcamento": "baixo"},
     "entao": {"placa_de_video": "placa de entrada"}},
    {"id": "R14", "se": {"video": "dedicado", "orcamento": "médio"},
     "entao": {"placa_de_video": "placa intermediária"}},
    {"id": "R15", "se": {"video": "dedicado", "orcamento": "alto"},
     "entao": {"placa_de_video": "placa avançada"}},

    # --- Grupo 5: avisos e dicas para o usuário ---
    {"id": "R16", "se": {"perfil": "gamer", "orcamento": "baixo"},
     "entao": {"aviso_orcamento": "Orçamento apertado para jogos: dá para jogar, mas com gráficos no mínimo."}},
    {"id": "R17", "se": {"perfil": "criador de conteúdo", "orcamento": "baixo"},
     "entao": {"aviso_orcamento": "Orçamento apertado para edição: os vídeos vão demorar para renderizar."}},
    {"id": "R18", "se": {"formato": "notebook", "video": "dedicado"},
     "entao": {"aviso_notebook": "Notebook com placa de vídeo esquenta: escolha um modelo com boa refrigeração."}},
    {"id": "R19", "se": {"formato": "notebook"},
     "entao": {"dica": "No notebook não dá para trocar processador nem placa: compre pensando no futuro."}},
    {"id": "R20", "se": {"formato": "desktop"},
     "entao": {"dica": "No desktop dá para trocar peças depois: comece simples e melhore aos poucos."}},
]


# -----------------------------------------------------------------------------
# 2. MOTOR DE INFERÊNCIA (encadeamento para frente)
# -----------------------------------------------------------------------------
# Ideia: partir dos fatos que o usuário informou e ir aplicando as regras até
# não sobrar nenhuma regra nova para aplicar.
#
# Passo a passo:
#   1. Percorre todas as regras da base de conhecimento.
#   2. Se TODAS as condições do "se" batem com a base de fatos, a regra "dispara":
#      os fatos do "entao" são acrescentados na base de fatos.
#   3. Cada regra dispara no máximo uma vez (guardamos quais já foram usadas).
#   4. Se alguma regra disparou, repete tudo, porque os fatos novos podem
#      ativar outras regras (é assim que acontece o encadeamento).
#   5. Quando uma volta inteira termina sem nenhuma regra nova, o motor para.

def condicoes_verdadeiras(regra, fatos):
    """Retorna True se TODAS as condições da regra estão na base de fatos."""
    for nome, valor in regra["se"].items():
        if fatos.get(nome) != valor:
            return False
    return True


def motor_de_inferencia(fatos):
    """Aplica as regras sobre os fatos e devolve a lista de regras usadas, na ordem."""
    regras_usadas = []
    alguma_regra_disparou = True

    while alguma_regra_disparou:          # repete enquanto surgirem fatos novos
        alguma_regra_disparou = False
        for regra in REGRAS:
            if regra["id"] in regras_usadas:
                continue                  # essa regra já foi usada, pula
            if condicoes_verdadeiras(regra, fatos):
                fatos.update(regra["entao"])      # acrescenta os novos fatos
                regras_usadas.append(regra["id"])  # guarda para a explicação
                alguma_regra_disparou = True

    return regras_usadas


# -----------------------------------------------------------------------------
# 3. INTERFACE NO TERMINAL (perguntas ao usuário)
# -----------------------------------------------------------------------------
# Cada pergunta tem o nome do fato que ela preenche e as opções possíveis.
# A opção escolhida vira um fato inicial na base de fatos.

PERGUNTAS = [
    {"fato": "uso", "texto": "Para que você vai usar o computador?",
     "opcoes": [("estudo", "Estudo e escritório"),
                ("programação", "Programação"),
                ("jogos", "Jogos"),
                ("edição de vídeo", "Edição de vídeo")]},
    {"fato": "orcamento", "texto": "Quanto você pode gastar?",
     "opcoes": [("baixo", "Até R$ 3.000"),
                ("médio", "De R$ 3.000 a R$ 6.000"),
                ("alto", "Acima de R$ 6.000")]},
    {"fato": "formato", "texto": "Você prefere desktop ou notebook?",
     "opcoes": [("desktop", "Desktop (computador de mesa)"),
                ("notebook", "Notebook")]},
]


def perguntar(numero, pergunta):
    """Mostra uma pergunta, lê a resposta e só aceita uma opção válida."""
    print(f"\nPergunta {numero} de {len(PERGUNTAS)}: {pergunta['texto']}")
    for i, (_, rotulo) in enumerate(pergunta["opcoes"], start=1):
        print(f"  {i}) {rotulo}")

    while True:
        resposta = input("Escolha uma opção: ").strip()
        if resposta.isdigit() and 1 <= int(resposta) <= len(pergunta["opcoes"]):
            valor, _ = pergunta["opcoes"][int(resposta) - 1]
            return valor
        print(f"Opção inválida. Digite um número de 1 a {len(pergunta['opcoes'])}.")


def coletar_fatos():
    """Faz todas as perguntas e monta a base de fatos inicial."""
    fatos = {}
    for numero, pergunta in enumerate(PERGUNTAS, start=1):
        fatos[pergunta["fato"]] = perguntar(numero, pergunta)
    return fatos


# -----------------------------------------------------------------------------
# 4. RESULTADO E EXPLICAÇÃO
# -----------------------------------------------------------------------------

def mostrar_recomendacao(fatos):
    """Mostra as peças recomendadas e os avisos (fatos deduzidos pelo motor)."""
    print("\n" + "-" * 60)
    print("  RECOMENDAÇÃO")
    print("-" * 60)
    print(f"  Perfil identificado: {fatos['perfil']}")
    print(f"  Processador:         {fatos['processador']}")
    print(f"  Memória RAM:         {fatos['memoria']}")
    print(f"  Placa de vídeo:      {fatos['placa_de_video']}")
    print(f"  Armazenamento:       {fatos['armazenamento']}")

    # Avisos e dicas só aparecem se alguma regra os criou.
    for nome in ("aviso_orcamento", "aviso_notebook"):
        if nome in fatos:
            print(f"\n  ATENÇÃO: {fatos[nome]}")
    print(f"\n  DICA: {fatos['dica']}")


def regra_em_texto(regra):
    """Escreve a regra no formato SE ... ENTÃO ... para mostrar ao usuário."""
    se = " E ".join(f"{nome} = {valor}" for nome, valor in regra["se"].items())
    entao = " E ".join(f"{nome} = {valor}" for nome, valor in regra["entao"].items())
    return f"SE {se} ENTÃO {entao}"


def mostrar_explicacao(regras_usadas):
    """Módulo de explicação: mostra as regras usadas, na ordem em que dispararam."""
    print("\n" + "-" * 60)
    print("  POR QUÊ? Regras usadas, na ordem em que o motor aplicou:")
    print("-" * 60)
    for id_regra in regras_usadas:
        regra = next(r for r in REGRAS if r["id"] == id_regra)
        print(f"  {id_regra}: {regra_em_texto(regra)}")


# -----------------------------------------------------------------------------
# 5. PROGRAMA PRINCIPAL
# -----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  MONTA AÍ - Sistema especialista que recomenda computadores")
    print("=" * 60)
    print("Responda 3 perguntas e eu indico o computador ideal para você.")

    while True:
        fatos = coletar_fatos()                     # 1. base de fatos inicial
        regras_usadas = motor_de_inferencia(fatos)  # 2. raciocínio
        mostrar_recomendacao(fatos)                 # 3. resultado
        mostrar_explicacao(regras_usadas)           # 4. explicação

        de_novo = input("\nDeseja fazer uma nova consulta? (s/n): ").strip().lower()
        if de_novo != "s":
            print("Até mais!")
            break


if __name__ == "__main__":
    main()
