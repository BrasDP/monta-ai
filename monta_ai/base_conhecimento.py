"""Base de conhecimento do Monta Aí.

Aqui fica todo o conhecimento do especialista em hardware, escrito como
regras de produção (SE ... ENTÃO ...). O motor de inferência não precisa
ser alterado para mudar o comportamento do sistema: basta editar as regras.

As peças são recomendadas por NÍVEL (faixa), e não por modelo, porque os
modelos e preços mudam o tempo todo. Os níveis são números para que as
regras possam comparar e limitar valores:

    Placa de vídeo (GPU): 0 integrada, 1 entrada, 2 intermediária,
                          3 intermediária-alta, 4 alta
    Processador (CPU):    1 entrada, 2 intermediário, 3 intermediário-alto, 4 alto
    Memória RAM:          1 = 8 GB, 2 = 16 GB, 3 = 32 GB, 4 = 64 GB
    Armazenamento:        1 = SSD 512 GB, 2 = SSD NVMe 1 TB, 3 = SSD NVMe 2 TB
    Faixa de orçamento:   1 até R$ 3 mil, 2 de 3 a 5 mil, 3 de 5 a 8 mil, 4 acima de 8 mil
"""

from .motor import ALERTAS, Regra

GAMERS = ("gamer_casual", "gamer_entusiasta")

