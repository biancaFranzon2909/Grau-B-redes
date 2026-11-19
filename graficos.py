"""Gera os gráficos BER x SNR e a tabela de compromisso a partir dos resultados brutos (CSV)."""
import csv
import os
from collections import defaultdict
from math import erfc, sqrt

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from modulacoes import BITS_POR_SIMBOLO, SNR_DB

ESTILO = {"BPSK": ("#2a78d6", "o"), "QPSK": ("#eb6834", "s"), "16-QAM": ("#1baf7a", "^")}
os.makedirs("graficos", exist_ok=True)

# ber[(modulação, canal)][snr] = lista com a BER de cada repetição
ber = defaultdict(lambda: defaultdict(list))
with open("resultados_modulacoes.csv") as f:
    for linha in csv.DictReader(f):
        ber[(linha["modulacao"], linha["canal"])][int(linha["snr_db"])].append(float(linha["ber"]))


def media_desvio(mod, canal):
    return ([np.mean(ber[(mod, canal)][s]) for s in SNR_DB], [np.std(ber[(mod, canal)][s]) for s in SNR_DB])


def ber_teorica(mod, snr_db):
    """BER teórica em AWGN, com SNR = Es/N0 e mapeamento Gray."""
    Q = lambda x: 0.5 * erfc(x / sqrt(2))
    g = 10 ** (snr_db / 10)
    if mod == "BPSK":
        return Q(sqrt(2 * g))
    if mod == "QPSK":
        return Q(sqrt(g))
    a = sqrt(g / 5)
    return (3 * Q(a) + 2 * Q(3 * a) - Q(5 * a)) / 4


def salvar(titulo, arquivo):
    plt.yscale("log")
    plt.ylim(1e-6, 1)
    plt.xticks(SNR_DB)
    plt.xlabel("SNR (dB)")
    plt.ylabel("BER")
    plt.title(titulo)
    plt.grid(True, which="both", color="#e4e4e0", linewidth=0.6)
    plt.legend()
    plt.savefig(os.path.join("graficos", arquivo), dpi=150, bbox_inches="tight")
    plt.close()


# 1) AWGN: simulação (média e desvio padrão das repetições) e curva teórica
plt.figure(figsize=(7, 4.5))
snr_fino = np.linspace(SNR_DB[0], SNR_DB[-1], 100)
for mod, (cor, marcador) in ESTILO.items():
    media, desvio = media_desvio(mod, "AWGN")
    plt.errorbar(SNR_DB, media, yerr=desvio, color=cor, marker=marcador, markersize=7, linewidth=2,
                 capsize=4, label=f"{mod} (simulada)")
    plt.plot(snr_fino, [ber_teorica(mod, s) for s in snr_fino], color=cor, linestyle=":", linewidth=1.2)
plt.plot([], [], color="gray", linestyle=":", linewidth=1.2, label="Teórica")
salvar("BER x SNR em canal AWGN (média e desvio de 5 repetições)", "ber_awgn.png")

# 2) AWGN x canal com rajadas
plt.figure(figsize=(7, 4.5))
for mod, (cor, marcador) in ESTILO.items():
    for canal, traco, preenchimento in [("AWGN", "--", "white"), ("Rajadas", "-", cor)]:
        media, desvio = media_desvio(mod, canal)
        plt.errorbar(SNR_DB, media, yerr=desvio, color=cor, marker=marcador, markersize=7, linewidth=2,
                     linestyle=traco, markerfacecolor=preenchimento, capsize=4, label=f"{mod} ({canal})")
salvar("BER x SNR: AWGN x canal com rajadas", "ber_awgn_x_rajadas.png")

# 3) Codificação de linha AMI, a partir de resultados_ber.csv
with open("resultados_ber.csv") as f:
    ami = [[float(v) for v in linha.values()] for linha in csv.DictReader(f)]
snr_ami, media_ami, desvio_ami = zip(*ami)
plt.figure(figsize=(7, 4.5))
plt.errorbar(snr_ami, media_ami, yerr=desvio_ami, color="#2a78d6", marker="o", markersize=7, linewidth=2,
             capsize=4, label="AMI")
salvar("BER x SNR da codificação de linha AMI em canal AWGN", "ber_ami.png")

# 4) Tabela de compromisso entre BER e eficiência espectral
linhas = ["| Modulação | Eficiência espectral nominal (bits/s/Hz) | BER AWGN 6 dB | BER AWGN 10 dB | "
          "BER AWGN 14 dB | BER Rajadas 14 dB | Menor SNR testada com BER ≤ 10⁻³ (AWGN) |",
          "|---|---|---|---|---|---|---|"]
for mod, k in BITS_POR_SIMBOLO.items():
    awgn = dict(zip(SNR_DB, media_desvio(mod, "AWGN")[0]))
    rajadas = dict(zip(SNR_DB, media_desvio(mod, "Rajadas")[0]))
    snr_min = next((f"{s} dB" for s in SNR_DB if awgn[s] <= 1e-3), "acima de 14 dB")
    linhas.append(f"| {mod} | {k} | {awgn[6]:.2e} | {awgn[10]:.2e} | {awgn[14]:.2e} | {rajadas[14]:.2e} | {snr_min} |")
with open("tabela_compromisso.md", "w") as f:
    f.write("\n".join(linhas) + "\n")
print("\n".join(linhas))
print("\nGráficos gravados na pasta graficos/ e tabela em tabela_compromisso.md")
