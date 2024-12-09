### **Documentação do Trabalho AES**

#### **Objetivo**
O objetivo do trabalho é implementar uma versão simplificada do AES (Advanced Encryption Standard) substituindo a Caixa-S por outra cifra de substituição e comparar o custo de sua execução com uma implementação do AES utilizando a OpenSSL. Decidimos substituir a Caixa-S por uma cifra monoalfabética. Ele permite criptografar e descriptografar arquivos de texto em dois modos de operação:

- **`-c` (Criptografar):** Converte um texto em um formato criptografado e salva no arquivo `texto_criptografado.txt`.
- **`-d` (Descriptografar):** Converte o texto criptografado de volta ao formato original e salva no arquivo `texto_descriptografado.txt`.
- **`-v` (Analise):** Converte um texto em um formato criptografado e converto para seu formato original.Além disso faz o calculo de tempo para criptografar e descriptografar.
---

### **Arquitetura do Código**

O programa está dividido em 3 arquivos principais:
2. **`aes.py`:** Implementa as operações principais do AES, como as transformações `MixColumns`, `ShiftRows`, e funções de criptografia/descriptografia.
3. **`main.py`:** Controla o fluxo principal do programa, lidando com entrada e saída de dados, e gerencia os modos de operação (`-c` e `-d`).

---

### **Descrição dos Arquivos**


#### **2. `aes.py`**
Este arquivo contém a implementação do algoritmo AES além de utilitários usados em várias partes do programa.

**Funções:**
- **`galois_multiply(a, b)`**
  - Realiza a multiplicação de dois números no campo de Galois \( GF(2^8) \) usando o polinômio irreduzível \( x^8 + x^4 + x^3 + x + 1 \) (0x11B).
  - **Entrada:** Dois inteiros `a` e `b`.
  - **Saída:** Resultado da multiplicação.

- **`verificar_chave(chave)`**
  - Valida se a chave fornecida é uma lista de 16 bytes.
  - **Entrada:** Uma lista de inteiros.
  - **Saída:** `True` se válida, caso contrário, `False`.

- **`verificar_tabela(tabela)`**
  - Valida se uma tabela de substituição contém 256 valores exclusivos.
  - **Entrada:** Um dicionário.
  - **Saída:** `True` se válida, caso contrário, `False`.
  ### A caixa S foi substituida por uma tabela de substituição 
- **`gerar_tabela_substituicao()`**
  - Gera uma tabela de substituição aleatória.
  - **Saída:** Um dicionário com 256 valores mapeados.

- **`gerar_tabela_inversa(tabela_substituicao)`**
  - Gera a tabela inversa (S-Box inversa) a partir de uma tabela de substituição.
  - **Entrada:** Um dicionário representando a tabela.
  - **Saída:** Um dicionário representando a tabela inversa.

- **`texto_para_blocos(texto)`**
  - Divide o texto em blocos de 16 bytes e converte para matrizes 4x4.
  - **Entrada:** Uma string.
  - **Saída:** Lista de blocos (matrizes 4x4).

- **`blocos_para_texto(blocos)`**
  - Converte blocos de matrizes 4x4 de volta para uma string.
  - **Entrada:** Lista de blocos (matrizes 4x4).
  - **Saída:** Uma string.
  
- **`mix_columns(matriz, inverso=False)`**
  - Aplica a operação `MixColumns` ou sua inversa em uma matriz 4x4.
  - **Entrada:** Matriz 4x4 (`np.array`), booleano `inverso`.
  - **Saída:** Matriz transformada.

- **`substitute_bytes(matriz, tabela)`**
  - Aplica substituições de bytes em uma matriz usando a tabela de substituição fornecida.
  - **Entrada:** Matriz 4x4 e tabela de substituição.
  - **Saída:** Matriz transformada.

- **`shift_rows(matriz, inverso=False)`**
  - Aplica a operação `ShiftRows` ou sua inversa em uma matriz 4x4.
  - **Entrada:** Matriz 4x4 (`np.array`), booleano `inverso`.
  - **Saída:** Matriz transformada.

