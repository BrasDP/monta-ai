"""Testes do Monta Aí.  Rode com:  python -m unittest"""

import itertools
import unittest

from monta_ai.base_conhecimento import REGRAS
from monta_ai.motor import MotorInferencia, Regra
from monta_ai.sistema import recomendar, regra_texto

GAMER_PESADO = dict(orcamento=6000, formato="desktop", uso="jogos", tipo_jogo="pesados",
                    resolucao="1440p", streaming="sim", upgrade="sim")


class TestMotor(unittest.TestCase):
    def test_encadeamento_para_frente(self):
        regras = [Regra("A", "", "", [("x", "==", 1)], [("y", 2)]),
                  Regra("B", "", "", [("y", "==", 2)], [("z", 3)])]
        motor = MotorInferencia(regras)
        fatos = motor.executar({"x": 1})
        self.assertEqual(fatos["z"], 3)
        self.assertEqual([d.regra.id for d in motor.historico], ["A", "B"])

    def test_prioridade_resolve_conflito(self):
        regras = [Regra("baixa", "", "", [("x", "==", 1)], [("y", "baixa")], prioridade=0),
                  Regra("alta", "", "", [("x", "==", 1)], [("y", "alta")], prioridade=9)]
        self.assertEqual(MotorInferencia(regras).executar({"x": 1})["y"], "alta")

    def test_referencia_e_expressao(self):
        regras = [Regra("A", "", "", [("a", ">", "?b")], [("c", ("min", ("soma", "?a", "?b"), 4))])]
        self.assertEqual(MotorInferencia(regras).executar({"a": 3, "b": 2})["c"], 4)

    def test_nao_dispara_sem_fato(self):
        regras = [Regra("A", "", "", [("x", "==", 1)], [("y", 1)])]
        motor = MotorInferencia(regras)
        self.assertNotIn("y", motor.executar({}))


class TestBaseConhecimento(unittest.TestCase):
    def test_ids_unicos(self):
        ids = [r.id for r in REGRAS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_todas_as_regras_tem_texto(self):
        for regra in REGRAS:
            self.assertTrue(regra_texto(regra).startswith("SE "), regra.id)

    def test_gamer_pesado_limitado_pelo_orcamento(self):
        r = recomendar(GAMER_PESADO)
        self.assertEqual(r.fatos["perfil"], "gamer_entusiasta")
        self.assertEqual(r.fatos["gpu_req"], 4)   # 3 do perfil + 1 pelo monitor 1440p
        self.assertEqual(r.fatos["gpu_rec"], 3)   # limitado pela faixa 3
        self.assertEqual(r.fatos["cpu_rec"], 3)   # 2 do perfil + 1 pelas lives
        self.assertTrue(any("abaixo do ideal" in a for a in r.alertas))

    def test_upgrade_tem_prioridade_na_fonte(self):
        self.assertIn("750 W", recomendar(GAMER_PESADO).fatos["fonte"])
        sem_upgrade = dict(GAMER_PESADO, upgrade="nao")
        self.assertIn("650 W", recomendar(sem_upgrade).fatos["fonte"])

    def test_notebook_nao_tem_fonte_nem_distribuicao(self):
        r = recomendar(dict(GAMER_PESADO, formato="notebook"))
        self.assertNotIn("fonte", r.fatos)
        self.assertEqual(r.distribuicao_em_reais(), [])
        self.assertTrue(any("notebooks" in a.lower() for a in r.alertas))

    def test_basico_com_orcamento_baixo_recomenda_8gb(self):
        basico = dict(formato="desktop", uso="escritorio", resolucao="1080p",
                      streaming="nao", upgrade="nao")
        r = recomendar(dict(basico, orcamento=2000))
        self.assertEqual(r.fatos["ram_rec"], 1)  # R55 vence a R11 pela prioridade
        self.assertEqual(r.motor.origem("ram_req").regra.id, "R55")
        self.assertTrue(any("8 GB" in a for a in r.alertas))
        # Com orçamento médio, volta a valer a regra padrão (16 GB).
        self.assertEqual(recomendar(dict(basico, orcamento=4000)).fatos["ram_rec"], 2)

    def test_ia_exige_nvidia(self):
        r = recomendar(dict(orcamento=9000, formato="desktop", uso="ia_dados",
                            resolucao="1080p", streaming="nao", upgrade="nao"))
        self.assertIn("NVIDIA", r.fatos["gpu_marca"])

    def test_explicacao_volta_ate_as_respostas(self):
        r = recomendar(GAMER_PESADO)
        ids = [linha.split(":")[0] for linha in r.explicar("gpu_rec") if not linha.startswith(" ")]
        self.assertEqual(ids[-1], "R28")
        self.assertIn("R08", ids)  # perfil
        self.assertIn("R03", ids)  # faixa de orçamento

    def test_todas_as_combinacoes_geram_recomendacao_completa(self):
        opcoes = dict(orcamento=[1500, 3500, 6000, 12000], formato=["desktop", "notebook"],
                      uso=["escritorio", "programacao", "jogos", "edicao_video", "ia_dados"],
                      tipo_jogo=["leves", "pesados"], resolucao=["1080p", "1440p", "4k"],
                      streaming=["sim", "nao"], upgrade=["sim", "nao"])
        for valores in itertools.product(*opcoes.values()):
            respostas = dict(zip(opcoes, valores))
            if respostas["uso"] != "jogos":
                del respostas["tipo_jogo"]
            r = recomendar(respostas)
            self.assertTrue(r.completa, respostas)
            self.assertLessEqual(r.fatos["gpu_rec"], r.fatos["gpu_teto"])
            if respostas["formato"] == "desktop":
                self.assertIn("fonte", r.fatos, respostas)
                self.assertIn("placa_mae", r.fatos, respostas)
                self.assertEqual(sum(p for _, p in r.fatos["distribuicao"]), 100)


if __name__ == "__main__":
    unittest.main()
