
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

from enlace import *
import time

# Serial Com Port
# para saber a sua porta, execute no terminal:
# python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411"  # Mac    (variacao de)
serialName = "COM5"                    # Windows(variacao de)

#arquivo = input("Selecione o arquivo (eg.: 'download.jpg'): \n \n")

def main():
    com = enlace(serialName) 
    # Ativa comunicacao
    com.enable()
    try:
        # Inicializa enlace ... variavel com possui todos 
        com.fisica.flush()
        # os metodos e propriedades do enlace, que funciona em threading
        # repare que o metodo construtor recebe um string (nome)
        start_time = time.time()
        
        # Log
        print("-------------------------")
        print("Comunicação inicializada")
        print("Porta : {}".format(com.fisica.name))
        print("-------------------------")
    
        # Carrega dados
        print ("Gerando dados para transmissao:")
        
        with open ('download.jpg', 'rb') as f:
            img = f.read()
            txBuffer = bytearray(img)
#        txBuffer = bytes("thiago", "utf-8")
        lenTx = len(txBuffer)
            
        eop = bytes("eop", "utf-8")
        
        for i in range(len(txBuffer) - 2):
            if txBuffer[i:i+3] == eop:
                txBuffer = txBuffer[:i] + bytes([2]) + txBuffer[i] + \
                bytes([2]) + txBuffer[i+1] + bytes([2]) + txBuffer[i+2:]
    
        head = len(txBuffer).to_bytes(10, byteorder="little")
        
        txBuffer = head + txBuffer + eop
        
        # Transmite dado
        print("tentado transmitir .... {} bytes".format(len(txBuffer)))
        com.sendData(txBuffer)
    
        # espera o fim da transmissão
        while(com.tx.getIsBusy()):
            pass
        
        # Atualiza dados da transmissão
        txSize = com.tx.getStatus()
        print ("Transmitido {} bytes ".format(txSize))
        
        while com.rx.getIsEmpty():
            pass
        
        #Recebe tamanho e compara com o que foi enviado
        rxBuffer = int.from_bytes(com.rx.getAllBuffer(len), byteorder="little")
        print("-------------------------")
        print("Verificação concluida")
        print("-------------------------")
        if rxBuffer == lenTx:
            print("O tamanho dos dados são iguais")
            print("-------------------------")
        else:
            print("ERRO")
            print("-------------------------")
            
        elapsed = time.time() - start_time
        print("Elapsed time: {} s" .format(elapsed))
        print("Taxa de Transmissão: {} bytes/s" .format(lenTx/elapsed))
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
        
    except:
        com.disable()

    #so roda o main quando for executado do terminal ... 
    #se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
