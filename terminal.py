"""Monta Aí no terminal: faz as perguntas, roda a inferência e explica o resultado.

Uso:  python terminal.py
"""

import sys

from monta_ai.catalogo import formatar_valor
from monta_ai.sistema import perguntas_aplicaveis, recomendar

LINHA = "─" * 64


def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ler_orcamento(texto):
    while True:
        bruto = input(f"{texto}\n> R$ ").strip().replace(".", "").replace(",", ".")
        try:
            valor = float(bruto)
            if valor > 0:
                return valor
        except ValueError:
            pass
        print("Digite só o valor, por exemplo 4500.")


def ler_opcao(pergunta):
    print(pergunta.texto)
    for i, (_, rotulo) in enumerate(pergunta.opcoes, 1):
        print(f"  {i}) {rotulo}")
    while True:
        escolha = input("> ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(pergunta.opcoes):
            return pergunta.opcoes[int(escolha) - 1][0]
        print(f"Escolha um número de 1 a {len(pergunta.opcoes)}.")


def coletar_respostas():
    respostas = {}
    # As perguntas dependem das respostas anteriores (ex.: tipo de jogo só para quem joga).
    while True:
        pendentes = [p for p in perguntas_aplicaveis(respostas) if p.atributo not in respostas]
        if not pendentes:
            return respostas
        pergunta = pendentes[0]
        print()
        if pergunta.opcoes:
            respostas[pergunta.atributo] = ler_opcao(pergunta)
        else:
            respostas[pergunta.atributo] = ler_orcamento(pergunta.texto)


def mostrar_resultado(resultado):
    print(f"\n{LINHA}\n  CONFIGURAÇÃO RECOMENDADA\n{LINHA}")
    print(f"Perfil identificado: {formatar_valor('perfil', resultado.fatos['perfil'])}")
    print(f"Faixa de orçamento:  {formatar_valor('faixa_orcamento', resultado.fatos['faixa_orcamento'])}\n")
    pecas = resultado.pecas()
    for i, (_, peca, nome, detalhe) in enumerate(pecas, 1):
        print(f"{i}. {peca}: {nome}")
        if detalhe:
            print(f"   {detalhe}")

    distribuicao = resultado.distribuicao_em_reais()
    if distribuicao:
        print(f"\nComo dividir o orçamento de {moeda(resultado.fatos['orcamento'])}:")
        for peca, pct, valor in distribuicao:
            print(f"   {peca:<15} {pct:>3}%  ≈ {moeda(valor)}")

    alertas = resultado.alertas
    if alertas:
        print("\nALERTAS")
        for i, alerta in enumerate(alertas, 1):
            print(f"  [A{i}] {alerta}")
    return pecas, alertas


def menu_explicacao(resultado, pecas, alertas):
    while True:
        print(f"\n{LINHA}")
        print("Digite o número de uma peça (ex.: 2) ou de um alerta (ex.: A1) para saber o porquê,")
        print("R para ver todas as regras disparadas, N para nova consulta ou S para sair.")
        escolha = input("> ").strip().upper()
        if escolha == "S":
            return False
        if escolha == "N":
            return True
        if escolha == "R":
            print("\nRegras disparadas, na ordem do encadeamento para frente:")
            for regra_id, descricao in resultado.rastro():
                print(f"  {regra_id}  {descricao}")
            continue
        linhas = None
        if escolha.isdigit() and 1 <= int(escolha) <= len(pecas):
            fato, peca, nome, _ = pecas[int(escolha) - 1]
            print(f"\nPor que {peca}: {nome}?")
            linhas = resultado.explicar(fato)
        elif escolha.startswith("A") and escolha[1:].isdigit() and 1 <= int(escolha[1:]) <= len(alertas):
            print(f"\nPor que o alerta {escolha}?")
            linhas = resultado.explicar_alerta(alertas[int(escolha[1:]) - 1])
        if linhas is None:
            print("Opção inválida.")
            continue
        for linha in linhas:
            print("  " + linha)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(LINHA)
    print("  MONTA AÍ: sistema especialista em recomendação de computadores")
    print(LINHA)
    print("Responda algumas perguntas e eu indico a configuração ideal para você.")
    while True:
        resultado = recomendar(coletar_respostas())
        pecas, alertas = mostrar_resultado(resultado)
        if not menu_explicacao(resultado, pecas, alertas):
            print("Até mais!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nAté mais!")
