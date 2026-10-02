# Atividade 1: Comunicação Digital na Camada Física usando Som

**Disciplina:** Redes de Computadores  
**Licença:** Open-Source (MIT)  

## Integrantes da Equipe
* **Guilherme Rodrigues Soares** - RA: 2254026


---

## 1. Fundamentação Teórica

### Modelo ISO/OSI
O modelo ISO/OSI é composto por 7 camadas: Aplicação, Apresentação, Sessão, Transporte, Rede, Enlace e Física. 

### A Camada Física e Comunicação Acústica
A Camada Física é responsável pela transmissão bruta de bits (*raw bits*) através do meio físico (neste caso, ondas sonoras propagadas no ar).
* **Sinais Analógicos vs. Digitais:** Variações binárias de dados (`0` e `1`) são convertidas em variações contínuas de pressão acústica (sinal analógico).
* **Amostragem e Largura de Banda:** Utilizou-se uma taxa de amostragem de 44.1 kHz para evitar o efeito de *aliasing* (Teorema de Nyquist).
* **Detecção de Erros:**
  * **Paridade Par (Método 1):** Garante que o número total de bits `1` em um quadro de 9 bits seja par ($b_9$).
  * **CRC-8 (Método 2):** Algoritmo polinomial ($x^8 + x^2 + x + 1$) utilizado para validação de integridade dos pacotes FSK em alta velocidade.

---

## 2. Engenharia e Arquitetura das Soluções

### Método 1: Impactos / Batidas Padronizadas
* **Padrão de Bit:**
  * `Bit 0`: Silêncio + 1 impacto + Silêncio.
  * `Bit 1`: Silêncio + 2 impactos consecutivos + Silêncio.
* **Mecanismo:** Janela temporal ajustada para 2.5 segundos por bit e filtragem de ruído baseada em limiar de amplitude (*threshold*).

### Método 2: Modulação FSK (Frequency-Shift Keying)
* **Codificação de Tons:**
  * `Bit 0`: Tom senoidal puro em **1200 Hz**.
  * `Bit 1`: Tom senoidal puro em **2200 Hz**.
* **Velocidade:** Duração de 50 ms por bit ($\approx 20\text{ bps}$).
* **Decodificação:** Aplicação de FFT (*Fast Fourier Transform*) no sinal capturado para identificar frequências de pico.

---

## 3. Divisão de Tarefas

* **Guilherme Rodrigues Soares:** Responsável pelo projeto completo do trabalho, incluindo a concepção da arquitetura, implementação dos algoritmos de áudio (FFT e geração FSK), integração da validação de erros (Paridade Par e CRC-8), testes práticos do microfone, estruturação do repositório no GitHub e gravação do vídeo de demonstração.

---

## 4. Desafios, Problemas e Soluções

* **Ruído e Duração do Sinal:** O tempo padrão por bit no Método 1 era excessivamente curto para reação humana. **Solução:** Expansão da janela de captura para 2.5s por bit e otimização dos limiares de picos.
* **Verificação de Erros no Sinal Acústico:** O meio acústico sofre interferência de reflexões e atenuação. A implementação da Paridade Par e do CRC-8 garantiu a sinalização precisa de **SUCESSO** e **FALHA DE TRANSMISSÃO** na interface do terminal.

---

## 5. Declaração do Uso de Inteligência Artificial Generativa

Ferramentas de IA Generativa foram utilizadas como auxílio para:
1. Estruturação inicial do código em Python para manipulação do `sounddevice` e `scipy`.
2. Formatação da documentação técnica no padrão Markdown.
3. Revisão do algoritmo de validação polinomial do CRC-8.

---

## 6. Conclusão

A atividade demonstrou na prática os desafios inerentes à Camada Física do modelo ISO/OSI ao utilizar o meio acústico como canal de transmissão. Foi possível comprovar a relevância dos mecanismos de verificação da Camada de Enlace para atenuar imperfeições físicas como o ruído ambiente e a perda de sincronismo.