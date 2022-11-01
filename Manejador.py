
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Manejador(QtCore.QThread):
	pintarLabel = QtCore.pyqtSignal(int)
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
				self.pintarLabel.emit(1)
				time.sleep(2)
				self.pintarLabel.emit(0)
				time.sleep(0.01)
				self.semaforoManejador[0]  = False
				if self.numeroPasadas == 0:
					self.semaforoControlador[0] = True
					self.primeraPasada = 1
				
