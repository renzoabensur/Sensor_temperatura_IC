from tkinter import *
import tkinter as tk
import time  # importa biblioteca Time
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import mypackage.Serial_acquire as serial_acquire

plt.style.use("seaborn-ticks")

def main():
    # Codigo do usuario
    # ------------------
    baudRate = 115200 # BaundRate do codigo em arduino
    dataNumBytes = 4  # Number de bytes de 1 ponto de dado
    # ------------------

    # Entaradas do usuario sao armazenadas nas variaveis tempo_exposicao, tempo_recuperacao e ciclos
    # --------------------------------------------------
    class GUI_interface(Frame):
        def __init__(self, master):
            Frame.__init__(self, master)
            self.grid()
            self.create_widgets()

        def create_widgets(self):
            self.option = tk.IntVar()
            self.instruction = Label(self,text="Qual porta:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=0, column=0)

            self.instruction = Label(self,text="Tempo total experiencia:",fg="black",font=("arial", 10, "bold"),padx=30,pady=10,bd=1,)
            self.instruction.grid(row=1, column=0)

            self.instruction = Label(self,text="Nome do arquivo txt:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=2, column=0)

            self.portName = Entry(self)
            self.portName.grid(row=0, column=1, sticky=W)

            self.Tempo_experiencia = Entry(self)
            self.Tempo_experiencia.grid(row=1, column=1, sticky=W)

            self.filename = Entry(self)
            self.filename.grid(row=2, column=1, sticky=W)

            self.start_button = Button(self,text="Start",command=self.start,fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.start_button.grid(row=7, column=1, sticky=W)

        def start(self):
            portName = self.portName.get()
            Tempo_experiencia = self.Tempo_experiencia.get()
            filename = self.filename.get()
            numPlots = 1

            Tempo_experiencia = int(Tempo_experiencia)#segundos

            maxPlotLength =  Tempo_experiencia # Maximo valor do eixo x do grafico (tempo) em segundos

            # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            s = serial_acquire.serialPlot(
                portName,
                baudRate,
                maxPlotLength,
                dataNumBytes,
                numPlots,
                Tempo_experiencia,
                filename,)

            s.readSerialStart()  # Comeca o backgroundThread

            # Comeca a plotar no grafico
            # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            s.close()  # Para de plotar o grafico

    root = Tk()
    root.title("IC")
    root.geometry("400x200")
    app = GUI_interface(root)

    root.mainloop()

if __name__ == "__main__":
    main()
