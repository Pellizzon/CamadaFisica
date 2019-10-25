# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:03:37 2019

@author: thive
"""

import time
from enlace import *
from PyCRC.CRC16 import CRC16

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM5"                  # Windows(variacao de)


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


def message_type2():
    message_type = 2
    lenPayload = 0
    package = message_type.to_bytes(1, byteorder="big") + \
    lenPayload.to_bytes(9, byteorder="big") + eop

    return package

def message_type4(lastapackage):
    message_type = 4
    lenPayload = 0
    package = message_type.to_bytes(1, byteorder="big") + \
    lastapackage.to_bytes(1,byteorder="big") + \
    lenPayload.to_bytes(8, byteorder="big") + eop
    
    return package

def message_type5():
    message_type = 5
    lenPayload = 0
    package = message_type.to_bytes(1, byteorder="big") + \
    lenPayload.to_bytes(9, byteorder="big") + eop
    return package
    
def message_type6(realpackage):
    message_type = 6
    lenPayload = 0
    package = message_type.to_bytes(1, byteorder="big") + \
    realpackage.to_bytes(1,byteorder="big") + \
    lenPayload.to_bytes(8, byteorder="big") + eop
    return package

crc = CRC16()

def main():
    com = enlace(serialName)
    com.rx.clearBuffer()
    # Ativa comunicacao
    com.enable()
    eopFound = True
    lista = []
    contador = 1
    temaki = False

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
    server = 2
    while True:
        if temaki:
            break
        starttime = time.time()
        # Separa o buffer em head e payload + eop
        while time.time()-starttime < 2:
            if temaki: 
                break
            if com.rx.getBufferLen() >= 10:
                head = com.getData(10)[0]
                #print(head)        
                messagetype = head[:1]
                #print(messagetype)
                identificador = int.from_bytes(head[1:2], byteorder="big")
                #print(identificador)
                crc_received = int.from_bytes(head[2:4], byteorder="big")
                lenPayload = head[4:10]
                #print(lenPayload)
                payload = com.getData(int.from_bytes(lenPayload, byteorder="big"))[0]
                crc_check = crc.calculate(payload)
                
                qntPack = int.from_bytes(payload, byteorder="big")
                eop = com.getData(3)[0]
                
                if crc_received != crc_check:
                    package = message_type6(contador)
                    com.sendData(package)
                    print("ERRO: crc check falhou")
                    with open ("log.txt", "a") as f:
                        f.write("MSG: 6 - enviada: {} - destinatário: {}\n"\
                        .format(messagetype, time.time()-starttime, identificador))
                    pass
                
                with open ("log.txt", "w") as f:
                    f.write("MSG: {} - recebida: {} - remetente: {}\n"\
                            .format(int.from_bytes(messagetype, byteorder="big"), time.time()-starttime, identificador))
                
                if identificador == server:
                    package = message_type2()
                    com.sendData(package)
                    contador = 1
                    with open ("log.txt", "a") as f:
                        f.write("MSG: 2 - enviada: {} - destinatário: {}\n"\
                            .format(time.time()-starttime, identificador))
                    
                    while contador != (qntPack+1):
                        send = time.time()
                        while com.rx.getIsEmpty():
                            if time.time() - starttime >= 20:
                                com.sendData(message_type5())
                                print("timeout")
                                with open ("log.txt", "a") as f:
                                    f.write("MSG: 5 - enviada: {} - destinatário: 2\n"\
                                        .format(messagetype, time.time()-starttime, identificador))
                                com.disable()
                                return
                            elif time.time() - send > 2:
                                package = message_type6(contador-1)
                                com.sendData(package)
                                send = time.time()
                                while com.tx.getIsBusy():
                                    pass
                            else:
                                pass

                        if time.time() - starttime >= 20:
                            com.sendData(message_type5())
                            print("timeout")
                            com.disable()
                            return
                        temaki = True
                        message = com.getData(10)[0]
                        messagetype = int.from_bytes(message[:1], byteorder="big")
                        with open ("log.txt", "a") as f:
                            f.write("MSG: {} - recebida: {} - remetente: {}\n"\
                                .format(messagetype, time.time()-starttime, identificador))
                    
                        if messagetype == 3:
                            qntpackages = int.from_bytes(message[1:3], byteorder="big")
                            atualpackage = int.from_bytes(message[3:5], byteorder="big")
                            crc_received2 = int.from_bytes(message[5:7], byteorder="big")
                            tamanhopack = int.from_bytes(message[7:], byteorder="big")
                        
                            if qntpackages == qntPack:
                                
                                tamanho = tamanhopack
                                numero = atualpackage
                                total = qntpackages
                                
                                rxBuffer = com.getData(tamanho+len(eop))[0]
                                eopFound, posEOP, rxBuffer = FindEOP(rxBuffer)
                                
                                crc_check2 = crc.calculate(bytes(rxBuffer))
                                
                                print(crc_check2, crc_received2)
                                
                                if crc_check2 != crc_received2:
                                    package = message_type6(contador)
                                    com.sendData(package)
                                    print("ERRO: crc check falhou")
                                    with open ("log.txt", "a") as f:
                                        f.write("MSG: 6 - enviada: {} - destinatário: {}\n"\
                                        .format(messagetype, time.time()-starttime, identificador))
                                    pass
                                
                                with open ("log.txt", "a") as f:
                                    f.write("MSG_buffer: {} - recebida: {} - remetente: {}\n"\
                                        .format(messagetype, time.time()-starttime, identificador))
                                                    
                                if eopFound and posEOP == tamanho:
                                            
                                    if numero == contador and numero != (total + 1):
                                        package = message_type4(numero)
                                        com.sendData(package)
                                        with open ("log.txt", "a") as f:
                                            f.write("MSG: 4 - enviada: {} - destinatário: {}\n"\
                                                .format(time.time()-starttime, identificador))
                                        lista.append(rxBuffer)
                                        print("Recebido pacote {} de {}".format\
                                              (numero, total))
                                        contador += 1
                                        starttime = time.time()
                                        pass
                                    else:
                                        print("ERRO:  Pacote incorreto")
                                        package = message_type6(contador)
                                        com.sendData(package)
                                        with open ("log.txt", "a") as f:
                                            f.write("MSG: 6 - enviada: {} - destinatário: {}\n"\
                                                .format(messagetype, time.time()-starttime, identificador))
                                        pass
                                else:
                                    package = message_type6(contador)
                                    com.sendData(package)
                                    print("ERRO: EOP fora do local esperado")
                                    with open ("log.txt", "a") as f:
                                            f.write("MSG: 6 - enviada: {} - destinatário: {}\n"\
                                                .format(messagetype, time.time()-starttime, identificador))
                                    pass
                        elif messagetype == 5:
                            print("timeout")
                            com.disable()

                else:
                    print("acabou")
                    break
                
            else:
                break
            
    mensagem = bytearray()
    for i in lista:            
        mensagem += i
   
    rxBuffer = RemoveStuffing(mensagem)
    
    with open ("Nomearquivo.png","wb") as f:
        f.write(rxBuffer)
        
    lenb = len(rxBuffer).to_bytes(2, byteorder="big")
    com.sendData(lenb)
    
    while (com.tx.getIsBusy()):
        pass
    
    overhead = (tamanho + len(head))/len(rxBuffer)
    
    print("-------------------------")
    print("Overhead: {:.2f}".format(overhead))
    print("Posição EOP: {}".format(posEOP))

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    com.disable()
            
if __name__ == "__main__":
    main()