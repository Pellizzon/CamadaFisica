#importe as bibliotecas
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    print("Inicializando encoder")
    
    #declare um objeto da classe da sua biblioteca de apoio (cedida)
    meuSinal = signalMeu()
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    freq = 44100
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:

    duration = 2 #tempo em segundos que ira emitir o sinal acustico 

    #relativo ao volume. Um ganho alto pode saturar sua placa... comece com .3    
    gainX  = 0.3
    gainY  = 0.3

    print("Gerando Tons base")
    
    table = {"1":[1209, 697], "2":[1336, 697], "3":[1477, 697],
         "4":[1209, 772], "5":[1336, 772], "6":[1447, 772],
         "7":[1209, 852], "8":[1336, 852], "9":[1447, 852], "0":[1336, 941]}
    
    #gere duas senoides para cada frequencia da tabela DTMF! Canal x e canal y 
    #use para isso sua biblioteca (cedida)
    #obtenha o vetor tempo tb.
    #deixe tudo como array
    
    #printe a mensagem para o usuario teclar um numero de 0 a 9. 
    #nao aceite outro valor de entrada.
     
    l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    while True:
        NUM = (input("Digite algum número, de 0 a 9: "))
        try:
           NUM = int(NUM)
        except ValueError:
           print("That's not an int!")
           pass
       
        if NUM in l:
            break
        else:
            pass
        
    n = str(NUM)
        
    tempo_x, sine_x = meuSinal.generateSin(table[n][0], gainX, duration, freq)
    tempo_y, sine_y = meuSinal.generateSin(table[n][1], gainY, duration, freq)
    
    sound = []
    for i in range(len(sine_x)):
        sound.append(sine_x[i] + sine_y[i])
    
    print("Gerando Tom referente ao símbolo : {}" .format(NUM))
    
    #construa o sinal a ser reproduzido. nao se esqueca de que é a soma das senoides
    
    #printe o grafico no tempo do sinal a ser reproduzido
    # reproduz o som
    sd.play(sound, freq)
    # Exibe gráficos
    plt.plot(tempo_x, sound)
    plt.xlim(0, 0.01)
    plt.show()
    # aguarda fim do audio
    sd.wait()

if __name__ == "__main__":
    main()