- **`add_round_key(matriz_bloco, chave_rodada)`**
  - Aplica a chave de rodada a um bloco (matriz 4x4) usando XOR.
  - **Entrada:** Matriz 4x4 e chave expandida.
  - **Saída:** Matriz transformada.

- **`expansao_chave(chave_inicial, tabela_substituicao, num_rodadas=10)`**
  - Gera as chaves expandidas para todas as rodadas do AES.
  - **Entrada:** Chave inicial (16 bytes), tabela de substituição, número de rodadas.
  - **Saída:** Lista de chaves expandidas.

- **`criptografar(blocos, chaves, tabela, num_rodadas=10)`**
  - Criptografa blocos de texto usando o AES.
  - **Entrada:** Lista de blocos, chaves expandidas, tabela de substituição.
  - **Saída:** Lista de blocos criptografados.

- **`descriptografar(blocos, chaves, tabela_inversa, num_rodadas=10)`**
  - Descriptografa blocos de texto usando o AES.
  - **Entrada:** Lista de blocos criptografados, chaves expandidas, tabela inversa.
  - **Saída:** Lista de blocos descriptografados.

- **`descriptografar_arquivo(nome_arquivo, chaves, tabela_inversa, num_rodadas=10)`**
  - Lê um arquivo criptografado, converte-o em blocos e descriptografa.
  - **Entrada:** Nome do arquivo, chaves expandidas, tabela inversa.
  - **Saída:** Texto descriptografado.

---

#### **3. `main.py`**
Controla o fluxo principal do programa e gerencia os modos de operação.

**Funções:**
- **`carregar_arquivo_json(nome_arquivo)`**
  - Lê um arquivo JSON e corrige o formato das tabelas, garantindo que as chaves sejam inteiras.
  - **Entrada:** Nome do arquivo JSON.
  - **Saída:** Dados carregados (tabelas e chave).

- **`salvar_arquivo_json(nome_arquivo, dados)`**
  - Salva os dados fornecidos em um arquivo JSON.
  - **Entrada:** Nome do arquivo JSON e dados.

- **`salvar_texto_criptografado(blocos, nome_arquivo="texto_criptografado.txt")`**
  - Salva os blocos criptografados em um arquivo no formato hexadecimal.
  - **Entrada:** Lista de blocos criptografados, nome do arquivo.

- **`main()`**
  - Ponto de entrada do programa.
  - Gerencia os modos `-c` e `-d`:
    - **`-c`:** Criptografa o texto de entrada e salva em `texto_criptografado.txt`.
    - **`-d`:** Descriptografa o arquivo criptografado e salva em `texto_descriptografado.txt`.

---

### **Exemplo de Uso**
1. **Criptografar um Arquivo:**
   ```bash
   python main.py -c texto.txt
   ```
   - Gera `texto_criptografado.txt` contendo o texto criptografado.

2. **Descriptografar um Arquivo:**
   ```bash
   python main.py -d texto_criptografado.txt
   ```
   - Gera `texto_descriptografado.txt` contendo o texto original.

---

### **Estrutura de Saída**
### Seram gerados arquivos como saidas para cada execução 

### **Executando no modo c** 
1. **Arquivo Criptografado**
### *Executando no modo d** 
1. **Arquivo Descriptografado**
### **Executando no modo v** 
1. **Arquivo Criptografado**
2. **Arquivo Descriptografado**
3. **Arquivo com o texto original para comparação**
4. **Relatorio**

#### Arquivo Criptografado (`texto_criptografado.txt`):
- Cada byte é representado em hexadecimal.
- Exemplo:
  ```
  2b7e151628aed2a6
  abf7158809cf4f3c
  ```

#### Arquivo Descriptografado (`texto_descriptografado.txt`):
- Contém o texto original em UTF-8.

---

### **Requisitos**
- **Bibliotecas:** `numpy`, `random`, `json`, `sys`, `os`.
- **Entrada:** Arquivos de texto em UTF-8.
