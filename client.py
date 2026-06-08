# Importações
import connection as cn             # importação do arquivo de connection para conexão local do jogo
from random import randint, random  # importação de gerador aleatório de números pra randomização da ação
import time                         # importação de pausa para garantir integridade do loop do jogo e algoritmo
import math                         # importação para tratamento do epsilon greedy quando mudar a plataforma inicial
import os                           # importação para checar se o arquivo txt já existe


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
    :return: não retorna nada
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
    :return: retorna o indice da acao que deve ser escolhida depois da política
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


# =====================================================================
#       Function: Decaimento do epsilon para balancear
# =====================================================================
def decair_epsilon(epsilon, decay_rate, epsilon_min=0.1):
    """
    Função que faz o tratamento do epsilon para a política do Epsilon Greedy, balanceando Exploration e Exploitation nos
    melhores momentos para serem usados
    :epsilon: parâmetro que indica a chance de ocorrer exploration, e seu complemento indica exploitation
    :decayrate: parâmetro de taxa de decaimento do epsilon a cada execução
    :epsilon_min: valor mínimo que epsilon pode assumir
    :return: retorna o novo valor de epsilon apos o decaimento
    """

    if (epsilon < epsilon_min): # nao pode ficar menor que o minimo definido
        return epsilon_min
    
    return epsilon - decay_rate # desconta a taxa


# =====================================================================
#    Function: Calculo de novos epsilons quando forcar novo spawn
# =====================================================================
def calcular_epsilon_dinamico(plataforma_nova, plataforma_antiga, epsilonInicial, k=2.4, epsilon_min=0.1):
    """
    Função de cálculo para a definição do novo valor de epsilon quando forçar uma definição de um novo spawn pro Amongois. Isso é
    importante pois, se ele explorou muito uma área do mapa do antigo spawn, o epsilon já diminuiu, e forçar o spawn pra uma área pouco
    explorada exige que o epsilon suba novamente. Usa-se então a diferença da distância do novo spawn pra definir o valor de epsilon
    :plataforma_nova: nova plataforma definida como spawn atual
    :plataforma_antiga: plataforma antiga que era o spawn anterior
    :k: parâmetro pra ajustar a taxa de crescimento da sigmoide (como temos 24 plataformas, o valor padrão é 2.4)
    :epsilon_min: valor mínimo que epsilon pode assumir
    :return: retorna o novo valor de epsilon para o novo spawn
    """
    # Pega a distancia absoluta (independe de direcao negativa ou positiva)
    distancia = abs(plataforma_nova - plataforma_antiga)
        
    # Aplicacao de uma sigmoide customizada (ja que epsilon varia ate 1, essa funcao se aplica muito bem)
    # Se a distancia for pequena, retorna um valor menor, pois o Amongois nao se distanciou tanto de seu spawn, nao precisa explorar tanto
    # Se a distancia for gigante, retorna perto de 1.0, pois o Amongois precisa explorar muito essa nova area que e distante de onde ele nascia
    novo_epsilon = 1.0 / (1.0 + math.exp(-(distancia - 4) / k)) # sigmoide: (-5) pra jogar a sigmoide, e seu ponto de equilibrio que era 0 = 0.5, pra direita
    
    # Retorna o novo valor garantindo os limites entre o epsilon min e 1.0
    return max(epsilon, max(epsilon_min, min(1.0, novo_epsilon)))


# =====================================================================
#         Function: Salvar e Carregar a Q-Table
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
#                      INICIO DA APLICACAO PRO JOGO
# ======================================================================
# Realização da conexão com o jogo através da porta
conexao_jogo = cn.connect(2037)

# Listagem de ações pra fazer a equivalência do random int (que será o índice) com a string de ação
acoes = ["left", "right", "jump"]

# Puxando tabela Q do arquivo "resultado"
q_table = carregar_tabela_q("resultado.txt")

# DEFINIÇÃO DO ESTADO INICIAL
linhaAntigoEstado = 0 

# Parâmetros pro Epsilon Greedy
ultimo_spawn = 0           # guarda o ultimo spawn do boneco pra ajustar o epsilon quando mudar o spawn
epsilon = 1.0              # começa em 100% aleatório
epsilon_min = 0.1          # mantém 10% de chance exploração no final
decay_rate = 0.00025        # taxa de decaimento por ação

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
    if (recompensa != -100 and recompensa != 300): # aqui é verificado se ele nao morreu nem ganhou, implicando que o aprendizado tem que considerar a proxima casa ligada a atual
        QLearning(q_table, linhaAntigoEstado, recompensa, acao_escolhida, linhaNovoEstado) # y = 1 -> pois esta dentro de um sequenciamento de acoes


    # ============== Detecção de morte ou vitoria (quando uma sequencia de acoes acaba) ===========
    else:  # quando ele morre ou ganha
        QLearning(q_table, linhaAntigoEstado, recompensa, acao_escolhida, linhaNovoEstado, y=0) # y = 0 -> seu sequenciamento de acoes foi interrompido por uma morte/vitoria e ele respawna, entao ele nao pode considerar no aprendizado a proxima casa para valorar a atual
        
        plataforma_atual = linhaNovoEstado//4

        salvar_tabela_q(q_table) 

        if (plataforma_atual != ultimo_spawn):
            epsilon = calcular_epsilon_dinamico(plataforma_atual, ultimo_spawn, epsilon, epsilon_min=epsilon_min) # calcula o novo epsilon
            ultimo_spawn = plataforma_atual # armazena o novo estado como o ultimo spawn, onde ele reiniciara
        #time.sleep(0.4)
        
    
    print()
    print()
    print()
    # ==================== CONTROLE DE DEBUG (PRINTS) ====================
    # Vamos pegar o valor da ação específica que foi atualizada para ver o "Antes" e "Depois"
    intAcao = getintAcao(acao_escolhida)
    
    # Como o QLearning já rodar ali em cima, o ideal para ver o "Antes" 
    # de verdade seria guardar o valor antes da função. Mas usando o histórico:
    print("-" * 40)
    print(f"Estado de Origem (Plataforma {linhaAntigoEstado//4}, Dir {linhaAntigoEstado%4}):")
    print(f" -> Q-Valores atuais desta linha: {q_table[linhaAntigoEstado]}")
    print(f" -> Ação tomada aqui foi '{acao_escolhida}' (Índice {intAcao})")
    
    print(f"\nEstado de Destino Alcançado (Plataforma {linhaNovoEstado//4}, Dir {linhaNovoEstado%4}):")
    print(f" -> Q-Valores na linha de destino: {q_table[linhaNovoEstado]}")
    
    # Esse sim é o coração da sua lógica de explotação:
    maior_q_destino = max(q_table[linhaNovoEstado])
    index_melhor_acao = q_table[linhaNovoEstado].index(maior_q_destino)
    print(f" -> Se o Amongois decidir por EXPLOITATION no próximo turno, a melhor ação será: {acoes[index_melhor_acao].upper()} (Valor Q: {maior_q_destino:.4f})")
    print("-" * 40)

    # Armazenamento das execuções anteriores para a nova iteração do Q-Learning
    linhaAntigoEstado = linhaNovoEstado
