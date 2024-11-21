import numpy as np
import os
import random

            # Encryption Process
            # INITIAL ROUND:
            # AddRoundKey
            # MAIN ROUNDSS:
            # SubBytes // S-BOX
            # ShiftRows
            # MixColumns
            # AddRoundKey

def inverse_substitute_bytes(matriz, tabela_substituicao_inversa):
    """
    Aplica a substituição inversa de bytes em uma matriz 4x4 usando a tabela de substituição inversa.
    """
    matriz_substituida = np.zeros((4, 4), dtype=np.uint8)
    for i in range(4):
        for j in range(4):
            matriz_substituida[i][j] = tabela_substituicao_inversa[matriz[i][j]]
    return matriz_substituida

def inverse_shift_rows(matriz):
    """
    Realiza a rotação inversa das linhas da matriz (ShiftRows inverso).
    """
    matriz[1] = np.roll(matriz[1], 1)  # Linha 1: rotaciona 1 posição à direita
    matriz[2] = np.roll(matriz[2], 2)  # Linha 2: rotaciona 2 posições à direita
    matriz[3] = np.roll(matriz[3], 3)  # Linha 3: rotaciona 3 posições à direita
    return matriz

def inverse_mix_columns(matriz):
    """
    Realiza a operação inversa de MixColumns em uma matriz 4x4.
    """
    multiplicadores_inversos = [0x0e, 0x0b, 0x0d, 0x09]
    matriz_resultante = np.zeros((4, 4), dtype=np.uint8)
    for c in range(4):
        coluna = matriz[:, c]
        resultado = np.zeros(4, dtype=np.uint8)
        for i in range(4):
            resultado[i] = (
                galois_multiply(multiplicadores_inversos[0], coluna[i]) ^
                galois_multiply(multiplicadores_inversos[1], coluna[(i + 1) % 4]) ^
                galois_multiply(multiplicadores_inversos[2], coluna[(i + 2) % 4]) ^
                galois_multiply(multiplicadores_inversos[3], coluna[(i + 3) % 4])
            )
        matriz_resultante[:, c] = resultado
    return matriz_resultante

def decrypt(bloco, chaves_rodada, tabela_substituicao, num_rodadas=10):
    """
    Realiza o processo de descriptografia de um bloco de 16 bytes (matriz 4x4).
    """
    # Gerar tabela inversa de substituição
    tabela_substituicao_inversa = {v: k for k, v in tabela_substituicao.items()}

    # Rodada inicial
    # bloco = add_round_key(bloco, chaves_rodada[10])
    # bloco = inverse_shift_rows(bloco)
    bloco = inverse_substitute_bytes(bloco, tabela_substituicao_inversa)

    # Rodadas principais
    for i in range(num_rodadas - 1, 0, -1):
        # bloco = add_round_key(bloco, chaves_rodada[i])
        # bloco = inverse_mix_columns(bloco)
        # bloco = inverse_shift_rows(bloco)
        bloco = inverse_substitute_bytes(bloco, tabela_substituicao_inversa)

    # Rodada final
    # bloco = add_round_key(bloco, chaves_rodada[0])
    return bloco



def substitute_bytes(matriz, tabela_substituicao):
    """
    Aplica substituições de bytes em uma matriz 4x4 usando a tabela de substituição.

    Parâmetros:
    - matriz: matriz 4x4 de bytes que será processada.
    - tabela_substituicao: dicionário de substituição aleatória.

    Retorna:
    - Uma nova matriz 4x4 após a substituição.
    """
    matriz_substituida = np.zeros((4, 4), dtype=np.uint8)
    for i in range(4):
        for j in range(4):
            matriz_substituida[i][j] = tabela_substituicao[matriz[i][j]]
    return matriz_substituida

# def add_round_key(matriz_bloco, chaves_rodada, tabela_substituicao, rodada):
#     """
#     Realiza a operação AddRoundKey com uma tabela de substituição aleatória para a chave da rodada atual.

#     Parâmetros:
#     - matriz_bloco: matriz 4x4 de bytes representando o bloco de texto.
#     - chaves_rodada: lista de chaves de rodada, onde cada chave é uma lista de 16 bytes.
#     - tabela_substituicao: dicionário de substituição aleatória.
#     - rodada: índice da rodada atual (int), para escolher a chave de rodada.

