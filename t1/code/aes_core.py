import numpy as np
import time 
import random

# Multiplicadores
multiplicadores_mix = [0x02, 0x03, 0x01, 0x01]
multiplicadores_mix_inv = [0x0e, 0x0b, 0x0d, 0x09]

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

# Geração de tabelas
def gerar_tabela_substituicao():
    valores = list(range(256))
    random.shuffle(valores)
    return {i: valores[i] for i in range(256)}
# Gera a tabela inversa para descriptografar
def gerar_tabela_inversa(tabela_substituicao):
    return {v: k for k, v in tabela_substituicao.items()}

# Manipulação de texto e blocos
def texto_para_blocos(texto):
    texto_bytes = texto.encode('utf-8')  # Codifica o texto em UTF-8
    padding_len = (16 - len(texto_bytes) % 16) % 16  # Calcular padding necessário

    # Adiciona o padding apenas para completar múltiplos de 16 bytes
    texto_bytes_padded = texto_bytes + b'\x00' * padding_len
    
    blocos = []
    for i in range(0, len(texto_bytes_padded), 16):
        bloco = np.array([list(texto_bytes_padded[j:j+4]) for j in range(i, i+16, 4)], dtype=np.uint8)
        blocos.append(bloco)

    return blocos


# Transforma um bloco em texto
def blocos_para_texto(blocos):
    texto = ''.join(''.join((b) for b in linha) for bloco in blocos for linha in bloco)
    return texto

def blocos_para_lista_bytes(blocos):
    return [byte for bloco in blocos for linha in bloco for byte in linha]

    
def bytes_para_texto(lista_bytes):
    # Converte a lista de bytes em um objeto bytes
    bytes_data = bytes(lista_bytes)
    
    # Decodifica os bytes em uma string UTF-8, ignorando valores inválidos
    return bytes_data.decode('utf-8', errors='ignore').rstrip('\x00')

# Operaçao mix_columns do AES original
def mix_columns(matriz, inverso=False):
    multiplicadores = multiplicadores_mix_inv if inverso else multiplicadores_mix
    matriz_resultante = np.zeros((4, 4), dtype=np.uint8)

    for c in range(4):  # Para cada coluna da matriz
        coluna = matriz[:, c]
        for i in range(4):  # Para cada linha da coluna
            resultado = 0
            for j in range(4):
                resultado ^= galois_multiply(multiplicadores[j], coluna[(i + j) % 4])
            
            matriz_resultante[i, c] = resultado

    return matriz_resultante

# Substituindo a caixa S, funcao que substitui pelo byte correspondente na tabela
def substitute_bytes(matriz, tabela):
    return np.vectorize(lambda b: tabela[b])(matriz)

#Operaçao shift_rows do AES original    
def shift_rows(matriz, inverso=False):
    direcao = 1 if inverso else -1
    for i in range(1, 4):
        matriz[i] = np.roll(matriz[i], i * direcao)
    return matriz

## Adiciona a chave da rodada
def add_round_key(matriz_bloco, chave_rodada):
    chave_rodada_matriz = np.array(chave_rodada).reshape(4, 4)
    return np.bitwise_xor(matriz_bloco, chave_rodada_matriz)

# Expande a chave inicial para as varias chaves da rodada (10)
def expansao_chave(chave_inicial, tabela_substituicao, num_rodadas=10):
    W = [chave_inicial[i:i+4] for i in range(0, 16, 4)]
    Rcon = [1 << (i - 1) for i in range(1, num_rodadas + 1)]
    for i in range(4, 4 * (num_rodadas + 1)):
        temp = W[i - 1]
        if i % 4 == 0:
            temp = [tabela_substituicao[b] for b in temp[1:] + temp[:1]]
            temp[0] ^= Rcon[(i // 4) - 1]
        W.append([(W[i - 4][j] ^ temp[j]) & 0xFF for j in range(4)])
    return [sum(W[4*i:4*(i+1)], []) for i in range(num_rodadas + 1)]

def criptografar(blocos, chaves, tabela, num_rodadas=10):
    for i in range(len(blocos)):
        bloco = blocos[i]
        bloco = add_round_key(bloco, chaves[0])
        for j in range(1, num_rodadas):
            bloco = substitute_bytes(bloco, tabela)
            bloco = shift_rows(bloco)
            bloco = mix_columns(bloco, inverso=False)
            bloco = add_round_key(bloco, chaves[j])
        bloco = substitute_bytes(bloco, tabela)
        bloco = shift_rows(bloco)
        bloco = add_round_key(bloco, chaves[num_rodadas])
        blocos[i] = bloco  # Atualiza o bloco no array original
    return blocos

def descriptografar(blocos, chaves, tabela_inversa, num_rodadas=10):
    for i in range(len(blocos)):
        bloco = blocos[i]
        bloco = add_round_key(bloco, chaves[num_rodadas])
        bloco = shift_rows(bloco, inverso=True)
        bloco = substitute_bytes(bloco, tabela_inversa)
        for j in range(num_rodadas - 1, 0, -1):
            bloco = add_round_key(bloco, chaves[j])
            bloco = mix_columns(bloco, inverso=True)
            bloco = shift_rows(bloco, inverso=True)
            bloco = substitute_bytes(bloco, tabela_inversa)

        bloco = add_round_key(bloco, chaves[0])
        
        blocos[i] = bloco  # Atualiza o bloco descriptografado no array original

    return blocos

##Lê um arquivo com texto criptografado, converte em blocos e os descriptografa.
def descriptografar_arquivo(nome_arquivo, chaves, tabela_inversa, num_rodadas=10):
    try:
        # Ler o conteúdo hexadecimal do arquivo
        with open(nome_arquivo, "r") as f:
            conteudo = f.read().strip()  # Remove espaços extras e quebras de linha
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return ""
    except IOError as e:
        print(f"Erro ao abrir o arquivo '{nome_arquivo}': {e}")
        return ""

    # Converter o conteúdo hexadecimal em uma lista de bytes
    bytes_conteudo = [int(conteudo[i:i+2], 16) for i in range(0, len(conteudo), 2)]
    print(f"Total de bytes convertidos: {len(bytes_conteudo)}")

    # Agrupar os bytes em blocos de 16 bytes (cada bloco é um array 4x4)
    blocos = []
    for i in range(0, len(bytes_conteudo), 16):
        bloco = bytes_conteudo[i:i+16]
        
        # Preencher com zeros se o último bloco não tiver 16 bytes completos
        if len(bloco) < 16:
            bloco += [0] * (16 - len(bloco))
        # Reshape para a estrutura 4x4
        bloco_array = np.array(bloco).reshape(4, 4)
        blocos.append(bloco_array)

    blocos_descriptografados = descriptografar(blocos, chaves, tabela_inversa, num_rodadas)
# Convertendo blocos em lista de bytes
    lista_bytes = blocos_para_lista_bytes(blocos_descriptografados)

# Decodificando bytes de volta ao texto
    texto_original = bytes_para_texto(lista_bytes)
    return texto_original
