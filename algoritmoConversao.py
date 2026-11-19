import numpy as np
import csv

print("Iniciand Simulação :)")

# 1. Plano Experimental
num_bits = 100000
snr_db_list = [0, 2, 4, 6, 8, 10, 12, 14]
num_repeticoes = 5

# Sequência binária aleatória longa 
np.random.seed(42)
bits_originais = np.random.randint(0, 2, num_bits)

# 2. AMI
def codificar_ami(bits):
    sinal = []
    ultimo_um = -1
    for b in bits:
        if b == 0:
            sinal.append(0.0)
        else:
            ultimo_um *= -1
            sinal.append(float(ultimo_um))
    return np.array(sinal)

sinal_base = codificar_ami(bits_originais)

# 3. Canal AWGN e Cálculo de BER
resultados = []

print(f"Transmitindo {num_bits} bits para {len(snr_db_list)} níveis de SNR ({num_repeticoes} repetições cada)...")

for snr in snr_db_list:
    ber_por_repeticao = []
    
    for rep in range(num_repeticoes):
        # Ruído AWGN com base na SNR
        potencia_sinal = np.mean(sinal_base ** 2)
        snr_linear = 10 ** (snr / 10)
        potencia_ruido = potencia_sinal / snr_linear
        desvio_padrao = np.sqrt(potencia_ruido)
        
        ruido = np.random.normal(0, desvio_padrao, len(sinal_base))
        sinal_recebido = sinal_base + ruido
        
        # Decodificação por limiar para AMI
        bits_recebidos = np.array([0 if abs(x) < 0.3 else 1 for x in sinal_recebido])
        
        # Cálculo da BER
        erros = np.sum(bits_originais != bits_recebidos)
        ber = erros / num_bits
        ber_por_repeticao.append(ber)

    
    ber_media = np.mean(ber_por_repeticao)
    ber_desvio = np.std(ber_por_repeticao)
    
    resultados.append([snr, ber_media, ber_desvio])
    print(f"SNR: {snr:2.0f} dB | BER Média: {ber_media:.6f} | Desvio Padrão: {ber_desvio:.6f}")

# 4. João, use os dados vindos aqui para gerar os graficos
nome_ficheiro = "resultados_ber.csv"
with open(nome_ficheiro, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["SNR_dB", "BER_Media", "BER_Desvio"])
    writer.writerows(resultados)

print(f"\nDados guardados em '{nome_ficheiro}")