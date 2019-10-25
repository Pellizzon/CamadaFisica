# importe as bibliotecas
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from scipy import signal
import soundfile as sf
import time


data, samplerate = sf.read("rilrilril.wav")
dados = []

for i in data:
    dados.append(i[0])

meuSinal = signalMeu()
freq = 44100
t = np.linspace(0, 2*1/freq, len(data))

mini = abs(min(dados))
maxi = abs(max(dados))

if mini > maxi:
    moduloMax = mini
else:
    moduloMax = maxi

l = []
for i in dados:
    v = i/moduloMax
    l.append(v)

# https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
nyq_rate = freq/2
width = 5.0/nyq_rate
ripple_db = 60.0  # dB
N, beta = signal.kaiserord(ripple_db, width)
cutoff_hz = 4000.0
taps = signal.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
yFiltrado = signal.lfilter(taps, 1.0, l)


TTTT, sinall = meuSinal.generateSin(14000, 1, len(yFiltrado)/freq, freq)

modulado = sinall * yFiltrado

delay = 2
for e in range(delay):
    print("A captação começará em {}".format(delay-e))
    # use um time.sleep para a espera
    time.sleep(1)

sd.play(modulado, freq)
sd.wait()

sf.write('modulado.wav', modulado, freq)

plt.plot(t, data)
plt.title("original x tempo")
plt.show()

meuSinal.plotFFT(dados, samplerate)
plt.title("original x freq")
plt.show()

plt.plot(t, l)
plt.title("normalizado x tempo")
plt.show()

meuSinal.plotFFT(l, samplerate)
plt.title("normalizado x freq")
plt.show()

plt.plot(t, yFiltrado)
plt.title("filtrado x tempo")
plt.show()

meuSinal.plotFFT(yFiltrado, samplerate)
plt.title("filtrado x freq")
plt.show()

plt.plot(t, modulado)
plt.title("modulado x tempo")
plt.show()

meuSinal.plotFFT(modulado, samplerate)
plt.title("modulado x freq")
plt.show()
