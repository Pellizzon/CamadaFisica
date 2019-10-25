#!/usr/bin/env python3

# Importe todas as bibliotecas
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy import signal
import time
import soundfile as sf


sinal = signalMeu()

# declare um objeto da classe da sua biblioteca de apoio (cedida)

# declare uma variavel com a frequencia de amostragem, sendo 44100
freqAmostragem = 44100

sd.default.samplerate = freqAmostragem  # taxa de amostragem
sd.default.channels = 2  # voce pode ter que alterar isso dependendo da sua placa
duration = 5  # tempo em segundos que ira aquisitar o sinal acustico captado pelo mic

# delay = 2
# for e in range(delay):
#     print("A captação começará em {}".format(delay-e))
#     # use um time.sleep para a espera
#     time.sleep(1)

print("Gravacao inicializada")


# numAmostras = duration*freqAmostragem
# audio = sd.rec(int(numAmostras), freqAmostragem, channels=1)
# sd.wait()


data, samplerate = sf.read("modulado.wav")


print("Fim da gravação")

audio_lista = []
for e in data:
    audio_lista.append(e)


time, Signal = sinal.generateSin(14000, 1, len(
    audio_lista)/freqAmostragem, freqAmostragem)


mini = abs(min(audio_lista))
maxi = abs(max(audio_lista))

if mini > maxi:
    moduloMax = mini
else:
    moduloMax = maxi

l = []
for i in audio_lista:
    v = i/moduloMax
    l.append(v)

demodulado = []
for i in range(len(l)):
    demodulado.append(l[i]*Signal[i])

# filtro
nyq_rate = freqAmostragem/2
width = 5.0/nyq_rate
ripple_db = 60.0  # dB
N, beta = signal.kaiserord(ripple_db, width)
cutoff_hz = 4000.0
taps = signal.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
yFiltrado = signal.lfilter(taps, 1.0, demodulado)


sd.play(yFiltrado, freqAmostragem)

sd.wait()


plt.plot(time, data)
plt.title("original x tempo")
plt.show()

sinal.plotFFT(audio_lista, samplerate)
plt.title("original x freq")
plt.show()

plt.plot(time, l)
plt.title("normalizado x tempo")
plt.show()

sinal.plotFFT(l, samplerate)
plt.title("normalizado x freq")
plt.show()

plt.plot(time, yFiltrado)
plt.title("filtrado x tempo")
plt.show()

sinal.plotFFT(yFiltrado, samplerate)
plt.title("filtrado x freq")
plt.show()

plt.plot(time, demodulado)
plt.title("modulado x tempo")
plt.show()

sinal.plotFFT(demodulado, samplerate)
plt.title("modulado x freq")
plt.show()
