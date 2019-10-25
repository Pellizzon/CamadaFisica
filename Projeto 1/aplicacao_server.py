
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

print("comecou")

from enlace import *
import time


# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)
print("abriu com")


def main():
    # Inicializa enlace ... variavel com possui todos 
    # os metodos e propriedades do enlace, que funciona em threading
    # repare que o metodo construtor recebe um string (nome)
    com = enlace(serialName) 
    # Ativa comunicacao
    com.enable()
    
    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("Porta : {}".format(com.fisica.name))
    print("-------------------------")
  
#    a, b = com.getData(2)
#    tamanho = int.from_bytes(a, byteorder="little")
#        
#    # repare que o tamanho da mensagem a ser lida é conhecida!     
#    rxBuffer, nRx = com.getData(tamanho + 2)
    
    while com.rx.getIsEmpty():
        pass
    
    tamanho_byte = com.rx.getBuffer(2)
    tamanho = int.from_bytes(tamanho_byte, byteorder="little")
    rxBuffer, nRx = com.getData(tamanho)

    # log 
    print ("Lido {} bytes ".format(nRx))
    
    with open ("Nomearquivo.png","wb") as arquivo:
        arquivo.write(rxBuffer)

    #Envia tamanho do que foi recebido para verifiacação
    lenRx = len(rxBuffer)
    txBuffer = lenRx.to_bytes(2, byteorder="little")
    com.sendData(txBuffer)
    
    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
    print ("Transmitido {} bytes ".format(txSize))

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
