# Importações
import connection as cn             # importação do arquivo de connection para conexão local do jogo
from random import randint, random  # importação de gerador aleatório de números pra randomização da ação
import time                         # importação de pausa para garantir integridade do loop do jogo e algoritmo

# =====================================================================
#        Function: Transforma determinada binaria em inteiro
# =====================================================================
def getBinario(strBinaria):
    """
    Função para facilitar a conversão de um valor string em binário para int
    :strBinaria: string contendo o texto do valor binário
    :return: retorna o valor convertido para inteiro
    """
    return int(strBinaria, 2)


# =====================================================================
#        Function: Transforma uma string de acao em inteiro
# =====================================================================
def getintAcao(strAcao):
    """
    Retorna um inteiro correspondente a ação aplicada representada pela string 'left', 'right' ou 'jump'
    :strAcao: string que indica a acao aplicada
    :return: retorna o inteiro correspondente a acao aplicada
    """
    if (strAcao == "left"):
        return 0
    elif (strAcao == "right"):
        return 1
    elif (strAcao == "jump"):
        return 2


# =====================================================================
#      Function: Acesso a linha especifica da tabela pelo estado
# =====================================================================
def getLinhaTabelaQ(plataforma, direcao):
    """
    Função para converter a indicação da plataforma atual e da direcao atual do boneco Amongois para a linha especifica da tabela Q correspondente
    :plataforma: int que indica a plataforma do Amongois
    :direcao: int que indica a direcao do Amongois 
    :return: retorna a linha da tabela Q que representa o estado atual considerando plataforma e direcao
    """

    return (plataforma * 4) + direcao