#     Retorna:
#     - Uma nova matriz 4x4 onde cada byte foi substituído pela tabela e XOR com a chave da rodada.
#     """
#     # Extrai a chave da rodada atual e transforma em uma matriz 4x4
#     chave_rodada_matriz = np.array(chaves_rodada[rodada]).reshape(4, 4)

#     # XOR entre a matriz do bloco e a matriz da chave da rodada
#     bloco_xor = np.zeros((4, 4), dtype=np.uint8)
#     for i in range(4):
#         for j in range(4):
#             bloco_xor[i][j] = matriz_bloco[i][j] ^ chave_rodada_matriz[i][j]

#     # Aplica a substituição usando a tabela
#     bloco_substituido = substitute_bytes(bloco_xor, tabela_substituicao)
#     return bloco_substituido

def add_round_key(matriz_bloco, chave_rodada):
    # Converte a chave de rodada em uma matriz 4x4
    chave_rodada_matriz = np.array(chave_rodada).reshape(4, 4)
    return np.bitwise_xor(matriz_bloco, chave_rodada_matriz)

def gerar_tabela_substituicao():
    # Cria uma lista com todos os valores de 0 a 255
    valores = list(range(256))
    # Embaralha a lista para criar uma substituição aleatória
    random.shuffle(valores)
    # Cria o dicionário de substituição onde cada valor de 0 a 255 é mapeado para um valor aleatório
    tabela_substituicao = {i: valores[i] for i in range(256)}
    return tabela_substituicao

def gerar_chave_inicial():
    # Gera uma chave inicial de 128 bits (16 bytes)
    chave_inicial = os.urandom(16)
    # Converte a chave para uma string hexadecimal
    chave_hex = chave_inicial.hex()
    return chave_hex

def dividir_chave_em_palavras(chave_hex):
    # Divide a chave em quatro partes de 32 bits (8 caracteres hexadecimais cada)
    W0 = chave_hex[0:8]
    W1 = chave_hex[8:16]
    W2 = chave_hex[16:24]
    W3 = chave_hex[24:32]
    return W0, W1, W2, W3

def galois_multiply(a, b):
    p = 0
    while b > 0:
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B  # Aplica o módulo 0x11B (polinômio irreduzível)
        b >>= 1
    return p
# Multiplicadores para MixColumns
multiplicadores = [0x02, 0x03, 0x01, 0x01]

# Aplica MixColumns a uma coluna
def mix_column(coluna):
    resultado = np.zeros(4, dtype=np.uint8)
    for i in range(4):
        resultado[i] = (galois_multiply(multiplicadores[0], coluna[i]) ^
                        galois_multiply(multiplicadores[1], coluna[(i + 1) % 4]) ^
                        galois_multiply(multiplicadores[2], coluna[(i + 2) % 4]) ^
                        galois_multiply(multiplicadores[3], coluna[(i + 3) % 4]))
    return resultado
# Aplica MixColumns a toda a

def mix_columns(matriz):
    matriz_resultante = np.zeros((4, 4), dtype=np.uint8)
    for c in range(4):
        coluna = matriz[:, c]  # Seleciona a coluna c da matriz
        matriz_resultante[:, c] = mix_column(coluna)
    return matriz_resultante

def shift_rows(matriz):
    """Rotação cíclica das linhas"""
    # Linha 0: não rotaciona
    # Linha 1: rotaciona 1 posição à esquerda
    matriz[1] = np.roll(matriz[1], -1)
    # Linha 2: rotaciona 2 posições à esquerda
    matriz[2] = np.roll(matriz[2], -2)
    # Linha 3: rotaciona 3 posições à esquerda
    matriz[3] = np.roll(matriz[3], -3)
    return matriz

def texto_para_bloco(texto):
    # Converte o texto em bytes usando a codificação UTF-8
    dados = texto.encode('utf-8')

    # Se o texto for menor que 16 bytes, adiciona padding
    if len(dados) < 16:
        dados += b'\x00' * (16 - len(dados))  # Preenche com bytes nulos (0x00)
    # Se o texto for maior que 16 bytes, trunca para os primeiros 16 bytes
    elif len(dados) > 16:
        dados = dados[:16]
    # Organiza os dados em uma matriz 4x4
    matriz = [list(dados[i:i+4]) for i in range(0, 16, 4)]

    return matriz  # Converte para uma lista de inteiros para representar o bloco

