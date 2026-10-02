"""
Software Único - Transmissão e Recepção via Camada Física Acústica
Atividade 1 - Redes de Computadores
"""

import sys

def menu_principal():
    while True:
        print("\n" + "="*55)
        print("   SISTEMA DE COMUNICAÇÃO ACÚSTICA - CAMADA FÍSICA")
        print("="*55)
        print("1. Método 1: Impacto/Batidas (Paridade Par - 9 Bits)")
        print("2. Método 2: Modulação FSK (Alta Velocidade - CRC-8)")
        print("3. Sair")
        print("="*55)
        
        opcao = input("Escolha uma opção (1-3): ").strip()

        if opcao == '1':
            try:
                import metodo1
                metodo1_menu(metodo1)
            except ImportError:
                print("[ERRO] Ficheiro 'metodo1.py' não encontrado na mesma pasta!")
        elif opcao == '2':
            try:
                import metodo2
                metodo2_menu(metodo2)
            except ImportError:
                print("[ERRO] Ficheiro 'metodo2.py' não encontrado na mesma pasta!")
        elif opcao == '3':
            print("\nEncerrando o sistema...")
            sys.exit(0)
        else:
            print("\n[!] Opção inválida. Tente novamente.")


def metodo1_menu(m1):
    while True:
        print("\n--- MÉTODO 1: BATIDAS (PARIDADE PAR) ---")
        print("1. Transmitir (Guia Emissor)")
        print("2. Receber (Escutar Microfone)")
        print("3. Voltar ao Menu Principal")
        op = input("Escolha: ").strip()

        if op == '1':
            msg = input("Digite um caractere para enviar: ")
            if len(msg) > 0:
                m1.guia_transmissao_metodo1(msg[0])
        elif op == '2':
            m1.escutar_quadro_metodo1()
        elif op == '3':
            break


def metodo2_menu(m2):
    while True:
        print("\n--- MÉTODO 2: MODULAÇÃO FSK (ALTA VELOCIDADE) ---")
        print("1. Transmitir Mensagem (Emitir Som)")
        print("2. Receber Mensagem (Escutar Som)")
        print("3. Voltar ao Menu Principal")
        op = input("Escolha: ").strip()

        if op == '1':
            txt = input("Digite a mensagem a enviar: ")
            if len(txt) > 0:
                m2.transmitir_fsk(txt)
        elif op == '2':
            try:
                tam = int(input("Informe o tamanho (nº de caracteres) da mensagem esperada: "))
                m2.escutar_fsk(tam)
            except ValueError:
                print("[!] Por favor, digite um número inteiro.")
        elif op == '3':
            break


if __name__ == "__main__":
    menu_principal()