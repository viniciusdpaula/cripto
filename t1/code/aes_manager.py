import json
import time
import random
import os
import sys
from typing import List, Dict, Any
from aes_core import (
    criptografar, 
    descriptografar_texto, 
    expansao_chave, 
    texto_para_blocos, 
    blocos_para_texto, 
    gerar_tabela_substituicao, 
    gerar_tabela_inversa
)

class GerenciadorAES:
    def __init__(self, arquivo_dados=None):
        # Define o caminho absoluto para o arquivo key.json
        if arquivo_dados is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório do script
            arquivo_dados = os.path.join(script_dir, "../utils/key.json")
        self.arquivo_dados = arquivo_dados

        self.carregar_configuracoes()

    def _normalizar_tabela(self, tabela: Dict[Any, Any]) -> Dict[int, int]:
        tabela_normalizada = {}
        for chave, valor in tabela.items():
            try:
                chave_int = int(chave)
                valor_int = int(valor)
                
                # Garante que o valor esteja no intervalo correto (0-255)
                if 0 <= chave_int <= 255 and 0 <= valor_int <= 255:
                    tabela_normalizada[chave_int] = valor_int
            except (ValueError, TypeError):
                print(f"Ignorando entrada inválida: {chave} -> {valor}")
        
        return tabela_normalizada

    def carregar_configuracoes(self):
        # Criar arquivo se não existir
        if not os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, "w") as f:
                json.dump({}, f)
        
        # Carregar dados
        try:
            with open(self.arquivo_dados, "r") as f:
                dados = json.load(f)
        except json.JSONDecodeError:
            # Se o arquivo estiver corrompido, reinicia com configurações padrão
            dados = {}
        
        # Normalizar tabela ou gerar nova se houver problemas
        tabela_carregada = dados.get("tabela", {})
        self.tabela = self._normalizar_tabela(tabela_carregada)
        
        # Se a tabela estiver vazia após normalização, gera uma nova
        if not self.tabela:
            self.tabela = gerar_tabela_substituicao()
        
        # Configurar chave padrão
        self.chave = dados.get("chave", [
            0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
            0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
        ])
        # Salvar configurações normalizadas
        with open(self.arquivo_dados, "w") as f:
            json.dump({
                "tabela": self.tabela, 
                "chave": self.chave
            }, f, indent=2)
        
        # Preparar chaves e tabelas
        self.tabela_inversa = gerar_tabela_inversa(self.tabela)
        self.chaves = expansao_chave(self.chave, self.tabela)

    def criptografar_arquivo(self, arquivo_entrada):
        try:
            with open(arquivo_entrada, "r", encoding="utf-8") as f:
                texto = f.read()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
            return None
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None

        inicio = time.time()
        blocos = texto_para_blocos(texto)
        blocos_criptografados = criptografar(blocos, self.chaves, self.tabela)
        resultado_hex = ""  # Variável para armazenar o resultado
        try:
            for bloco in blocos_criptografados:
                for linha in bloco:
                    resultado_hex += ''.join(f"{byte:02x}" for byte in linha)
            print(f"{resultado_hex}")
            tempo = time.time() - inicio
            # print(f"\nTempo de criptografia: {tempo:.6f} segundos\n")
            return resultado_hex
        except Exception as e:
            print(f"Erro ao salvar arquivo criptografado: {e}")
            return None

    def descriptografar_arquivo(self, arquivo_entrada='', texto=None):

        inicio = time.time()
        if texto == None:
            try:
                # Ler o conteúdo hexadecimal do arquivo
                with open(arquivo_entrada, "r") as f:
                    texto = f.read().strip()  # Remove espaços extras e quebras de linha
                    print(texto)
            except FileNotFoundError:
                print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
                return ""
            except IOError as e:
                print(f"Erro ao abrir o arquivo '{arquivo_entrada}': {e}")
                return ""         
        texto_descriptografado = descriptografar_texto(texto, self.chaves, self.tabela_inversa)
        
        if texto_descriptografado:
            tempo = time.time() - inicio
            print(f"Tempo de descriptografia: {tempo:.6f} segundos")
            print(f"Mensagem decifrada: {texto_descriptografado}")
            return texto_descriptografado
        
        print("Erro ao descriptografar o arquivo.")
        return None

    def processar_arquivo(self, arquivo_original):
        # Processo completo: criptografar e descriptografar
        inicio = time.time()
        
        # Criptografar
        resultado_hex = self.criptografar_arquivo(arquivo_original)
        if not resultado_hex:
            return False
        
        # Descriptografar
        texto_descriptografado = self.descriptografar_arquivo(texto=resultado_hex)
        if not texto_descriptografado:
            return False
        # Comparar conteúdo dos arquivos
        try:
            with open(arquivo_original, "r", encoding="utf-8") as f_original:
                texto_original = f_original.read()
        except Exception as e:
            print(f"Erro ao comparar arquivos: {e}")
            return False
        
        resultado = texto_original == texto_descriptografado
        tempo_total = time.time() - inicio
        
        print(f"Tempo total de processamento: {tempo_total:.6f} segundos")
        print(" Processamento concluído" if resultado else "Processamento falhou")
        
        return resultado

def main():
    if len(sys.argv) < 3:
        print("Uso: python main.py <-c|-d|-p> <caminho do arquivo>")
        sys.exit(1)

    processador = GerenciadorAES()
    modo = sys.argv[1]
    arquivo = sys.argv[2]

    if modo == "-c":
        processador.criptografar_arquivo(arquivo)
    elif modo == "-d":
        processador.descriptografar_arquivo(arquivo_entrada=arquivo)
    elif modo == "-v":
        processador.processar_arquivo(arquivo)
    else:
        print("Modo inválido. Use '-c' para criptografar, '-d' para descriptografar, '-p' para processamento completo.")
        sys.exit(1)

if __name__ == "__main__":
    main()