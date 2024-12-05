import math

def sieve_of_eratosthenes(limit):
    """Gera todos os números primos menores que 'limit' usando o Crivo de Eratóstenes."""
    sieve = [True] * limit
    sieve[0:2] = [False, False]  # 0 e 1 não são primos
    for current in range(2, int(math.sqrt(limit)) + 1):
        if sieve[current]:
            for multiple in range(current*current, limit, current):
                sieve[multiple] = False
    primes = [num for num, is_prime in enumerate(sieve) if is_prime]
    return primes

def extended_gcd(a, b):
    """Algoritmo de Euclides estendido.
    Retorna uma tupla (gcd, x, y) tal que a*x + b*y = gcd."""
    if b == 0:
        return (a, 1, 0)
    else:
        gcd, x1, y1 = extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return (gcd, x, y)

def mod_inverse(e, phi):
    """Encontra o inverso modular de e mod phi."""
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise Exception('Inverso modular não existe.')
    else:
        return x % phi

def find_private_key(e, n):
    """Encontra a chave privada d dado e & n."""
    primes = sieve_of_eratosthenes(1024)
    p = None
    q = None
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
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    return d, p, q

def encrypt_plaintext(plaintext, e, n):
    """Cifra o texto plaintext usando a chave pública {e, n}."""
    ciphertext = [str(pow(ord(char), e, n)) for char in plaintext]
    return ' '.join(ciphertext)

def decrypt_ciphertext(ciphertext, d, n):
    """Decifra o texto cifrado usando a chave privada d e módulo n."""
    decrypted_chars = []
    for num in ciphertext.split():
        c = int(num)
        if c >= n:
            raise Exception(f"Valor cifrado {c} é maior ou igual a n={n}. Decriptação inválida.")
        m = pow(c, d, n)
        decrypted_char = chr(m)
        decrypted_chars.append(decrypted_char)
    decrypted_text = ''.join(decrypted_chars)
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
        print("1. Cifrar um texto")
        print("2. Decifrar um texto cifrado")
        print("3. Sair")
        choice = input("Digite o número da opção desejada: ").strip()

        if choice == '1':# Cifrar
            plaintext = input("\nDigite o texto a ser cifrado:\n")
            ciphertext = encrypt_plaintext(plaintext, e, n)
            print(f"\nTexto cifrado (cada número representa um bloco cifrado, separado por espaço):\n{ciphertext}")
        elif choice == '2':# Decifrar
            print("\nDigite o texto cifrado. Insira os números separados por espaço.")
            ciphertext_input = input("Texto cifrado: ").strip()
            try:
                decrypted_text = decrypt_ciphertext(ciphertext_input, d, n)
                print(f"\nTexto decifrado:\n{decrypted_text}")
            except Exception as ex:
                print(f"Erro na decifragem: {ex}")
        elif choice == '3':
            print("Encerrando o programa.")
            break
        else:
            print("Opção inválida. Por favor, escolha 1, 2 ou 3.")

if __name__ == "__main__":
    main()
