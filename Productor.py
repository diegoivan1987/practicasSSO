from random import randint
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Productor(QtCore.QThread):
	actualizaTablaPaginas = QtCore.pyqtSignal(dict)
	pintarTablaMemoria = QtCore.pyqtSignal(dict)

	def __init__(self,semaforoProductor,semaforoConsumidor,procesosPendientes,paginasDisponibles,tablaPaginas,tablaMemoria,procesosEnMemoria):
		super(Productor, self).__init__(None)
		self.semaforoProductor = semaforoProductor
		self.semaforoConsumidor = semaforoConsumidor
		self.procesosPendientes = procesosPendientes
		self.paginasDisponibles = paginasDisponibles
		self.tablaPaginas = tablaPaginas
		self.tablaMemoria = tablaMemoria
		self.procesosEnMemoria = procesosEnMemoria

	def run(self):
		while True:
			if(self.semaforoProductor[0]==True):
				#recorremos los procesos pendientes
				if len(self.procesosPendientes)>0:
					procesoActual = self.procesosPendientes.pop(0)
					tamanio = procesoActual.tamanio
					self.procesosEnMemoria.append(procesoActual)
					paginasNecesitadas = math.ceil(tamanio/8)
					indiceAuxiliar = 1
					#llenamos la tabla de paginas
					for i in range(paginasNecesitadas):#repetimos segun los marcos que necesite el proceso, usamos el numero de paginas porque se supone tienen el mismo tamaño que los marcos
						for j in range(self.tablaPaginas.rowCount()):
							if self.tablaPaginas.item(j,0).text()=="-":
								self.actualizaTablaPaginas.emit({"fila":j,"proceso":procesoActual.id,"indice":indiceAuxiliar})
								time.sleep(0.05)
								indiceAuxiliar+=1
								self.paginasDisponibles[0] -= 1
								break
					#pintamos la memoria fisica de acuerdo a la tabla de paginas
					tamanioAuxiliar = procesoActual.tamanio#tamanio total del proceso que ira disminuyendo
					color = QColor(procesoActual.color[0],procesoActual.color[1],procesoActual.color[2])
					for i in range(self.tablaPaginas.rowCount()):	
						if self.tablaPaginas.item(i,0).text()==str(procesoActual.id):
								posicionMarco = int(self.tablaPaginas.item(i,2).text())
								for j in range(8):
									if tamanioAuxiliar>0:#mientras no se haya pintado la misma cantidad de espacios que el tamanio del proceso
										columna = QtWidgets.QTableWidgetItem("")
										columna.setBackground(color)
										self.pintarTablaMemoria.emit({"fila":posicionMarco,"columna":j,"item":columna})
										time.sleep(0.05)
										tamanioAuxiliar-=1
				else:#si ya se terminaron todos los procesos pendientes, tambien sale del productor
					self.semaforoProductor[0] = False
					self.semaforoConsumidor[0] = True