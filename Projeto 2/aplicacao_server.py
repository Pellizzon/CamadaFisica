
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

from enlace import *
# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)

def main():
    com = enlace(serialName) 
    # Ativa comunicacao
    com.enable()
    try:
        # Inicializa enlace ... variavel com possui todos 
        com.fisica.flush()
        # os metodos e propriedades do enlace, que funciona em threading
        # repare que o metodo construtor recebe um string (nome)
        # Ativa comunicacao
#        com.fisica.flush()
        # Log
        print("-------------------------")
        print("Comunicação inicializada")
        print("Porta : {}".format(com.fisica.name))
        print("-------------------------")
      
        eopFound = True
        eop = bytes("eop", "utf-8")
        stuffing = bytes("2e2o2p", "utf-8")
        
        while com.rx.getIsEmpty():
            pass
        
        # Separa o buffer em head e payload + eop
        allBuffer = com.rx.getAllBuffer(len)
        head = allBuffer[:10]
        tamanho = int.from_bytes(head, byteorder="little")
        rxBuffer = allBuffer[10:]
        
        # Localiza EOP
        for i in range(len(rxBuffer) - 2):
            if rxBuffer[i:i+3] == eop:
                rxBuffer = rxBuffer[:i]
                eopFound = True
            else:
                eopFound = False
            posEOP = i
            
        if eopFound and posEOP == tamanho:
            # Remove stuffing
            for i in range(len(rxBuffer) - 5):
                if rxBuffer[i:i+6] == stuffing:
                    rxBuffer = rxBuffer[:i] + rxBuffer[i+1] + rxBuffer[i+3] \
                    + rxBuffer[i+5:]
            
            # Salva arquivo
            with open ("Nomearquivo.png","wb") as arquivo:
                arquivo.write(rxBuffer)
        
            overhead = (tamanho + len(head))/len(rxBuffer)
            
            print("Overhead: {:.2f}".format(overhead))
            print("Posição EOP: {}".format(posEOP))
            
            #Envia tamanho do que foi recebido para verifiacação
            lenRx = len(rxBuffer)
            txBuffer = lenRx.to_bytes(2, byteorder="little")
            com.sendData(txBuffer)
            
            # Atualiza dados da transmissão
            txSize = com.tx.getStatus()
            print ("Transmitido {} bytes ".format(txSize))
            
        elif posEOP != tamanho:
            print("ERRO: EOP localizado fora do local esperados")
            erro = bytes("erro 1", "utf-8")
            com.sendData(erro)
                
        else:
            print("ERRO: EOP não encontrado")
            erro = bytes("erro 2", "utf-8")
            com.sendData(erro)
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except:
        com.sendData(bytes("erro", "utf-8"))
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
