# Proposta Inicial do Jogo

Este documento deve ser preenchido pelo grupo na Semana 1 do projeto.

A proposta deve apresentar uma ideia simples, clara e viável para ser desenvolvida com Python e Pygame dentro do prazo disponível.

## 1. Nome provisório do jogo

> Cyberpunk Delivery: Neon Overdrive

## 2. Integrantes do grupo

Liste os integrantes do grupo.

- Nome 1: Luis Guilherme Pacheco Noacco
- Nome 2: Matheus Henrique Barbosa de Andrade
- Nome 3: Arthur Nunes Cristóvão 
- Nome 4: Davi Lavalle Carneiro

## 3. Tipo de jogo

Tipo escolhido pelo grupo:

> Jogo de desviar de obstáculos / Corrida simples com obstáculos (Estilo Arcade/Morte Súbita)

## 4. Descrição geral do jogo

Explique, em poucas linhas, como o jogo funcionará.

Descrição:

> O jogo adota uma perspectiva de cima para baixo (*top-down*). Na tela, aparece uma rodovia escura com linhas de sinalização neon que se movem verticalmente para simular alta velocidade. O jogador controla uma moto de entregas futurista na parte inferior da tela, movendo-se apenas horizontalmente para desviar dos obstáculos que surgem continuamente no topo (como carros de polícia, drones e bloqueios cibernéticos). O principal desafio é a velocidade progressiva: a cada intervalo de tempo, os obstáculos descem mais rápido. Como o foco é a precisão e o reflexo, o regime é de morte súbita: qualquer colisão encerra o programa imediatamente.

## 5. Objetivo do jogador

Explique qual é o objetivo principal do jogador.

Objetivo:

> Sobreviver ao tráfego e aos bloqueios pelo maior tempo possível, acumulando a maior pontuação baseada na distância percorrida e quebrando o recorde máximo (*High Score*) do sistema.

## 6. Regras principais

Regras do grupo:

- Regra 1: A moto do jogador fica posicionada na base da tela, movendo-se estritamente para a esquerda e para a direita.
- Regra 2: Os obstáculos surgem no topo da tela com posições horizontais ($X$) e velocidades iniciais geradas aleatoriamente.
- Regra 3: A cada 10 segundos de sobrevivência, a velocidade base de descida de todos os obstáculos aumenta.
- Regra 4: Não há sistema de múltiplas vidas ou barra de saúde; o impacto com qualquer obstáculo destrói o veículo na hora.
- Regra 5: Pontos são computados continuamente enquanto o jogador se mantiver na pista sem colidir.

## 7. Condição de vitória

Condição de vitória:

> Por ser um jogo no formato arcade infinito, não há uma tela de vitória definitiva. O jogador atinge seu objetivo ao superar a pontuação máxima gravada no arquivo de recordes do jogo.

## 8. Condição de derrota ou encerramento

Condição de derrota ou encerramento:

> A partida termina imediatamente quando a caixa de colisão (*hitbox*) da moto interceptar a caixa de colisão de qualquer obstáculo ativo na tela. Ao colidir, o loop de jogabilidade é interrompido, exibindo a tela de fim de jogo e fechando o programa em seguida.

## 9. Elementos previstos no jogo

Descreva os principais elementos que farão parte do jogo.

## Jogador ou elemento principal

> Uma moto futurista representada por um retângulo vertical estilizado com cores neon vibrantes (como ciano ou magenta), controlada lateralmente pelas teclas do teclado.

## Obstáculos, inimigos ou desafios

> Blocos geométricos de tamanhos e cores contrastantes que surgem no topo da janela e se deslocam para baixo. Eles representam logicamente três tipos de perigos: carros de polícia (rápidos), drones (menores) e barricadas de estrada (largas).

## Itens, alvos ou objetos de interação

> Por ser um escopo focado estritamente na esquiva pura e mecânica limpa, não haverá coleta de itens na versão inicial. Toda a interação se resume a evitar o contato com as matrizes de obstáculos.

## Pontuação, vidas, tempo ou progresso

> O jogo conta com um marcador de pontuação baseado no tempo de execução do loop principal (distância percorrida). No topo da tela, um painel textual (HUD) exibe os pontos atuais e a velocidade atual do cenário. Não existem vidas adicionais (1 colisão = Game Over).

## 10. Controles previstos

Controles do grupo:

- Tecla `Seta Esquerda` ou `A`: Mover a moto para a esquerda.
- Tecla `Seta Direita` ou `D`: Mover a moto para a direita.
- Tecla `ESC`: Sair do programa imediatamente.
- Tecla `R`: Reiniciar a partida (quando estiver na tela de Game Over).

## 11. Organização inicial do código

Explique como o grupo pretende organizar o código.

Organização planejada:

> O grupo utilizará a estrutura modular proposta pelo template oficial da disciplina:
> - `main.py`: Ponto de entrada que inicializa o Pygame e dispara a execução.
> - `src/config.py`: Dicionários e constantes globais (dimensões da tela, cores neon RGB, FPS, velocidades).
> - `src/logica.py`: Funções puras de lógica, como cálculo matemático de colisões delimitadoras e incremento de dificuldade.
> - `src/arquivos.py`: Funções responsáveis pela leitura e escrita assíncrona do recorde em um arquivo externo.
> - `src/cenas.py`: Funções de renderização da pista, tratamento de eventos do teclado e controle do loop principal do jogo.

## 12. Recursos externos previstos

Recursos previstos:

> Não pretendemos utilizar recursos externos de imagem ou sprites complexos. Toda a identidade visual Cyberpunk será construída via código através da renderização de formas geométricas primitivas (retângulos e linhas) nativas do Pygame com cores personalizadas. Uma fonte TTF gratuita estilo pixelizada poderá ser incluída na pasta de assets para o HUD.

## 13. Principais dificuldades esperadas

Dificuldades previstas:

- Dificuldade 1: **Cálculo e precisão de colisão:** Garantir que a detecção de sobreposição dos blocos funcione de forma justa para o jogador, sem registrar colisões invisíveis.
- Dificuldade 2: **Gerenciamento de memória na lista de obstáculos:** Garantir que cada elemento que saia da parte inferior da tela seja removido corretamente da lista em tempo de execução para evitar travamentos.
- Dificuldade 3: **Sincronização de velocidade:** Equilibrar a taxa de atualização de quadros (FPS) com o movimento das linhas da pista para criar uma sensação real de velocidade sem distorcer os gráficos.

## 14. Escopo mínimo para a entrega final

Descreva qual será a versão mínima aceitável do jogo.

Escopo mínimo:

> Uma janela Pygame inicializada exibindo a pista com linhas móveis, controle lateral responsivo da moto, geração contínua e randômica de pelo menos um tipo de obstáculo em formato de bloco, detecção funcional de colisão que encerra o programa e salvamento persistente do recorde em um arquivo `.txt` ou `.json`.

## 15. Possíveis melhorias, caso haja tempo

Melhorias possíveis:

- Melhoria 1: Implementação de um menu inicial simples de interatividade antes de iniciar a corrida.
- Melhoria 2: Inclusão de efeitos sonoros baseados em síntese de áudio (estilo *chiptune*) para colisões e marcação de recordes.
- Melhoria 3: Adição de variações visuais nos obstáculos (formatos diferentes para drones e viaturas) e efeitos de rastro de luz neon atrás da moto.