# AES Modificado

## Introdução
Este projeto implementa uma versão personalizada do AES, substituindo a S-Box padrão por uma tabela de substituição baseada em uma **cifra monoalfabética personalizada**. O objetivo é analisar o impacto dessa modificação no desempenho, avaliando o tempo total e o custo computacional de cada fase do algoritmo para arquivos de tamanhos variados. Além disso, os resultados serão comparados com uma implementação do AES na biblioteca OpenSSL, permitindo uma análise detalhada de eficiência e viabilidade.
Ele permite a **criptografia**, **descriptografia**, e **validação de desempenho** comparada à implementação do AES utilizando OpenSSL.

---------------------------------------------------

## Índice

1. [Substituição da Caixa-S](#substituição-da-caixa-s-por-outra-tabela-de-substituição-cifra-monoalfabética)
2. [Análise de Custo](#análise-de-custo-computacional-do-algoritmo-aes-modificado)
3. [aes_manager.py](#arquivo-aes_managerpy)
  - 3.1 [main()](#main)
  - 3.2 [GerenciadorAES](#gerenciadoraes)
  - 3.2.1 [_init()](#_initself-arquivo_dadosnone_)
  - 3.2.2 [_normalizar_tabela()](#_normalizar_tabelaself-tabela-dictany-any---dictint-int)
  - 3.2.3 [carregar_configuracoes()](#carregar_configuracoesself)
  - 3.2.4 [criptografar_arquivo()](#criptografar_arquivoself-arquivo_entrada-option)
  - 3.2.5 [descriptografar_arquivo()](#descriptografar_arquivoself-arquivo_entrada-textonone)
  - 3.2.6 [processar_arquivo()](#processar_arquivoself-arquivo_original)
4. [aes_core.py]()
5. [aes_openssl.py]()
6. [Requisitos](#requisitos)


---------------------------------------------------

### Substituição da Caixa-S por Outra Tabela de Substituição (Cifra Monoalfabética)
Nesta implementação, a S-BOX original foi substituída por uma **tabela de substituição gerada aleatoriamente**. Essa nova tabela utiliza o conceito de **Cifra Monoalfabética**, onde cada byte (0-255) é substituído por outro byte único.

#### Nova Tabela de Substituição
A nova tabela é gerada como uma permutação aleatória dos valores de 0 a 255. Isso garante que:
1. Cada byte tenha um único valor correspondente na substituição.
2. Não existam valores duplicados ou bytes não mapeados.

A tabela inversa, usada na **descriptografia**, também é gerada automaticamente, sendo o mapeamento inverso da tabela de substituição.

#### **Código para Gerar a Tabela**
(gerar_tabela_substituicao)[]

#### **Armazenamento da Tabela (key.json)**  
A tabela de substituição gerada é armazenada em um arquivo JSON chamado **`key.json`**. O formato do arquivo contém dois elementos principais:

1. **`tabela`**: Mapeamento de substituição direto.
2. **`chave`**: A chave AES usada no algoritmo.

##### Exemplo de Estrutura de `key.json`:

```json
{
    "tabela": {
        "0": 172,
        "1": 45,
        "2": 198,
        "3": 127,
        "...": "...",
        "255": 12
    },
    "chave": [43, 126, 21, 22, 40, 174, 210, 166, 171, 247, 21, 136, 9, 207, 79, 60]
}
```

Ao iniciar o programa, a tabela de substituição é carregada a partir do arquivo `key.json`. Se o arquivo não existir, uma nova tabela é gerada e salva automaticamente.

##### Código para Carregar ou Gerar a Tabela:

()[carregar_configuracoes]

#### **Funcionamento da Tabela na Criptografia**

1. Durante a criptografia, a etapa de substituição (`substitute_bytes`) usa a tabela carregada do `key.json`.
2. Na descriptografia, a tabela inversa é usada para reverter a substituição.

[Voltar ao índice](#índice)

---------------------------------------------------

### Análise de Custo Computacional do Algoritmo AES Modificado

1. **SubBytes**: Substitui cada byte da matriz de estado pela tabela de substituição (S-Box).
2. **ShiftRows**: Desloca as linhas da matriz de estado.
3. **MixColumns**: Realiza uma operação linear nas colunas da matriz de estado.
4. **AddRoundKey**: Aplica uma operação XOR entre a matriz de estado e a chave da rodada.

##### 1. SubBytes (Substituição de Bytes)
- **Descrição:**  
  Cada byte da matriz de estado (totalizando 16 bytes) é substituído por um valor correspondente na tabela de substituição **S-Box**.
- **Custo Computacional:**
  - A tabela de substituição é uma operação de **busca constante (O(1))** para cada byte.
  - Total de 16 bytes no estado, portanto 16 buscas são realizadas.
  - **Custo:** \( O(16) \).

##### 2. ShiftRows (Deslocamento de Linhas)
- **Custo Computacional:**
  - Total de **3 linhas deslocadas** (linha 0 não é deslocada).
  - **Custo:** \( O(12) \) (pois 3 linhas são deslocadas e cada deslocamento afeta 4 elementos).

##### 3. MixColumns (Mistura de Colunas)
- **Custo Computacional:**
  - Como há 4 colunas, o custo total para **MixColumns** é:
    - \( 4 \text{ colunas} \times (4 \text{ multiplicações} + 3 \text{ XORs}) = 16 \text{ multiplicações} + 12 \text{ XORs} \).
  - **Custo:** \( O(16) \).

##### 4. AddRoundKey (Adição da Chave de Rodada)
- **Custo Computacional:**
  - Cada operação XOR entre dois bytes tem custo \( O(1) \).
  - Como são feitas 16 operações XOR, o custo é:
  - **Custo:** \( O(16) \).

##### 5. Expansão de Chave
- **Custo Computacional:**
  - Cada chave de rodada envolve a aplicação de **substituição** e **XOR**.
  - A chave inicial de 16 bytes é expandida em 44 palavras de 4 bytes, gerando as chaves de rodada.
  - **Custo total:** \( O(40) \), considerando 10 rodadas de expansão e as substituições e XORs necessárias.

#### **Análise de Custo por Rodada**
##### **Custo por Rodada de Criptografia**
Cada rodada de criptografia realiza as operações **SubBytes**, **ShiftRows**, **MixColumns**, e **AddRoundKey**:

| Fase            | Custo por Operação | Operações por Rodada | Custo Total |
|------------------|--------------------|-----------------------|-------------|
| **SubBytes**     | \( O(1) \)         | 16                    | \( O(16) \) |
| **ShiftRows**    | \( O(1) \)         | 12                    | \( O(12) \) |
| **MixColumns**   | \( O(1) \)         | 16                    | \( O(16) \) |
| **AddRoundKey**  | \( O(1) \)         | 16                    | \( O(16) \) |
| **Total por Rodada** |                  |                       | **\( O(60) \)** |

##### Última Rodada (Sem MixColumns)
**MixColumns** não é executado:

| Fase            | Custo por Operação | Operações por Rodada | Custo Total |
|------------------|--------------------|-----------------------|-------------|
| **SubBytes**     | \( O(1) \)         | 16                    | \( O(16) \) |
| **ShiftRows**    | \( O(1) \)         | 12                    | \( O(12) \) |
| **AddRoundKey**  | \( O(1) \)         | 16                    | \( O(16) \) |
| **Total (Última Rodada)** |               |                       | **\( O(44) \)** |

#### **Custo Total do Algoritmo**

Considerando **10 rodadas** de AES:

- **9 Rodadas Completas** (com **MixColumns**):  
  \( 9 \times O(60) = O(540) \).

- **Última Rodada** (sem **MixColumns**):  
  \( O(44) \).

- **Expansão de Chave**:  
  \( O(40) \) para gerar as chaves de rodada.

- **Custo Total para Criptografia/Descriptografia:**  
  \( O(540 + 44 + 40) = O(624) \).

#### **Custo do Texto de Entrada**
O custo do AES é **linearmente proporcional ao número de blocos** de 16 bytes no texto de entrada:

1. **Texto de 32 bytes (2 blocos):**  
   \( O(2 \times 624) = O(1248) \).

2. **Texto de 160 bytes (10 blocos):**  
   \( O(10 \times 624) = O(6240) \).

3. **Texto de 1024 bytes (64 blocos):**  
   \( O(64 \times 624) = O(39936) \).

##### **Considerações**
1. A última rodada elimina **MixColumns**, reduzindo o custo.
2. A expansão de chave é linear e ocorre apenas uma vez.
3. O uso de tabelas de substituição acelera operações de substituição de bytes.
4. O custo computacional é linear em relação ao tamanho do texto de entrada.

[Voltar ao índice](#índice)

---------------------------------------------------

### Arquivo aes_manager.py
#### main
O arquivo aes_manager.py gerencia o fluxo principal de operações do AES personalizado, incluindo criptografia, descriptografia e verificação de consistência. Ele também implementa o carregamento de tabelas de substituição e chaves, além de permitir medições de desempenho e comparações. O script pode ser executado diretamente para realizar tarefas específicas com base em argumentos fornecidos.
[Ler mais](#aes_managerpy)

#### GerenciadorAES
O `GerenciadorAES` é uma classe que encapsula as principais funcionalidades do algoritmo AES modificado. Ele gerencia operações de criptografia e descriptografia de arquivos, incluindo o carregamento e normalização de tabelas de substituição, geração de chaves, e execução de fluxos de processamento completos com medições de desempenho. É o núcleo do sistema AES implementado.

[Ler mais](#gerenciadoraes-1)

### Arquivo aes_core.py

---------------------------------------------------


### aes_manager.py
#### main()
A função `main` é o ponto de entrada do programa, projetada para realizar operações de criptografia e descriptografia em arquivos utilizando o algoritmo AES. Ela oferece flexibilidade para diferentes modos de operação e fornece um feedback claro sobre o processamento. 

##### Funcionamento
###### 1. **Verificação de Argumentos**
   - O programa exige ao menos dois argumentos:
     1. **Modo de operação** (`-c`, `-d`, ou `-p`).
     2. **Caminho do arquivo** a ser processado.
   - Caso os argumentos estejam ausentes ou incompletos, uma mensagem de uso é exibida, e o programa é encerrado.

###### 2. **Inicialização do Gerenciador AES**
   - A função cria uma instância do objeto `GerenciadorAES`, que realiza as operações de criptografia e descriptografia.

###### 3. **Modo de Operação**
   - Com base no argumento de modo fornecido, o programa executa uma das seguintes operações:
     - **`-c` (Criptografar):**
       - Criptografa o arquivo especificado.
       - Salva o resultado em um arquivo de saída.
     - **`-d` (Descriptografar):**
       - Descriptografa o arquivo especificado.
       - Salva o texto original em um arquivo de saída.
     - **`-p` (Processamento completo):**
       - Realiza a criptografia e descriptografia do arquivo.
       - Exibe as seguintes métricas no final:
         - Tempo gasto para criptografar.
         - Total de bytes processados.
         - Tempo gasto para descriptografar.
         - Tempo total do processamento.
     - **Outros Modos:** 
       - Exibe uma mensagem de erro para argumentos inválidos e encerra o programa.

###### 4. **Tratamento de Erros**
   - Caso ocorra um erro durante o processamento (argumentos ausentes ou modo inválido), o programa fornece mensagens claras para auxiliar o usuário.

##### Exemplo de Uso
1. **Criptografar um arquivo:**
`python code/aes_manager.py -c utils/textos/texto.txt`
- **Entrada:** Arquivo com Texto em linguagem normal
- **Saída:** 
`bafd26f5322a42c8668ac41cc73551868182b7d829d282eaca4c2aced2102485df72a4a52c5fed1bf9eb86bd31a4d50f759a9a5380e94d626802590aaf4f0858`
2. **Descriptografar um arquivo criptografado:**
`python code/aes_manager.py -d texto_criptografado.txt`
- **Entrada:** Arquivo com texto criptografado
- **Saída:** 
```
Total de bytes convertidos: 64
Tempo de descriptografia: 0.005436 segundos
Mensagem decifrada: ola isso e um teste
ola isso e um teste
ola isso e um teste
```
3. **Processamento completo:**
`python code/aes_manager.py -p utils/textos/texto.txt`
- **Entrada:** Arquivo com Texto em linguagem normal
- **Saída:** 
```
bafd26f5322a42c8668ac41cc73551868182b7d829d282eaca4c2aced2102485df72a4a52c5fed1bf9eb86bd31a4d50f759a9a5380e94d626802590aaf4f0858
Tempo de criptografia: 0.005305 segundos
Total de bytes convertidos: 64
Tempo de descriptografia: 0.005388 segundos
Mensagem decifrada: ola isso e um teste
ola isso e um teste
ola isso e um teste
Tempo total de processamento: 0.010777 segundos
```
##### Mensagem de Ajuda
Se o programa for executado sem argumentos ou com argumentos inválidos, a seguinte mensagem será exibida:
```
Uso: python main.py <-c|-d|-p> <caminho do arquivo>
      Onde: 
        '-c': Criptografar um arquivo
        '-d': Descriptografar um arquivo
        '-p': Processamento completo. Mostrando o Tempo para criptografar, Total de Bytes convertidos, Tempo para descriptografar & Tempo total de Processamento 
```
[Voltar ao índice](#índice)

#### GerenciadorAES
##### Métodos Principais
- **`__init__(arquivo_dados=None)`**:
  - Inicializa o gerenciador configurando o caminho do arquivo JSON para armazenar as configurações. Caso o arquivo não exista ou esteja corrompido, cria padrões e salva.

- **`_normalizar_tabela(tabela)`**:
  - Normaliza a tabela de substituição, garantindo que todas as entradas sejam inteiras no intervalo de 0 a 255.

- **`carregar_configuracoes()`**:
  - Carrega ou cria configurações para tabelas de substituição e chaves. Também gera tabelas auxiliares e expande as chaves necessárias para o AES.

- **`criptografar_arquivo(arquivo_entrada, option)`**:
  - Criptografa o conteúdo de um arquivo de texto, retornando o resultado em hexadecimal e exibindo o tempo gasto no processo.

- **`descriptografar_arquivo(arquivo_entrada='', texto=None)`**:
  - Descriptografa o conteúdo de um arquivo ou string hexadecimal e retorna o texto original. Exibe o tempo de processamento.

- **`processar_arquivo(arquivo_original)`**:
  - Realiza o fluxo completo de criptografia e descriptografia, comparando o texto descriptografado com o original e exibindo métricas detalhadas.

[Voltar ao índice](#índice)

#### `_ini(tself, arquivo_dados=None)`

O método `__init__` da classe `GerenciadorAES` é responsável por inicializar a instância do gerenciador, configurando o caminho para o arquivo JSON que armazena as configurações de tabela de substituição e chave criptográfica. Ele também carrega ou cria as configurações iniciais necessárias para o funcionamento do algoritmo AES.

##### Argumentos
- **`arquivo_dados`** (`str`, opcional):
  - Caminho para o arquivo JSON de configurações.
  - Se não fornecido, utiliza um caminho padrão localizado no diretório `../utils/key.json`.

##### Funcionamento
1. **Determinação do Caminho do Arquivo de Configuração:**
   - Caso o argumento `arquivo_dados` não seja fornecido, utiliza o caminho padrão no diretório `../utils/key.json` com base no local do script atual.

2. **Inicialização das Configurações:**
   - Chama o método `carregar_configuracoes` para carregar as configurações do arquivo JSON.
   - Se o arquivo não existir ou estiver corrompido, define valores padrão e os salva no arquivo.

##### Observações
- Este método é projetado para garantir flexibilidade no gerenciamento de configurações, permitindo o uso de arquivos específicos ou de um padrão predefinido.
- Caso o arquivo de configurações seja inválido ou não exista, o sistema assegura que padrões válidos sejam definidos e salvos automaticamente.

[Voltar ao índice](#índice)


#### `_normalizar_tabela(self, tabela: Dict[Any, Any]) -> Dict[int, int]`
O método `_normalizar_tabela` da classe `GerenciadorAES` é utilizado para garantir que uma tabela de substituição carregada possua apenas entradas válidas. Ele filtra e converte os valores da tabela para o formato esperado, assegurando que todas as chaves e valores estejam dentro do intervalo permitido pelo algoritmo AES (0-255).

##### Argumentos
- **`tabela`** (`Dict[Any, Any]`):
  - Dicionário contendo a tabela de substituição carregada de um arquivo de configuração.
  - As chaves e os valores podem estar em formatos variados (como strings), mas precisam ser convertíveis para inteiros no intervalo 0-255.

##### Retorno
- **`Dict[int, int]`:**
  - Dicionário contendo a tabela normalizada, com todas as chaves e valores convertidos para inteiros dentro do intervalo 0-255.

##### Funcionamento
1. **Criação da Tabela Normalizada:**
   - Inicializa um dicionário vazio para armazenar a tabela validada.

2. **Validação de Entradas:**
   - Para cada par chave-valor na tabela fornecida:
     - Converte ambos para inteiros.
     - Verifica se os valores estão dentro do intervalo válido (0-255).
     - Adiciona os pares válidos ao dicionário normalizado.
   - Entradas inválidas são ignoradas, e uma mensagem de erro é exibida no console.

3. **Retorno da Tabela Normalizada:**
   - Retorna o dicionário contendo apenas entradas válidas.

##### Exemplo de Uso
1. **Entrada com valores válidos:**
```
   tabela = {"0": "255", "1": "128"}
   gerenciador = GerenciadorAES()
   tabela_normalizada = gerenciador._normalizar_tabela(tabela)
   print(tabela_normalizada)
   # Saída: {0: 255, 1: 128}
```
2. **Entrada com valores inválidos:**
```python
tabela = {"0": "300", "a": "b"}
gerenciador = GerenciadorAES()
tabela_normalizada = gerenciador._normalizar_tabela(tabela)
# Saída no console: Ignorando entrada inválida: a -> b
print(tabela_normalizada)
# Saída: {}
```

##### Observações
- Este método é chamado internamente pela função carregar_configuracoes para validar a tabela carregada de um arquivo.
- Entradas inválidas não interrompem a execução do programa, mas são ignoradas com uma notificação no console.
- A normalização é essencial para garantir o funcionamento correto do algoritmo AES, que depende de tabelas de substituição bem definidas.

[Voltar ao índice](#índice)


#### `carregar_configuracoes(self)`

O método `carregar_configuracoes` da classe `GerenciadorAES` é responsável por carregar as configurações de chave e tabela de substituição de um arquivo JSON. Ele garante que os dados necessários para o funcionamento do AES estejam disponíveis, gerando valores padrão caso o arquivo esteja ausente ou corrompido.

##### Funcionamento
1. **Verificação da Existência do Arquivo de Configuração:**
   - Se o arquivo especificado por `self.arquivo_dados` não existir, cria um arquivo JSON vazio.

2. **Carregamento das Configurações:**
   - Tenta carregar o conteúdo do arquivo JSON.
   - Em caso de falha no carregamento (como arquivo corrompido), configura padrões para as tabelas e chaves.

3. **Normalização da Tabela de Substituição:**
   - Utiliza o método `_normalizar_tabela` para validar e corrigir a tabela de substituição carregada.
   - Se a tabela carregada for inválida ou inexistente, gera uma nova tabela usando `gerar_tabela_substituicao`.

4. **Definição da Chave:**
   - Carrega a chave do arquivo JSON.
   - Se a chave estiver ausente ou inválida, define uma chave padrão de 16 bytes.

5. **Salvar Configurações Atualizadas:**
   - Escreve as configurações normalizadas no arquivo JSON, garantindo persistência.

6. **Geração de Tabelas Auxiliares e Expansão de Chaves:**
   - Gera a tabela inversa de substituição utilizando `gerar_tabela_inversa`.
   - Expande a chave criptográfica com o método `expansao_chave`.

##### Exemplo de Uso
```
gerenciador = GerenciadorAES()
gerenciador.carregar_configuracoes()
# As configurações agora estão carregadas e prontas para uso.
```
##### Padrões Configurados
- Tabela de Substituição:
  - Gera uma nova tabela se a carregada não for válida.
- Chave:
  - Usa a chave padrão:
```python
[
    0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
]
```

##### Observações
- Este método é chamado automaticamente durante a inicialização do GerenciadorAES.
- Garante que o sistema esteja em um estado válido, mesmo que o arquivo JSON seja inválido ou ausente.
- Todas as operações são projetadas para garantir que as configurações sejam persistentes e reutilizáveis.

[Voltar ao índice](#índice)

#### `criptografar_arquivo(self, arquivo_entrada, option)`

O método `criptografar_arquivo` da classe `GerenciadorAES` é responsável por criptografar o conteúdo de um arquivo de texto, transformando-o em uma sequência hexadecimal usando o algoritmo AES modificado. Ele lida com o processamento de blocos de texto e retorna o conteúdo criptografado ou exibe mensagens de erro em caso de falhas.

##### Argumentos
- **`arquivo_entrada`** (`str`):
  - Caminho do arquivo de texto a ser criptografado.
- **`option`** (`str`):
  - Indicador de modo para determinar se o tempo de criptografia deve ser exibido (`-c` para omitir).

##### Retorno
- **`str`**:
  - Conteúdo criptografado em formato hexadecimal.
  - Retorna `None` em caso de erro durante o processo.

##### Funcionamento
1. **Leitura do Arquivo de Entrada:**
   - Abre e lê o conteúdo do arquivo especificado.
   - Lida com exceções como arquivo não encontrado ou erros de leitura.

2. **Divisão em Blocos:**
   - Divide o texto em blocos utilizando a função `texto_para_blocos`, garantindo que o conteúdo esteja preparado para o AES.

3. **Processo de Criptografia:**
   - Utiliza o método `criptografar` para criptografar cada bloco de texto com as chaves e a tabela de substituição.
   - Concatena os blocos criptografados em uma string hexadecimal.

4. **Cálculo do Tempo de Execução (Opcional):**
   - Exibe o tempo de criptografia se a opção fornecida não for `-c`.

5. **Tratamento de Exceções:**
   - Captura erros durante a concatenação ou salvamento do conteúdo criptografado e exibe mensagens claras.

##### Exemplo de Uso
```python
gerenciador = GerenciadorAES()
resultado_hex = gerenciador.criptografar_arquivo("meu_arquivo.txt", option="-p")
if resultado_hex:
    print("Conteúdo criptografado:", resultado_hex)
```

##### Exemplo de Saída
Para um arquivo de entrada com o texto "Exemplo":
- Entrada: "Exemplo"
- Saída: `1a2b3c4d...` (sequência hexadecimal criptografada)

##### Observações
- O método é projetado para lidar apenas com arquivos de texto. Formatos binários podem exigir ajustes adicionais.
- O conteúdo criptografado é retornado em formato hexadecimal, ideal para armazenamento ou transmissão.
- Exceções são tratadas para garantir que falhas como arquivo inexistente sejam devidamente notificadas ao usuário.

[Voltar ao índice](#índice)

#### `descriptografar_arquivo(self, arquivo_entrada='', texto=None)`

O método `descriptografar_arquivo` da classe `GerenciadorAES` é responsável por realizar a descriptografia de conteúdo criptografado em formato hexadecimal. Ele permite processar tanto arquivos quanto strings diretamente, retornando o texto original ou exibindo mensagens de erro em caso de falhas.

##### Argumentos
- **`arquivo_entrada`** (`str`, opcional):
  - Caminho para o arquivo contendo o conteúdo criptografado em hexadecimal.
  - Este argumento é ignorado se o conteúdo for fornecido diretamente pelo parâmetro `texto`.
- **`texto`** (`str`, opcional):
  - Conteúdo criptografado em hexadecimal, fornecido como string.

##### Retorno
- **`str`**:
  - Texto descriptografado.
  - Retorna uma string vazia (`""`) em caso de erro durante o processo.

##### Funcionamento
1. **Leitura do Conteúdo Criptografado:**
   - Se o argumento `texto` não for fornecido, lê o conteúdo do arquivo especificado em `arquivo_entrada`.
   - Lida com exceções como arquivo não encontrado ou erros de leitura.

2. **Processo de Descriptografia:**
   - Utiliza a função `descriptografar_texto` para descriptografar o conteúdo hexadecimal com as chaves e a tabela inversa de substituição.
   - Registra o tempo de execução da operação.

3. **Exibição dos Resultados:**
   - Exibe o tempo total da descriptografia.
   - Retorna o texto original descriptografado, se bem-sucedido.

4. **Tratamento de Erros:**
   - Captura erros durante a leitura do arquivo ou o processo de descriptografia, exibindo mensagens claras para o usuário.

##### Exemplo de Uso
1. **Descriptografar um arquivo:**
```python
   gerenciador = GerenciadorAES()
   texto_original = gerenciador.descriptografar_arquivo(arquivo_entrada="arquivo_criptografado.enc")
   if texto_original:
       print("Texto descriptografado:", texto_original)
```
2. **Descriptografar uma string diretamente**:
```python
gerenciador = GerenciadorAES()
texto_original = gerenciador.descriptografar_arquivo(texto="1a2b3c4d...")
if texto_original:
    print("Texto descriptografado:", texto_original)
```
##### Exemplo de Saída
Para um arquivo criptografado com conteúdo hexadecimal "`1a2b3c4d...`":
- Entrada: "`1a2b3c4d...`"
- Saída: "Exemplo"

##### Observações
- O método é flexível, aceitando tanto arquivos quanto strings diretamente.
- A descriptografia depende da integridade da tabela inversa e das chaves previamente carregadas.
- Mensagens de erro informativas são exibidas para auxiliar o usuário em caso de falhas.

[Voltar ao índice](#índice)

#### `processar_arquivo(self, arquivo_original)`

O método `processar_arquivo` da classe `GerenciadorAES` realiza o fluxo completo de criptografia e descriptografia em um arquivo, verificando se o texto descriptografado é idêntico ao conteúdo original. Ele também exibe o tempo total gasto no processo.

##### Argumentos
- **`arquivo_original`** (`str`):
  - Caminho do arquivo de texto original a ser processado.

##### Retorno
- **`bool`**:
  - Retorna `True` se o processo for bem-sucedido (o texto descriptografado é igual ao texto original).
  - Retorna `False` caso ocorra qualquer erro durante o processo.

##### Funcionamento
1. **Criptografia do Arquivo:**
   - Utiliza o método `criptografar_arquivo` para gerar o conteúdo criptografado em formato hexadecimal.
   - Retorna `False` se ocorrer qualquer erro durante a criptografia.

2. **Descriptografia do Conteúdo:**
   - Utiliza o método `descriptografar_arquivo` para restaurar o texto original a partir do conteúdo criptografado.
   - Retorna `False` se ocorrer qualquer erro durante a descriptografia.

3. **Comparação de Textos:**
   - Lê o conteúdo original do arquivo.
   - Compara o texto original com o texto descriptografado.
   - Exibe uma mensagem indicando se o processo foi bem-sucedido.

4. **Medição do Tempo de Processamento:**
   - Calcula e exibe o tempo total gasto no processo de criptografia e descriptografia.

5. **Retorno do Resultado:**
   - Retorna `True` se o texto original for igual ao texto descriptografado.
   - Retorna `False` em caso de divergências ou falhas.

##### Exemplo de Uso
```python
gerenciador = GerenciadorAES()
sucesso = gerenciador.processar_arquivo("meu_arquivo.txt")
if sucesso:
    print("Processamento concluído com sucesso.")
else:
    print("Erro durante o processamento.")
```

##### Exemplo de Saída
Para um arquivo original com o texto "Exemplo":
- Entrada: "Exemplo"
- Saída:
  - Mensagem: "Tempo total de processamento: 0.123456 segundos"
  - Retorno: True (se o texto for restaurado corretamente)

##### Observações
- Este método é útil para validar a integridade do processo de criptografia e descriptografia.
- Caso o conteúdo descriptografado não seja igual ao original, uma mensagem de erro é exibida.
- Mensagens claras ajudam a identificar problemas em etapas específicas do fluxo.

[Voltar ao índice](#índice)

--------------------------------------------------

### aes_core.py

--------------------------------------------------

### aes_openssl.py

--------------------------------------------------

### Requisitos
1. **Python 3.10+**
2. **Bibliotecas Necessárias:**
   - `random`
   - `numpy`
   - `os`
   - `sys`
   - `time`
   - `json`
   - `typing`: Modules
      - `Dict`
      - `Any`
3. **OpenSSL**.

[Voltar ao índice](#índice)