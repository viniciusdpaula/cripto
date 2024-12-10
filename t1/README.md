# **Documentação do Projeto AES**

## **Descrição Geral**
O projeto implementa uma versão personalizada do AES (Advanced Encryption Standard) substituindo a S-Box padrão por uma **cifra monoalfabética personalizada**. Ele permite a **criptografia**, **descriptografia**, e **validação de desempenho** comparada à implementação do AES utilizando OpenSSL.

- **`-c` (Criptografar):** Converte um texto em um formato criptografado e salva no arquivo `texto_criptografado.txt`.
- **`-d` (Descriptografar):** Converte o texto criptografado de volta ao formato original e salva no arquivo `texto_descriptografado.txt`.
- **`-v` (Verificação Completa):** Realiza o fluxo completo de criptografia e descriptografia, comparando a saída com o texto original e reportando os tempos de execução.

---

## **Arquitetura do Projeto**

### **Diretórios**
1. **`code/`**:  
   Contém os arquivos de código principais.
   
2. **`utils/`**:  
   Contém arquivos utilitários como tabelas de substituição e chaves.

3. **`textos/`**:  
   Contém arquivos de texto usados para testes.

4. **`saidas/`**:  
   Contém os resultados das operações, como arquivos criptografados e descriptografados.


### **Estrutura de Arquivos**
1. **`aes_manager.py`**:  
   Controla o fluxo principal do programa (criptografia, descriptografia, validação).

2. **`aes_core.py`**:  
   Implementa as operações internas do AES, incluindo manipulação de texto, tabelas de substituição e transformações.

3. **`aes_openssl.py`**:  
   Integra o projeto com OpenSSL para comparações de desempenho.

4. **`key.json`**:  
   Contém a tabela de substituição e a chave de criptografia.
  
---

## **Descrição dos Arquivos e Funções**

### **1. Arquivo `aes_manager.py`**
Gerencia o fluxo principal de execução. Define a classe `GerenciadorAES`, que centraliza as operações de criptografia, descriptografia e verificação.

#### **Funções e Métodos**

##### **Classe `GerenciadorAES`**
- **`__init__(self, arquivo_dados="../utils/key.json")`**
  - Inicializa o gerenciador, carregando as configurações (chave e tabela de substituição) de um arquivo JSON.

- **`carregar_configuracoes(self)`**
  - Carrega ou cria as configurações (chave e tabela de substituição) a partir de um arquivo JSON. Se o arquivo estiver corrompido ou não existir, ele cria novos valores padrão.

2. **`criptografar_arquivo(arquivo_entrada, arquivo_saida)`**
   - **Descrição:**  
     Realiza a criptografia de um arquivo.
   - **Parâmetros:**
     - `arquivo_entrada` (str): Caminho do arquivo de texto a ser criptografado.
     - `arquivo_saida` (str): Caminho do arquivo onde a saída será salva.
   - **Retorno:**  
     Caminho do arquivo onde a saída será salva.

3. **`descriptografar_arquivo(arquivo_entrada, arquivo_saida)`**
   - **Descrição:**  
     Realiza a descriptografia de um arquivo.
   - **Parâmetros:**
     - `arquivo_entrada` (str): Caminho do arquivo criptografado.
     - `arquivo_saida` (str): Caminho do arquivo onde o texto descriptografado será salvo.
   - **Retorno:**  
     Caminho do arquivo onde o texto descriptografado será salvo.

4. **`processar_arquivo(arquivo_original)`**
   - **Descrição:**  
     Realiza a verificação completa, criptografando e descriptografando o arquivo original.
   - **Parâmetros:**
     - `arquivo_original` (str): Caminho do arquivo de texto original.
   - **Retorno:**  
     Resultado do precessamento.

##### **Função `main()`**
- **Descrição:**  
  Define o ponto de entrada do programa, processando os argumentos da linha de comando.
- **Parâmetros:**  
  Nenhum diretamente (processa `sys.argv`).
- **Retorno:**  
  Nenhum.

---

### **2. Arquivo `aes_core.py`**
Implementa as operações fundamentais do AES.

#### **Funções**

1. **`galois_multiply(a, b)`**
   - **Descrição:**  
     Realiza a multiplicação no campo de Galois GF(2⁸), usada em `MixColumns`.
   - **Parâmetros:**
     - `a` (int): Primeiro número.
     - `b` (int): Segundo número.
   - **Retorno:**  
     Resultado da multiplicação (int).

