
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
from tkinter import filedialog
from tkinter import *

# Serial Com Port
# para saber a sua porta, execute no terminal:
# python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411"  # Mac    (variacao de)
serialName = "COM5"                    # Windows(variacao de)
print("abriu com")

arquivo = input("Selecione o arquivo (eg.: 'download.jpg'): \n \n")

root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
print (root.filename)

def main():
    # Inicializa enlace ... variavel com possui todos 
    # os metodos e propriedades do enlace, que funciona em threading
    # repare que o metodo construtor recebe um string (nome)
    com = enlace(serialName) 
    # Ativa comunicacao
    com.enable()
    
    start_time = time.time()
    
    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("Porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega dados
    print ("Gerando dados para transmissao:")
    
    with open (arquivo, 'rb') as f:
        img = f.read()
        txBuffer = bytearray(img)
        
        lenTx = len(txBuffer)
        txBuffer = lenTx.to_bytes(2, byteorder="little") + txBuffer    

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
        print("ERRO: tamanho de saida e entrada divergentes")
        print("-------------------------")
        
    elapsed = time.time() - start_time
    print("Elapsed time: {} s" .format(elapsed))
    print("Taxa de Transmissão: {} bytes/s" .format(lenTx/elapsed))

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... 
    #se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
