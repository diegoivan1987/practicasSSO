from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Consumidor(QtCore.QThread):
	actualizaTablaPaginas = QtCore.pyqtSignal(dict)
	pintarTablaMemoria = QtCore.pyqtSignal(dict)
	actualizarBarra = QtCore.pyqtSignal(dict)
	quitarDeTablaPendientes = QtCore.pyqtSignal(int)
	agregarATerminados = QtCore.pyqtSignal(int)

	def __init__(self,semaforoProductor,semaforoConsumidor,procesosPendientes,paginasDisponibles,tablaPaginas,tablaMemoria,procesosEnMemoria):
		super(Consumidor, self).__init__(None)
		self.semaforoProductor = semaforoProductor
		self.semaforoConsumidor = semaforoConsumidor
		self.procesosPendientes = procesosPendientes
		self.paginasDisponibles = paginasDisponibles
		self.tablaPaginas = tablaPaginas
		self.tablaMemoria = tablaMemoria
		self.procesosEnMemoria = procesosEnMemoria

	def run(self):
		while True:
			if(self.semaforoConsumidor[0]==True):
				#recorremos la lista de procesos en memoria
				if len(self.procesosEnMemoria)>0:
					procesoActual = self.procesosEnMemoria.pop(0)
					tamanio = procesoActual.tamanio
					rangoAumento = math.floor(100/tamanio)
					porcentajeActual = 0
					numeroAumentos = 0
					#vamos procesandolo por aumentos, no de 1 en 1
					while numeroAumentos < tamanio:
						porcentajeActual += rangoAumento
						self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":porcentajeActual})
						numeroAumentos += 1
						time.sleep(0.1)
					if(porcentajeActual<100):#solo por si llegase a quedar incompleto despues de haber dado los aumentos
						self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":100})
						time.sleep(0.1)
					#quitarlo de pendientes
					self.quitarDeTablaPendientes.emit(1)
					time.sleep(0.05)
					#quitarlo de la memoria
					tamanioAuxiliar = procesoActual.tamanio#tamanio total del proceso que ira disminuyendo
					color = QColor(255,255,255)
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
					#sobreescribir tabla de paginas
					for i in range(self.tablaPaginas.rowCount()):#recorremos la tabla de paginas
						if self.tablaPaginas.item(i,0).text()==str(procesoActual.id):
							self.actualizaTablaPaginas.emit({"fila":i,"proceso":"-","indice":"-"})
							time.sleep(0.05)
							self.paginasDisponibles[0] += 1
					#añadirlo a procesos terminados
					self.agregarATerminados.emit(procesoActual.id)
					time.sleep(0.05)
				else:#cambiar semaforos y vaciar la barra de carga
					self.actualizarBarra.emit({"idProceso":"","porcentajeBarra":0})#vaciamos la barra de carga
					time.sleep(0.1)
					self.semaforoConsumidor[0]=False
					self.semaforoProductor[0]=True