
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Manejador(QtCore.QThread):
	pintarLabel = QtCore.pyqtSignal(int)

	def __init__(self,semaforoManejador,semaforoConsumidor):
		super(Manejador, self).__init__(None)
		self.semaforoManejador = semaforoManejador
		self.semaforoConsumidor = semaforoConsumidor

	def run(self): 
		while True:
			if self.semaforoManejador[0] == True:
				self.pintarLabel.emit(1)
				time.sleep(2)
				self.pintarLabel.emit(0)
				time.sleep(0.01)
				self.semaforoManejador[0]  = False