# Monta Aí: sistema especialista que recomenda computadores

Trabalho da **Atividade Avaliativa A1** da disciplina **Programação de Sistemas Especialistas**
do curso de Ciência da Computação da Universidade Veiga de Almeida (Campus Tijuca),
com o Prof. Vinicius Marques da Silva Ferreira.

**Integrantes:** Lucas Pires da Costa (1250122691), Ruan da Silva Marques (1250124415) e
Lucas Santos Garcia (1250117441).

## O que o sistema faz

O usuário responde 3 perguntas no terminal (uso do computador, orçamento e desktop ou notebook).
O sistema aplica 20 regras e recomenda processador, memória RAM, placa de vídeo e armazenamento,
com avisos e dicas. No final, mostra quais regras usou para chegar à resposta.

## Como executar

**Rodar no navegador (sem instalar nada):** https://brasdp.github.io/monta-ai/

Precisa apenas do Python 3, sem nenhuma biblioteca extra:

```bash
python monta_ai.py
```

Todo o sistema está em um único arquivo, [`monta_ai.py`](monta_ai.py), comentado parte por parte.

## Partes do sistema especialista

| Parte | Onde está no código |
|---|---|
| Minimundo | Comentário no início do arquivo |
| Base de conhecimento | Lista `REGRAS` (20 regras SE ... ENTÃO ...) |
| Base de fatos | Dicionário `fatos` (respostas + fatos deduzidos) |
| Motor de inferência | Função `motor_de_inferencia` (encadeamento para frente) |
| Explicação | Função `mostrar_explicacao` (mostra as regras usadas) |
| Interface | Funções `perguntar`, `coletar_fatos` e `mostrar_recomendacao` |

## Regras

| Regra | SE | ENTÃO |
|---|---|---|
| R1 | uso = estudo | perfil = básico |
| R2 | uso = programação | perfil = desenvolvedor |
| R3 | uso = jogos | perfil = gamer |
| R4 | uso = edição de vídeo | perfil = criador de conteúdo |
| R5 | perfil = básico | processador de entrada, 8 GB, vídeo integrado |
| R6 | perfil = desenvolvedor | processador intermediário, 16 GB, vídeo integrado |
| R7 | perfil = gamer | processador intermediário, 16 GB, vídeo dedicado |
| R8 | perfil = criador de conteúdo | processador avançado, 32 GB, vídeo dedicado |
| R9 | orçamento = baixo | SSD de 256 GB |
| R10 | orçamento = médio | SSD de 512 GB |
| R11 | orçamento = alto | SSD de 1 TB |
| R12 | vídeo = integrado | não precisa de placa de vídeo |
| R13 | vídeo = dedicado E orçamento = baixo | placa de entrada |
| R14 | vídeo = dedicado E orçamento = médio | placa intermediária |
| R15 | vídeo = dedicado E orçamento = alto | placa avançada |
| R16 | perfil = gamer E orçamento = baixo | aviso de orçamento apertado para jogos |
| R17 | perfil = criador E orçamento = baixo | aviso de orçamento apertado para edição |
| R18 | formato = notebook E vídeo = dedicado | aviso sobre aquecimento |
| R19 | formato = notebook | dica: notebook não permite trocar peças |
| R20 | formato = desktop | dica: desktop permite melhorar aos poucos |

## Diagramas e protótipo

- Fluxograma: [`docs/img/fluxograma.png`](docs/img/fluxograma.png)
- Diagrama de caso de uso: [`docs/img/casos_de_uso.png`](docs/img/casos_de_uso.png)
- Diagrama de estado: [`docs/img/estados.png`](docs/img/estados.png)
- Protótipo de telas: https://brasdp.github.io/monta-ai/prototipo/
- Relatório (ABNT): [`docs/Relatorio_MontaAi.pdf`](docs/Relatorio_MontaAi.pdf)
