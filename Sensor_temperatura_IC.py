from tkinter import *
import tkinter as tk
import time  # importa biblioteca Time
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import mypackage.Serial_acquire as serial_acquire
import flask
from flask import request, render_template


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
    @app.route('/', methods=['GET'])   
    def get_input():
        return render_template('homepage.html')

    @app.route('/', methods=['POST']) 
    def start():
        portName = request.form['portName']
        tempo_experiencia = request.form['tempo_experiencia']
        filename = request.form['filename']

        numPlots = 1
        tempo_experiencia = int(tempo_experiencia)#segundos
        maxPlotLength =  tempo_experiencia # Maximo valor do eixo x do grafico (tempo) em segundos

        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        s = serial_acquire.serialPlot(
            portName,
            baudRate,
            maxPlotLength,
            dataNumBytes,
            numPlots,
            tempo_experiencia,
            filename,)

        s.readSerialStart()  # Comeca o backgroundThread

        # Comeca a plotar no grafico
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        xmin = 0  # Valor minimo do X do grafico
        xmax = maxPlotLength  # Valor maximo do X do grafico
        ymin = 0  # Valor minimo do y do grafico
        ymax = 50  # Valor maximo do y do grafico
        fig = plt.figure()
        ax = plt.axes(xlim=(xmin, xmax), ylim=(ymin, ymax))
        ax.set_title("Projeto IC")  # Titulo do grafico
        ax.set_xlabel("Tempo")  # Titulo do eixo x
        ax.set_ylabel("Deta (T1-T2)")  # Titulo do eixo y

        lineLabel = ["Delta"]
        style = ["r-"]  # linestyles for the different plots
        timeText = ax.text(0.50, 0.95, "", transform=ax.transAxes)
        lines = []
        lineValueText = []
        for i in range(numPlots):
            lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
            lineValueText.append(ax.text(0.70, 0.90 - i * 0.05, "", transform=ax.transAxes))
        anim = animation.FuncAnimation(fig,s.getSerialData,fargs=(lines, lineValueText, lineLabel, timeText))  # Envia as variaveis para plotar o grafico

        plt.legend(loc="upper left")  # Local da legenda no graafico
        plt.show()
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        s.close()  # Para de plotar o grafico
        return render_template('homepage.html')
    app.run()

if __name__ == "__main__":
    main()
