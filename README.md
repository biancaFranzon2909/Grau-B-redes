# Trabalho do Grau B (Redes de Computadores)

Simulador de comunicação digital desenvolvido em Python para a disciplina de Redes de Computadores.

## Arquitetura do Sistema

O fluxo de simulação segue as etapas principais de um enlace digital:
1. **Geração de Dados:** Conversão de mensagens ASCII para sequências binárias e geração de massa de dados aleatória (100.000 bits) para análise estatística.
2. **Codificação de Linha:** Transformação dos bits em níveis de tensão utilizando as técnicas **Manchester** e **AMI** (*Alternate Mark Inversion*).
3. **Modulação Digital:** Mapeamento do sinal em portadoras utilizando **BPSK**, **QPSK** e **16-QAM**.
4. **Canal Ruidoso:** Simulação de canal **AWGN** com controle de Relação Sinal-Ruído (SNR) e segundo cenário de degradação (ruído em rajadas).
5. **Recepção e Métricas:** Demodulação, detecção por limiar, reconstrução da mensagem, cálculo da **BER** e análise de **Eficiência Espectral**.

---

## Divisão de Responsabilidades da Dupla

### Integrante A — Bianca da Silva Franzon
* **Geração de Dados:** Implementação da conversão de strings ASCII para sequências binárias e geração de amostras de 100.000 bits.
* **Codificação de Linha:** Implementação das codificações Manchester e AMI (com alternância de polaridade para eliminação de componente DC).
* **Modelagem de Canal e Métricas:** Desenvolvimento do canal ruidoso AWGN com variação em 8 níveis de SNR, execução das 5 repetições aleatórias por ponto, cálculo da BER média e desvio padrão, e exportação dos resultados brutos para `resultados_ber.csv`.

### Integrante B — João Fidelis
* **Modulações Digitais:** Implementação das modulações e demodulações **BPSK**, **QPSK** e **16-QAM**.
* **Segundo Cenário e Eficiência Espectral:** Modelagem do canal com ruído em rajadas e cálculo da eficiência espectral nominal ($\text{bits/s/Hz}$).
* **Análise Visual e Documentação Final:** Geração das curvas comparativas de $\text{BER} \times \text{SNR}$ com barras de erro a partir dos dados brutos, montagem da tabela de compromisso e gravação do vídeo demonstrativo.

---

## Parâmetros Experimentais Adotados

* **Volume de Transmissão:** $100.000\text{ bits}$ por ensaio.
* **Faixa de SNR (AWGN):** $0, 2, 4, 6, 8, 10, 12\text{ e }14\text{ dB}$ (8 pontos).
* **Repetições Estatísticas:** $5$ execuções independentes por nível de SNR para cálculo de média e variabilidade (desvio padrão).
* **Semente Aleatória Base:** `seed = 42` para reprodutibilidade dos experimentos.

---

## Como Instalar e Executar

### 1. Pré-requisitos
Certifique-se de ter o **Python 3** instalado juntamente com as bibliotecas `numpy` e `matplotlib`:

```bash
pip install numpy matplotlib
python algorimConversao.py