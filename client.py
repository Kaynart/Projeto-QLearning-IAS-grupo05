# Importações
import connection as cn # importação do arquivo de connection para conexão local do jogo
from random import randint # importação de gerador aleatório de números pra randomização da ação


def getBinario(stringBinaria):
    """
    Função para facilitar a conversão de um valor string em binário para int
    :string: string contendo o texto do valor binário
    :return: retorna o valor convertido para inteiro
    """
    return int(stringBinaria, 2)


# Realização da conexão com o jogo através da porta
conexao_jogo = cn.connect(2037)

# Listagem de ações pra fazer a equivalência do random int (que será o índice) com a string de ação
acoes = ["jump", "left", "right"]

# Loop do jogo
while True:
    indice = randint(0,2) # pega o índice aleatório pra ação
    acao_escolhida = acoes[indice] # obtendo, enfim, a ação randomizada

    estado, recompensa = cn.get_state_reward(conexao_jogo, acao_escolhida) # função do conecction.py que devolve o novo estado e a recompensa recebida pela ação executada

    print (f"O Amongois realizou a ação {acao_escolhida} e parou no estado {estado} com recompensa {recompensa}!") # impressão geral pra acompanhamento

#Aqui vocês irão colocar seu algoritmo de aprendizado