import random
import numpy as np

def galois_multiply(a, b):
    """
    Realiza a multiplicação de dois números no campo finito (Galois Field GF(2⁸)).
    A operação segue as regras do campo finito GF(2⁸), usando o polinômio irreduzível 
    0x11B para modular os resultados que excedem 8 bits.
    Args:
        a (int): Primeiro número (multiplicando).
        b (int): Segundo número (multiplicador).
    Returns:
        int: Resultado da multiplicação no campo GF(2⁸).
    """
    p = 0  # Inicializa o acumulador para o produto
    while b > 0:
        # Verifica se o bit menos significativo de b é 1
        if b & 1:
            p ^= a # Realiza a operação XOR entre o acumulador e a
        a <<= 1 # Desloca 'a' um bit para a esquerda
        # Aplica o módulo 0x11B se 'a' ultrapassar 8 bits
        if a & 0x100:
            a ^= 0x11B  # Realiza redução polinomial
        b >>= 1 # Desloca 'b' um bit para a direita
    return p

def gerar_tabela_substituicao():
    """
    Gera uma tabela de substituição aleatória para uso em criptografia.
    A tabela de substituição é um dicionário que mapeia cada byte (0-255) 
    para um valor único e aleatório no mesmo intervalo.
    Returns:
        dict: Um dicionário com 256 entradas, onde a chave é o valor original 
              (0-255) e o valor é um número aleatório único (0-255).
    """
    # Cria uma lista com todos os valores possíveis de um byte (0 a 255)
    valores = list(range(256))
    # Embaralha os valores para gerar uma substituição aleatória
    random.shuffle(valores)
    # Cria e retorna o dicionário de substituição
    return {i: valores[i] for i in range(256)} # A chave é o índice (0-255), e o valor é o elemento correspondente da lista embaralhada

def gerar_tabela_inversa(tabela_substituicao):
    """
    Gera a tabela inversa a partir de uma tabela de substituição fornecida.
    A tabela inversa é usada para descriptografia, permitindo mapear os valores 
    substituídos de volta às suas chaves originais.
    Args:
        tabela_substituicao (dict): Tabela de substituição original, onde cada 
                                    chave (0-255) mapeia para um valor único (0-255).
    Returns:
        dict: Tabela inversa, onde as chaves e valores da tabela original são trocados.
              O valor substituído torna-se a chave, e a chave original torna-se o valor.
    """
    # Retorna um dicionário onde as chaves e valores da tabela de substituição são invertidos
    return {v: k for k, v in tabela_substituicao.items()}

def texto_para_blocos(texto):
    """
    Divide o texto em blocos de 16 bytes, adicionando padding quando necessário.
    Essa função é usada para preparar o texto para criptografia no modo AES, 
    que processa blocos de tamanho fixo de 16 bytes (128 bits).
    Args:
        texto (str): O texto a ser convertido em blocos.
    Returns:
        list: Uma lista de blocos, onde cada bloco é uma matriz numpy 4x4 de inteiros (uint8).
    """
    # Converte o texto para bytes usando a codificação UTF-8
    texto_bytes = texto.encode('utf-8')
    # Calcula o número de bytes de padding necessário para atingir múltiplos de 16 bytes
    padding_len = (16 - len(texto_bytes) % 16) % 16
    # Adiciona padding (bytes de valor 0) ao final do texto para completar múltiplos de 16 bytes
    texto_bytes_padded = texto_bytes + b'\x00' * padding_len
    # Inicializa a lista para armazenar os blocos
    blocos = []
    # Divide o texto em blocos de 16 bytes
    for i in range(0, len(texto_bytes_padded), 16):
        # Cria uma matriz 4x4 para cada bloco de 16 bytes
        bloco = np.array([list(texto_bytes_padded[j:j+4]) for j in range(i, i+16, 4)], dtype=np.uint8)
        blocos.append(bloco)
    # Retorna a lista de blocos
    return blocos

