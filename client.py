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


def getintAcao(StrAcao):
    """
    Retorna um inteiro correspondente a acao aplicada representada pela string 'left', 'right' ou 'jump'
    :StrAcao: string que indica a acao aplicada
    :return: retorna o inteiro correspondente a acao aplicada
    """
    if (StrAcao == "left"):
        return 0
    elif (StrAcao == "right"):
        return 1
    elif (StrAcao == "jump"):
        return 2


def getLinhaTabelaQ(plataforma, direcao):
    """
    Funcao para converter o indicador da plataforma e da direcao do Amongois na linha especifica da tabela Q correspondente
    :plataforma: int que indica a plataforma do Amongois
    :direcao: int que indica a direcao do Amongois 
    :return: retorna a linha da tabela Q que representa o estado atual considerando plataforma e direcao
    """

    return (plataforma * 4) + direcao


def QLearning(matrizTabelaQ, linhaAntigoEstado, recompensaImediata, acaoAplicada, linhaNovoEstado, a=0.5, y=1):
    """
    
    :return:
    """

    taxaAprendizagem = a
    gamma = y

    intAcao = getintAcao(acaoAplicada)

    # Pega o valor 'antigo' do estado testado de acordo com a tabela Q
    valorInicialQ = matrizTabelaQ[linhaAntigoEstado][intAcao]

    novoEstadoLeft =  matrizTabelaQ[linhaNovoEstado][0] 
    novoEstadoRight = matrizTabelaQ[linhaNovoEstado][1] 
    novoEstadoJump =  matrizTabelaQ[linhaNovoEstado][2] 
    
    # Equação de bellman para atualização do valor da ação realizada
    atualizacaoValorQ = valorInicialQ + taxaAprendizagem*(recompensaImediata + gamma*(max(novoEstadoLeft, novoEstadoRight, novoEstadoJump)) - valorInicialQ) 

    matrizTabelaQ[linhaAntigoEstado][intAcao] = atualizacaoValorQ


# Realização da conexão com o jogo através da porta
conexao_jogo = cn.connect(2037)

# Listagem de ações pra fazer a equivalência do random int (que será o índice) com a string de ação
acoes = ["jump", "left", "right"]

# Gera a Tabela Q por meio de uma matriz onde as linhas são os estados e as colunas, as ações 
q_table = [[0.0 for _ in range(3)] for _ in range(96)] # 96 linhas com 3 elementos (colunas) inicializadno em 0.0


estadoAnterior = 0 # DEFINICAO DO ESTADO INICIAL

#Aqui vocês irão colocar seu algoritmo de aprendizado
# Loop do jogo
while True:
    indice = randint(0,2) # pega o índice aleatório pra ação
    acao_escolhida = acoes[indice] # obtendo, enfim, a ação randomizada

    estado, recompensa = cn.get_state_reward(conexao_jogo, acao_escolhida) # função do conecction.py que devolve o novo estado e a recompensa recebida pela ação executada

    print(f"O Amongois realizou a ação {acao_escolhida} e parou no estado {estado} com recompensa {recompensa}!") # impressão geral pra acompanhamento

    # Trata o estado e a direcao, como binarios, para obter a plataforma correspondente e a direcao nela
    bits_estado = estado[2:7] # corta a string para a parte binaria somente do estado
    plataforma = getBinario(bits_estado) # converte

    bits_direcao = estado[7:9] # corta a string para a parte binaria somente da direcao
    direcao = getBinario(bits_direcao) # converte

    # Pega a linha da tabela correspondente a esse estado novo alcancado
    linhaNovoEstado = getLinhaTabelaQ(plataforma, direcao)

    # Aplicação do Q-Learning para atualização do valor da ação executada no estado atual
    if (estadoAnterior is not None):
        QLearning(q_table, estadoAnterior, recompensa, acao_escolhida, linhaNovoEstado)

    # Detecção de morte
    if (recompensa == -1): 
        estado_anterior = 0
        continue # continua para a nova execucao

    # Armazenamento das execuções anteriores para a nova iteração do Q-Learning
    estadoAnterior = linhaNovoEstado
    # acaoAnterior = acao_escolhida

    print(f"{q_table[estadoAnterior]}")
    print()


