# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:07:00 2019

@author: vitor
"""


from enlace import *
# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM7"                  # Windows(variacao de)


def RemoveStuffing(rxBuffer):
    stuffing = bytes("2e2o2p", "utf-8")
    for i in range(len(rxBuffer) - 5):
                if rxBuffer[i:i+6] == stuffing:
                    rxBuffer = rxBuffer[:i] + rxBuffer[i+1] + rxBuffer[i+3] \
                    + rxBuffer[i+5:]
                    
    return rxBuffer

def FindEOP(rxBuffer):
    # Localiza EOP
    for i in range(len(rxBuffer) - 2):
        if rxBuffer[i:i+3] == eop:
            rxBuffer = rxBuffer[:i]
            eopFound = True
        else:
            eopFound = False
        posEOP = i
    
    return eopFound, posEOP, rxBuffer

eop = bytes("eop", "utf-8")

def main():
    com = enlace(serialName)
    com.rx.clearBuffer()
    # Ativa comunicacao
    com.enable()
    x = 10
    
    # =========================================================================
    # -----------------------------NOSSAS VARIÁVEIS----------------------------
    # =========================================================================
    eopFound = True
    lista = []
    contador = 1
    # =========================================================================
    # -------------------------------------------------------------------------
    # =========================================================================
    try:
        # Inicializa enlace ... variavel com possui todos 
        com.fisica.flush()
        # os metodos e propriedades do enlace, que funciona em threading
        # repare que o metodo construtor recebe um string (nome)
        # Ativa comunicacao
        # Log
        print("-------------------------")
        print("Comunicação inicializada")
        print("Porta : {}".format(com.fisica.name))
        print("-------------------------")
        
        while True:
            while com.rx.getIsEmpty():
                pass
            # Separa o buffer em head e payload + eop
            head = com.getData(10)[0]
            tamanho = int.from_bytes(head[4:10], byteorder="little")
            numero = int.from_bytes(head[2:4], byteorder="little")
            total = int.from_bytes(head[0:2], byteorder="little")
            print(tamanho)
            rxBuffer = com.getData(tamanho+len(eop))[0]
            eopFound, posEOP, rxBuffer = FindEOP(rxBuffer)
            print(numero, total, contador)
                
            if eopFound and posEOP == tamanho:
                        
                if numero == contador and numero != (total + 1):
                    lista.append(rxBuffer)
                    print("Recebido pacote {} de {}".format(numero, total))
                else:
                    print("ERRO: pacote fora de ordem")
                    com.disable()
                    
                if total == numero:
                    txBuffer = bytes([2])
                    com.sendData(txBuffer)
                
                elif len(rxBuffer) == tamanho:
                     #Envia tam  anho do que foi recebido para verifiacação
                     txBuffer = bytes([1])
                     com.sendData(txBuffer)
                else:
                    txBuffer = bytes([0])
                    com.sendData(txBuffer)
                    
            elif posEOP != tamanho:
                print("ERRO: EOP localizado fora do local esperados")
                print(posEOP)
                print(tamanho)
                erro = bytes("erro 1", "utf-8")
                com.sendData(erro)
                com.disable()
                
            else:
                print("ERRO: EOP não encontrado")
                erro = bytes("erro 2", "utf-8")
                com.sendData(erro)
                com.disable()
                    
            if contador == total:
                break
            else:
                contador += 1
                pass
            
        mensagem = bytearray()
        for i in lista:            
            mensagem += i
        

            
        rxBuffer = RemoveStuffing(mensagem)
        print(len(rxBuffer))
        
        with open ("Nomearquivo.png","wb") as arquivo:
#        arquivo.write(rxBuffer[2:])
            arquivo.write(rxBuffer)
            
        # Salva arquivo
#        with open ("Nomearquivo.jpg","wb") as arquivo:
#            arquivo.write(rxBuffer)
        lenb = len(rxBuffer).to_bytes(2, byteorder="little")
        print(lenb)
        com.sendData(lenb)
        
        
        while (com.tx.getIsBussy()):
            pass
        
    
        overhead = (tamanho + len(head))/len(rxBuffer)
        
        print("Overhead: {:.2f}".format(overhead))
        print("Posição EOP: {}".format(posEOP))
            
        # Atualiza dados da transmissão
        txSize = com.tx.getStatus()
        print ("Transmitido {} bytes ".format(txSize))
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        print(lenb)
        com.disable()
    except:
        com.sendData(bytes("erro", "utf-8"))
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
