
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Manejador(QtCore.QThread):
	pintarLabel = QtCore.pyqtSignal(int)
	cambiarLabelInstruccion = QtCore.pyqtSignal(str)
	aniadirInfo = QtCore.pyqtSignal(dict)
	pintarTablaBufferRam = QtCore.pyqtSignal(dict)
	pintarTablaBufferControlador = QtCore.pyqtSignal(dict)
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
				if self.numeroPasadas == 3:
					for proceso in self.procesosEnMemoria:
						if proceso.id == 2:
							aux = proceso.tamanio
							#no se porque motivo es la fila 2 y tampoco se porque no manda los marcos adecuados, por eso esta harcodeado
							color = QColor(255,128,0)
							blanco = QColor(255,255,255)
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							aux+=1
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							aux+=1
							self.aniadirInfo.emit({"columna":aux,"color":color})
							time.sleep(0.1)
							proceso.tamanio += 3
							self.numeroPasadas +=1
							self.semaforoManejador[0]  = False
							for i in range(3):
								columna = QtWidgets.QTableWidgetItem("")
								columna.setBackground(blanco)
								self.pintarTablaBufferRam.emit({"fila":0,"columna":i,"item":columna})
								time.sleep(0.1)
				if self.numeroPasadas == 2:
					#llenamos el buffer del controlador con la info encontrada
					color = QColor(255,128,0)
					for i in range(3):
						columna = QtWidgets.QTableWidgetItem("")
						columna.setBackground(color)
						self.pintarTablaBufferControlador.emit({"fila":0,"columna":i,"item":columna})
						time.sleep(0.1)
					time.sleep(0.5)
					#encendemos el manejador
					self.pintarLabel.emit(1)
					time.sleep(0.01)
					#hacemos la transferencia
					blanco = QColor(255,255,255)
					for i in range(3):
						columna = QtWidgets.QTableWidgetItem("")
						columna.setBackground(blanco)
						self.pintarTablaBufferControlador.emit({"fila":0,"columna":i,"item":columna})
						time.sleep(0.1)
						columna = QtWidgets.QTableWidgetItem("")
						columna.setBackground(color)
						self.pintarTablaBufferRam.emit({"fila":0,"columna":i,"item":columna})
						time.sleep(0.1)
					#apagamos el manejador
					self.pintarLabel.emit(0)
					time.sleep(0.01)
					self.numeroPasadas+=1
				if self.numeroPasadas == 1:
					#vaciamos el buffer del controlador
					blanco = QColor(255,255,255)
					for i in range(2):
						columna = QtWidgets.QTableWidgetItem("")
						columna.setBackground(blanco)
						self.pintarTablaBufferControlador.emit({"fila":0,"columna":i,"item":columna})
						time.sleep(0.1)
					#simulamos que se esta buscando la info
					self.semaforoManejador[0]  = False
					self.cambiarLabelInstruccion.emit("Leyendo")
					time.sleep(1)
					self.semaforoControlador[0] = True	
					self.numeroPasadas+=1
				if self.numeroPasadas == 0:
					#prendemos el manejador
					self.pintarLabel.emit(1)
					time.sleep(0.01)
					#hacemos la transferencia
					blanco = QColor(255,255,255)
					for proceso in self.procesosEnMemoria:
						if proceso.id == 2:
							color = QColor(proceso.color[0],proceso.color[1],proceso.color[2])
					for i in range(2):
						columna = QtWidgets.QTableWidgetItem("")
						columna.setBackground(blanco)
						self.pintarTablaBufferRam.emit({"fila":0,"columna":i,"item":columna})
						time.sleep(0.1)
						columna = QtWidgets.QTableWidgetItem("")
						columna.setBackground(color)
						self.pintarTablaBufferControlador.emit({"fila":0,"columna":i,"item":columna})
						time.sleep(0.1)
					#apagamos el manejador
					self.pintarLabel.emit(0)
					time.sleep(0.01)
					self.semaforoManejador[0]  = False

					self.cambiarLabelInstruccion.emit("Checksum")
					time.sleep(1)
					self.semaforoControlador[0] = True
					self.numeroPasadas+=1
				