def rot_word(word):
    return word[1:] + word[:1]

def sub_word(word, tabela_substituicao):
    return [tabela_substituicao[b] for b in word]

def expansao_chave(chave_inicial, tabela_substituicao, num_rodadas=10):
    # Divide a chave inicial em palavras de 4 bytes
    W = [chave_inicial[i:i+4] for i in range(0, 16, 4)]

    # Constantes de rodada (exemplo para 10 rodadas do AES-128)
    Rcon = [1 << (i - 1) for i in range(1, num_rodadas + 1)]

    # Expande a chave para gerar palavras adicionais
    for i in range(4, 4 * (num_rodadas + 1)):
        temp = W[i - 1]

        if i % 4 == 0:
            temp = sub_word(rot_word(temp), tabela_substituicao)
            temp[0] ^= Rcon[(i // 4) - 1] & 0xFF  # Garante que Rcon fique no intervalo 0-255

        W.append([(W[i - 4][j] ^ temp[j]) & 0xFF for j in range(4)])  # Garante que cada byte esteja em 0-255

    # Agrupa em chaves de rodada de 16 bytes
    chaves_rodada = [W[4*i:4*(i+1)] for i in range(num_rodadas + 1)]
    return [sum(rodada, []) for rodada in chaves_rodada]  # Concatenando as palavras de cada

# Exibe a tabela de substituição
def printa_tabela(tabela_substituicao):
    for chave, valor in tabela_substituicao.items():
        print(f"{chave:02x} -> {valor:02x}")

def bloco_para_texto(bloco):
    """
    Converte um bloco 4x4 de bytes em uma string, removendo bytes de preenchimento e tratando bytes inválidos.

    Parâmetros:
    - bloco: matriz 4x4 de bytes representando o bloco descriptografado.

    Retorna:
    - Uma string decodificada.
    """
    texto_bytes = bytearray()
    for i in range(4):
        for j in range(4):
            texto_bytes.append(bloco[i][j])

    # Decodifica para string UTF-8, substituindo bytes inválidos


def main():
    # Gerando a chave inicial e dividindo em palavras
    chave = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
         0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    # Gera a tabela de substituição aleatória
    tabela_substituicao = gerar_tabela_substituicao()
    chaves_rodada = expansao_chave(chave, tabela_substituicao)

    # Exemplo de uso
    texto = "Exemplo AES"
    bloco = np.array(texto_para_bloco(texto), dtype=np.uint8)

    # print("Chave da rodada:", chaves_rodada)
    bloco_criptografado = add_round_key(bloco, chaves_rodada[0])
    for i in range(1,10):
        # Substituição de bytes (SubBytes)
        bloco_criptografado = substitute_bytes(bloco, tabela_substituicao)

        ## Etapa ShiftRows
        # bloco_criptografado = shift_rows(bloco)
        print("Bloco de 16 bytes i :", i)
        #  Etapa MixColumns
        # bloco_criptografado = mix_columns(bloco)
        # Realiza a operação AddRoundKey com substituição aleatória
        # bloco_criptografado = add_round_key(bloco_criptografado, chaves_rodada[i])

    bloco_criptografado = substitute_bytes(bloco, tabela_substituicao)
    bloco_criptografado = shift_rows(bloco)
    bloco_criptografado = add_round_key(bloco_criptografado, chaves_rodada[10])
    # Exibe o resultado
    # print("Bloco de Entrada:", [hex(x) for x in bloco])
    # print("Chave da Rodada:", [hex(x) for x in chave])
    # print("Resultado AddRoundKey:", [hex(x) for x in resultado])

    # Descriptografia
    bloco_descriptografado = decrypt(bloco_criptografado, chaves_rodada, tabela_substituicao)
    # Resultado
    print("Texto Original:", texto)
    print("Bloco original", bloco)
    print("Bloco Criptografado:", bloco_criptografado)
    print("Bloco Descriptografado:", bloco_descriptografado)

if __name__ == "__main__":
    main()