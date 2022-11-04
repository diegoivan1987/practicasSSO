from random import randint
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Productor(QtCore.QThread):
	actualizaTablaPaginas = QtCore.pyqtSignal(dict)
	pintarTablaMemoria = QtCore.pyqtSignal(dict)
	pintarTablaMemoriaVirtual = QtCore.pyqtSignal(dict)

	def __init__(self,semaforoProductor,semaforoConsumidor,procesosPendientes,paginasDisponibles,tablaPaginas,tablaMemoria,procesosEnMemoria,numeroMarcoFisico,numeroMarcoVirtual):
		super(Productor, self).__init__(None)
		self.semaforoProductor = semaforoProductor
		self.semaforoConsumidor = semaforoConsumidor
		self.procesosPendientes = procesosPendientes
		self.paginasDisponibles = paginasDisponibles
		self.tablaPaginas = tablaPaginas
		self.tablaMemoria = tablaMemoria
		self.procesosEnMemoria = procesosEnMemoria
		self.numeroMarcoFisico = numeroMarcoFisico
		self.numeroMarcoVirtual = numeroMarcoVirtual

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
					primerMarco = 1 #servira para añadir solamente el primer marco a RAM
					#llenamos la tabla de paginas
					for i in range(paginasNecesitadas):#repetimos segun los marcos que necesite el proceso, usamos el numero de paginas porque se supone tienen el mismo tamaño que los marcos
						if primerMarco == 1:
							self.actualizaTablaPaginas.emit({"proceso":procesoActual.id,"indice":indiceAuxiliar,"funcion":"agregar","RAM":1,"numeroMarco":self.numeroMarcoFisico[0]})#mandamos la primer pagina a la RAM
							time.sleep(0.05)
							self.actualizaTablaPaginas.emit({"proceso":procesoActual.id,"indice":indiceAuxiliar,"funcion":"agregar","RAM":0,"numeroMarco":self.numeroMarcoVirtual[0]})#tambien mandamos su respaldo a la virtual
							time.sleep(0.05)
							
							self.numeroMarcoFisico[0]+= 1
							self.numeroMarcoVirtual[0] += 1
							primerMarco = 0
						else:
							self.actualizaTablaPaginas.emit({"proceso":procesoActual.id,"indice":indiceAuxiliar,"funcion":"agregar","RAM":0,"numeroMarco":self.numeroMarcoVirtual[0]})#mandamos virtuales
							
							time.sleep(0.05)
							self.numeroMarcoVirtual[0] += 1
							
						indiceAuxiliar+=1
					#pintamos la memoria fisica de acuerdo a la tabla de paginas
					tamanioAuxiliar = procesoActual.tamanio#tamanio total del proceso que ira disminuyendo
					color = QColor(procesoActual.color[0],procesoActual.color[1],procesoActual.color[2])
					for i in range(self.tablaPaginas.rowCount()):
						posicionMarco = int(self.tablaPaginas.item(i,2).text())	
						if self.tablaPaginas.item(i,0).text()==str(procesoActual.id):
							if self.tablaPaginas.item(i,3).text() == "1":#si es un marco de memoria fisica
								for j in range(8):
									if tamanioAuxiliar>0:#mientras no se haya pintado la misma cantidad de espacios que el tamanio del proceso
										columna = QtWidgets.QTableWidgetItem("")
										columna.setBackground(color)
										self.pintarTablaMemoria.emit({"fila":posicionMarco,"columna":j,"item":columna,"RAM":1})
										time.sleep(0.05)
										tamanioAuxiliar-=1
					#pintamos la memoria virtual de acuerdo a la tabla de paginas
					tamanioAuxiliarVirtual = procesoActual.tamanio #servira para llenar la memoria virtual
					colorVirtual = QColor(procesoActual.colorVirtual[0],procesoActual.colorVirtual[1],procesoActual.colorVirtual[2])
					for i in range(0,self.tablaPaginas.rowCount(),1):
						posicionMarco = int(self.tablaPaginas.item(i,2).text())	
						if self.tablaPaginas.item(i,0).text()==str(procesoActual.id):
							if self.tablaPaginas.item(i,3).text() == "0":#las demas paginas van en memoria virtual
								for j in range(8):
									if tamanioAuxiliarVirtual>0:#mientras no se haya pintado la misma cantidad de espacios que el tamanio del proceso
										columna = QtWidgets.QTableWidgetItem("")
										columna.setBackground(colorVirtual)
										
										self.pintarTablaMemoriaVirtual.emit({"id":procesoActual.id,"fila":posicionMarco,"columna":j,"item":columna,"RAM":0})
										time.sleep(0.1)
										tamanioAuxiliarVirtual-=1
				else:#si ya se terminaron todos los procesos pendientes, tambien sale del productor
					self.semaforoProductor[0] = False
					self.semaforoConsumidor[0] = True