REGRAS = [
    # ------------------------------------------------------------------
    # Grupo 1: classificação do orçamento
    # ------------------------------------------------------------------
    Regra("R01", "Classificação do orçamento",
          "Orçamento abaixo de R$ 3.000 é faixa 1 (baixo).",
          [("orcamento", "<", 3000)],
          [("faixa_orcamento", 1)]),
    Regra("R02", "Classificação do orçamento",
          "Orçamento de R$ 3.000 a R$ 4.999 é faixa 2 (médio).",
          [("orcamento", ">=", 3000), ("orcamento", "<", 5000)],
          [("faixa_orcamento", 2)]),
    Regra("R03", "Classificação do orçamento",
          "Orçamento de R$ 5.000 a R$ 7.999 é faixa 3 (alto).",
          [("orcamento", ">=", 5000), ("orcamento", "<", 8000)],
          [("faixa_orcamento", 3)]),
    Regra("R04", "Classificação do orçamento",
          "Orçamento a partir de R$ 8.000 é faixa 4 (premium).",
          [("orcamento", ">=", 8000)],
          [("faixa_orcamento", 4)]),

    # ------------------------------------------------------------------
    # Grupo 2: perfil de uso (primeiro nível de dedução)
    # ------------------------------------------------------------------
    Regra("R05", "Perfil de uso",
          "Quem usa para estudo e escritório tem perfil básico.",
          [("uso", "==", "escritorio")],
          [("perfil", "basico")]),
    Regra("R06", "Perfil de uso",
          "Quem usa para programar tem perfil desenvolvedor.",
          [("uso", "==", "programacao")],
          [("perfil", "desenvolvedor")]),
    Regra("R07", "Perfil de uso",
          "Quem joga jogos leves tem perfil gamer casual.",
          [("uso", "==", "jogos"), ("tipo_jogo", "==", "leves")],
          [("perfil", "gamer_casual")]),
    Regra("R08", "Perfil de uso",
          "Quem joga jogos pesados tem perfil gamer entusiasta.",
          [("uso", "==", "jogos"), ("tipo_jogo", "==", "pesados")],
          [("perfil", "gamer_entusiasta")]),
    Regra("R09", "Perfil de uso",
          "Quem edita vídeo tem perfil criador de conteúdo.",
          [("uso", "==", "edicao_video")],
          [("perfil", "criador_conteudo")]),
    Regra("R10", "Perfil de uso",
          "Quem trabalha com IA e ciência de dados tem perfil de computação intensiva.",
          [("uso", "==", "ia_dados")],
          [("perfil", "computacao_intensiva")]),

    # ------------------------------------------------------------------
    # Grupo 3: requisitos de cada perfil (segundo nível de dedução)
    # ------------------------------------------------------------------
    Regra("R11", "Requisitos do perfil",
          "Perfil básico: vídeo integrado, processador de entrada, 16 GB e SSD de 512 GB.",
          [("perfil", "==", "basico")],
          [("gpu_base", 0), ("cpu_base", 1), ("ram_req", 2), ("armaz_req", 1)]),
    Regra("R12", "Requisitos do perfil",
          "Desenvolvedor: vídeo integrado, processador intermediário, 32 GB (IDE, Docker e "
          "navegador abertos juntos) e SSD de 1 TB.",
          [("perfil", "==", "desenvolvedor")],
          [("gpu_base", 0), ("cpu_base", 2), ("ram_req", 3), ("armaz_req", 2)]),
    Regra("R13", "Requisitos do perfil",
          "Gamer casual: placa de vídeo de entrada, processador intermediário, 16 GB e SSD de 1 TB.",
          [("perfil", "==", "gamer_casual")],
          [("gpu_base", 1), ("cpu_base", 2), ("ram_req", 2), ("armaz_req", 2)]),
    Regra("R14", "Requisitos do perfil",
          "Gamer entusiasta: placa de vídeo intermediária-alta, processador intermediário, "
          "16 GB e SSD de 1 TB.",
          [("perfil", "==", "gamer_entusiasta")],
          [("gpu_base", 3), ("cpu_base", 2), ("ram_req", 2), ("armaz_req", 2)]),
    Regra("R15", "Requisitos do perfil",
          "Criador de conteúdo: placa de vídeo intermediária, processador intermediário-alto, "
          "32 GB e SSD de 2 TB para os arquivos de vídeo.",
          [("perfil", "==", "criador_conteudo")],
          [("gpu_base", 2), ("cpu_base", 3), ("ram_req", 3), ("armaz_req", 3)]),
    Regra("R16", "Requisitos do perfil",
          "Computação intensiva: placa de vídeo intermediária-alta, processador "
          "intermediário-alto, 32 GB e SSD de 1 TB.",
          [("perfil", "==", "computacao_intensiva")],
          [("gpu_base", 3), ("cpu_base", 3), ("ram_req", 3), ("armaz_req", 2)]),

    # ------------------------------------------------------------------
    # Grupo 4: ajustes pela resolução do monitor e por transmissões ao vivo
    # ------------------------------------------------------------------
    Regra("R17", "Ajustes do perfil",
          "Para jogos, monitor 1080p não exige placa de vídeo extra.",
          [("perfil", "in", GAMERS), ("resolucao", "==", "1080p")],
          [("bonus_resolucao", 0)]),
    Regra("R18", "Ajustes do perfil",
          "Para jogos, monitor 1440p exige uma placa de vídeo um nível acima.",
          [("perfil", "in", GAMERS), ("resolucao", "==", "1440p")],
          [("bonus_resolucao", 1)]),
    Regra("R19", "Ajustes do perfil",
          "Para jogos, monitor 4K exige uma placa de vídeo dois níveis acima.",
          [("perfil", "in", GAMERS), ("resolucao", "==", "4k")],
          [("bonus_resolucao", 2)]),
    Regra("R20", "Ajustes do perfil",
          "Fora dos jogos, a resolução do monitor não muda a placa de vídeo necessária.",
          [("perfil", "not in", GAMERS)],
          [("bonus_resolucao", 0)]),
    Regra("R21", "Ajustes do perfil",
          "Quem faz lives ou grava a tela precisa de um processador um nível acima.",
          [("streaming", "==", "sim")],
          [("bonus_streaming", 1)]),
    Regra("R22", "Ajustes do perfil",
          "Sem lives nem gravação de tela, o processador não precisa de ajuste.",
          [("streaming", "==", "nao")],
          [("bonus_streaming", 0)]),
    Regra("R23", "Ajustes do perfil",
          "Placa de vídeo necessária = nível do perfil + ajuste da resolução (máximo 4).",
          [("gpu_base", "!=", None), ("bonus_resolucao", "!=", None)],
          [("gpu_req", ("min", ("soma", "?gpu_base", "?bonus_resolucao"), 4))]),
    Regra("R24", "Ajustes do perfil",
          "Processador necessário = nível do perfil + ajuste de streaming (máximo 4).",
          [("cpu_base", "!=", None), ("bonus_streaming", "!=", None)],
          [("cpu_req", ("min", ("soma", "?cpu_base", "?bonus_streaming"), 4))]),

    # ------------------------------------------------------------------
    # Grupo 5: quanto o orçamento permite (teto por faixa)
    # ------------------------------------------------------------------
    Regra("R25", "Limite do orçamento",
          "No desktop, a faixa de orçamento define o nível máximo de placa de vídeo e processador.",
          [("formato", "==", "desktop"), ("faixa_orcamento", "!=", None)],
          [("gpu_teto", "?faixa_orcamento"), ("cpu_teto", "?faixa_orcamento")]),
    Regra("R26", "Limite do orçamento",
          "No notebook, a placa de vídeo custa mais caro: o teto dela fica um nível abaixo da faixa.",
          [("formato", "==", "notebook"), ("faixa_orcamento", "!=", None)],
          [("gpu_teto", ("soma", "?faixa_orcamento", -1)), ("cpu_teto", "?faixa_orcamento")]),
    Regra("R27", "Limite do orçamento",
          "O orçamento permite memória um nível acima da faixa (máximo 64 GB).",
          [("faixa_orcamento", "!=", None)],
          [("ram_teto", ("min", ("soma", "?faixa_orcamento", 1), 4))]),

    # ------------------------------------------------------------------
    # Grupo 6: recomendação final = o necessário, limitado pelo orçamento
    # ------------------------------------------------------------------
    Regra("R28", "Recomendação",
          "Placa de vídeo recomendada = a necessária, limitada pelo orçamento.",
          [("gpu_req", "!=", None), ("gpu_teto", "!=", None)],
          [("gpu_rec", ("min", "?gpu_req", "?gpu_teto"))]),
    Regra("R29", "Recomendação",
          "Processador recomendado = o necessário, limitado pelo orçamento.",
          [("cpu_req", "!=", None), ("cpu_teto", "!=", None)],
          [("cpu_rec", ("min", "?cpu_req", "?cpu_teto"))]),
    Regra("R30", "Recomendação",
          "Memória recomendada = a necessária, limitada pelo orçamento.",
          [("ram_req", "!=", None), ("ram_teto", "!=", None)],
          [("ram_rec", ("min", "?ram_req", "?ram_teto"))]),
    Regra("R31", "Recomendação",
          "Armazenamento recomendado = o necessário, limitado pela faixa de orçamento.",
          [("armaz_req", "!=", None), ("faixa_orcamento", "!=", None)],
          [("armaz_rec", ("min", "?armaz_req", "?faixa_orcamento"))]),
    Regra("R32", "Recomendação",
          "Para IA e ciência de dados, a placa de vídeo deve ser NVIDIA (CUDA).",
          [("perfil", "==", "computacao_intensiva")],
          [("gpu_marca", "NVIDIA (necessária para CUDA)")], prioridade=5),
    Regra("R33", "Recomendação",
          "Nos demais usos, NVIDIA e AMD atendem: vale a que estiver mais barata.",
          [("gpu_rec", ">=", 1)],
          [("gpu_marca", "NVIDIA ou AMD, a que tiver melhor preço")]),

    # ------------------------------------------------------------------
    # Grupo 7: fonte e placa-mãe (só desktop). Mostra a resolução de
    # conflitos: as regras de upgrade têm prioridade maior que as padrão.
    # ------------------------------------------------------------------
    Regra("R34", "Fonte e placa-mãe",
          "Quem pretende fazer upgrade e tem placa de vídeo dedicada precisa de fonte com folga.",
          [("formato", "==", "desktop"), ("upgrade", "==", "sim"), ("gpu_rec", ">=", 2)],
          [("fonte", "750 W, 80 Plus Gold (com folga para upgrade)")], prioridade=10),
    Regra("R35", "Fonte e placa-mãe",
          "Quem pretende fazer upgrade, mesmo com vídeo simples, deve comprar fonte com folga.",
          [("formato", "==", "desktop"), ("upgrade", "==", "sim"), ("gpu_rec", "<=", 1)],
          [("fonte", "550 W, 80 Plus Bronze (com folga para colocar placa de vídeo depois)")],
          prioridade=10),
    Regra("R36", "Fonte e placa-mãe",
          "Placa de vídeo intermediária-alta ou alta pede fonte de 650 W.",
          [("formato", "==", "desktop"), ("gpu_rec", ">=", 3)],
          [("fonte", "650 W, 80 Plus Bronze ou superior")]),
    Regra("R37", "Fonte e placa-mãe",
          "Placa de vídeo intermediária pede fonte de 550 W.",
          [("formato", "==", "desktop"), ("gpu_rec", "==", 2)],
          [("fonte", "550 W, 80 Plus Bronze")]),
    Regra("R38", "Fonte e placa-mãe",
          "Vídeo integrado ou de entrada pede fonte de 450 W.",
          [("formato", "==", "desktop"), ("gpu_rec", "<=", 1)],
          [("fonte", "450 W, 80 Plus (marca confiável)")]),
    Regra("R39", "Fonte e placa-mãe",
          "Quem pretende fazer upgrade precisa de placa-mãe com slots sobrando.",
          [("formato", "==", "desktop"), ("upgrade", "==", "sim")],
          [("placa_mae", "Com 4 slots de memória e 2 entradas M.2, para ampliar depois")]),
    Regra("R40", "Fonte e placa-mãe",
          "Sem planos de upgrade, uma placa-mãe de entrada compatível basta.",
          [("formato", "==", "desktop"), ("upgrade", "==", "nao")],
          [("placa_mae", "Modelo de entrada compatível com o processador")]),

    # ------------------------------------------------------------------
    # Grupo 8: como dividir o dinheiro entre as peças (só desktop)
    # ------------------------------------------------------------------
    Regra("R41", "Distribuição do orçamento",
          "Para jogos, a maior parte do dinheiro vai para a placa de vídeo.",
          [("formato", "==", "desktop"), ("perfil", "in", GAMERS)],
          [("distribuicao", (("Placa de vídeo", 40), ("Processador", 20), ("Placa-mãe", 10),
                             ("Memória RAM", 10), ("SSD", 8), ("Fonte", 7), ("Gabinete", 5)))]),
    Regra("R42", "Distribuição do orçamento",
          "Para edição e IA, o dinheiro é dividido entre processador, placa de vídeo e memória.",
          [("formato", "==", "desktop"),
           ("perfil", "in", ("criador_conteudo", "computacao_intensiva"))],
          [("distribuicao", (("Placa de vídeo", 30), ("Processador", 25), ("Memória RAM", 15),
                             ("Placa-mãe", 10), ("SSD", 10), ("Fonte", 6), ("Gabinete", 4)))]),
    Regra("R43", "Distribuição do orçamento",
          "Para escritório e programação, sem placa de vídeo, o foco é processador, memória e SSD.",
          [("formato", "==", "desktop"), ("perfil", "in", ("basico", "desenvolvedor"))],
          [("distribuicao", (("Processador", 35), ("Memória RAM", 20), ("Placa-mãe", 15),
                             ("SSD", 15), ("Fonte", 8), ("Gabinete", 7)))]),

    # ------------------------------------------------------------------
    # Grupo 9: alertas, gargalos e incompatibilidades
    # ------------------------------------------------------------------
    Regra("R44", "Alertas",
          "Se a placa de vídeo necessária passa do teto, avisa que o orçamento está curto.",
          [("gpu_req", ">", "?gpu_teto")],
          [(ALERTAS, "Seu orçamento está abaixo do ideal para a placa de vídeo que o seu uso "
                     "pede. Vai funcionar, mas com qualidade gráfica menor. Se puder, aumente o "
                     "orçamento ou procure peças usadas com garantia.")]),
    Regra("R45", "Alertas",
          "Se o processador necessário passa do teto, avisa que dá para trocar depois.",
          [("cpu_req", ">", "?cpu_teto")],
          [(ALERTAS, "O processador ideal para o seu uso não cabe no orçamento. Recomendamos o "
                     "melhor possível na sua faixa; ele pode ser trocado mais tarde.")]),
    Regra("R46", "Alertas",
          "Se a memória necessária passa do teto, sugere começar menor e ampliar depois.",
          [("ram_req", ">", "?ram_teto")],
          [(ALERTAS, "A memória ideal não cabe no orçamento. Comece com a recomendada, em "
                     "2 pentes, e amplie depois.")]),
    Regra("R47", "Alertas",
          "Placa de vídeo dois níveis acima do processador indica risco de gargalo.",
          [("gpu_rec", ">=", ("soma", "?cpu_rec", 2))],
          [(ALERTAS, "Gargalo: a placa de vídeo está bem acima do processador. Se sobrar "
                     "dinheiro, suba o processador um nível para não perder desempenho em "
                     "jogos com muitos FPS.")]),
    Regra("R48", "Alertas",
          "Notebook não permite trocar processador nem placa de vídeo.",
          [("formato", "==", "notebook"), ("upgrade", "==", "sim")],
          [(ALERTAS, "Em notebooks, normalmente só dá para trocar a memória RAM e o SSD. "
                     "Processador e placa de vídeo não têm upgrade: escolha já pensando no futuro.")]),
    Regra("R49", "Alertas",
          "Para IA, lembra que as bibliotecas dependem de CUDA.",
          [("gpu_marca", "==", "NVIDIA (necessária para CUDA)")],
          [(ALERTAS, "Para IA e ciência de dados, prefira placa NVIDIA: PyTorch e TensorFlow "
                     "usam CUDA, que só funciona nelas.")]),
    Regra("R50", "Alertas",
          "Treinar modelos em notebook causa superaquecimento e perda de desempenho.",
          [("perfil", "==", "computacao_intensiva"), ("formato", "==", "notebook")],
          [(ALERTAS, "Treinar modelos em notebook esquenta e faz o desempenho cair "
                     "(throttling). Para tarefas longas, considere um desktop ou a nuvem "
                     "(Google Colab, Kaggle).")]),
    Regra("R51", "Alertas",
          "Jogar em 4K sem placa de vídeo alta exige upscaling.",
          [("perfil", "in", GAMERS), ("resolucao", "==", "4k"), ("gpu_rec", "<=", 3)],
          [(ALERTAS, "Para jogar em 4K com essa placa de vídeo, ative o upscaling (DLSS ou "
                     "FSR) ou jogue em 1440p.")]),
    Regra("R52", "Alertas",
          "Notebook gamer na faixa mais baixa de orçamento não compensa.",
          [("perfil", "in", GAMERS), ("formato", "==", "notebook"), ("faixa_orcamento", "==", 1)],
          [(ALERTAS, "Notebooks gamer abaixo de R$ 3 mil são raros e fracos. Pelo mesmo preço, "
                     "um desktop rende bem mais.")]),
    Regra("R53", "Alertas",
          "Live sem placa de vídeo dedicada sobrecarrega o processador.",
          [("streaming", "==", "sim"), ("gpu_rec", "==", 0)],
          [(ALERTAS, "Sem placa de vídeo dedicada, a codificação da live fica com o processador. "
                     "No OBS, use o codificador de hardware do processador (Quick Sync ou AMF).")]),

    # ------------------------------------------------------------------
    # Objetivo: todas as peças principais foram definidas.
    # ------------------------------------------------------------------
    Regra("R54", "Objetivo",
          "Com processador, placa de vídeo, memória e armazenamento definidos, a recomendação está completa.",
          [("gpu_rec", "!=", None), ("cpu_rec", "!=", None),
           ("ram_rec", "!=", None), ("armaz_rec", "!=", None)],
          [("recomendacao", "completa")], prioridade=-10),
]
