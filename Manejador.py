
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Manejador(QtCore.QThread):
	pintarLabel = QtCore.pyqtSignal(int)
	cambiarLabelInstruccion = QtCore.pyqtSignal(str)
	aniadirInfo = QtCore.pyqtSignal(dict)
	numeroPasadas = 0

	def __init__(self,semaforoManejador,semaforoControlador,procesosEnMemoria):
		super(Manejador, self).__init__(None)
		self.semaforoManejador = semaforoManejador
		self.semaforoControlador = semaforoControlador
		self.numeroPasadas = 0
		self.procesosEnMemoria = procesosEnMemoria

	def run(self): 
		while True:
			if self.semaforoManejador[0] == True:
				if self.numeroPasadas == 0 or self.numeroPasadas == 1 or self.numeroPasadas == 3:
					self.pintarLabel.emit(1)
					time.sleep(2)
					self.pintarLabel.emit(0)
					time.sleep(0.01)
					self.semaforoManejador[0]  = False
				if self.numeroPasadas == 3:
					self.cambiarLabelInstruccion.emit("Escribiendo en dispositivo")
					time.sleep(0.01)
					self.semaforoControlador[0]=True
					self.numeroPasadas+=1
				if self.numeroPasadas == 2:
					for proceso in self.procesosEnMemoria:
						if proceso.id == 2:
							aux = proceso.tamanio
							#no se porque motivo es la fila 2 y tampoco se porque no manda los marcos adecuados, por eso esta harcodeado
							color = QColor(proceso.color[0],proceso.color[1],proceso.color[2])
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							aux+=1
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							proceso.tamanio += 2
							self.numeroPasadas +=1
							self.semaforoManejador[0]  = False
				if self.numeroPasadas == 1:
					self.cambiarLabelInstruccion.emit("Transfiriendo a memoria")
					time.sleep(0.01)
					self.semaforoControlador[0]=True
					self.numeroPasadas+=1
					
					
				if self.numeroPasadas == 0:
					self.cambiarLabelInstruccion.emit("Leyendo")
					time.sleep(0.01)
					self.semaforoControlador[0] = True
					self.numeroPasadas+=1
				

