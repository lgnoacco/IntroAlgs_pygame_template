Cyberdelivery
Projeto final da disciplina de Introdução a Algoritmos/Programação, desenvolvido com Python e Pygame.

Este repositório contém a versão final do jogo, que evoluiu de um template básico para um arcade de corrida endless runner com mecânicas de esquiva, coleta de itens e progressão de dificuldade, ambientado em uma estética Cyberpunk/Retrowave.

Integrantes do grupo
Luis Guilherme Pacheco Noacco

Matheus Henrique Barbosa de Andrade

Arthur Nunes Cristóvão

Davi Lavalle Carneiro

Estrutura do projeto
main.py: ponto de entrada da aplicação.

src/: código-fonte principal do jogo (loop, regras, sprites e dados).

assets/: imagens, fontes e sons.

data/: arquivos persistentes (recorde/ranking).

tests/: testes unitários com pytest.

docs/: documentação do projeto, incluindo proposta inicial.

Descrição do jogo
Cyberdelivery é um jogo arcade de reflexos rápidos com visão top-down. O jogador controla um entregador em uma hoverbike (moto flutuante) de alta velocidade, cruzando uma rodovia futurista de 3 faixas. É preciso desviar do tráfego intenso de veículos, poças perigosas e ataques de feixes de laser, tudo isso sob a iluminação de prédios em neon.

Objetivo do jogador
O objetivo é sobreviver o maior tempo possível na rodovia para alcançar a maior pontuação (Recorde). Para isso, o jogador deve coletar entregas (pontos e escudos) para acumular multiplicadores de combo, enquanto desvia de todos os obstáculos que surgem na pista em velocidades cada vez maiores.

Regras do jogo
Faixas de Movimento: A pista possui 3 faixas. A moto transita instantaneamente entre elas.

Coletáveis (Entregas):

Caixas: Concedem pontos e aumentam o multiplicador de Combo (até 5x).

Escudos: Criam uma barreira de energia azul em volta da moto que absorve exatamente 1 impacto.

Obstáculos e Perigos:

Carros: Colidir com veículos causa dano, zera o combo e consome 1 vida (se o jogador não tiver escudo).

Poças (Derrapagem): Passar por uma poça faz a moto girar em 360 graus, zerando o combo e jogando o jogador para uma faixa lateral aleatória.

Laser: Um feixe vermelho mortal mira em uma faixa. Após um breve aviso visual translúcido, ele dispara. Ficar na faixa atingida causa dano severo.

Progressão: A cada meta de pontos atingida, o Nível do jogo sobe, aumentando a velocidade da pista e o spawn de obstáculos.

Fim de Jogo: A partida termina (Game Over) quando o jogador perde todas as vidas.

Controles
Seta para a Esquerda / Tecla A: Mudar para a faixa da esquerda

Seta para a Direita / Tecla D: Mudar para a faixa da direita

Seta Esquerda/Direita (no Menu): Alternar entre os modos de jogo ("Apresentação" ou "Souls-like")

ENTER ou ESPAÇO: Iniciar a partida (no menu) ou Voltar ao menu (no Game Over)

ESC: Pausar / Despausar o jogo

Como executar o projeto
1. Clonar o repositório e instalar dependências
Bash
git clone LINK_DO_REPOSITORIO
cd NOME_DA_PASTA
pip install -r requirements.txt
python main.py
Como executar os testes
Os testes unitários validam as lógicas de cálculo de pontuação com combos, sistema de dano e a condição de derrota.

Bash
python -m pytest
🎧 Créditos e Assets Externos
Para a composição da estética futurista do jogo, foram utilizados e adaptados os seguintes recursos externos:

Engine Principal: Desenvolvido puramente com Pygame CE.

Trilha Sonora: A música de fundo "Neon Pursuit Override" foi gerada através de inteligência artificial especializada em áudio (Suno AI).

Sprites (Hoverbike e Cenário): A pixel art base foi gerada com auxílio de inteligência artificial gráfica e posteriormente tratada, recortada e adaptada manualmente no código para suportar o formato spritesheet com transparências.