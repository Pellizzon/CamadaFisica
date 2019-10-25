from enlace import *
import time
from PyCRC.CRC16 import CRC16

# Serial Com Port
# para saber a sua porta, execute no terminal:
# python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411"  # Mac    (variacao de)
serialName = "COM4"                    # Windows(variacao de)

#arquivo = input("Selecione o arquivo (eg.: 'download.jpg'): \n \n")
def stuffing(txBuffer):
    eop = bytes("eop", "utf-8")
    for i in range(len(txBuffer) - 2):
        if txBuffer[i:i+3] == eop:
            txBuffer = txBuffer[:i] + bytes([2]) + txBuffer[i] + \
            bytes([2]) + txBuffer[i+1] + bytes([2]) + txBuffer[i+2:]
            
    return txBuffer

#FUNÇÃO PARA SABER QUANTOS PACOTES SERÃO ENVIADOS
def quantPacking(txBuffer):
    tamanho = len(txBuffer)
    if (tamanho%115 == 0):
         qntpacotes = (tamanho//115)
    else:
         qntpacotes = (tamanho//115 + 1)
         
    return qntpacotes

#FUNÇÃO DE CONVITE PARA COMUNICAÇÃO
def message_type1(quantidade, identificador):
    message_type = 1
    payload = quantidade.to_bytes(10,byteorder="big")
    lenPayload = len(payload)
    cr = crc.calculate(payload)
    
    pack = message_type.to_bytes(1, byteorder="big") + \
    identificador.to_bytes(1,byteorder="big") + \
    cr.to_bytes(2, byteorder="big") + \
    lenPayload.to_bytes(6, byteorder="big") + \
    payload + eop
    return pack

# NOSSA NOVA PACKING 
def message_type3(txBuffer, quantidade):  
    pacoteatual = 1       
    lista_pacotes = []
    message_type = 3
    
    for i in range(quantidade):
        if i < (quantidade - 1):
            payload = txBuffer[(115*i):115+(115*i)]
        else:
            payload = txBuffer[i*115:]

        cr = crc.calculate(bytes(payload))
        print(cr)
            
        tamanho = len(payload)
    
        head = message_type.to_bytes(1, byteorder="big") + \
        quantidade.to_bytes(2, byteorder="big") + \
        pacoteatual.to_bytes(2, byteorder="big") + \
        cr.to_bytes(2, byteorder="big") + \
        tamanho.to_bytes(3, byteorder="big")
        
        lista_pacotes.append(head + payload + eop)
        pacoteatual += 1
    
    return lista_pacotes

#FUNÇÃO DE TIMEOUT ENVIA E ENCERRA COMUNICAÇÃO
def message_type5():
    message_type = 5
    lenPay = 0
    package = message_type.to_bytes(1, byteorder="big") + \
    lenPay.to_bytes(9, byteorder="big") + eop
    
    return package
    
eop = bytes("eop", "utf-8")
crc = CRC16()

def main():
    com = enlace(serialName)
    # Ativa comunicacao
    com.enable()

    # Inicializa enlace ... variavel com possui todos 
    com.fisica.flush()
    com.rx.clearBuffer()
    # os metodos e propriedades do enlace, que funciona em threading
    # repare que o metodo construtor recebe um string (nome)
    start_time = time.time()
    starttt = time.time()
    
    temaki = False
    
    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("Porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega dados
    while True:
        if temaki:
            break        
        arquivo = 'download.jpg'
        log = "logclient.txt"
        
        
        
        with open (arquivo, 'rb') as f:
            img = f.read()
            mensagem = bytearray(img)
            lenTx = len(mensagem)
        number_of_packages = quantPacking(mensagem)
        identificador = 2  # NÃO FAÇO A MINIMA IDEIA DO QUE É
        startcom = message_type1(number_of_packages, identificador)
        start = time.time()
        #ENVIA A MENSAGEM TIPO 1

        com.sendData(startcom)
        with open (log, 'w') as f:
            f.write("Msg: 1 – enviada: {} – destinatário: {} \n".format(time.time() - start,identificador ))
        

        
        while com.tx.getIsBusy():
            pass
        start_time = time.time()
        
        while time.time() - start_time < 2:
            if temaki:
                break
            if com.rx.getBufferLen() >= 13:

                confirmcom = com.getData(10)[0]
                print(confirmcom)
                message_type = int.from_bytes(confirmcom[:1], byteorder="big")
                lenPayload = confirmcom[1:]
                eop = com.getData(3)[0]
                with open (log, 'a') as f:
                    f.write("Msg: {} – rebecida: {} – remetente: {} \n".format(message_type,time.time() - start_time,identificador ))
                
                if message_type == 2:
                    txBuffer = stuffing(mensagem)
                    
                    lista_pacotes = message_type3(txBuffer, number_of_packages)
                    
                    
                    contador = 1
        
                    while True:
                        if number_of_packages == (contador-1):
                            break
                        elif time.time() - start >= 20:
                            print("Timeout")
                            com.sendData(message_type5())
                            with open (log, 'a') as f:
                                f.write("Msg: 5 – enviada: {} – destinatário: {} \n".format(time.time()-start_time, identificador)) 
                            return 
                    
                        com.sendData(lista_pacotes[contador - 1])
                        with open (log, 'a') as f:
                            f.write("Msg: 3 – enviada: {} – destinatário: {} \n".format(time.time() - start_time,identificador ))                        
                        #posso receber uma mensagem do tipo 4 ou tipo 6 que vem 2 bytes
                        while com.rx.getIsEmpty():
                            if time.time() - starttt > 20:
                                print("Timeout")
                                com.sendData(message_type5())
                                com.disable()
                                with open (log, 'a') as f:
                                    f.write("Msg: 5 – enviada: {} – destinatário: {} \n".format(time.time()-start_time, identificador)) 
                                return 
                            else:
                                pass
                            
                        confirmpack = com.getData(10)[0]
                        confirm_type = int.from_bytes(confirmpack[:1], byteorder="big")
                        with open (log, 'a') as f:
                            f.write("Msg: {} – recebida: {} – destinatário: {} \n".format(confirm_type,time.time() - start,identificador ))                        
                        
                        if confirm_type == 4:
                            lastpackage = int.from_bytes(confirmpack[1:2],byteorder="big")
                            #print(lastpackage)
                            eop = com.getData(3)[0]
                            #print("pacote confirmado")
                            if lastpackage == contador:
                                contador += 1
                                temaki = True
                                start = time.time()
                                starttt = time.time()
                                pass

                        #SIGNIFICA QUE O SERVIDOR MANDOU UMA MENSAGEM TIPO 6 (PACOTE REPETIDO OU FORA DE ORDEM)
                        elif confirm_type == 6:
                            realpackage = int.from_bytes(confirmpack[1:2],byteorder="big")
                            lenPayload = confirmpack[2:]
                            eop = com.getData(3)[0]
                            #ENTÃO VAMOS ENVIAR O PACOTE CERTO
                            com.sendData(lista_pacotes[realpackage-1])
                            contador = realpackage
                            with open (log, 'a') as f:
                                f.write("Msg: {} – enviada: {} – destinatário: {} \n".format(3,time.time() - start_time,identificador ))
                                
                        elif confirm_type == 5:
                            print("Timeout")
                            com.disable()
                            
                        else:
                            print("ERRO")
                            package = message_type5()
                            com.sendData(package)
                            with open (log, 'a') as f:
                                f.write("Msg: {} – enviada: {} – destinatário: {} \n".format(5,time.time() - start_time,identificador ))
                            com.disable()
                        
                        
    while(com.rx.getIsEmpty()):
            pass
        
    rxBuffer = int.from_bytes(com.getData(2)[0], byteorder="big")
    

    print("---------------------------------------")
    print("Verificação concluida")
    print("---------------------------------------")
    if rxBuffer == lenTx:
        print("O tamanho dos dados são iguais")
        print("---------------------------------------")
    else:
        print("ERRO")
        print("---------------------------------------")
        
    elapsed = time.time() - start
    print("Elapsed time: {} s" .format(elapsed))
    print("Taxa de Transmissão: {} bytes/s" .format(lenTx/elapsed))

    # Encerra comunicação
    print("---------------------------------------")
    print("Comunicação encerrada")
    print("---------------------------------------")
    com.disable()
            
        
       
if __name__ == "__main__":
    main()