# =====================================================================
#         Function: Atualizacao de Q valores com QLearning
# =====================================================================
def QLearning(matrizTabelaQ, linhaAntigoEstado, recompensaImediata, acaoAplicada, linhaNovoEstado, a=0.5, y=1):
    """
    Função que aplica o algoritmo de QLearning e atualiza o valor de cada acao testada e passada como parametro na matriz que representa a tabela Q;
    aplicação de aprendizado por reforço para valorar, por teste de ações, cada uma em respectivos estados
    :matrizTabelaQ: matriz que representa a tabela Q do algoritmo de aprendizado por reforço
    :linhaAntigoEstado: número da linha na tabela que representa o estado no qual aplicou-se a ação
    :recompensaImediata: valor da recompensa imediatada recebida
    :acaoAplicada: string da ação que foi aplicada
    :linhaNovoEstado: número da linha na tabela que representa o novo estado alcançado com a ação aplicada
    :a: alpha - parâmetro de taxa de aprendizado
    :y: gamma - parâmetro de valorização das ações futuras
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



# =====================================================================
#       Function: Politica de escolha de acao Epsilon Greedy
# =====================================================================
def escolher_acao_EpsilonGreedy(matrizTabelaQ, linhaEstadoAtual, epsilon):
    """
    Função com comportamento da política de escolha de ação Epsilon Greedy
    :matrizTabelaQ: matriz que representa a tabela Q do algoritmo de aprendizado por reforço
    :linhaAntigoEstado: número da linha na tabela que representa o estado no qual aplicou-se a ação
    :epsilon: parâmetro que indica a chance de ocorrer exploration, e seu complemento indica exploitation
    :return:
    """
    # Gera uma chance aleatoria entre 0.0 e 1.0
    chance = random()

    # EXPLORATION
    if (chance < epsilon):
        return randint(0, 2)                                # escolhe a acao aleatoriamente (indice)
    
    # EXPLOITATION
    else:
        valores_q_estado = matrizTabelaQ[linhaEstadoAtual]  # pega os valores pro estado atual
        maior_valor = max(valores_q_estado)                 # pega o que tem maior valor
        return valores_q_estado.index(maior_valor)          # retorna o indice dessa acao



def decair_epsilon(epsilon, decay_rate, epsilon_min=0.1):
    """
    Função que faz o tratamento do epsilon para a política do Epsilon Greedy, balanceando Exploration e Exploitation nos
    melhores momentos para serem usados
    :epsilon: parâmetro que indica a chance de ocorrer exploration, e seu complemento indica exploitation
    :decayrate: parâmetro de taxa de decaimento do epsilon a cada execução
    :epsilon_min: valor mínimo que epsilon pode assumir
    :return:
    """

    if (epsilon < epsilon_min): # nao pode ficar menor que o minimo definido
        return epsilon_min
    
    return epsilon - decay_rate # desconta a taxa

# ======================================================================
#                      INICIO DA APLICACAO PRO JOGO
# ======================================================================
# Realização da conexão com o jogo através da porta
conexao_jogo = cn.connect(2037)

# Listagem de ações pra fazer a equivalência do random int (que será o índice) com a string de ação
acoes = ["left", "right", "jump"]

# Gera a Tabela Q por meio de uma matriz onde as linhas são os estados e as colunas, as ações 
q_table = [[0.0 for _ in range(3)] for _ in range(96)] # 96 linhas com 3 elementos (colunas) inicializadno em 0.0

# DEFINIÇÃO DO ESTADO INICIAL
linhaAntigoEstado = 0 

# Parâmetros pro Epsilon Greedy
ultimo_spawn = 0           # guarda o ultimo spawn do boneco pra ajustar o epsilon quando mudar o spawn
epsilon = 1.0              # começa em 100% aleatório
epsilon_min = 0.1          # mantém 10% de chance exploração no final
decay_rate = 0.0005        # taxa de decaimento por ação

# =======================================================================
#              PRATICA DO JOGO E APLICACAO DO ALGORITMO
# =======================================================================
#Aqui vocês irão colocar seu algoritmo de aprendizado

# variável para definir se quer mover o boneco ou somente analisar o algoritmo automatico
control = 2
# 0 -> Controle Manual com jogador
# 1 -> Algoritmo QLearning com ações aleatórias
# 2 -> Algoritmo QLearning com Epsilon Greedy

# Loop do jogo
while True:
    # =============== DECISAO MANUAL ================
    if (control == 0):
        indice = input(f"SELECIONA UMA AÇÃO [0 - left | 1 = right | 2 = jump]: ")
        acao_escolhida = acoes[int(indice)]         # obtendo, enfim, a acao decidida/


    # =============== DECISAO ALGORITMICA ALEATÓRIA ================
    elif (control == 1):
        indice = randint(0,2)                       # pega o índice aleatório pra ação
        acao_escolhida = acoes[indice]              # obtendo, enfim, a ação randomizada


    # =============== DECISAO ALGORITMICA EPSILON-GREEDY ================
    elif (control == 2):
        indice = escolher_acao_EpsilonGreedy(q_table, linhaAntigoEstado, epsilon)   # pega o indice da acao escolhida pela politica Epsilon
        acao_escolhida = acoes[indice]                                              # obtendo, enfim, a ação Epsilon Greedy
        epsilon = decair_epsilon(epsilon, decay_rate, epsilon_min)                  # decai o epsilon pras proximas execucoes


    # ============ Obtencao do estado e recompensa pela acao executada ==============
    estado, recompensa = cn.get_state_reward(conexao_jogo, acao_escolhida) # função do conecction.py que devolve o novo estado e a recompensa recebida pela ação executada

    if (control == 2) : print(f"{epsilon:.4f}\n")
    print(f"O Amongois realizou a ação {acao_escolhida} e parou no estado {estado} com recompensa {recompensa}!") # impressão geral pra acompanhamento


    # ============ Tratamento do estado e da direcao, binarios, para obter a plataforma correspondente e a direcao nela =============
    bits_estado = estado[2:7] # corta a string para a parte binaria somente do estado
    plataforma = getBinario(bits_estado) # converte

    bits_direcao = estado[7:9] # corta a string para a parte binaria somente da direcao
    direcao = getBinario(bits_direcao) # converte


    # Pega a linha da tabela correspondente a esse estado novo alcancado
    linhaNovoEstado = getLinhaTabelaQ(plataforma, direcao)


    # ============== Aplicação do Q-Learning para atualização do valor da ação executada no estado atual ==============
    if (recompensa != -100 and recompensa != 200): # aqui é verificado se ele nao morreu nem ganhou, implicando que o aprendizado tem que considerar a proxima casa ligada a atual
        QLearning(q_table, linhaAntigoEstado, recompensa, acao_escolhida, linhaNovoEstado) # y = 1 -> pois esta dentro de um sequenciamento de acoes


    # ============== Detecção de morte ou vitoria (quando uma sequencia de acoes acaba) ===========
    else:  # quando ele morre ou ganha
        QLearning(q_table, linhaAntigoEstado, recompensa, acao_escolhida, linhaNovoEstado, y=0) # y = 0 -> seu sequenciamento de acoes foi interrompido por uma morte e ele reinicia, entao ele nao pode considerar no aprendizado a proxima casa para valorar a atual
        time.sleep(0.4)
        
    # Armazenamento das execuções anteriores para a nova iteração do Q-Learning
    linhaAntigoEstado = linhaNovoEstado

    print(f"{q_table[linhaAntigoEstado]}")
    print()