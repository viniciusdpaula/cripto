import os
import sys
import time
import json
from typing import Dict, Any
from aes_core import (
    criptografar, 
    descriptografar_texto, 
    expansao_chave, 
    texto_para_blocos, 
    gerar_tabela_substituicao, 
    gerar_tabela_inversa
)

class GerenciadorAES:
    def __init__(self, arquivo_dados=None):
        """
        Inicializa o gerenciador AES, configurando o arquivo de dados para armazenar as configurações de tabela de substituição e chave.
        Args:
            arquivo_dados (str, opcional): Caminho para o arquivo JSON de configurações.Se não fornecido, usa um caminho padrão.
        """
        # Determina o caminho do arquivo JSON que armazena as configurações
        if arquivo_dados is None:
            script_dir = os.path.dirname(os.path.abspath(__file__)) # Diretório do script atual
            arquivo_dados = os.path.join(script_dir, "../utils/key.json")
        self.arquivo_dados = arquivo_dados
        # Carrega configurações iniciais do arquivo ou define padrões
        self.carregar_configuracoes()

    def _normalizar_tabela(self, tabela: Dict[Any, Any]) -> Dict[int, int]:
        """
        Normaliza uma tabela de substituição, garantindo que todas as entradas estejam no intervalo 0-255 e sejam inteiros.
        Args:
            tabela (Dict[Any, Any]): Tabela de substituição carregada do arquivo.
        Returns:
            Dict[int, int]: Tabela normalizada com valores válidos.
        """
        tabela_normalizada = {}
        for chave, valor in tabela.items():
            try:
                # Converte chave e valor para inteiros
                chave_int = int(chave)
                valor_int = int(valor)
                # Verifica se ambos estão no intervalo 0-255
                if 0 <= chave_int <= 255 and 0 <= valor_int <= 255:
                    tabela_normalizada[chave_int] = valor_int
            except (ValueError, TypeError):
                # Ignora entradas inválidas e informa o problema
                print(f"Ignorando entrada inválida: {chave} -> {valor}")
        return tabela_normalizada

    def carregar_configuracoes(self):
        """
        Carrega as configurações de chave e tabela de substituição do arquivo JSON. 
        Caso o arquivo não exista ou esteja corrompido, configura padrões e salva.
        """
        # Verifica se o arquivo de configurações existe; cria um vazio se necessário
        if not os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, "w") as f:
                json.dump({}, f)
        try:
            # Tenta carregar o conteúdo do arquivo
            with open(self.arquivo_dados, "r") as f:
                dados = json.load(f)
        except json.JSONDecodeError:
            # Define configurações padrão se o arquivo estiver corrompido
            dados = {}

        # Tenta carregar e normalizar a tabela de substituição
        tabela_carregada = dados.get("tabela", {})
        self.tabela = self._normalizar_tabela(tabela_carregada)
        if not self.tabela:
            # Gera uma nova tabela caso a carregada seja inválida ou vazia
            self.tabela = gerar_tabela_substituicao()

        # Define a chave padrão se nenhuma chave válida estiver presente
        self.chave = dados.get("chave", [
            0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
            0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
        ])

        # Salva as configurações normalizadas no arquivo JSON
        with open(self.arquivo_dados, "w") as f:
            json.dump({"tabela": self.tabela, "chave": self.chave}, f, indent=2)

        # Gera tabelas auxiliares e chaves expandidas para criptografia
        self.tabela_inversa = gerar_tabela_inversa(self.tabela)
        self.chaves = expansao_chave(self.chave, self.tabela)

    def criptografar_arquivo(self, arquivo_entrada, option):
        """
        Criptografa o conteúdo de um arquivo de texto usando o AES modificado.
        Args:
            arquivo_entrada (str): Caminho do arquivo de texto a ser criptografado.
        Returns:
            str: Conteúdo criptografado em hexadecimal ou None em caso de erro.
        """
        try:
            # Abre e lê o conteúdo do arquivo de entrada
            with open(arquivo_entrada, "r", encoding="utf-8") as f:
                texto = f.read()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
            return None
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None
        # Inicia o processo de criptografia
        inicio = time.time()
        blocos = texto_para_blocos(texto) # Divide o texto em blocos para AES
        blocos_criptografados = criptografar(blocos, self.chaves, self.tabela)
        resultado_hex = "" # Armazena o resultado criptografado em hexadecimal
        try:
            # Concatena os blocos criptografados em formato hexadecimal
            for bloco in blocos_criptografados:
                for linha in bloco:
                    resultado_hex += ''.join(f"{byte:02x}" for byte in linha)
            print(f"{resultado_hex}")
            if option != '-c':
                print(f"Tempo de criptografia: {time.time() - inicio:.6f} segundos")
            return resultado_hex
        except Exception as e:
            print(f"Erro ao salvar arquivo criptografado: {e}")
            return None

    def descriptografar_arquivo(self, arquivo_entrada='', texto=None):
        """
        Descriptografa o conteúdo hexadecimal de um arquivo ou string.
        Args:
            arquivo_entrada (str, opcional): Caminho do arquivo com conteúdo criptografado.
            texto (str, opcional): Conteúdo criptografado em hexadecimal.
        Returns:
            str: Texto descriptografado ou None em caso de erro.
        """
        # Lê o texto criptografado do arquivo se não for fornecido diretamente
        if texto is None:
            try:
                with open(arquivo_entrada, "r") as f:
                    texto = f.read().strip()
            except FileNotFoundError:
                print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
                return ""
            except IOError as e:
                print(f"Erro ao abrir o arquivo '{arquivo_entrada}': {e}")
                return ""
        # Realiza a descriptografia do conteúdo
        inicio = time.time()
        texto_descriptografado = descriptografar_texto(texto, self.chaves, self.tabela_inversa)
        if texto_descriptografado:
            print(f"Tempo de descriptografia: {time.time() - inicio:.6f} segundos")
            print(f"Mensagem decifrada: {texto_descriptografado}")
            return texto_descriptografado
        print("Erro ao descriptografar o arquivo.")
        return None

    def processar_arquivo(self, arquivo_original):
        """
        Executa o processo completo de criptografia e descriptografia, verificando se o conteúdo descriptografado é igual ao original.
        Args:
            arquivo_original (str): Caminho do arquivo original.
        Returns:
            bool: True se o processo foi bem-sucedido, False caso contrário.
        """
        # Inicia o processamento
        inicio = time.time()
        # Criptografa o conteúdo do arquivo
        resultado_hex = self.criptografar_arquivo(arquivo_original, option='-p')
        if not resultado_hex:
            return False
        # Descriptografa o conteúdo criptografado
        texto_descriptografado = self.descriptografar_arquivo(texto=resultado_hex)
        if not texto_descriptografado:
            return False
        # Lê o texto original do arquivo para comparação
        try:
            with open(arquivo_original, "r", encoding="utf-8") as f_original:
                texto_original = f_original.read()
        except Exception as e:
            print(f"Erro ao comparar arquivos: {e}")
            return False
        # Compara o texto original com o texto descriptografado
        resultado = texto_original == texto_descriptografado
        print(f"Tempo total de processamento: {time.time() - inicio:.6f} segundos")
        return resultado