2. **`gerar_tabela_substituicao()` e `gerar_tabela_inversa(tabela)`**
   - **Descrição:**  
     Gera uma tabela de substituição e sua tabela inversa.
   - **Parâmetros:**  
     - Para `gerar_tabela_inversa`: `tabela` (dict).
   - **Retorno:**  
     - `dict`: Tabela gerada.

3. **`texto_para_blocos(texto)` e `blocos_para_texto(blocos)`**
   - **Descrição:**  
     Convertem texto para blocos de 16 bytes e vice-versa.
   - **Parâmetros:**
     - `texto` (str): Texto de entrada.
     - `blocos` (list): Lista de blocos.
   - **Retorno:**  
     Texto ou blocos convertidos.

4. **Transformações do AES**
   - **`substitute_bytes`**, **`shift_rows`**, **`mix_columns`**, **`add_round_key`**:  
     Executam transformações específicas do AES.

5. **`expansao_chave(chave_inicial, tabela_substituicao)`**
   - **Descrição:**  
     Expande uma chave inicial para gerar chaves de rodada.
   - **Parâmetros:**
     - `chave_inicial` (list): Lista de 16 bytes.
     - `tabela_substituicao` (dict): Tabela.
   - **Retorno:**  
     Lista de chaves expandidas.

6. **`criptografar` e `descriptografar`**
   - **Descrição:**  
     Criptografa ou descriptografa uma lista de blocos.
   - **Parâmetros:**  
     Blocos, chaves e tabela de substituição (ou inversa).
   - **Retorno:**  
     Lista de blocos criptografados ou descriptografados.

---

### **3. Arquivo `aes_openssl.py`**
Integra o projeto com o OpenSSL para comparações de desempenho.

#### **Funções**

1. **`processar_arquivo(input_file, output_file, chave, iv, operacao)`**
   - **Descrição:**  
     Usa o OpenSSL para criptografar ou descriptografar arquivos.
   - **Parâmetros:**
     - `input_file` (str): Caminho do arquivo de entrada.
     - `output_file` (str): Caminho do arquivo de saída.
     - `chave` (bytes): Chave de criptografia.
     - `iv` (bytes): Vetor de inicialização.
     - `operacao` (str): `-e` para criptografia ou `-d` para descriptografia.
   - **Retorno:**  
     Tempo de execução (float).

---

## **Análise de Custo Computacional do Algoritmo AES**

1. **SubBytes**: Substitui cada byte da matriz de estado pela tabela de substituição (S-Box).
2. **ShiftRows**: Desloca as linhas da matriz de estado.
3. **MixColumns**: Realiza uma operação linear nas colunas da matriz de estado.
4. **AddRoundKey**: Aplica uma operação XOR entre a matriz de estado e a chave da rodada.

---

### **1. SubBytes (Substituição de Bytes)**
- **Descrição:**  
  Cada byte da matriz de estado (totalizando 16 bytes) é substituído por um valor correspondente na tabela de substituição **S-Box**.

- **Custo Computacional:**
  - A tabela de substituição é uma operação de **busca constante (O(1))** para cada byte.
  - Total de 16 bytes no estado, portanto 16 buscas são realizadas.
  - **Custo:** \( O(16) \).

---

### **2. ShiftRows (Deslocamento de Linhas)**
- **Custo Computacional:**
  - Total de **3 linhas deslocadas** (linha 0 não é deslocada).
  - **Custo:** \( O(12) \) (pois 3 linhas são deslocadas e cada deslocamento afeta 4 elementos).

---

### **3. MixColumns (Mistura de Colunas)**
- **Custo Computacional:**
  - Como há 4 colunas, o custo total para **MixColumns** é:
    - \( 4 \text{ colunas} \times (4 \text{ multiplicações} + 3 \text{ XORs}) = 16 \text{ multiplicações} + 12 \text{ XORs} \).
  - **Custo:** \( O(16) \).

---

### **4. AddRoundKey (Adição da Chave de Rodada)**
- **Custo Computacional:**
  - Cada operação XOR entre dois bytes tem custo \( O(1) \).
  - Como são feitas 16 operações XOR, o custo é:
  - **Custo:** \( O(16) \).

---

