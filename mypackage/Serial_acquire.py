from threading import Thread
import serial  # importa biblioteca Serial
import time  # importa biblioteca Time
import collections
import struct
import copy
import pandas as pd
import os
from pathlib import Path
import shutil
import matplotlib.ticker as ticker
import numpy as np



class serialPlot:  # define classe serialPlot
    def __init__(
        self,
        serialPort="COM12",
        serialBaud = 9600,
        plotLength = 100,
        dataNumBytes = 2,
        numPlots = 2,
        Tempo_experiencia = 0,
        potencia = 0,
        ax = 0,
        option =0,
        filename = "filename",
    ):
        # variaveis definidas para a classe serialPlot
        # ----------------------
        self.ax = ax
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        self.Tempo_experiencia = Tempo_experiencia
        self.potencia = potencia
        self.rawData = bytearray(numPlots * dataNumBytes)
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = "d"  # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = "f"  # 4 byte float
        self.data = []
        self.data.append(collections.deque([0] * plotLength, maxlen=plotLength)) # give an array for each type of data and store them in a list
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.tempo = 0
        self.i = 0
        self.x = 0
        self.mili_sec = 0
        self.filename = filename
        self.txtData = []
        self.option = option
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Comeca a comunicacao serial com o arduino
        print("Trying to connect to: " + str(serialPort) + " at " + str(serialBaud) + " BAUD.")
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print("Connected to " + str(serialPort) + " at " + str(serialBaud) + " BAUD.")
        except:
            print("Failed to connect with " + str(serialPort) + " at " + str(serialBaud) + " BAUD.")

    def readSerialStart(self):
        # Envia para o arduino as entradas de potencia
        # ---------------------------------------------------------------------------
        time.sleep(2)
        self.serialConnection.write(f"i;p;{self.potencia:05d};f\n".encode())
        # ---------------------------------------------------------------------------

        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            while self.isReceiving != True:  # Fica no loop ate comecar a receber dados
                time.sleep(0.1)


    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        # Plota no grafico o tempo e os dados recebidos dos sensores
        # --------------------------------------------------------------
        self.serialConnection.write(b"i;s;00000;f\n")  # Inicia a leitura do sensor analogico no arduino
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)  # the first reading will be erroneous
        if self.i == 0:
            self.tempo = 0
            self.plotTimer = 0
            self.mili_sec = 0
            self.i = 1
        else:
            self.tempo = round(self.tempo + self.plotTimer / 1000, 2)
        self.previousTimer = currentTimer
        self.finish_time = round(self.Tempo_experiencia-self.tempo,2)

        day_total = self.tempo//86400
        hour_total = self.tempo%86400//3600
        minutes_total = ((self.tempo%86400)%3600)//60
        seconds_total = (((self.tempo%86400)%3600)%60)

        day_finish =  self.finish_time//86400
        hour_finish =  self.finish_time%86400//3600
        minutes_finish = ((self.finish_time%86400)%3600)//60
        seconds_finish = (((self.finish_time%86400)%3600)%60)

        timeText.set_text("Tempo = %d:%d:%d:%d s" % (day_total, hour_total, minutes_total, seconds_total) + " , Restante = %d:%d:%d:%d s" % (day_finish, hour_finish, minutes_finish, seconds_finish) + " , Plot Interval = " + str(self.plotTimer) + "ms")
        privateData = copy.deepcopy(self.rawData[:])  # so that the 3 values in our plots will be synchronized to the same sample time

        if self.option == 1:
            self.txtData.append("   %06d" %self.tempo)
            self.sec = "(s)   "
        elif self.option == 2:
            self.mili_sec = self.plotTimer + self.mili_sec
            self.txtData.append("   %07d" %self.mili_sec)
            self.sec = "(ms)  "

        for i in range(self.numPlots):
            data = privateData[(i * self.dataNumBytes) : (self.dataNumBytes + i * self.dataNumBytes)]
            value, = struct.unpack(self.dataType, data)
            self.data[i].append(value)                                                # we get the latest data point and append it to our array
            lines[i].set_data(range( self.plotMaxLength), self.data[i])
            lineValueText[i].set_text("[" + lineLabel[i] + "] = " + str(value))
            self.txtData.append("       %03d"  %value + " ")
        self.txtData.append("\n")
        
        # --------------------------------------------------------------

    def backgroundThread(self):  # Recupera `data`
        time.sleep(1.0)  # Da um tempo para o buffer armazenar os dados
        self.serialConnection.reset_input_buffer()
        while self.isRun:
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print("Disconnected...")
        if not os.path.exists('Dados'):
            os.makedirs('Dados')
        file_out = open(str(self.filename) + ".txt", "a")
        file_out.writelines(
            "   Tempo" +  self.sec   + "   Rth: (T1-T2)/P  \n"
        )
        file_out.writelines(self.txtData)
        file_out.close()

        shutil.move("C:/Users/renzo/OneDrive/Documents/IC/IC_project/Sensor_temperatura_IC/" + self.filename + ".txt", "C:/Users/renzo/OneDrive/Documents/IC/IC_project/Sensor_temperatura_IC/Dados/" + self.filename + ".txt")
       