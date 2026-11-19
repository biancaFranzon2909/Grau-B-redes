"""Modulações BPSK, QPSK e 16-QAM em canal AWGN e em canal com ruído em rajadas.

Roda o teste de consistência com a mensagem ASCII e o experimento de BER,
gravando os resultados brutos em resultados_modulacoes.csv.
"""
import csv
import numpy as np

NUM_BITS = 100_000
SNR_DB = [0, 2, 4, 6, 8, 10, 12, 14]
REPETICOES = 5
SEED = 42
MENSAGEM = "Redes de Computadores, Unisinos 2026/2. Trabalho do Grau B: BPSK, QPSK e 16-QAM."

# Bits por símbolo. Com banda de Nyquist (B = taxa de símbolos), este valor é a
# eficiência espectral nominal em bits/s/Hz.
BITS_POR_SIMBOLO = {"BPSK": 1, "QPSK": 2, "16-QAM": 4}

# Rajadas: cada símbolo inicia uma rajada com probabilidade P_RAJADA. A rajada dura
# TAM_RAJADA símbolos e soma um ruído com a potência do sinal (0 dB dentro da rajada).
P_RAJADA = 0.005
TAM_RAJADA = 20
POT_RAJADA = 1.0

PAM4 = np.array([-3, -1, 3, 1])  # índice 2*b0 + b1, mapeamento Gray: 00, 01, 11, 10


def texto_para_bits(texto):
    return np.unpackbits(np.frombuffer(texto.encode("ascii"), dtype=np.uint8)).astype(int)


def bits_para_texto(bits):
    return "".join(chr(b) if 32 <= b < 127 else "?" for b in np.packbits(bits))


def modular(bits, mod):
    """Bits -> símbolos complexos com potência média 1."""
    if mod == "BPSK":
        return (2.0 * bits - 1) + 0j
    if mod == "QPSK":
        b = 2.0 * bits.reshape(-1, 2) - 1
        return (b[:, 0] + 1j * b[:, 1]) / np.sqrt(2)
    b = bits.reshape(-1, 4)  # 16-QAM: 2 bits no eixo I e 2 bits no eixo Q
    return (PAM4[2 * b[:, 0] + b[:, 1]] + 1j * PAM4[2 * b[:, 2] + b[:, 3]]) / np.sqrt(10)


def demodular(simbolos, mod):
    """Símbolos recebidos -> bits, por detecção de limiar em cada eixo."""
    i, q = simbolos.real, simbolos.imag
    if mod == "BPSK":
        return (i > 0).astype(int)
    if mod == "QPSK":
        return np.column_stack([i > 0, q > 0]).astype(int).ravel()
    lim = 2 / np.sqrt(10)
    return np.column_stack([i > 0, abs(i) < lim, q > 0, abs(q) < lim]).astype(int).ravel()


def canal(simbolos, snr_db, rng, rajadas=False):
    """AWGN com SNR = potência do símbolo / potência do ruído. Com rajadas=True, soma as rajadas."""
    n = len(simbolos)
    pot_ruido = np.full(n, 10 ** (-snr_db / 10))
    if rajadas:
        inicio = rng.random(n) < P_RAJADA
        em_rajada = np.convolve(inicio, np.ones(TAM_RAJADA))[:n] > 0
        pot_ruido = pot_ruido + POT_RAJADA * em_rajada
    ruido = np.sqrt(pot_ruido / 2) * (rng.normal(size=n) + 1j * rng.normal(size=n))
    return simbolos + ruido


def transmitir(bits, mod, snr_db, rng, rajadas=False):
    return demodular(canal(modular(bits, mod), snr_db, rng, rajadas), mod)


def teste_mensagem():
    """Envia a mensagem ASCII em canal ideal, em SNR elevada e na maior SNR do experimento."""
    bits = texto_para_bits(MENSAGEM)
    rng = np.random.default_rng(SEED)
    print(f'Mensagem enviada ({len(bits)} bits): "{MENSAGEM}"')
    casos = [("Canal ideal", np.inf, False), ("AWGN 30 dB", 30, False), ("Rajadas 30 dB", 30, True),
             ("AWGN 14 dB", 14, False), ("Rajadas 14 dB", 14, True)]
    for nome, snr_db, rajadas in casos:
        print(f"\n{nome}")
        for mod in BITS_POR_SIMBOLO:
            recebidos = transmitir(bits, mod, snr_db, rng, rajadas)
            errados = np.flatnonzero(bits != recebidos)
            print(f'  {mod:6s} "{bits_para_texto(recebidos)}"')
            print(f"         bits incorretos: {len(errados)} {errados.tolist() if len(errados) else ''}")


def experimento(arquivo="resultados_modulacoes.csv"):
    """BER de cada modulação, canal e SNR, com REPETICOES sequências aleatórias de NUM_BITS bits."""
    rng = np.random.default_rng(SEED)
    with open(arquivo, "w", newline="") as f:
        saida = csv.writer(f)
        saida.writerow(["modulacao", "canal", "snr_db", "repeticao", "bits", "erros", "ber"])
        for mod in BITS_POR_SIMBOLO:
            for nome_canal, rajadas in [("AWGN", False), ("Rajadas", True)]:
                for snr_db in SNR_DB:
                    for rep in range(1, REPETICOES + 1):
                        bits = rng.integers(0, 2, NUM_BITS)
                        erros = int(np.sum(bits != transmitir(bits, mod, snr_db, rng, rajadas)))
                        saida.writerow([mod, nome_canal, snr_db, rep, NUM_BITS, erros, erros / NUM_BITS])
    print(f"\nResultados brutos gravados em {arquivo}")


if __name__ == "__main__":
    teste_mensagem()
    experimento()
