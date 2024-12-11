import os
import time
import subprocess

def processar_arquivo(input_file, output_file, chave, iv, operacao):
    """
    Processa um arquivo utilizando a criptografia OpenSSL, permitindo realizar operações
    de criptografia ou descriptografia com base na operação especificada.
    Args:
        input_file (str): Caminho para o arquivo de entrada que será processado.
        output_file (str): Caminho para o arquivo de saída onde o resultado será salvo.
        chave (str): Chave criptográfica utilizada para o processo de criptografia/descriptografia.
                     Deve ser uma string hexadecimal representando 32 bytes (256 bits).
        iv (str): Vetor de inicialização (IV) necessário para o algoritmo de criptografia.
                  Deve ser uma string hexadecimal representando 16 bytes (128 bits).
        operacao (str): Tipo de operação a ser realizada: "encrypt" para criptografar ou 
                        "decrypt" para descriptografar.
    Returns:
        float: Tempo (em segundos) gasto na operação de criptografia ou descriptografia.
               Retorna -1 em caso de falha na execução.
    Raises:
        ValueError: Se a operação especificada não for "encrypt" ou "decrypt".
        Exception: Erros gerais relacionados ao comando OpenSSL.
    """
    # Valida se a operação fornecida é válida
    if operacao not in ["-e", "-d"]:
        raise ValueError("Operação inválida. Use '-e' para criptografar ou '-d' para descriptografar.")
    # Monta o comando OpenSSL
    cmd = [
        "openssl", "enc", "-aes-256-cbc",
        operacao, "-in", input_file,
        "-out", output_file,
        "-K", chave,
        "-iv", iv
    ]
    try:
        # Marca o início do processo para calcular o tempo
        start_time = time.time()
        # Executa o comando OpenSSL
        subprocess.run(cmd, check=True)
        # Calcula o tempo de execução
        end_time = time.time()
        print(f"Tempo para {operacao} o arquivo: {end_time - start_time:.6f} segundos")
        return end_time - start_time
    except subprocess.CalledProcessError as e:
        # Captura erros do subprocess
        print(f"Erro ao executar o comando OpenSSL: {e}")
        return -1
    except Exception as e:
        # Captura erros gerais
        print(f"Erro inesperado ao {operacao} o arquivo: {e}")
        return -1

def main():
    """
    Função principal do programa que gerencia o processo de criptografia e
    descriptografia de um arquivo utilizando o algoritmo AES-256-CBC.
    O programa solicita o caminho do arquivo de entrada, realiza a criptografia, 
    descriptografia e verifica se o conteúdo do arquivo original e do arquivo 
    descriptografado são equivalentes.
    Args:
        None
    Returns:
        None
    """
    # Solicita o caminho do arquivo de entrada ao usuário
    input_file = input(f"""Hint: diretório atual -> {os.getcwd()}
                       Digite o caminho do arquivo de entrada: """)
    if not os.path.exists(input_file):
        # Verifica se o arquivo de entrada existe
        print(f"O arquivo '{input_file}' não foi encontrado.")
    else:
        # Define o caminho base relativo ao diretório de execução
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Define o diretório "saidas"
        dir_saidas = os.path.join(base_dir, "utils", "saidas")
        # Cria o diretório "saidas" caso ele não exista
        os.makedirs(dir_saidas, exist_ok=True)
        # Define os caminhos dos arquivos de saída para criptografia e descriptografia
        arquivo_criptografado = os.path.join(dir_saidas, "mensagem_criptografada.aes")
        arquivo_decifrado = os.path.join(dir_saidas, "mensagem_descriptografada.txt")
        # Gera uma chave criptográfica de 256 bits e um vetor de inicialização (IV) de 128 bits
        chave = os.urandom(32).hex()  # Chave AES-256
        iv = os.urandom(16).hex()     # IV de 16 bytes
        # Criptografa o arquivo de entrada e mede o tempo gasto
        tempo_cripto = processar_arquivo(input_file, arquivo_criptografado, chave, iv, operacao="-e")
        # Decifra o arquivo criptografado e mede o tempo gasto
        tempo_total = processar_arquivo(arquivo_criptografado, arquivo_decifrado, chave, iv, operacao="-d") + tempo_cripto
        # Compara o conteúdo do arquivo original com o arquivo descriptografado
        try:
            with open(input_file, 'r', encoding="utf-8") as original, open(arquivo_decifrado, 'r', encoding="utf-8") as descriptografado:
                texto_original = original.read()
                texto_resultante = descriptografado.read()
                # Exibe o resultado da verificação
                print("\nVerificação:")
                print("Descriptografia bem-sucedida:", texto_original == texto_resultante)
                print(f"Tempo total {tempo_total:.6f} segundos")
        except Exception as e:
            # Captura e exibe erros ao ler os arquivos
            print(f"Erro ao comparar arquivos: {e}")
            
if __name__ == "__main__":
    main()