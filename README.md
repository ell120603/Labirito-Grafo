# Labirinto-Grafo

Um pequeno aplicativo de visualização e solução de labirintos em Python com interface gráfica (Tkinter).

Este projeto fornece um editor/visualizador de labirintos onde é possível:

- Desenhar paredes e caminhos manualmente.
- Definir um ponto de início (S) e fim (E).
- Gerar um labirinto aleatório.
- Escolher entre múltiplos algoritmos de busca e ver a busca animada no grid.
- Ver estatísticas da busca (nós explorados, comprimento do caminho, tempo).

## Algoritmos implementados

- BFS (Busca em Largura) — anima a expansão em camadas.
- DFS (Busca em Profundidade) — comportamento em pilha.
- Dijkstra — busca de menor custo com fila de prioridade.
- A* — com heurística de distância de Manhattan (grid sem pesos).

## Estrutura do projeto

- `main.py` — ponto de entrada. Cria a janela Tk e instancia a GUI.
- `maze_gui.py` — implementação da GUI, geração aleatória de labirintos e algoritmos de busca.

## Requisitos

- Python 3.x (testado com 3.8+)
- Tkinter (normalmente incluído com instalações padrão do Python)

Observação: não há dependências externas além da biblioteca padrão.


## Controles e uso

- Ferramenta: escolha entre desenhar paredes (`#`), caminhos (espaço), definir Início (`S`) e Fim (`E`).
- Algoritmo: selecione o algoritmo desejado no menu suspenso antes de iniciar a busca.
- Iniciar Busca: inicia animação da busca usando o algoritmo selecionado.
- Resetar Busca: para/limpa a visualização da busca (mantendo o labirinto).
- Limpar Labirinto: reseta todo o grid para caminhos vazios.
- Gerar Labirinto Aleatório: cria um labirinto aleatório (com probabilidade configurável no código).

Legenda das cores (na interface):
- Parede — cor escura
- Caminho — branco
- Início (S) — verde
- Fim (E) — vermelho
- Fronteira — cor para nós na fila/frontier
- Visitado — cor para nós já explorados
- Caminho Final — cor dourada para o caminho reconstruído

## Estatísticas

Após a busca terminar (ou falhar), a área de estatísticas será atualizada com:
- Algoritmo
- Encontrado: Sim/Não
- Nós explorados
- Comprimento do caminho (se encontrado)
- Tempo decorrido (segundos)