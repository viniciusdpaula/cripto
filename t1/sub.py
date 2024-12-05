import numpy as np
import random


def gerar_tabela_substituicao():
    """
    Gera uma tabela de substituição aleatória.
    """
    valores = list(range(256))
    random.shuffle(valores)
    tabela_substituicao = {i: valores[i] for i in range(256)}
    return tabela_substituicao


def compor_tabela(tabela1, tabela2):
    """
    Compoe duas tabelas de substituição.
    """
    return {k: tabela2[v] for k, v in tabela1.items()}

def gerar_tabelas_compostas(tabela_substituicao, num_rodadas):
    """
    Gera tabelas compostas para várias rodadas e suas respectivas inversas.
    """
    tabelas = {1: tabela_substituicao}  # Começa a indexar de 1
    tabelas_inversas = {1: {v: k for k, v in tabela_substituicao.items()}}

    for i in range(2, num_rodadas + 1):  # Inicia em 2, já que 1 é a primeira rodada
        tabela_composta = compor_tabela(tabelas[i - 1], tabela_substituicao)
        tabela_inversa_composta = {v: k for k, v in tabela_composta.items()}
        tabelas[i] = tabela_composta
        tabelas_inversas[i] = tabela_inversa_composta

    return tabelas, tabelas_inversas


def substitute_bytes(matriz, tabela_substituicao):
    """
    Aplica substituições de bytes em uma matriz 4x4 usando a tabela de substituição.
    """
    matriz_substituida = np.zeros((4, 4), dtype=np.uint8)
    for i in range(4):
        for j in range(4):
            matriz_substituida[i][j] = tabela_substituicao[matriz[i][j]]
    return matriz_substituida


def texto_para_bloco(texto):
    """
    Converte um texto em uma matriz 4x4 de bytes.
    """
    dados = texto.encode('utf-8')

    if len(dados) < 16:
        dados += b'\x00' * (16 - len(dados))
    elif len(dados) > 16:
        dados = dados[:16]

    matriz = [list(dados[i:i+4]) for i in range(0, 16, 4)]
    return matriz


def decrypt(bloco, tabelas_inversas):
    """
    Realiza o processo de descriptografia usando as tabelas inversas apropriadas.
    """
    bloco = substitute_bytes(bloco, tabelas_inversas[10])

    for i in range(9, 0, -1):  # Percorre os índices das tabelas inversas
        bloco = substitute_bytes(bloco, tabelas_inversas[i])
    return bloco


def main():
    # Gerar tabela de substituição inicial
    tabela_substituicao = gerar_tabela_substituicao()

    # Número de rodadas
    num_rodadas = 10

    # Gerar tabelas compostas e inversas para as rodadas
    tabelas, tabelas_inversas = gerar_tabelas_compostas(tabela_substituicao, num_rodadas)

    # Texto a ser criptografado
    texto = "Exemplo AES"
    bloco = np.array(texto_para_bloco(texto), dtype=np.uint8)

    print("Texto Original:", texto)
    print("Bloco Original:", bloco)

   # Criptografar o bloco
    for i in range(1, num_rodadas):  # Índice começa em 1
        print(i)
        bloco = substitute_bytes(bloco, tabelas[i])
    bloco = substitute_bytes(bloco, tabelas[10])

    print("Bloco Criptografado:", bloco)

    # Descriptografar o bloco
    bloco_descriptografado = decrypt(bloco, tabelas_inversas)

    print("Bloco Descriptografado:", bloco_descriptografado)


if __name__ == "__main__":
    main()
