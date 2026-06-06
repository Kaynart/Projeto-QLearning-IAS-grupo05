# Importações
import connection as cn             # importação do arquivo de connection para conexão local do jogo
from random import randint, random  # importação de gerador aleatório de números pra randomização da ação
import time                          # importação de pausa para garantir integridade do loop do jogo e algoritmo
import os                            # importação para checar se o arquivo txt já existe

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
    Função que faz o tratamento do epsilon para a política do Epsilon Greedy
    """
    if (epsilon < epsilon_min): # nao pode ficar menor que o minimo definido
        return epsilon_min
    
    return epsilon - decay_rate # desconta a taxa


# =====================================================================
#         Function:Salvar e Carregar a Q-Table
# =====================================================================
def salvar_tabela_q(matrizTabelaQ, nome_arquivo="resultado.txt"):
    try:
        with open(nome_arquivo, "w") as f:
            for linha in matrizTabelaQ:
                # Escreve Left, Right e Jump separados por espaço, sem cabeçalhos
                f.write(f"{linha[0]} {linha[1]} {linha[2]}\n")
        
        print(f"-> [BACKUP] Tabela Q salva com sucesso em '{nome_arquivo}'!")
    
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")


def carregar_tabela_q(nome_arquivo="resultado.txt"):
    tabela = [[0.0 for _ in range(3)] for _ in range(96)]
    
    # Se a tabela já existir, tenta ler os valores do arquivo txt para continuar o treino anterior
    if os.path.exists(nome_arquivo): 
        try:
            with open(nome_arquivo, "r") as f:
                linhas = f.readlines()
                for i, linha in enumerate(linhas):
                    if i < 96:
                        valores = [float(x) for x in linha.strip().split()]
                        if len(valores) == 3:
                            tabela[i] = valores
            
            print(f"-> [SUCESSO] Memória carregada de '{nome_arquivo}'. Continuando treino anterior!")
        
        except Exception as e:
            print(f"Erro ao ler arquivo existente ({e}). Inicializando com zeros.")
    
    # Se a tabela não existir, inicia do zero
    else:
        print(f"-> [AVISO] '{nome_arquivo}' não encontrado. Iniciando cérebro do zero (0.0).")
        
    return tabela


# ======================================================================
#                     INICIO DA APLICACAO PRO JOGO
# ======================================================================
# Realização da conexão com o jogo através da porta
conexao_jogo = cn.connect(2037)

# Listagem de ações pra fazer a equivalência do random int (que será o índice) com a string de ação
acoes = ["left", "right", "jump"]

# <--- MODIFICADO: Em vez de gerar do zero fixo, ele tenta ler o arquivo txt primeiro
q_table = carregar_tabela_q("resultado.txt")

# DEFINIÇÃO DO ESTADO INICIAL
linhaAntigoEstado = 0 

# Parâmetros pro Epsilon Greedy
ultimo_spawn = 0           # guarda o ultimo spawn do boneco pra ajustar o epsilon quando mudar o spawn
epsilon = 1.0              # começa em 100% aleatório
epsilon_min = 0.1          # mantém 10% de chance exploração no final
decay_rate = 0.0005        # taxa de decaimento por ação

# variável para definir se quer mover o boneco ou somente analisar o algoritmo automatico
control = 2

# =======================================================================
#              PRATICA DO JOGO E APLICACAO DO ALGORITMO
# =======================================================================

while True:
    # =============== DECISAO MANUAL ================
    if (control == 0):
        indice = input(f"SELECIONA UMA AÇÃO [0 - left | 1 = right | 2 = jump]: ")
        acao_escolhida = acoes[int(indice)]


    # =============== DECISAO ALGORITMICA ALEATÓRIA ================
    elif (control == 1):
        indice = randint(0,2)                               # pega o índice aleatório pra ação
        acao_escolhida = acoes[indice]                      # obtendo, enfim, a ação randomizada


    # =============== DECISAO ALGORITMICA EPSILON-GREEDY ================
    elif (control == 2):
        indice = escolher_acao_EpsilonGreedy(q_table, linhaAntigoEstado, epsilon)   # pega o indice da acao escolhida pela politica Epsilon
        acao_escolhida = acoes[indice]                                              # obtendo, enfim, a ação Epsilon Greedy
        epsilon = decair_epsilon(epsilon, decay_rate, epsilon_min)                  # decai o epsilon pras proximas execucoes


    # ============ Obtencao do estado e recompensa pela acao executada ==============
    estado, recompensa = cn.get_state_reward(conexao_jogo, acao_escolhida) 

    if (control == 2) : print(f"Epsilon atual: {epsilon:.4f}")
    print(f"O Amongois realizou a ação {acao_escolhida} e parou no estado {estado} com recompensa {recompensa}!")


    # ============ Tratamento do estado e da direcao, binarios =============
    bits_estado = estado[2:7] 
    plataforma = getBinario(bits_estado) 

    bits_direcao = estado[7:9] 
    direcao = getBinario(bits_direcao) 

    # Pega a linha da tabela correspondente a esse estado novo alcancado
    linhaNovoEstado = getLinhaTabelaQ(plataforma, direcao)


    # ============== Aplicação do Q-Learning para atualização ==============
    if (recompensa != -100 and recompensa != 200): 
        QLearning(q_table, linhaAntigoEstado, recompensa, acao_escolhida, linhaNovoEstado) 


    # ============== Detecção de morte ou vitoria ===========
    else:  # quando ele morre ou ganha
        QLearning(q_table, linhaAntigoEstado, recompensa, acao_escolhida, linhaNovoEstado, y=0) 
        
        # Atualiza a tabela após derrota ou vitoria
        salvar_tabela_q(q_table, "resultado.txt")
        
        time.sleep(0.4)
        
    # Armazenamento das execuções anteriores para a nova iteração do Q-Learning
    linhaAntigoEstado = linhaNovoEstado

    print(f"Valores Q do estado atual: {q_table[linhaAntigoEstado]}")
    print("-" * 50)