def blocos_para_texto(blocos):
    """
    Converte uma lista de blocos de dados em uma string de texto.
    Essa função é usada para transformar blocos processados (criptografados ou descriptografados) de volta em uma string legível.
    Args:
        blocos (list): Lista de blocos, onde cada bloco é uma matriz numpy 4x4 contendo inteiros (uint8).
    Returns:
        str: O texto resultante da concatenação dos blocos.
    """
    # Concatena todos os bytes dos blocos em uma única string
    texto = ''.join(
        ''.join(chr(b) for b in linha) # Converte cada byte (int) de uma linha para caractere
        for bloco in blocos            # Itera sobre cada bloco
        for linha in bloco             # Itera sobre cada linha dentro do bloco
    )
    return texto

def blocos_para_lista_bytes(blocos):
    """
    Converte uma lista de blocos em uma lista linear de bytes.
    Essa função é usada para transformar blocos (matrizes 4x4) em uma sequência plana 
    de bytes, útil para operações como escrita em arquivos ou comparações diretas.
    Args:
        blocos (list): Lista de blocos, onde cada bloco é uma matriz numpy 4x4 contendo inteiros (uint8).
    Returns:
        list: Uma lista linear de bytes (valores inteiros de 0 a 255).
    """
    # Itera sobre todos os blocos, linhas e bytes, criando uma lista linear
    return [
        byte                 # Adiciona cada byte individualmente à lista
        for bloco in blocos  # Itera sobre cada bloco
        for linha in bloco   # Itera sobre cada linha dentro do bloco
        for byte in linha    # Itera sobre cada byte dentro da linha
    ]

def bytes_para_texto(lista_bytes):
    """
    Converte uma lista de bytes em uma string de texto legível.
    Essa função transforma uma sequência de bytes em uma string, decodificando os 
    valores com a codificação UTF-8 e removendo padding adicional, como bytes nulos.
    Args:
        lista_bytes (list): Uma lista de bytes (valores inteiros de 0 a 255) a ser convertida.
    Returns:
        str: A string de texto resultante da decodificação dos bytes.
    """
    # Converte a lista de bytes em um objeto do tipo bytes
    bytes_data = bytes(lista_bytes)
    # Decodifica os bytes para uma string UTF-8
    # O parâmetro `errors='ignore'` ignora valores inválidos durante a decodificação
    texto = bytes_data.decode('utf-8', errors='ignore')
    # Remove bytes nulos ('\x00') adicionais ao final da string
    texto = texto.rstrip('\x00')
    # Retorna a string decodificada e limpa
    return texto

def mix_columns(matriz, inverso=False):
    """
    Implementa a operação MixColumns do AES, responsável por embaralhar os bytes 
    em cada coluna de uma matriz 4x4. Pode ser usada tanto para criptografia 
    quanto para descriptografia.
    Args:
        matriz (numpy.ndarray): Matriz 4x4 (uint8) representando os dados do estado AES.
        inverso (bool, opcional): Se True, executa a versão inversa da operação (para descriptografia).
    Returns:
        numpy.ndarray: A matriz resultante após a operação MixColumns.
    """
    # Define os multiplicadores padrão e inverso para MixColumns
    multiplicadores_mix = [0x02, 0x03, 0x01, 0x01]  # Multiplicadores para criptografia
    multiplicadores_mix_inv = [0x0e, 0x0b, 0x0d, 0x09]  # Multiplicadores para descriptografia
    # Seleciona o conjunto de multiplicadores com base no modo (normal ou inverso)
    multiplicadores = multiplicadores_mix_inv if inverso else multiplicadores_mix
    # Inicializa a matriz resultante com zeros (tipo uint8)
    matriz_resultante = np.zeros((4, 4), dtype=np.uint8)
    # Processa cada coluna da matriz de entrada
    for c in range(4):  # Itera sobre as 4 colunas da matriz
        coluna = matriz[:, c]  # Extrai a coluna atual
        for i in range(4):  # Itera sobre as 4 linhas da coluna
            resultado = 0
            # Calcula o valor resultante aplicando os multiplicadores no campo GF(2⁸)
            for j in range(4):
                # Multiplica o byte correspondente pelo multiplicador, usando Galois Field
                resultado ^= galois_multiply(multiplicadores[j], coluna[(i + j) % 4])
            # Atribui o resultado à matriz resultante
            matriz_resultante[i, c] = resultado
    # Retorna a matriz processada
    return matriz_resultante

