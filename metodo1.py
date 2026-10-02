"""
Módulo do Método 1: Transmissão e Recepção Acústica por Impacto (Batidas)
Camada Física de Redes de Computadores
"""

import time
import numpy as np
import sounddevice as sd
from scipy.signal import find_peaks

# --- CONFIGURAÇÕES DE ÁUDIO E PARÂMETROS ---
SAMPLE_RATE = 44100          
CHUNK_DURATION = 2.5         
THRESHOLD = 0.12             
MIN_DISTANCE_SAMPLES = 6615  


def calcular_bit_paridade(bits_8):
    """Calcula o bit de paridade par para 8 bits de dados."""
    return 0 if (sum(bits_8) % 2 == 0) else 1


def empacotar_quadro(byte_val):
    """Converte um caractere/número de 8 bits em um quadro de 9 bits com Paridade Par."""
    bits = [(byte_val >> i) & 1 for i in reversed(range(8))]
    p_bit = calcular_bit_paridade(bits)
    return bits + [p_bit]


def validar_quadro(quadro_9_bits):
    """Valida a paridade par do quadro recebido."""
    if len(quadro_9_bits) != 9:
        return False, "Quadro incompleto."

    dados = quadro_9_bits[:8]
    paridade_recebida = quadro_9_bits[8]
    paridade_esperada = calcular_bit_paridade(dados)

    if paridade_recebida == paridade_esperada:
        byte_val = 0
        for bit in dados:
            byte_val = (byte_val << 1) | bit
        char_rec = chr(byte_val) if 32 <= byte_val <= 126 else f"0x{byte_val:02X}"
        return True, f"Caractere Decodificado: '{char_rec}' [Bits: {dados}, Paridade Par: {paridade_recebida}]"
    else:
        return False, f"Erro de Paridade Par! Esperado: {paridade_esperada}, Recebido: {paridade_recebida}"


def guia_transmissao_metodo1(mensagem):
    print("\n--- INICIANDO TRANSMISSÃO (MÉTODO 1 - BATIDAS) ---")
    print("Instruções:")
    print(" Bit 0 -> 1 BATIDA  (Silêncio + 1 Batida + Silêncio)")
    print(" Bit 1 -> 2 BATIDAS (Silêncio + 2 Batidas Rápidas + Silêncio)")
    print("-" * 50)

    for char in mensagem:
        byte_val = ord(char)
        quadro = empacotar_quadro(byte_val)
        print(f"\nTransmitindo '{char}' -> Quadro de 9 bits: {quadro}")
        input("Pressione ENTER para iniciar o envio deste caractere...")

        for idx, bit in enumerate(quadro):
            print(f"\n[Bit {idx+1}/9] Enviar BIT {bit}:")
            if bit == 0:
                print(" -> Faça exatamente 1 BATIDA!")
            else:
                print(" -> Faça exatamente 2 BATIDAS RÁPIDAS!")
            
            time.sleep(CHUNK_DURATION)

    print("\n--- Transmissão Concluída! ---")


def detectar_bit_em_chunk(audio_chunk):
    """Classifica o bit de acordo com o número de picos detectados."""
    amplitude = np.abs(audio_chunk)
    peaks, _ = find_peaks(amplitude, height=THRESHOLD, distance=MIN_DISTANCE_SAMPLES)
    num_peaks = len(peaks)
    max_amp = np.max(amplitude)

    if num_peaks == 1:
        return 0, num_peaks, max_amp
    elif num_peaks == 2:
        return 1, num_peaks, max_amp
    else:
        return -1, num_peaks, max_amp


def escutar_quadro_metodo1():
    print("\n--- MODO RECEPTOR (MÉTODO 1) ATIVADO ---")
    print(f"Cada bit terá uma janela de {CHUNK_DURATION}s. (1 Batida = Bit 0 | 2 Batidas = Bit 1)")
    input("\nPressione ENTER para começar a escutar o quadro de 9 bits...")

    quadro_recebido = []
    historico_picos = []
    historico_amps = []

    for i in range(9):
        print(f"\n[Bit {i+1}/9] Escutando... (Bata agora!)")
        
        recording = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        
        audio_flat = recording.flatten()
        bit_detectado, picos, max_amp = detectar_bit_em_chunk(audio_flat)

        historico_picos.append(picos)
        historico_amps.append(max_amp)

        if bit_detectado != -1:
            print(f" -> Detetado {picos} impacto(s) (Pico Max: {max_amp:.2f}) => BIT {bit_detectado}")
            quadro_recebido.append(bit_detectado)
        else:
            print(f" -> Ruído/Silêncio ({picos} impactos, Pico Max: {max_amp:.2f}). Assumindo Bit 0.")
            quadro_recebido.append(0)

    # Processamento e Validação da Paridade
    sucesso, resultado = validar_quadro(quadro_recebido)

    # ========================================================
    # DEMONSTRATIVO VISUAL DO QUADRO RECEBIDO NO TERMINAL
    # ========================================================
    print("\n" + "="*60)
    print("           DEMONSTRATIVO DE RECEPÇÃO DO QUADRO")
    print("="*60)
    print(" Bit Nº | Batidas Lidas | Amp. Max | Bit Decodificado | Gráfico")
    print("-" * 60)
    
    for idx in range(9):
        bit_val = quadro_recebido[idx]
        picos_lidos = historico_picos[idx]
        amp = historico_amps[idx]
        # Gera uma barra em texto proporcional à amplitude do sinal
        barra_grafica = "█" * int(amp * 30)
        
        tipo_bit = "DADO" if idx < 8 else "PARIDADE"
        print(f"   {idx+1}   |      {picos_lidos}        |   {amp:.2f}   |      [{bit_val}] ({tipo_bit})   | {barra_grafica}")

    print("-" * 60)
    print(f" Quadro Final (9 Bits): {quadro_recebido}")
    print(f" Bits de Dados (8 Bits): {quadro_recebido[:8]}")
    print(f" Bit de Paridade Par ($b_9$): {quadro_recebido[8]}")
    print("-" * 60)

    if sucesso:
        print(f" STATUS DE PROCESSAMENTO: [ SUCESSO ]")
        print(f" Detalhe: {resultado}")
    else:
        print(f" STATUS DE PROCESSAMENTO: [ FALHA DE TRANSMISSÃO ]")
        print(f" Detalhe: {resultado}")
    print("="*60 + "\n")


if __name__ == "__main__":
    while True:
        print("\n--- CAMADA FÍSICA / MÉTODO 1 (BATIDAS) ---")
        print("1. Transmitir (Guia)")
        print("2. Receber (Escutar Microfone)")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            msg = input("Digite um caractere para enviar: ")
            if len(msg) > 0:
                guia_transmissao_metodo1(msg[0])
        elif opcao == '2':
            escutar_quadro_metodo1()
        elif opcao == '3':
            break
        else:
            print("Opção inválida.")