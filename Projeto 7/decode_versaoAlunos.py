#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""

#Importe todas as bibliotecas
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window
import time
import peakutils



#funcao para transformas intensidade acustica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
     
    #declare um objeto da classe da sua biblioteca de apoio (cedida)   
    
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    freqAmostragem = 44100
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    
    sd.default.samplerate = freqAmostragem #taxa de amostragem
    sd.default.channels = 2  #voce pode ter que alterar isso dependendo da sua placa
    duration = 2 #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic
    
    
    # faca um printo na tela dizendo que a captacao comecará em n segundos. e entao
    delay = 2
    for e in range(delay):
        print("A captação começará em {}".format(delay-e))
        #use um time.sleep para a espera
        time.sleep(1)
       
    #faca um print informando que a gravacao foi inicializada
    print("Gravacao inicializada")
       
    #declare uma variavel "duracao" com a duracao em segundos da gravacao. poucos segundos ... 
    duracao = duration
    #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes)
    
    numAmostras = duracao*freqAmostragem
    audio = sd.rec(int(numAmostras), freqAmostragem, channels=1)
    sd.wait()
    print("...     FIM")
    
    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    audio_lista = []
    #grave uma variavel com apenas a parte que interessa (dados)
    for e in audio:
        audio_lista.append(e[0])
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    inicio = 0
    fim = duracao
    numPontos = int(numAmostras)
    t = np.linspace(inicio,fim,numPontos)
    
    # plot do gravico  áudio vs tempo!    
    plt.plot(t,audio_lista)
    
    table = {697:{1209:"1", 1336:"2", 1477:"3"}, 
         772:{1209:"4", 1336:"5", 1477:"6"},
         852:{1209:"7", 1336:"8", 1477:"9"},
         941:{1336:"0"}, 0: {0: "ERRO"}}
    plt.show()
    
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    signal = signalMeu()
    xf, yf = signal.calcFFT(audio_lista, freqAmostragem)
    plt.figure("F(y)")
    plt.plot(xf,yf)
    plt.grid()
    plt.title('Fourier audio')
    plt.show()
    
    
    #esta funcao analisa o fourier e encontra os picos
    #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
    
    index = peakutils.indexes(yf, 0.2, 200)
    
    picos = []
    for i in index:
        picos.append(xf[i])
    temaki = 0
    temaki2 = 0

    for pico in picos: 
        if temaki == 0:
            for i in table:
                if abs(pico-i) < 30:
                    temaki = i
        if temaki != 0:
            for i in table[temaki]:
                if abs(pico-i) < 30:
                    print(i)
                    temaki2 = i
    
    #printe os picos encontrados! 
    
    print("Picos: {}".format(picos))
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print a tecla.
    
    
    print("resposta: {}".format(table[temaki][temaki2]))
    
    ## Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()