def substitute_bytes(matriz, tabela):
    """
    Substitui cada byte de uma matriz 4x4 pelos valores correspondentes 
    em uma tabela de substituição personalizada.
    Essa função é usada para realizar uma operação similar à etapa SubBytes do AES, 
    mas utilizando uma tabela de substituição personalizada criada pelo usuário, 
    e não a S-Box original do AES.
    Args:
        matriz (numpy.ndarray): Matriz 4x4 (uint8) representando os dados do estado AES.
        tabela (dict): Tabela de substituição personalizada, mapeando bytes (0-255) para seus valores substituídos.
    Returns:
        numpy.ndarray: Matriz 4x4 (uint8) com os bytes substituídos.
    """
    # Aplica a substituição a cada byte da matriz usando a tabela fornecida.
    # np.vectorize aplica a função a cada elemento da matriz individualmente.
    return np.vectorize(lambda b: tabela[b])(matriz)

def shift_rows(matriz, inverso=False):
    """
    Realiza a operação ShiftRows do AES em uma matriz 4x4.
    A operação ShiftRows desloca ciclicamente as linhas da matriz para a esquerda 
    (criptografia) ou para a direita (descriptografia), modificando o estado AES. 
    Args:
        matriz (numpy.ndarray): Matriz 4x4 (uint8) representando os dados do estado AES.
        inverso (bool, opcional): Se True, realiza o deslocamento na direção inversa (direita).
                                  Caso contrário, realiza o deslocamento padrão (esquerda).
    Returns:
        numpy.ndarray: A matriz 4x4 modificada após a operação ShiftRows.
    """
    # Define a direção do deslocamento: -1 para esquerda (padrão) ou 1 para direita (inverso)
    direcao = 1 if inverso else -1
    # Realiza o deslocamento para as linhas 1 a 3 (linha 0 permanece inalterada)
    for i in range(1, 4):
        # Desloca a linha `i` em `i` posições na direção definida
        matriz[i] = np.roll(matriz[i], i * direcao)
    # Retorna a matriz modificada
    return matriz

def add_round_key(matriz_bloco, chave_rodada):
    """
    Realiza a operação AddRoundKey do AES, aplicando a chave da rodada ao estado atual.
    Essa operação realiza uma soma XOR entre a matriz de estado atual e a chave 
    correspondente à rodada, combinando os dados do bloco com a chave.
    Args:
        matriz_bloco (numpy.ndarray): Matriz 4x4 (uint8) representando o estado atual do bloco.
        chave_rodada (list): Lista de 16 bytes (uint8) representando a chave da rodada.
    Returns:
        numpy.ndarray: A matriz resultante após a operação XOR com a chave da rodada.
    """
    # Converte a lista da chave da rodada em uma matriz 4x4
    chave_rodada_matriz = np.array(chave_rodada).reshape(4, 4)
    # Realiza a operação XOR entre a matriz do bloco e a chave da rodada
    return np.bitwise_xor(matriz_bloco, chave_rodada_matriz)