### **5. Expansão de Chave**
- **Custo Computacional:**
  - Cada chave de rodada envolve a aplicação de **substituição** e **XOR**.
  - A chave inicial de 16 bytes é expandida em 44 palavras de 4 bytes, gerando as chaves de rodada.
  - **Custo total:** \( O(40) \), considerando 10 rodadas de expansão e as substituições e XORs necessárias.

---

## **Análise de Custo por Rodada**

### **Custo por Rodada de Criptografia**
Cada rodada de criptografia realiza as operações **SubBytes**, **ShiftRows**, **MixColumns**, e **AddRoundKey**:

| Fase            | Custo por Operação | Operações por Rodada | Custo Total |
|------------------|--------------------|-----------------------|-------------|
| **SubBytes**     | \( O(1) \)         | 16                    | \( O(16) \) |
| **ShiftRows**    | \( O(1) \)         | 12                    | \( O(12) \) |
| **MixColumns**   | \( O(1) \)         | 16                    | \( O(16) \) |
| **AddRoundKey**  | \( O(1) \)         | 16                    | \( O(16) \) |
| **Total por Rodada** |                  |                       | **\( O(60) \)** |

#### Última Rodada (Sem MixColumns)
**MixColumns** não é executado:

| Fase            | Custo por Operação | Operações por Rodada | Custo Total |
|------------------|--------------------|-----------------------|-------------|
| **SubBytes**     | \( O(1) \)         | 16                    | \( O(16) \) |
| **ShiftRows**    | \( O(1) \)         | 12                    | \( O(12) \) |
| **AddRoundKey**  | \( O(1) \)         | 16                    | \( O(16) \) |
| **Total (Última Rodada)** |               |                       | **\( O(44) \)** |

---

## **Custo Total do Algoritmo**

Considerando **10 rodadas** de AES:

- **9 Rodadas Completas** (com **MixColumns**):  
  \( 9 \times O(60) = O(540) \).

- **Última Rodada** (sem **MixColumns**):  
  \( O(44) \).

- **Expansão de Chave**:  
  \( O(40) \) para gerar as chaves de rodada.

- **Custo Total para Criptografia/Descriptografia:**  
  \( O(540 + 44 + 40) = O(624) \).

---

## **Custo do Texto de Entrada**
O custo do AES é **linearmente proporcional ao número de blocos** de 16 bytes no texto de entrada:

1. **Texto de 32 bytes (2 blocos):**  
   \( O(2 \times 624) = O(1248) \).

2. **Texto de 160 bytes (10 blocos):**  
   \( O(10 \times 624) = O(6240) \).

3. **Texto de 1024 bytes (64 blocos):**  
   \( O(64 \times 624) = O(39936) \).

---

## **Considerações**
1. A última rodada elimina **MixColumns**, reduzindo o custo.
2. A expansão de chave é linear e ocorre apenas uma vez.
3. O uso de tabelas de substituição acelera operações de substituição de bytes.
4. O custo computacional é linear em relação ao tamanho do texto de entrada.

---

## **Exemplo de Execução**

### **1. Criptografia `-c`**  
Comando:  
```bash
python aes_manager.py -c exemplo.txt
```  
Saída:  
`../utils/saidas/texto_criptografado.txt`  

**Tempo de criptografia:** 0.007567 segundos  

---

### **2. Descriptografia `-d`**  
Comando:  
```bash
python aes_manager.py -d exemplo.txt
```  
Saída:  
`../utils/saidas/texto_descriptografado.txt`  

**Total de bytes convertidos:** 32  
**Tempo de descriptografia:** 0.005801 segundos  

---

### **3. Verificação Completa `-v`**  
Comando:  
```bash
python aes_manager.py -v exemplo.txt
```  
Resultado:  
**Tempo de criptografia:** 0.005078 segundos  
**Total de bytes convertidos:** 32  
**Tempo de descriptografia:** 0.018146 segundos  
**Tempo total de processamento:** 0.031357 segundos  
**Processamento concluído**  

---

### **Estruturas de Saída**
1. Arquivo criptografado (`.txt`):  
   Texto criptografado em formato hexadecimal.
   
2. Arquivo descriptografado (`.txt`):  
   Texto original restaurado, idêntico ao original.

3. Log de comparação (`comparacao_textos.txt`):  
   Detalhes da verificação, incluindo tempos de execução.

---

## **Requisitos**
1. **Python 3.8+**
2. **Bibliotecas Necessárias:**
   - `numpy`
   - `json`
   - `subprocess`
3. **OpenSSL**.

---
