# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 13:59:37 2019

@author: vitor
"""

from enlace import *
import time

# Serial Com Port
# para saber a sua porta, execute no terminal:
# python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411"  # Mac    (variacao de)
serialName = "COM5"                    # Windows(variacao de)

#arquivo = input("Selecione o arquivo (eg.: 'download.jpg'): \n \n")
def stuffing(txBuffer):
    for i in range(len(txBuffer) - 2):
        if txBuffer[i:i+3] == eop:
            txBuffer = txBuffer[:i] + bytes([2]) + txBuffer[i] + \
            bytes([2]) + txBuffer[i+1] + bytes([2]) + txBuffer[i+2:]
    
    return txBuffer


def packing(txBuffer, eop):
    tamanho = len(txBuffer)
    if (tamanho%115 == 0):
         qntpacotes = (tamanho//115)
    else:
         qntpacotes = (tamanho//115 + 1)
         
    pacoteatual = 1   
    
    #Definir quantidade de pacotes
    
    lista_pacotes = []
    
    for i in range(qntpacotes):
        
            
            if i < (qntpacotes - 1):
                payload = txBuffer[(115*i):115+(115*i)]
            else:
                payload = txBuffer[i*115:]
                
            tamanho = len(payload)
                
            head = qntpacotes.to_bytes(2, byteorder="little") + \
            pacoteatual.to_bytes(2, byteorder="little") + \
            tamanho.to_bytes(6, byteorder="little")
            
            lista_pacotes.append(head + payload + eop)
            pacoteatual += 1
    
    return lista_pacotes
            
eop = bytes("eop", "utf-8")

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
        arquivo = 'download.jpg'
        
        with open (arquivo, 'rb') as f:
            img = f.read()
            txBuffer = bytearray(img)
    
        
        lenTx = len(txBuffer)
        
        txBuffer2 = stuffing(txBuffer)

        lista_pacotes = packing(txBuffer2, eop)
        
        for i in lista_pacotes:
            com.sendData(i)
            
            # espera o fim da transmissão
            while(com.tx.getIsBusy()):
                pass
            while(com.rx.getIsEmpty()):
                pass
            
            Zou1 = int.from_bytes(com.getData(1)[0], byteorder="little")
            
            if Zou1 == 0:
                print("ERRO: pacotes fora de sequência")
                com.disable()
            elif Zou1 == 2:
                print("Todos pacotes enviados")
                break
            else:
                pass
        
        while(com.rx.getIsEmpty()):
            pass
        
        rxBuffer = int.from_bytes(com.getData(2)[0], byteorder="little")
    
        print("---------------------------------------")
        print("Verificação concluida")
        print("---------------------------------------")
        if rxBuffer == lenTx:
            print("O tamanho dos dados são iguais")
            print("---------------------------------------")
        else:
            print("ERRO")
            print("---------------------------------------")
            
        elapsed = time.time() - start_time
        print("Elapsed time: {} s" .format(elapsed))
        print("Taxa de Transmissão: {} bytes/s" .format(lenTx/elapsed))
    
        # Encerra comunicação
        print("---------------------------------------")
        print("Comunicação encerrada")
        print("---------------------------------------")
        com.disable()
        
    except:
        com.disable()

    #so roda o main quando for executado do terminal ... 
    #se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
