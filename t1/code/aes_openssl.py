import os
import subprocess
import time
# Funçao generica, abre um processo do openssl para criptografar ou decifrar,de acordo com a operação.
def processar_arquivo(input_file, output_file, chave, iv, operacao):

    cmd = [
        "openssl", "enc", "-aes-256-cbc",
        operacao, "-in", input_file,
        "-out", output_file,
        "-K", chave.hex(),
        "-iv", iv.hex()
    ]

    try:
        start_time = time.time()
        subprocess.run(cmd, check=True)
        end_time = time.time()
        print(f"Tempo para {operacao} o arquivo: {end_time - start_time:.6f} segundos")
        return end_time - start_time
    except Exception as e:
        print(f"Erro ao {operacao} o arquivo: {e}")

# Solicita o caminho do arquivo ao usuário
input_file = input("Digite o caminho do arquivo de entrada: ")

if not os.path.exists(input_file):
    print(f"O arquivo '{input_file}' não foi encontrado.")
else:
    arquivo_criptografado = "../utils/saidas/mensagem_criptografada.aes"
    arquivo_decifrado = "../utils/saidas/mensagem_descriptografada.txt"

    # Gera a chave e o IV aleatoriamente
    chave = os.urandom(32)  # Chave AES-256 bits
    iv = os.urandom(16)     # IV de 16 bytes

    # Criptografa o arquivo
    tempo_cripto = processar_arquivo(input_file, arquivo_criptografado, chave, iv, operacao="-e")

    # Decifra o arquivo
    tempo_total = processar_arquivo(arquivo_criptografado, arquivo_decifrado, chave, iv, operacao="-d") + tempo_cripto

    # Compara os arquivos originais e descriptografados
    with open(input_file, 'r', encoding="utf-8") as original, open(arquivo_decifrado, 'r', encoding="utf-8") as descriptografado:
        texto_original = original.read()
        texto_resultante = descriptografado.read()

        print("\nVerificação:")
        print("Descriptografia bem-sucedida:", texto_original == texto_resultante)
        print(f"Tempo total {tempo_total:.6f}")
