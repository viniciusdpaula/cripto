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
4. [aes_core.py](#arquivo-aes_corepy)
  - 4.1 [galois_multiply()](#galois_multiply)
  - 4.2 [gerar_tabela_substituicao()](#gerar_tabela_substituicao)
  - 4.3 [gerar_tabela_inversa()](#gerar_tabela_inversa)
  - 4.4 [texto_para_blocos()](#texto_para_blocos)
  - 4.5 [blocos_para_texto()](#blocos_para_texto)
  - 4.6 [blocos_para_lista_bytes()](#blocos_para_lista_bytes)
  - 4.7 [bytes_para_texto()](#bytes_para_texto)
  - 4.8 [mix_columns()](#mix_columns)
  - 4.9 [substitute_bytes()](#substitute_bytes)
  - 4.10 [shift_rows()](#shift_rows)
  - 4.11 [add_round_key()](#add_round_key)
  - 4.12 [expansao_chave()](#expansao_chave)
  - 4.13 [criptografar()](#criptografar)
  - 4.14 [descriptografar()](#descriptografar)
  - 4.15 [descriptografar_texto()](#descriptografar_texto)
5. [aes_openssl.py](#arquivo-aes_opensslpy)
  - 5.1 [main()](#main-1)
  - 5.2 [processar_arquivo()](#processar_arquivo)
6. [Requisitos](#requisitos)


--------------------------------------------------

### Substituição da Caixa-S por Outra Tabela de Substituição (Cifra Monoalfabética)
Nesta implementação, a S-BOX original foi substituída por uma **tabela de substituição gerada aleatoriamente**. Essa nova tabela utiliza o conceito de **Cifra Monoalfabética**, onde cada byte (0-255) é substituído por outro byte único.

#### Nova Tabela de Substituição
A nova tabela é gerada como uma permutação aleatória dos valores de 0 a 255. Isso garante que:
1. Cada byte tenha um único valor correspondente na substituição.
2. Não existam valores duplicados ou bytes não mapeados.

A tabela inversa, usada na **descriptografia**, também é gerada automaticamente, sendo o mapeamento inverso da tabela de substituição.

#### **Código de Geraração das Tabelas**
**gerar_tabela_substituicao():**
```python
def gerar_tabela_substituicao():
    # Cria uma lista com todos os valores possíveis de um byte (0 a 255)
    valores = list(range(256))
    # Embaralha os valores para gerar uma substituição aleatória
    random.shuffle(valores)
    # Cria e retorna o dicionário de substituição
    return {i: valores[i] for i in range(256)} # A chave é o índice (0-255), e o valor é o elemento correspondente da lista embaralhada
```
[Ver Especificações](#gerar_tabela_substituicao-1)

**gerar_tabela_inversa():**
```python
def gerar_tabela_inversa(tabela_substituicao):
    # Retorna um dicionário onde as chaves e valores da tabela de substituição são invertidos
    return {v: k for k, v in tabela_substituicao.items()}
```
[Ver Especificações](#gerar_tabela_inversatabela_substituicao)

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
```python
  def carregar_configuracoes(self):
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
```
[Ver Especificações](#carregar_configuracoesself)

#### **Funcionamento da Tabela na Criptografia**

1. Durante a criptografia, a etapa de substituição (`substitute_bytes`) usa a tabela carregada do `key.json`.
2. Na descriptografia, a tabela inversa é usada para reverter a substituição.
[Voltar ao índice](#índice)

--------------------------------------------------

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

--------------------------------------------------

### Arquivo aes_manager.py
#### main
O arquivo aes_manager.py gerencia o fluxo principal de operações do AES personalizado, incluindo criptografia, descriptografia e verificação de consistência. Ele também implementa o carregamento de tabelas de substituição e chaves, além de permitir medições de desempenho e comparações. O script pode ser executado diretamente para realizar tarefas específicas com base em argumentos fornecidos.
[Ler mais](#aes_managerpy)

#### GerenciadorAES
O `GerenciadorAES` é uma classe que encapsula as principais funcionalidades do algoritmo AES modificado. Ele gerencia operações de criptografia e descriptografia de arquivos, incluindo o carregamento e normalização de tabelas de substituição, geração de chaves, e execução de fluxos de processamento completos com medições de desempenho. É o núcleo do sistema AES implementado.
[Ler mais](#gerenciadoraes-1)

### Arquivo aes_core.py
#### galois_multiply
A função galois_multiply implementa multiplicação no campo finito GF(2⁸) utilizando redução polinomial. É comumente usada em algoritmos de criptografia como o AES para garantir operações matemáticas seguras e consistentes.
[Ler mais](#galois_multiplya-b)

#### gerar_tabela_substituicao
A função gerar_tabela_substituicao cria um dicionário que embaralha de forma aleatória os valores entre 0 e 255, garantindo unicidade. É um componente essencial em nosso sistemas criptográfico para criar operações de substituição seguras e imprevisíveis.
[Ler mais](#gerar_tabela_substituicao-1)

#### gerar_tabela_inversa
A função gerar_tabela_inversa cria uma tabela que reverte os mapeamentos de uma tabela de substituição, trocando chaves e valores. É um componente fundamental para a etapa de descriptografia em nosso sistema que utiliza substituições criptográficas.
[Ler mais](#gerar_tabela_inversatabela_substituicao)

#### texto_para_blocos
A função texto_para_blocos prepara textos para criptografia no modo AES, dividindo-os em blocos de tamanho fixo de 16 bytes com padding. Os blocos são retornados como matrizes 4x4, facilitando sua manipulação no algoritmo.
[Ler mais](#texto_para_blocostexto)

#### blocos_para_texto
A função blocos_para_texto converte blocos processados de dados (em formato de matrizes 4x4) de volta para uma string de texto legível, facilitando a recuperação de dados criptografados ou descriptografados.
[Ler mais](#blocos_para_textoblocos)

#### blocos_para_lista_bytes
A função blocos_para_lista_bytes converte blocos estruturados (matrizes 4x4) em uma lista linear de bytes. Ela é ideal para operações que exigem uma representação sequencial de dados, como escrita ou análise direta.
[Ler mais](#blocos_para_lista_bytesblocos)

#### bytes_para_texto
A função bytes_para_texto decodifica listas de bytes em strings legíveis usando UTF-8, removendo padding adicional. Ela é uma etapa crucial para recuperar textos originais após processos de criptografia ou manipulação de dados.
[Ler mais](#bytes_para_textolista_bytes)

#### mix_columns
A função mix_columns implementa a operação de mistura de colunas do AES, aplicando transformações lineares no campo Galois. É usada tanto na criptografia quanto na descriptografia, sendo essencial para a difusão de dados no algoritmo.
[Ler mais](#mix_columnsmatriz-inversofalse)

#### substitute_bytes
A função substitute_bytes substitui bytes de uma matriz 4x4 utilizando uma tabela de substituição personalizada. Ela é equivalente à etapa SubBytes do AES, mas permite flexibilidade no uso de tabelas customizadas, sendo crucial para operações criptográficas.
[Ler mais](#substitute_bytesmatriz-tabela)

#### shift_rows
A função shift_rows implementa a etapa de deslocamento de linhas do AES, misturando os bytes da matriz. Ela desloca linhas para a esquerda ou para a direita, dependendo do modo de operação, sendo fundamental para difundir os dados no estado do AES.
[Ler mais](#shift_rowsmatriz-inversofalse)

#### add_round_key
A função add_round_key combina a matriz de estado atual com a chave da rodada utilizando a operação XOR. Essa etapa garante a integração direta da chave criptográfica ao processo de transformação do AES modificado, sendo fundamental para a segurança do algoritmo.
[Ler mais](#add_round_keymatriz_bloco-chave_rodada)

#### expansao_chave
A função expansao_chave gera uma sequência de chaves únicas para cada rodada do AES modificado, garantindo segurança por meio de substituições, deslocamentos e operações XOR. É essencial para o funcionamento do algoritmo, fornecendo chaves específicas para cada etapa de criptografia ou descriptografia.
[Ler mais](#expansao_chavechave_inicial-tabela_substituicao-num_rodadas10)

#### criptografar
A função criptografar aplica o algoritmo AES para transformar blocos de dados em blocos criptografados. Ela utiliza operações como [SubBytes](#substitute_bytesmatriz-tabela), [ShiftRows](#shift_rowsmatriz-inversofalse), [MixColumns](#mix_columnsmatriz-inversofalse), e [AddRoundKey](#add_round_keymatriz_bloco-chave_rodada), repetindo-as em rodadas para garantir segurança e difusão no processo de criptografia.
[Ler mais](#criptografarblocos-chaves-tabela-num_rodadas10)

#### descriptografar
A função descriptografar aplica o algoritmo AES para reverter blocos criptografados, utilizando operações como [AddRoundKey](#add_round_keymatriz_bloco-chave_rodada), [SubBytes inverso](#substitute_bytesmatriz-tabela), [ShiftRows inverso](#shift_rowsmatriz-inversofalse), e [MixColumns inverso](#mix_columnsmatriz-inversofalse). Ela restaura os dados originais com segurança, seguindo as etapas do AES em ordem inversa.
[Ler mais](#descriptografarblocos-chaves-tabela_inversa-num_rodadas10)

#### descriptografar_texto
A função descriptografar_texto converte texto criptografado em hexadecimal para blocos, aplica o algoritmo AES para descriptografia, e retorna o texto original. É uma implementação eficiente para restaurar dados em formato legível após processos de criptografia.
[Ler mais](#descriptografar_textoconteudo-chaves-tabela_inversa-num_rodadas10)

### Arquivo aes_openssl.py
#### main
A função `main` gerencia a criptografia e descriptografia de um arquivo utilizando AES-256-CBC. Ela verifica a integridade dos dados processados e mede o tempo total das operações, garantindo segurança e consistência no processamento de arquivos.
[Ler mais](#main-3)

#### processar_arquivo
A função processar_arquivo usa OpenSSL para criptografar ou descriptografar arquivos com AES-256-CBC. Ela aceita chaves e IVs em formato hexadecimal e calcula o tempo gasto na operação, retornando-o para análise. Em caso de erro, retorna `-1`. Ideal para automação de segurança de dados em arquivos
[Ler mais](#processar_arquivoinput_file-output_file-chave-iv-operacao)

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
#### galois_multiply(a, b)
A função `galois_multiply` realiza a multiplicação de dois números no campo finito GF(2⁸), seguindo as regras específicas do campo. Ela utiliza o polinômio irreduzível `0x11B` para modular os resultados que excedem 8 bits, garantindo a conformidade com as operações no campo Galois.

##### Argumentos
- **`a`** (`int`): 
  - Primeiro número (multiplicando).
- **`b`** (`int`): 
  - Segundo número (multiplicador).

##### Retorno
- **`int`**: 
  - Resultado da multiplicação no campo finito GF(2⁸).

##### Funcionamento
1. **Inicialização do Acumulador:**
   - Inicia o produto como `0`.

2. **Multiplicação com Redução Polinomial:**
   - Realiza a operação XOR (`p ^= a`) sempre que o bit menos significativo de `b` é `1`.
   - Desloca `a` para a esquerda e aplica a redução polinomial com `0x11B` se `a` ultrapassar 8 bits.
   - Desloca `b` para a direita até que todos os bits sejam processados.

3. **Retorno do Resultado:**
   - Retorna o valor final acumulado no produto.

##### Exemplo de Uso
```python
resultado = galois_multiply(0x57, 0x83)
print(hex(resultado))  # Saída: 0xc1
```
##### Observações
- A função é essencial em operações de criptografia como AES, onde a multiplicação no campo Galois é usada para mixagem de colunas.
- O uso do polinômio irreduzível 0x11B é padrão para GF(2⁸).
[Voltar ao índice](#índice)

#### gerar_tabela_substituicao()
A função `gerar_tabela_substituicao` cria uma tabela de substituição aleatória, que é um dicionário mapeando cada byte (valores de 0 a 255) para outro valor único e aleatório no mesmo intervalo. Essa tabela é comumente usada em criptografia para operações de substituição.

##### Retorno
- **`dict`**:
  - Um dicionário com 256 entradas, onde:
    - As chaves são valores originais (0-255).
    - Os valores são números únicos e aleatórios no intervalo (0-255).

##### Funcionamento
1. **Geração de Valores Originais:**
   - Cria uma lista de todos os números de 0 a 255.

2. **Embaralhamento dos Valores:**
   - Usa a função `random.shuffle` para reorganizar a lista de forma aleatória.

3. **Criação da Tabela de Substituição:**
   - Mapeia cada índice da lista embaralhada para o valor correspondente.
   - Retorna o resultado como um dicionário.

##### Exemplo de Uso
```python
tabela = gerar_tabela_substituicao()
print(tabela)
# Saída: {0: 34, 1: 56, ..., 255: 12} (valores aleatórios)
```
##### Observações
- A tabela gerada garante que cada byte tem exatamente um mapeamento único.
- Essa abordagem é útil em sistemas criptográficos para introduzir não-linearidade.
[Voltar ao índice](#índice)

#### gerar_tabela_inversa(tabela_substituicao)
A função `gerar_tabela_inversa` cria uma tabela inversa a partir de uma tabela de substituição fornecida. A tabela inversa é essencial para operações de descriptografia, permitindo que os valores substituídos sejam mapeados de volta às suas chaves originais.

##### Argumentos
- **`tabela_substituicao`** (`dict`):
  - Tabela de substituição original, onde cada chave (0-255) é mapeada para um valor único (0-255).

##### Retorno
- **`dict`**:
  - Tabela inversa, onde:
    - As chaves e valores da tabela original são trocados.
    - O valor substituído na tabela original torna-se a chave, e a chave original torna-se o valor.

##### Funcionamento
1. **Inversão de Chaves e Valores:**
   - Usa compreensão de dicionário para inverter os pares chave-valor da tabela original.
   - As chaves da tabela de substituição tornam-se os valores da tabela inversa, e vice-versa.

2. **Retorno da Tabela Inversa:**
   - Retorna um dicionário contendo a tabela invertida.

##### Exemplo de Uso
```python
tabela_substituicao = {0: 34, 1: 56, 2: 78}
tabela_inversa = gerar_tabela_inversa(tabela_substituicao)
print(tabela_inversa)
# Saída: {34: 0, 56: 1, 78: 2}
```

##### Observações
- A tabela original deve conter mapeamentos únicos e completos para garantir a validade da inversão.
- A tabela inversa é utilizada principalmente em processos de descriptografia, revertendo transformações aplicadas por uma tabela de substituição.
[Voltar ao índice](#índice)

#### texto_para_blocos(texto)
A função `texto_para_blocos` divide um texto em blocos de 16 bytes, adicionando padding quando necessário. Essa operação é usada para preparar o texto para criptografia no modo AES, que exige blocos de tamanho fixo de 16 bytes (128 bits).

##### Argumentos
- **`texto`** (`str`):
  - O texto a ser convertido em blocos.

##### Retorno
- **`list`**:
  - Uma lista de blocos, onde cada bloco é representado como uma matriz 4x4 de inteiros (`numpy.uint8`).

##### Funcionamento
1. **Conversão para Bytes:**
   - Converte o texto em sua representação em bytes usando a codificação UTF-8.

2. **Adição de Padding:**
   - Calcula o número de bytes de padding necessários para que o texto seja múltiplo de 16.
   - Adiciona bytes de valor `0` (`\x00`) ao final do texto para preencher o espaço restante.

3. **Divisão em Blocos:**
   - Divide o texto ajustado em segmentos de 16 bytes.
   - Cada segmento é convertido em uma matriz 4x4 de inteiros.

4. **Retorno dos Blocos:**
   - Retorna uma lista contendo todas as matrizes 4x4 geradas.

##### Exemplo de Uso
```python
texto = "Exemplo de texto"
blocos = texto_para_blocos(texto)
for bloco in blocos:
    print(bloco)
# Saída: Matrizes 4x4 representando os blocos do texto
```
##### Observações
- A função utiliza padding para garantir que o tamanho do texto seja sempre um múltiplo de 16 bytes, necessário para o modo de operação do AES.
- Cada bloco é representado como uma matriz numpy 4x4, facilitando operações no campo criptográfico.
[Voltar ao índice](#índice)

#### blocos_para_texto(blocos)
A função `blocos_para_texto` converte uma lista de blocos de dados em uma string de texto legível. É usada para transformar dados processados (criptografados ou descriptografados) de volta ao formato original.

##### Argumentos
- **`blocos`** (`list`):
  - Lista de blocos, onde cada bloco é uma matriz `numpy` 4x4 contendo inteiros (`uint8`).

##### Retorno
- **`str`**:
  - O texto resultante da concatenação dos blocos.

##### Funcionamento
1. **Iteração pelos Blocos:**
   - Percorre cada bloco na lista fornecida.

2. **Conversão de Bytes:**
   - Para cada linha em um bloco, converte cada byte (inteiro) em um caractere (`chr`).

3. **Concatenação:**
   - Concatena os caracteres de todas as linhas de todos os blocos em uma única string.

4. **Retorno:**
   - Retorna a string resultante da concatenação.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de blocos 4x4
blocos = [np.array([[69, 120, 101, 109], [112, 108, 111, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.uint8)]
texto = blocos_para_texto(blocos)
print(texto)
# Saída: "Exemplo"
```
##### Observações
- A função não remove padding automaticamente. Se o texto original tinha padding, ele será incluído na saída.
- Cada bloco deve ter tamanho 4x4, representando 16 bytes de dados processados.
[Voltar ao índice](#índice)

#### blocos_para_lista_bytes(blocos)
A função `blocos_para_lista_bytes` transforma uma lista de blocos (matrizes 4x4) em uma sequência linear de bytes. Essa conversão é útil para operações que requerem uma representação plana de dados, como gravação em arquivos ou comparações.

##### Argumentos
- **`blocos`** (`list`):
  - Lista de blocos, onde cada bloco é uma matriz `numpy` 4x4 contendo inteiros (`uint8`).

##### Retorno
- **`list`**:
  - Uma lista linear contendo os bytes de todos os blocos em sequência. Cada elemento é um valor inteiro entre 0 e 255.

##### Funcionamento
1. **Iteração pelos Blocos:**
   - Percorre cada bloco na lista fornecida.

2. **Extração de Bytes:**
   - Para cada linha em um bloco, percorre cada byte e o adiciona à lista linear.

3. **Retorno da Lista Linear:**
   - Retorna a sequência de bytes resultante.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de blocos 4x4
blocos = [np.array([[69, 120, 101, 109], [112, 108, 111, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.uint8)]
lista_bytes = blocos_para_lista_bytes(blocos)
print(lista_bytes)
# Saída: [69, 120, 101, 109, 112, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```
##### Observações
- A função retorna todos os bytes em uma única lista linear, preservando a ordem em que aparecem nos blocos.
- É frequentemente usada para serialização de dados, como ao gravar blocos criptografados em arquivos.
[Voltar ao índice](#índice)

#### bytes_para_texto(lista_bytes)
A função `bytes_para_texto` converte uma lista de bytes em uma string de texto legível. Ela utiliza a codificação UTF-8 para decodificar os valores e remove padding adicional, como bytes nulos, ao final do texto.

##### Argumentos
- **`lista_bytes`** (`list`):
  - Uma lista de bytes (valores inteiros de 0 a 255) que será convertida em texto.

##### Retorno
- **`str`**:
  - Uma string de texto resultante da decodificação da lista de bytes.

##### Funcionamento
1. **Conversão para Objeto `bytes`:**
   - Transforma a lista de inteiros em um objeto do tipo `bytes`.

2. **Decodificação para UTF-8:**
   - Converte os bytes para uma string utilizando a codificação UTF-8.
   - O parâmetro `errors='ignore'` ignora valores inválidos durante a decodificação.

3. **Remoção de Padding:**
   - Remove bytes nulos (`\x00`) adicionais ao final da string usando `rstrip('\x00')`.

4. **Retorno do Texto:**
   - Retorna a string decodificada e limpa.

##### Exemplo de Uso
```python
lista_bytes = [69, 120, 101, 109, 112, 108, 111, 0, 0, 0]
texto = bytes_para_texto(lista_bytes)
print(texto)
# Saída: "Exemplo"
```
##### Observações
- A função ignora erros de decodificação, garantindo robustez ao lidar com listas de bytes que possam conter valores inválidos.
- O uso de rstrip('\x00') assegura que padding adicionado durante a criptografia seja removido.
[Voltar ao índice](#índice)

#### mix_columns(matriz, inverso=False)
A função `mix_columns` implementa a operação **MixColumns** do AES, que realiza uma mistura linear dos bytes em cada coluna de uma matriz 4x4. Essa operação é essencial para difundir os dados no algoritmo AES, podendo ser usada tanto para criptografia quanto para descriptografia.

##### Argumentos
- **`matriz`** (`numpy.ndarray`):
  - Matriz 4x4 (`uint8`) representando o estado atual dos dados no AES.
- **`inverso`** (`bool`, opcional):
  - Se `True`, executa a versão inversa da operação (para descriptografia). Por padrão, realiza a operação para criptografia.

##### Retorno
- **`numpy.ndarray`**:
  - Matriz 4x4 resultante após a operação MixColumns.

##### Funcionamento
1. **Definição de Multiplicadores:**
   - Utiliza diferentes conjuntos de multiplicadores no campo Galois (GF(2⁸)):
     - `multiplicadores_mix` para criptografia.
     - `multiplicadores_mix_inv` para descriptografia.

2. **Seleção do Modo:**
   - Escolhe o conjunto de multiplicadores com base no argumento `inverso`.

3. **Processamento por Coluna:**
   - Para cada coluna da matriz:
     - Calcula o novo valor de cada byte aplicando a operação no campo Galois (com `galois_multiply`) e acumulando os resultados com XOR.

4. **Construção da Matriz Resultante:**
   - Substitui os valores das colunas pela nova matriz resultante.

5. **Retorno:**
   - Retorna a matriz 4x4 processada.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de matriz 4x4
matriz = np.array([
    [0xd4, 0xbf, 0x5d, 0x30],
    [0xe0, 0xb4, 0x52, 0xae],
    [0xb8, 0x41, 0x11, 0xf1],
    [0x1e, 0x27, 0x98, 0xe5]
], dtype=np.uint8)

# Aplicar MixColumns para criptografia
resultado = mix_columns(matriz)
print(resultado)

# Aplicar MixColumns inverso para descriptografia
resultado_inverso = mix_columns(matriz, inverso=True)
print(resultado_inverso)
```
##### Observações
- MixColumns utiliza operações no campo finito GF(2⁸), implementadas pela função [galois_multiply](#galois_multiplya-b).
- A operação é crucial para garantir a difusão no AES, tornando o algoritmo mais resistente a ataques.
- A matriz de entrada e saída deve ser do tipo numpy.uint8 para garantir compatibilidade.
[Voltar ao índice](#índice)

#### substitute_bytes(matriz, tabela)
A função `substitute_bytes` substitui cada byte de uma matriz 4x4 pelos valores correspondentes em uma tabela de substituição personalizada. Ela realiza uma operação semelhante à etapa **SubBytes** do AES, mas utilizando uma tabela definida pelo usuário em vez da S-Box padrão.

##### Argumentos
- **`matriz`** (`numpy.ndarray`):
  - Matriz 4x4 (`uint8`) representando os dados do estado no AES.
- **`tabela`** (`dict`):
  - Tabela de substituição personalizada que mapeia cada byte (0-255) para seu valor correspondente.

##### Retorno
- **`numpy.ndarray`**:
  - Matriz 4x4 (`uint8`) com os bytes substituídos de acordo com a tabela fornecida.

##### Funcionamento
1. **Substituição dos Bytes:**
   - Utiliza a função `np.vectorize` para aplicar a tabela de substituição a cada elemento da matriz.
   - Cada byte da matriz é substituído pelo valor correspondente na tabela.

2. **Retorno da Nova Matriz:**
   - Retorna uma nova matriz 4x4 com os bytes substituídos.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de matriz 4x4
matriz = np.array([
    [0x00, 0x01, 0x02, 0x03],
    [0x10, 0x11, 0x12, 0x13],
    [0x20, 0x21, 0x22, 0x23],
    [0x30, 0x31, 0x32, 0x33]
], dtype=np.uint8)

# Exemplo de tabela de substituição
tabela = {i: (i + 1) % 256 for i in range(256)}

# Substituir os bytes da matriz
matriz_substituida = substitute_bytes(matriz, tabela)
print(matriz_substituida)
```
##### Observações
- A tabela de substituição personalizada deve mapear todos os valores de byte (0-255) para evitar erros durante a substituição.
- É uma operação essencial para introduzir não-linearidade em algoritmos criptográficos, aumentando a resistência a ataques.
[Voltar ao índice](#índice)

#### shift_rows(matriz, inverso=False)
A função `shift_rows` realiza a operação **ShiftRows** do AES em uma matriz 4x4, deslocando ciclicamente as linhas da matriz para a esquerda (criptografia) ou para a direita (descriptografia). Essa operação é essencial para misturar os bytes na transformação do estado AES.

##### Argumentos
- **`matriz`** (`numpy.ndarray`):
  - Matriz 4x4 (`uint8`) representando os dados do estado no AES.
- **`inverso`** (`bool`, opcional):
  - Se `True`, realiza o deslocamento na direção inversa (direita), usado na descriptografia.
  - Se `False` (padrão), realiza o deslocamento padrão para a esquerda, usado na criptografia.

##### Retorno
- **`numpy.ndarray`**:
  - A matriz 4x4 modificada após a operação **ShiftRows**.

##### Funcionamento
1. **Definição da Direção:**
   - Define o sentido do deslocamento:
     - `-1` para deslocamento à esquerda (criptografia).
     - `1` para deslocamento à direita (descriptografia).

2. **Deslocamento das Linhas:**
   - A linha 0 permanece inalterada.
   - As linhas 1, 2 e 3 são deslocadas em 1, 2 e 3 posições, respectivamente, na direção definida.

3. **Modificação da Matriz:**
   - Usa `np.roll` para realizar o deslocamento circular das linhas.

4. **Retorno da Matriz Modificada:**
   - Retorna a matriz após a aplicação da operação.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de matriz 4x4
matriz = np.array([
    [0x00, 0x01, 0x02, 0x03],
    [0x10, 0x11, 0x12, 0x13],
    [0x20, 0x21, 0x22, 0x23],
    [0x30, 0x31, 0x32, 0x33]
], dtype=np.uint8)

# Aplicar ShiftRows para criptografia (esquerda)
matriz_shift = shift_rows(matriz.copy())
print("Criptografia (esquerda):")
print(matriz_shift)

# Aplicar ShiftRows inverso para descriptografia (direita)
matriz_shift_inversa = shift_rows(matriz.copy(), inverso=True)
print("Descriptografia (direita):")
print(matriz_shift_inversa)
```
##### Observações
- A linha 0 da matriz permanece inalterada durante a operação.
- A direção do deslocamento é controlada pelo parâmetro inverso, permitindo o uso do mesmo método para criptografia e descriptografia.
[Voltar ao índice](#índice)

#### add_round_key(matriz_bloco, chave_rodada)
A função `add_round_key` implementa a operação **AddRoundKey** do AES, combinando a matriz de estado atual com a chave da rodada por meio de uma operação XOR. Essa etapa é essencial para integrar a chave criptográfica ao processamento do estado.

##### Argumentos
- **`matriz_bloco`** (`numpy.ndarray`):
  - Matriz 4x4 (`uint8`) representando o estado atual do bloco de dados.
- **`chave_rodada`** (`list`):
  - Lista de 16 bytes (`uint8`) representando a chave da rodada.

##### Retorno
- **`numpy.ndarray`**:
  - A matriz 4x4 resultante após a aplicação da operação XOR entre o estado atual e a chave da rodada.

##### Funcionamento
1. **Conversão da Chave da Rodada:**
   - Transforma a lista de 16 bytes em uma matriz 4x4 utilizando `numpy`.

2. **Aplicação do XOR:**
   - Realiza uma operação bit a bit XOR entre os elementos correspondentes da matriz do bloco e a matriz da chave da rodada.

3. **Retorno da Matriz Modificada:**
   - Retorna a matriz resultante da operação.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de matriz de estado 4x4 (bloco)
matriz_bloco = np.array([
    [0x32, 0x88, 0x31, 0xe0],
    [0x43, 0x5a, 0x31, 0x37],
    [0xf6, 0x30, 0x98, 0x07],
    [0xa8, 0x8d, 0xa2, 0x34]
], dtype=np.uint8)

# Exemplo de chave de rodada
chave_rodada = [
    0x2b, 0x7e, 0x15, 0x16,
    0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x15, 0x88,
    0x09, 0xcf, 0x4f, 0x3c
]

# Aplicar AddRoundKey
resultado = add_round_key(matriz_bloco, chave_rodada)
print("Resultado:")
print(resultado)
```
##### Observações
- **AddRoundKey** é uma operação reversível, pois o XOR aplicado com a mesma chave restaura os dados originais.
- A matriz da chave deve ser representada exatamente como uma lista de 16 bytes.
[Voltar ao índice](#índice)

#### expansao_chave(chave_inicial, tabela_substituicao, num_rodadas=10)
A função `expansao_chave` realiza a expansão de uma chave inicial para gerar as chaves de cada rodada do AES. Esse processo é fundamental para garantir que cada rodada use uma chave única, derivada da chave inicial, utilizando substituições, deslocamentos circulares e operações XOR com constantes de rodada.

##### Argumentos
- **`chave_inicial`** (`list`):
  - Lista de 16 bytes (`uint8`) representando a chave inicial.
- **`tabela_substituicao`** (`dict`):
  - Tabela de substituição personalizada (equivalente à S-Box).
- **`num_rodadas`** (`int`, opcional):
  - Número de rodadas do AES (padrão: 10).

##### Retorno
- **`list`**:
  - Lista de chaves expandidas, onde cada chave é uma lista linear de 16 bytes.

##### Funcionamento
1. **Divisão da Chave Inicial:**
   - A chave inicial de 16 bytes é dividida em 4 palavras (listas de 4 bytes cada).

2. **Geração de Rcon:**
   - Calcula as constantes de rodada (`Rcon`), que são usadas no processo de expansão.

3. **Expansão das Palavras:**
   - Gera novas palavras usando as palavras anteriores:
     - Substitui e aplica deslocamento circular na palavra a cada múltiplo de 4.
     - Aplica XOR com a constante de rodada na primeira posição.
     - Realiza XOR com a palavra 4 posições atrás para formar a nova palavra.

4. **Combinação em Chaves Expandidas:**
   - Agrupa as palavras em blocos de 4 para formar as chaves de 16 bytes de cada rodada.

5. **Retorno:**
   - Retorna uma lista contendo todas as chaves expandidas.

##### Exemplo de Uso
```python
# Exemplo de chave inicial e tabela de substituição
chave_inicial = [
    0x2b, 0x7e, 0x15, 0x16,
    0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x15, 0x88,
    0x09, 0xcf, 0x4f, 0x3c
]
tabela_substituicao = {i: (i + 1) % 256 for i in range(256)}  # Exemplo de tabela personalizada

# Geração das chaves expandidas
chaves_expandidas = expansao_chave(chave_inicial, tabela_substituicao)
print("Chaves Expandidas:")
for i, chave in enumerate(chaves_expandidas):
    print(f"Rodada {i}: {chave}")
```
##### Observações
- A chave inicial deve ter exatamente 16 bytes para garantir compatibilidade com o AES.
- A tabela de substituição (S-Box) deve mapear todos os valores de byte (0-255) para evitar erros durante a expansão.
- O número de rodadas pode ser ajustado para diferentes tamanhos de chave (por exemplo, 12 ou 14 rodadas).
[Voltar ao índice](#índice)

#### criptografar(blocos, chaves, tabela, num_rodadas=10)
A função `criptografar` aplica o algoritmo AES modificado para criptografar uma lista de blocos de dados. Utilizando chaves expandidas, uma tabela de substituição personalizada (S-Box) e as transformações do AES, ela processa cada bloco em múltiplas rodadas, gerando blocos criptografados.

##### Argumentos
- **`blocos`** (`list`):
  - Lista de blocos, onde cada bloco é uma matriz 4x4 (`uint8`) representando o estado inicial.
- **`chaves`** (`list`):
  - Lista de chaves expandidas, com cada chave sendo uma lista linear de 16 bytes.
- **`tabela`** (`dict`):
  - Tabela de substituição personalizada (S-Box) usada para a substituição de bytes.
- **`num_rodadas`** (`int`, opcional):
  - Número de rodadas do AES (padrão: 10).

##### Retorno
- **`list`**:
  - Lista de blocos criptografados, com cada bloco sendo uma matriz 4x4 (`uint8`).

##### Funcionamento
1. **Processamento de Cada Bloco:**
   - Para cada bloco na lista:
     - Aplica a etapa inicial com a primeira chave (AddRoundKey).

2. **Rodadas Intermediárias:**
   - Em cada uma das rodadas intermediárias:
     - **SubBytes:** Substitui os bytes usando a tabela S-Box.
     - **ShiftRows:** Realiza deslocamento das linhas.
     - **MixColumns:** Mistura as colunas para difusão.
     - **AddRoundKey:** Aplica a chave correspondente à rodada.

3. **Rodada Final:**
   - Realiza as operações **SubBytes**, **ShiftRows**, e **AddRoundKey**, omitindo **MixColumns**.

4. **Atualização dos Blocos:**
   - Substitui o bloco original pelo estado criptografado resultante.

5. **Retorno dos Blocos Criptografados:**
   - Retorna a lista de blocos após a criptografia.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de entrada
blocos = [
    np.array([
        [0x32, 0x88, 0x31, 0xe0],
        [0x43, 0x5a, 0x31, 0x37],
        [0xf6, 0x30, 0x98, 0x07],
        [0xa8, 0x8d, 0xa2, 0x34]
    ], dtype=np.uint8)
]
chaves = expansao_chave(
    chave_inicial=[
        0x2b, 0x7e, 0x15, 0x16,
        0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88,
        0x09, 0xcf, 0x4f, 0x3c
    ],
    tabela_substituicao={i: (i + 1) % 256 for i in range(256)}
)
tabela = {i: (i + 1) % 256 for i in range(256)}

# Criptografia dos blocos
blocos_criptografados = criptografar(blocos, chaves, tabela)
print("Blocos Criptografados:")
for bloco in blocos_criptografados:
    print(bloco)
```
##### Observações
- Cada bloco deve ser uma matriz 4x4 para compatibilidade com as transformações do AES.
- As chaves expandidas devem ser pré-geradas e correspondentes ao número de rodadas definido.
- A tabela de substituição deve mapear todos os valores de byte (0-255).
[Voltar ao índice](#índice)

#### descriptografar(blocos, chaves, tabela_inversa, num_rodadas=10)
A função `descriptografar` aplica o algoritmo AES modificado para reverter a criptografia de uma lista de blocos de dados. Utilizando chaves expandidas e uma tabela de substituição inversa (S-Box inversa), ela processa cada bloco em múltiplas rodadas para restaurar os dados originais.

##### Argumentos
- **`blocos`** (`list`):
  - Lista de blocos, onde cada bloco é uma matriz 4x4 (`uint8`) representando o estado criptografado.
- **`chaves`** (`list`):
  - Lista de chaves expandidas, com cada chave sendo uma lista linear de 16 bytes.
- **`tabela_inversa`** (`dict`):
  - Tabela de substituição inversa (S-Box inversa) usada para a substituição de bytes durante a descriptografia.
- **`num_rodadas`** (`int`, opcional):
  - Número de rodadas do AES (padrão: 10).

##### Retorno
- **`list`**:
  - Lista de blocos descriptografados, com cada bloco sendo uma matriz 4x4 (`uint8`).

##### Funcionamento
1. **Processamento de Cada Bloco:**
   - Para cada bloco na lista:
     - Aplica a última chave (AddRoundKey).
     - Realiza as operações inversas de **ShiftRows** e **SubBytes**.

2. **Rodadas Intermediárias:**
   - Em cada rodada intermediária (em ordem inversa):
     - **AddRoundKey:** Aplica a chave correspondente à rodada.
     - **MixColumns inverso:** Reverte a difusão.
     - **ShiftRows inverso:** Realiza deslocamento das linhas para a direita.
     - **SubBytes inverso:** Substitui os bytes usando a S-Box inversa.

3. **Rodada Final:**
   - Realiza a última aplicação de **AddRoundKey** com a chave inicial.

4. **Atualização dos Blocos:**
   - Substitui o bloco original pelo estado descriptografado resultante.

5. **Retorno dos Blocos Descriptografados:**
   - Retorna a lista de blocos após a descriptografia.

##### Exemplo de Uso
```python
import numpy as np

# Exemplo de entrada (blocos criptografados)
blocos = [
    np.array([
        [0x39, 0x02, 0xdc, 0x19],
        [0x25, 0xdc, 0x11, 0x6a],
        [0x84, 0x09, 0x85, 0x0b],
        [0x1d, 0xfb, 0x97, 0x32]
    ], dtype=np.uint8)
]
chaves = expansao_chave(
    chave_inicial=[
        0x2b, 0x7e, 0x15, 0x16,
        0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88,
        0x09, 0xcf, 0x4f, 0x3c
    ],
    tabela_substituicao={i: (i + 1) % 256 for i in range(256)}
)
tabela_inversa = {v: k for k, v in {i: (i + 1) % 256 for i in range(256)}.items()}

# Descriptografia dos blocos
blocos_descriptografados = descriptografar(blocos, chaves, tabela_inversa)
print("Blocos Descriptografados:")
for bloco in blocos_descriptografados:
    print(bloco)
```
##### Observações
- A ordem inversa das rodadas é fundamental para reverter a criptografia.
- As chaves expandidas e a S-Box inversa devem ser correspondentes às usadas na criptografia.
- Cada bloco deve ser uma matriz 4x4 para compatibilidade com as transformações do AES.
[Voltar ao índice](#índice)

#### descriptografar_texto(conteudo, chaves, tabela_inversa, num_rodadas=10)
A função `descriptografar_texto` realiza a descriptografia de um texto criptografado representado em formato hexadecimal. Ela converte os dados em blocos de 16 bytes, aplica o algoritmo AES modificado para descriptografia e retorna o texto original legível.

##### Argumentos
- **`conteudo`** (`str`):
  - String hexadecimal representando o texto criptografado.
- **`chaves`** (`list`):
  - Lista de chaves expandidas, com cada chave sendo uma lista linear de 16 bytes.
- **`tabela_inversa`** (`dict`):
  - Tabela de substituição inversa (S-Box inversa) usada para descriptografia.
- **`num_rodadas`** (`int`, opcional):
  - Número de rodadas do AES (padrão: 10).

##### Retorno
- **`str`**:
  - Texto original descriptografado.

##### Funcionamento
1. **Conversão de Hexadecimal para Bytes:**
   - Transforma a string hexadecimal em uma lista de bytes.
   - Exibe o total de bytes convertidos.

2. **Formação de Blocos:**
   - Agrupa os bytes em blocos de 16 bytes.
   - Aplica padding (preenchimento com zeros) no último bloco, caso necessário.
   - Converte cada bloco em uma matriz 4x4.

3. **Descriptografia dos Blocos:**
   - Usa a função `descriptografar` para aplicar o algoritmo AES modificado em cada bloco.

4. **Conversão de Blocos para Texto:**
   - Converte os blocos descriptografados para uma lista linear de bytes.
   - Decodifica a lista de bytes em texto legível, removendo padding.

5. **Retorno:**
   - Retorna o texto original descriptografado.

##### Exemplo de Uso
```python
# Exemplo de entrada
conteudo_criptografado = "39dc191125dc116a8409850b1dfb9732"
chaves = expansao_chave(
    chave_inicial=[
        0x2b, 0x7e, 0x15, 0x16,
        0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88,
        0x09, 0xcf, 0x4f, 0x3c
    ],
    tabela_substituicao={i: (i + 1) % 256 for i in range(256)}
)
tabela_inversa = {v: k for k, v in {i: (i + 1) % 256 for i in range(256)}.items()}

# Descriptografia do texto
texto_original = descriptografar_texto(conteudo_criptografado, chaves, tabela_inversa)
print("Texto Original Descriptografado:", texto_original)
```
##### Observações
- O conteúdo criptografado deve estar no formato hexadecimal, sem espaços ou separadores.
- A tabela inversa (S-Box inversa) e as chaves expandidas devem ser correspondentes às usadas na criptografia.
- Padding (zeros adicionais) é removido automaticamente ao final do processo.
[Voltar ao índice](#índice)

--------------------------------------------------

### aes_openssl.py
#### main()
A função `main` é o ponto de entrada do programa, gerenciando o processo de criptografia e descriptografia de um arquivo utilizando o algoritmo AES-256-CBC. Ela solicita ao usuário o arquivo de entrada, realiza a criptografia, descriptografia, e verifica a integridade dos dados comparando o arquivo original com o resultado descriptografado.

##### Funcionamento
1. **Solicitação do Arquivo de Entrada:**
   - O programa solicita ao usuário o caminho do arquivo a ser processado.
   - Verifica se o arquivo existe antes de continuar.

2. **Configuração dos Arquivos de Saída:**
   - Define os caminhos para os arquivos criptografado e descriptografado.

3. **Geração de Chave e IV:**
   - Gera uma chave de 256 bits e um vetor de inicialização (IV) de 128 bits utilizando `os.urandom`.

4. **Processo de Criptografia:**
   - Criptografa o arquivo de entrada, salva o resultado e mede o tempo gasto.

5. **Processo de Descriptografia:**
   - Descriptografa o arquivo criptografado e mede o tempo total (incluindo criptografia e descriptografia).

6. **Verificação de Integridade:**
   - Lê e compara o conteúdo do arquivo original com o arquivo descriptografado.
   - Exibe o resultado da verificação e o tempo total de processamento.

7. **Tratamento de Erros:**
   - Captura e exibe erros relacionados ao acesso ou comparação dos arquivos.

##### Exemplo de Uso
1. O programa solicita ao usuário o caminho do arquivo de entrada:
```bash
Digite o caminho do arquivo de entrada: arquivo.txt
```
2. Após a execução, exibe:
```bash
Verificação: Descriptografia
Bem-sucedida: True 
Tempo total 0.123456 segundos
```

##### Observações
- Os arquivos criptografados e descriptografados são salvos nos diretórios configurados na função.
- O programa gera chaves e IVs de forma aleatória a cada execução.
- Para garantir que os arquivos sejam processados corretamente, é necessário que o OpenSSL esteja configurado no ambiente.
[Voltar ao índice](#índice)

#### processar_arquivo(input_file, output_file, chave, iv, operacao)
A função `processar_arquivo` utiliza o comando OpenSSL para criptografar ou descriptografar arquivos. Ela suporta o algoritmo AES-256-CBC e realiza operações baseadas em uma chave e um vetor de inicialização (IV) fornecidos pelo usuário.

##### Argumentos
- **`input_file`** (`str`):
  - Caminho para o arquivo de entrada que será processado.
- **`output_file`** (`str`):
  - Caminho para o arquivo de saída onde o resultado será salvo.
- **`chave`** (`str`):
  - Chave criptográfica em formato hexadecimal representando 32 bytes (256 bits).
- **`iv`** (`str`):
  - Vetor de inicialização (IV) em formato hexadecimal representando 16 bytes (128 bits).
- **`operacao`** (`str`):
  - Tipo de operação a ser realizada:
    - `"-e"` para criptografia.
    - `"-d"` para descriptografia.

##### Retorno
- **`float`**:
  - Tempo (em segundos) gasto na operação de criptografia ou descriptografia.
  - Retorna `-1` em caso de falha na execução.

##### Exceções
- **`ValueError`**:
  - Lançada se a operação especificada não for válida.
- **`Exception`**:
  - Lançada para erros gerais durante a execução do comando OpenSSL.

##### Funcionamento
1. **Validação da Operação:**
   - Verifica se a operação é válida (`-e` para criptografar, `-d` para descriptografar).
   - Lança um erro se a operação for inválida.

2. **Configuração do Comando OpenSSL:**
   - Monta o comando OpenSSL com os parâmetros fornecidos.

3. **Execução do Comando:**
   - Marca o tempo inicial antes da execução.
   - Executa o comando usando `subprocess.run`.

4. **Cálculo do Tempo de Execução:**
   - Calcula o tempo decorrido durante a execução do comando.
   - Exibe o tempo gasto no console.

5. **Tratamento de Erros:**
   - Captura erros relacionados ao subprocess ou gerais e exibe mensagens claras.

##### Exemplo de Uso
```python
# Parâmetros de entrada
input_file = "entrada.txt"
output_file = "saida.enc"
chave = "603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4"
iv = "000102030405060708090a0b0c0d0e0f"
operacao = "-e"  # Criptografar

# Processa o arquivo
tempo = processar_arquivo(input_file, output_file, chave, iv, operacao)
if tempo != -1:
    print(f"Operação concluída em {tempo:.6f} segundos.")
else:
    print("Erro na operação.")
```
##### Observações
- O OpenSSL deve estar instalado e configurado no ambiente para que a função funcione.
- A chave e o IV devem estar no formato hexadecimal e corresponder aos tamanhos esperados (32 bytes para chave e 16 bytes para IV).
- Essa função é útil para integrar processos de criptografia e descriptografia baseados em arquivos.
[Voltar ao índice](#índice)

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
   - `subprocess`
   - `typing`: Modules
      - `Dict`
      - `Any`
3. **OpenSSL**.

[Voltar ao índice](#índice)