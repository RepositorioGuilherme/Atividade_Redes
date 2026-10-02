import time
import numpy as np
import sounddevice as sd


SAMPLE_RATE = 44100     
FREQ_BIT_0 = 1200        
FREQ_BIT_1 = 2200       
BIT_DURATION = 0.05      


# ==========================================
# 1. CAMADA DE ENLACE: VERIFICAÇÃO CRC-8
# ==========================================

def calcular_crc8(dados_bytes):
    """
    Calcula o Checksum CRC-8 (Polinômio x^8 + x^2 + x + 1 | 0x07)
    para garantir a integridade da mensagem em alta velocidade.
    """
    crc = 0x00
    for byte in dados_bytes:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


# ==========================================
# 2. EMISSOR (GERADOR DE SINAIS FSK)
# ==========================================

def gerar_onda_tom(frequencia, duracao):
    """Gera uma onda senoidal analógica para a frequência especificada."""
    t = np.linspace(0, duracao, int(SAMPLE_RATE * duracao), False)
    onda = 0.5 * np.sin(2 * np.pi * frequencia * t)
    return onda


def transmitir_fsk(texto):
    """Converte o texto em bits, gera o CRC-8 e emite os sons FSK pelo alto-falante."""
    print(f"\n--- TRANSMITINDO VIA FSK (MÉTODO 2) ---")
    print(f"Mensagem: '{texto}'")

    dados_bytes = texto.encode('utf-8')
    crc_valor = calcular_crc8(dados_bytes)
    
    # Adiciona o byte do CRC-8 ao final do pacote de dados
    pacote_completo = dados_bytes + bytes([crc_valor])

    # Converte os bytes do pacote em uma sequência de bits
    bits_totais = []
    for b in pacote_completo:
        bits_totais.extend([(b >> i) & 1 for i in reversed(range(8))])

    print(f"Pacote (Dados + CRC-8): {len(pacote_completo)} bytes ({len(bits_totais)} bits)")
    print("Iniciando emissão sonora de alta velocidade...")

    # Concatena os tons senoidais de cada bit num único sinal de áudio
    sinal_audio = np.array([], dtype=np.float32)
    for bit in bits_totais:
        freq = FREQ_BIT_1 if bit == 1 else FREQ_BIT_0
        tom = gerar_onda_tom(freq, BIT_DURATION)
        sinal_audio = np.concatenate((sinal_audio, tom))

    # Reproduz o sinal de áudio na caixa de som
    sd.play(sinal_audio, SAMPLE_RATE)
    sd.wait()

    taxa_bps = 1 / BIT_DURATION
    print(f"Transmissão Concluída! Taxa aproximada: {taxa_bps:.1f} bps\n")


# ==========================================
# 3. RECEPTOR (DECODIFICADOR FSK POR FFT)
# ==========================================

def detectar_frequencia_dominante(chunk_audio):
    """Utiliza a Transformada Rápida de Fourier (FFT) para identificar o tom recebido."""
    # Aplica janela Hanning para reduzir vazamento espectral
    janela = chunk_audio * np.hanning(len(chunk_audio))
    espectro = np.abs(np.fft.rfft(janela))
    frequencias = np.fft.rfftfreq(len(janela), 1 / SAMPLE_RATE)

    # Identifica a frequência com maior energia
    indice_pico = np.argmax(espectro)
    freq_detectada = frequencias[indice_pico]
    return freq_detectada


def escutar_fsk(num_caracteres_esperados):
    """
    Escuta o áudio do microfone, processa os blocos FSK, extrai os bits e valida com CRC-8.
    """
    # Total de bytes = caracteres de dados + 1 byte de CRC-8
    total_bytes = num_caracteres_esperados + 1
    total_bits = total_bytes * 8
    duracao_total = total_bits * BIT_DURATION

    print(f"\n--- MODO RECEPTOR FSK ATIVADO ---")
    print(f"Aguardando sinal de {duracao_total:.2f} segundos ({total_bits} bits)...")
    input("Aproxime o microfone do alto-falante e pressione ENTER para escutar...")

    # Grava o áudio do microfone pela duração exata da mensagem
    gravacao = sd.rec(int(duracao_total * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()

    sinal_plano = gravacao.flatten()
    amostras_por_bit = int(SAMPLE_RATE * BIT_DURATION)
    bits_recebidos = []

    # Processa cada fatia de áudio correspondente a 1 bit
    for i in range(total_bits):
        inicio = i * amostras_por_bit
        fim = inicio + amostras_por_bit
        chunk = sinal_plano[inicio:fim]

        freq = detectar_frequencia_dominante(chunk)

        # Classifica com base na frequência do tom detectado
        if abs(freq - FREQ_BIT_1) < abs(freq - FREQ_BIT_0):
            bits_recebidos.append(1)
        else:
            bits_recebidos.append(0)

    # Reconstrói os bytes recebidos
    bytes_reconstruidos = bytearray()
    for b in range(total_bytes):
        byte_bits = bits_recebidos[b*8 : (b+1)*8]
        val = 0
        for bit in byte_bits:
            val = (val << 1) | bit
        bytes_reconstruidos.append(val)

    dados_finais = bytes_reconstruidos[:-1]
    crc_recebido = bytes_reconstruidos[-1]
    crc_calculado = calcular_crc8(dados_finais)

    # Exibição clara e obrigatória do status de integridade
    print("\n" + "="*50)
    if crc_recebido == crc_calculado:
        texto_decodificado = dados_finais.decode('utf-8', errors='replace')
        print(" STATUS: [ SUCESSO ]")
        print(f" Mensagem Recebida: '{texto_decodificado}'")
        print(f" Validação CRC-8: OK (Recebido: 0x{crc_recebido:02X})")
    else:
        print(" STATUS: [ FALHA DE TRANSMISSÃO ]")
        print(" Erro de CRC-8: Dados corrompidos pelo ruído ambiente.")
        print(f" CRC Esperado: 0x{crc_calculado:02X} | CRC Recebido: 0x{crc_recebido:02X}")
    print("="*50 + "\n")


# ==========================================
# 4. MENU PRINCIPAL DE TESTES
# ==========================================

if __name__ == "__main__":
    while True:
        print("\n--- CAMADA FÍSICA / MÉTODO 2 (MODULAÇÃO FSK - ALTA VELOCIDADE) ---")
        print("1. Transmitir Mensagem (Emitir Som)")
        print("2. Receber Mensagem (Escutar Som)")
        print("3. Sair")
        op = input("Escolha uma opção: ")

        if op == '1':
            txt = input("Digite a mensagem para enviar: ")
            if len(txt) > 0:
                transmitir_fsk(txt)
        elif op == '2':
            try:
                tam = int(input("Informe a quantidade de letras da mensagem esperada: "))
                escutar_fsk(tam)
            except ValueError:
                print("Por favor, digite um número inteiro válido.")
        elif op == '3':
            break
        else:
            print("Opção inválida.")