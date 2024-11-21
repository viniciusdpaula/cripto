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
def add_round_key(matriz_bloco, chaves_rodada, tabela_substituicao, rodada):
    """
    Realiza a operação AddRoundKey com uma tabela de substituição aleatória.
    
    Parâmetros:
    - bloco: lista de bytes representando o bloco de texto (16 bytes para AES-128).
    - chave: lista de bytes representando a chave de rodada (16 bytes para AES-128).
    - tabela_substituicao: dicionário de substituição aleatória.

    Retorna:
    - Um novo bloco onde cada byte foi substituído pela tabela e XOR com a chave da rodada.
    """
    # Extrai a chave da rodada atual e transforma em uma matriz 4x4
    chave_rodada_matriz = np.array(chaves_rodada[rodada]).reshape(4, 4)

    bloco_substituido = np.zeros((4, 4), dtype=np.uint8)
    for i in range(4):
        for j in range(4):
            byte_bloco = matriz_bloco[i][j]
            byte_chave = chave_rodada_matriz[i][j]

            # XOR e substituição usando a tabela
            bloco_substituido[i][j] = tabela_substituicao[byte_bloco ^ byte_chave]
    return bloco_substituido

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

    print("Chave da rodada:", chaves_rodada)

    for i in range(1,2): 
        ## subBytes
        bloco = shift_rows(bloco)
        # print("Bloco de 16 bytes i :", i, bloco)
        bloco = mix_columns(bloco)
        # Realiza a operação AddRoundKey com substituição aleatória
        bloco = add_round_key(bloco, chaves_rodada, tabela_substituicao, i)  # Passa a rodada atual

    # Exibe o resultado
    # print("Bloco de Entrada:", [hex(x) for x in bloco])
    # print("Chave da Rodada:", [hex(x) for x in chave])
    # print("Resultado AddRoundKey:", [hex(x) for x in resultado])

if __name__ == "__main__":
    main()

matriz = np.array([
        ['d4', 'e0', 'b8', '1e'],
        ['27', 'bf', 'b4', '41'],
        ['11', '98', '5d', '52'],
        ['ae', 'f1', 'e5', '30']
    ])
# Exemplo de uma coluna da matriz M
coluna = np.array([0xd4, 0xbf, 0x5d, 0x30], dtype=np.uint8)