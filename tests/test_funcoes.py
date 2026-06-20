import unittest
from src.funcoes import calcular_pontos, jogador_perdeu, tomar_dano

class TestLógicaDoJogo(unittest.TestCase):
    
    def test_calcular_pontos(self):
        # Testa se a soma de pontos com combo está funcionando
        self.assertEqual(calcular_pontos(100, 50), 150)
        
    def test_tomar_dano(self):
        # Testa se a vida é reduzida corretamente
        self.assertEqual(tomar_dano(5, 1), 4)
        
    def test_jogador_perdeu(self):
        # Testa a condição de Game Over
        self.assertTrue(jogador_perdeu(0))
        self.assertFalse(jogador_perdeu(3))

if __name__ == '__main__':
    unittest.main()