import math

def sieve_of_eratosthenes(limit):
    """Gera todos os números primos menores que 'limit' usando o Crivo de Eratóstenes."""
    # Inicializa uma lista que assume que todos os números são primos
    sieve = [True] * limit
    sieve[0:2] = [False, False]  # Define 0 e 1 como não primos
    # Itera até a raiz quadrada de 'limit' para marcar múltiplos de cada número como não primos
    for current in range(2, int(math.sqrt(limit)) + 1):
        if sieve[current]:  # Verifica se o número é primo
            for multiple in range(current * current, limit, current):
                sieve[multiple] = False  # Marca os múltiplos como não primos
    # Retorna a lista de números primos
    primes = [num for num, is_prime in enumerate(sieve) if is_prime]
    return primes

def extended_gcd(a, b):
    """Algoritmo de Euclides estendido. gcd=Greatest Common Divisor
    Retorna uma tupla (gcd, x, y) tal que a*x + b*y = gcd."""
    if b == 0:
        return (a, 1, 0)  # Caso base
    else:
        gcd, x1, y1 = extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return (gcd, x, y)

def mod_inverse(e, phi):
    """Encontra o inverso modular de e mod phi."""
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise Exception('Inverso modular não existe.')  # O inverso modular só existe se "e" e "phi" são coprimos
    else:
        return x % phi  # Ajusta o resultado para estar no intervalo [0, phi-1]

def find_private_key(e, n):
    """Encontra a chave privada d dado e & n."""
    primes = sieve_of_eratosthenes(1024)  # Gera números primos entre 1 e 1024 para fatorar n
    p = None
    q = None
    # Tenta encontrar os fatores primos "p" e "q" de n
    for prime in primes:
        if n % prime == 0:
            p = prime
            q = n // p
            if q in primes:
                break
            else:
                p = None
                q = None
    if p is None or q is None:
        raise Exception('Fatores primos p e q não encontrados com os limites fornecidos.')
    # Calcula o totiente de n
    phi = (p - 1) * (q - 1)
    # Calcula o inverso modular de e
    d = mod_inverse(e, phi)
    return d, p, q

def encrypt_plaintext(plaintext, e, n):
    """Cifra o texto plaintext usando a chave pública {e, n}."""
    # Para cada caractere, calcula o valor cifrado usando a fórmula c = m^e mod n
    ciphertext = [str(pow(ord(char), e, n)) for char in plaintext]
    return ' '.join(ciphertext)  # Retorna os valores cifrados como uma string

def decrypt_ciphertext(ciphertext, d, n):
    """Decifra o texto cifrado usando a chave privada d e módulo n."""
    decrypted_chars = []
    for num in ciphertext.split():  # Divide os blocos cifrados
       c = int(num)
       if c >= n:
           raise Exception(f"Valor cifrado {c} é maior ou igual a n={n}. Decriptação inválida.")
       # Calcula o valor decifrado usando m = c^d mod n
       m = pow(c, d, n)
       decrypted_char = chr(m)  # Converte o valor decifrado de volta para um caractere
       decrypted_chars.append(decrypted_char)
    decrypted_text = ''.join(decrypted_chars)  # Junta os caracteres decifrados
    return decrypted_text

def main():
    # Entrada: Chave pública {e, n}
    print("=== RSA Cifragem e Decifragem ===")
    try:
        e = int(input("Digite o valor de e (expoente público) conhecido: ").strip())
        n = int(input("Digite o valor de n (produto de p e q) conhecido: ").strip())
    except ValueError:
        print("Erro: Por favor, insira valores inteiros válidos para e e n.")
        return

    try:
        d, p, q = find_private_key(e, n)
        print(f"\nChave privada encontrada:")
        print(f"d = {d}")
        print(f"p = {p}")
        print(f"q = {q}")
    except Exception as ex:
        print(f"Erro ao encontrar a chave privada: {ex}")
        return

    while True:
        print("\nEscolha uma operação:")
        print(f"1. Cifrar um texto, com {d}")
        print(f"2. Decifrar um texto cifrado, com {d}")
        print("3. Sair")
        choice = input("Digite o número da opção desejada: ").strip()
        match choice:
            case '1': # Cifrar
                plaintext = input("\nDigite o texto a ser cifrado:\n")
                # Verifica se todos os caracteres têm m<n
                max_m = max(ord(char) for char in plaintext)
                if max_m > n:
                    print(f"Erro: O valor máximo de m ({max_m}) é maior que n ({n}). Impossibilitando a cifra correta!")
                    exit(1)
                ciphertext = encrypt_plaintext(plaintext, e, n)
                print(f"\nTexto cifrado (cada número representa um bloco cifrado, separado por espaço):\n{ciphertext}")
            case '2':  # Decifrar
                print("\nDigite o texto cifrado. Insira os números separados por espaço.")
                ciphertext_input = input("Texto cifrado: ").strip()
                try:
                    decrypted_text = decrypt_ciphertext(ciphertext_input, d, n)
                    print(f"\nTexto decifrado:\n{decrypted_text}")
                except Exception as ex:
                    print(f"Erro na decifragem: {ex}")
            case '3':
                print("Encerrando o programa.")
                break
            case _:
                print("Opção inválida. Por favor, escolha 1, 2 ou 3.")

if __name__ == "__main__":
    main()
