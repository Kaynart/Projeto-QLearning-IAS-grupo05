# Importações
import connection as cn # importação do arquivo de connection para conexão local do jogo
from random import randint # importação de gerador aleatório de números pra randomização da ação

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
#        Function: Transforma uma string de ação em inteiro
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



# ======================================================================
#                      INICIO DA APLICACAO PRO JOGO
# ======================================================================
# Realização da conexão com o jogo através da porta
conexao_jogo = cn.connect(2037)

# Listagem de ações pra fazer a equivalência do random int (que será o índice) com a string de ação
acoes = ["left", "right", "jump"]

# Gera a Tabela Q por meio de uma matriz onde as linhas são os estados e as colunas, as ações 
q_table = [[0.0 for _ in range(3)] for _ in range(96)] # 96 linhas com 3 elementos (colunas) inicializadno em 0.0


estado_anterior = 0 # DEFINICAO DO ESTADO INICIAL

# =======================================================================
#              PRATICA DO JOGO E APLICACAO DO ALGORITMO
# =======================================================================
#Aqui vocês irão colocar seu algoritmo de aprendizado

# variável para definir se quer mover o boneco ou somente analisar o algoritmo automatico
manualControl = True

# Loop do jogo
while True:
    # =============== DECISAO MANUAL ================
    if (manualControl):
        indice = input(f"SELECIONA UMA AÇÃO [0 - left | 1 = right | 2 = jump]: ")
        acao_escolhida = acoes[int(indice)] # obtendo, enfim, a acao decidida/


    # =============== DECISAO ALGORITMICA ================
    else:
        # ============ Obtencao da acao aleatoria ==============
        indice = randint(0,2) # pega o índice aleatório pra ação
        acao_escolhida = acoes[indice] # obtendo, enfim, a ação randomizada

    # ============ Obtencao do estado e recompensa pela acao executada ==============
    estado, recompensa = cn.get_state_reward(conexao_jogo, acao_escolhida) # função do conecction.py que devolve o novo estado e a recompensa recebida pela ação executada

    print(f"O Amongois realizou a ação {acao_escolhida} e parou no estado {estado} com recompensa {recompensa}!") # impressão geral pra acompanhamento

    # ============ Tratamento do estado e da direcao, binarios, para obter a plataforma correspondente e a direcao nela =============
    bits_estado = estado[2:7] # corta a string para a parte binaria somente do estado
    plataforma = getBinario(bits_estado) # converte

    bits_direcao = estado[7:9] # corta a string para a parte binaria somente da direcao
    direcao = getBinario(bits_direcao) # converte

    # Pega a linha da tabela correspondente a esse estado novo alcancado
    linhaNovoEstado = getLinhaTabelaQ(plataforma, direcao)

    # ============== Aplicação do Q-Learning para atualização do valor da ação executada no estado atual ==============
    if (estado_anterior is not None): # !!!!!!!!!!!!!!! PROVAVELMENTE ISSO PODE SER TIRADO !!!!!!!!!!!!!!!
        QLearning(q_table, estado_anterior, recompensa, acao_escolhida, linhaNovoEstado)

    # Detecção de morte
    if (recompensa == -1):  # !!!!!!!!!!!!!!! CHECAR SE A IDENTIFICACAO DE MORTE TA CERTA (ver estado e/ou recompensa de morrer) !!!!!!!!!!!!!!!
        estado_anterior = 0
        continue # continua para a nova execucao

    # Armazenamento das execuções anteriores para a nova iteração do Q-Learning
    estado_anterior = linhaNovoEstado
    # acaoAnterior = acao_escolhida

    print(f"{q_table[estado_anterior]}")
    print()