def main():
    # Verifica se os argumentos necessários foram fornecidos
    if len(sys.argv) < 3:
        print("""Uso: python main.py <-c|-d|-p> <caminho do arquivo>
              Onde: 
                '-c': Criptografar um arquivo
                '-d': Descriptografar um arquivo
                '-p': Processamento completo. Mostrando o Tempo para criptografar, Total de Bytes convertidos, Tempo para descriptografar & Tempo total de Processamento 
              """)
        sys.exit(1) # Sai do programa se os argumentos forem insuficientes
    # Inicializa o gerenciador AES
    processador = GerenciadorAES()
    # Lê o modo de operação e o caminho do arquivo dos argumentos
    modo = sys.argv[1]
    arquivo = sys.argv[2]
    # Executa a operação correspondente com base no argumento de modo
    match modo:
        case "-c": # Realiza criptografia do arquivo especificado
            processador.criptografar_arquivo(arquivo, option='-c')
        case "-d": # Realiza descriptografia do arquivo especificado
            processador.descriptografar_arquivo(arquivo_entrada=arquivo)
        case "-p": # Executa o processamento completo (criptografar e descriptografar)
            processador.processar_arquivo(arquivo)
        case _: # Exibe mensagem de erro para modos inválidos
            print("""Modo inválido. Uso: python main.py <-c|-d|-p> <caminho do arquivo>
                  Onde: 
                    '-c': Criptografar um arquivo
                    '-d': Descriptografar um arquivo
                    '-p': Processamento completo. Mostrando o Tempo para criptografar, Total de Bytes convertidos, Tempo para descriptografar & Tempo total de Processamento 
                  """)
            sys.exit(1)

if __name__ == "__main__":
    main()