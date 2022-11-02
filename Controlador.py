from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import time

class Controlador(QtCore.QThread):
	aumentarControlador = QtCore.pyqtSignal(int)

	def __init__(self,semaforoControlador,semaforoManejador):
		super(Controlador, self).__init__(None)
		self.semaforoControlador = semaforoControlador
		self.semaforoManejador = semaforoManejador

	def run(self): 
		while True:
			if self.semaforoControlador[0] == True:
				for i in range(1,101):
					self.aumentarControlador.emit(i)
					time.sleep(0.01)
				self.aumentarControlador.emit(0)
				time.sleep(0.01)
				self.semaforoControlador[0]  = False
				self.semaforoManejador[0] = True