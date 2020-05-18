from tkinter import *
import tkinter as tk
import time  # importa biblioteca Time
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import mypackage.Serial_acquire as serial_acquire
import flask
from flask import request, render_template
import datetime
import numpy as np
import matplotlib.ticker as ticker

app = flask.Flask(__name__)

app.config["DEBUG"] = True

plt.style.use("seaborn-ticks")


def main():
    # Codigo do usuario
    # ------------------
    baudRate = 115200 # BaundRate do codigo em arduino
    dataNumBytes = 4  # Number de bytes de 1 ponto de dado
    # ------------------

    # Entaradas do usuario sao armazenadas nas variaveis tempo_exposicao, tempo_recuperacao e ciclos
    # --------------------------------------------------
    print("Aperte nesse link com o crtl http://127.0.0.1:5000/")
    @app.route('/', methods=['GET'])   
    def get_input():
        return render_template('homepage.html')

    @app.route('/', methods=['POST']) 
    def start():
        portName = request.form['portName']
        tempo_experiencia = request.form['tempo_experiencia']
        potencia = int(request.form['potencia'])
        plotInterval = int(request.form['plotInterval'])
        option = int(request.form['expressar tempo'])
        filename = request.form['filename']


        numPlots = 1
        tempo_experiencia = int(tempo_experiencia) #segundos
        nframes = int((tempo_experiencia*1000)//plotInterval)
        maxPlotLength = nframes + 1   # Maximo valor do eixo x do grafico (tempo) em segundos

        xmin = 0  # Valor minimo do X do grafico
        xmax = maxPlotLength # Valor maximo do X do grafico
        ymin = 0  # Valor minimo do y do grafico
        ymax = 80  # Valor maximo do y do grafico
        fig, ax = plt.subplots(facecolor=(.18, .31, .31),figsize=(17,5))
        ax = plt.axes()
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)


        #ReScale x label
        x = np.linspace(xmin,xmax)
        scale_x = 1000/(plotInterval)
        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_x))
        ax.xaxis.set_major_formatter(ticks_x)
        ax.set_xticks(np.arange(xmin,xmax))

        ax.set_title("Projeto IC", color='peachpuff')  # Titulo do grafico
        ax.set_xlabel("Tempo",  color='peachpuff')  # Titulo do eixo x
        ax.set_ylabel("Rth: (T1-T2)/P", color='peachpuff')  # Titulo do eixo y
        ax.set_facecolor('#eafff5')
        ax.grid(True)

        lineLabel = ["Rth"]
        style = ["r-"]  # linestyles for the different plots
        timeText = ax.text(0.30, 0.95, "", transform=ax.transAxes)
        lines = []
        lineValueText = []
        for i in range(numPlots):
            lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
            lineValueText.append(ax.text(0.70, 0.90 - i * 0.05, "", transform=ax.transAxes))
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        s = serial_acquire.serialPlot(
            portName,
            baudRate,
            maxPlotLength,
            dataNumBytes,
            numPlots,
            tempo_experiencia,
            potencia,
            ax,
            option,
            filename,)

        s.readSerialStart()  # Comeca o backgroundThread

        # Comeca a plotar no grafico
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        anim = animation.FuncAnimation(fig,s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText),frames = nframes, interval = plotInterval, repeat = False)  # Envia as variaveis para plotar o grafico

        plt.legend(loc="upper left")  # Local da legenda no graafico
        plt.show()
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        s.close()  # Para de plotar o grafico
        return render_template('backpage.html')
    app.run()

if __name__ == "__main__":
    main()
