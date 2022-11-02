
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Manejador(QtCore.QThread):
	pintarLabel = QtCore.pyqtSignal(int)
	aniadirInfo = QtCore.pyqtSignal(dict)
	actualizarTablaPendientes = QtCore.pyqtSignal(str)
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
				self.pintarLabel.emit(1)
				time.sleep(2)
				self.pintarLabel.emit(0)
				time.sleep(0.01)
				self.semaforoManejador[0]  = False
				if self.numeroPasadas == 1:
					for proceso in self.procesosEnMemoria:
						if proceso.id == 2:
							aux = 0
							for i in range(proceso.tamanio):
								aux+=1
							#no se porque motivo es la fila 2 y tampoco se porque no manda los marcos adecuados, por eso esta harcodeado
							color = QColor(proceso.color[0],proceso.color[1],proceso.color[2])
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							aux+=1
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							proceso.tamanio += 2
							self.actualizarTablaPendientes.emit(str(proceso.tamanio))
							time.sleep(0.05)
							self.numeroPasadas +=1
				if self.numeroPasadas == 0:
					self.semaforoControlador[0] = True
					self.numeroPasadas = 1
				