def expansao_chave(chave_inicial, tabela_substituicao, num_rodadas=10):
    """
    Expande a chave inicial para gerar as chaves de cada rodada do AES.
    A expansão de chave é um processo que gera várias chaves (uma para cada rodada do AES)
    a partir de uma chave inicial de 16 bytes. Utiliza operações de substituição (S-Box),
    deslocamento circular e XOR com uma constante de rodada (Rcon).
    Args:
        chave_inicial (list): Lista de 16 bytes (uint8) representando a chave inicial.
        tabela_substituicao (dict): Tabela de substituição personalizada (S-Box).
        num_rodadas (int, opcional): Número de rodadas do AES (padrão é 10).
    Returns:
        list: Lista de chaves expandidas, onde cada chave é uma lista linear de 16 bytes.
    """
    # Divide a chave inicial em 4 palavras (listas de 4 bytes cada)
    W = [chave_inicial[i:i+4] for i in range(0, 16, 4)]
    # Gera a constante de rodada Rcon (1, 2, 4, ..., 2^(num_rodadas-1))
    Rcon = [1 << (i - 1) for i in range(1, num_rodadas + 1)]
    # Gera as palavras para as chaves expandidas
    for i in range(4, 4 * (num_rodadas + 1)):
        temp = W[i - 1]  # Recupera a palavra anterior
        if i % 4 == 0:
            # Substitui e faz o deslocamento circular na palavra anterior
            temp = [tabela_substituicao[b] for b in temp[1:] + temp[:1]]
            # Aplica XOR com a constante de rodada
            temp[0] ^= Rcon[(i // 4) - 1]
        # Cria a nova palavra como XOR entre a palavra anterior e a 4 posições atrás
        W.append([(W[i - 4][j] ^ temp[j]) & 0xFF for j in range(4)])
    # Combina as palavras em chaves de 16 bytes (4 palavras por chave)
    return [sum(W[4*i:4*(i+1)], []) for i in range(num_rodadas + 1)]

def criptografar(blocos, chaves, tabela, num_rodadas=10):
    """
    Realiza a criptografia de uma lista de blocos usando o algoritmo AES modificado.
    Essa função aplica as etapas do AES a cada bloco de entrada, utilizando as 
    chaves expandidas e a tabela de substituição (S-Box) fornecidas.
    Args:
        blocos (list): Lista de blocos, onde cada bloco é uma matriz 4x4 (uint8) representando o estado inicial.
        chaves (list): Lista de chaves expandidas, onde cada chave é uma lista linear de 16 bytes.
        tabela (dict): Tabela de substituição personalizada (S-Box) para substituição de bytes.
        num_rodadas (int, opcional): Número de rodadas do AES (padrão é 10).
    Returns:
        list: Lista de blocos criptografados, com cada bloco sendo uma matriz 4x4 (uint8).
    """
    # Itera sobre todos os blocos da lista
    for i in range(len(blocos)):
        bloco = blocos[i]
        # Etapa Inicial: Aplica a chave inicial ao bloco (AddRoundKey)
        bloco = add_round_key(bloco, chaves[0])
        # Etapas Principais: realiza as rodadas intermediárias
        for j in range(1, num_rodadas):
            # Substitui os bytes do bloco usando a tabela S-Box
            bloco = substitute_bytes(bloco, tabela)
            # Realiza o deslocamento das linhas (ShiftRows)
            bloco = shift_rows(bloco)
            # Mistura as colunas para difusão (MixColumns)
            bloco = mix_columns(bloco, inverso=False)
            # Aplica a chave da rodada ao bloco (AddRoundKey)
            bloco = add_round_key(bloco, chaves[j])
        # Etapa final: aplica SubBytes, ShiftRows e AddRoundKey
        bloco = substitute_bytes(bloco, tabela)
        bloco = shift_rows(bloco)
        bloco = add_round_key(bloco, chaves[num_rodadas])
        # Atualiza o bloco no array original com o estado criptografado
        blocos[i] = bloco  
    # Retorna a lista de blocos criptografados
    return blocos

def descriptografar(blocos, chaves, tabela_inversa, num_rodadas=10):
    """
    Realiza a descriptografia de uma lista de blocos usando o algoritmo AES modificado.
    Essa função aplica as etapas inversas do AES a cada bloco de entrada, utilizando as 
    chaves expandidas e a tabela de substituição inversa (S-Box inversa) fornecidas.
    Args:
        blocos (list): Lista de blocos, onde cada bloco é uma matriz 4x4 (uint8) representando o estado criptografado.
        chaves (list): Lista de chaves expandidas, onde cada chave é uma lista linear de 16 bytes.
        tabela_inversa (dict): Tabela de substituição inversa (S-Box inversa) para substituição de bytes.
        num_rodadas (int, opcional): Número de rodadas do AES (padrão é 10).
    Returns:
        list: Lista de blocos descriptografados, com cada bloco sendo uma matriz 4x4 (uint8).
    """
    # Itera sobre todos os blocos da lista
    for i in range(len(blocos)):
        bloco = blocos[i]
        # Etapa 1: Aplica a última chave da rodada ao bloco (AddRoundKey)
        bloco = add_round_key(bloco, chaves[num_rodadas])
        # Etapa 2: Realiza as operações inversas de ShiftRows e SubBytes
        bloco = shift_rows(bloco, inverso=True)
        bloco = substitute_bytes(bloco, tabela_inversa)
        # Etapas principais: realiza as rodadas intermediárias em ordem inversa
        for j in range(num_rodadas - 1, 0, -1):
            # Aplica AddRoundKey com a chave correspondente à rodada
            bloco = add_round_key(bloco, chaves[j])
            # Realiza MixColumns na direção inversa (reversão da difusão)
            bloco = mix_columns(bloco, inverso=True)
            # Realiza o deslocamento das linhas na direção inversa (ShiftRows inverso)
            bloco = shift_rows(bloco, inverso=True)
            # Substitui os bytes do bloco usando a tabela inversa (SubBytes inverso)
            bloco = substitute_bytes(bloco, tabela_inversa)
        # Etapa final: Aplica a chave inicial (AddRoundKey) para concluir a descriptografia
        bloco = add_round_key(bloco, chaves[0])
        # Atualiza o bloco descriptografado na lista de blocos
        blocos[i] = bloco  
    # Retorna a lista de blocos descriptografados
    return blocos

def descriptografar_texto(conteudo, chaves, tabela_inversa, num_rodadas=10):
    """
    Lê texto criptografado em formato hexadecimal, converte em blocos e realiza a descriptografia.
    Essa função decodifica texto criptografado representado como uma sequência hexadecimal,
    descriptografa os dados em blocos de 16 bytes utilizando o algoritmo AES modificado, e converte o
    resultado de volta para texto legível.
    Args:
        conteudo (str): String hexadecimal representando o texto criptografado.
        chaves (list): Lista de chaves expandidas, onde cada chave é uma lista linear de 16 bytes.
        tabela_inversa (dict): Tabela de substituição inversa (S-Box inversa) para substituição de bytes.
        num_rodadas (int, opcional): Número de rodadas do AES (padrão é 10).
    Returns:
        str: Texto original descriptografado.
    """
    # Converte o conteúdo hexadecimal em uma lista de bytes
    bytes_conteudo = [int(conteudo[i:i+2], 16) for i in range(0, len(conteudo), 2)]
    print(f"Total de bytes convertidos: {len(bytes_conteudo)}")
    blocos = []
    for i in range(0, len(bytes_conteudo), 16):
        # Agrupa os bytes em blocos de 16 bytes
        bloco = bytes_conteudo[i:i+16]
        # Preenche com zeros se o último bloco tiver menos de 16 bytes(padding)
        if len(bloco) < 16:
            bloco += [0] * (16 - len(bloco))
        # Converte o bloco em uma matriz 4x4
        bloco_array = np.array(bloco).reshape(4, 4)
        blocos.append(bloco_array)
    # Descriptografa os blocos utilizando a função de descriptografia AES
    blocos_descriptografados = descriptografar(blocos, chaves, tabela_inversa, num_rodadas)
    # Converte os blocos descriptografados em uma lista linear de bytes
    lista_bytes = blocos_para_lista_bytes(blocos_descriptografados)
    # Decodifica a lista de bytes de volta em texto legível
    texto_original = bytes_para_texto(lista_bytes)
    return texto_original