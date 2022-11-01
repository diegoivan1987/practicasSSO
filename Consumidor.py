from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import  QColor
import math
import time

class Consumidor(QtCore.QThread):
	actualizaTablaPaginas = QtCore.pyqtSignal(dict)
	pintarTablaMemoria = QtCore.pyqtSignal(dict)
	actualizarBarra = QtCore.pyqtSignal(dict)
	quitarDeTablaPendientes = QtCore.pyqtSignal(list)
	agregarATerminados = QtCore.pyqtSignal(int)

	def __init__(self,semaforoProductor,semaforoConsumidor,procesosPendientes,paginasDisponibles,tablaPaginas,tablaMemoria,procesosEnMemoria,semaforoManejador):
		super(Consumidor, self).__init__(None)
		self.semaforoProductor = semaforoProductor
		self.semaforoConsumidor = semaforoConsumidor
		self.procesosPendientes = procesosPendientes
		self.paginasDisponibles = paginasDisponibles
		self.tablaPaginas = tablaPaginas
		self.tablaMemoria = tablaMemoria
		self.procesosEnMemoria = procesosEnMemoria
		self.semaforoManejador = semaforoManejador

	def run(self):
		while True:
			if self.semaforoManejador[0] ==  False:
				if(self.semaforoConsumidor[0]==True):
					#recorremos la lista de procesos en memoria
					if len(self.procesosEnMemoria)>0:
						procesoActual = self.procesosEnMemoria.pop(0)
						if procesoActual.id != 2:#cualquier proceso que no sea el 2
							
							#procesamos el proceso
							while procesoActual.porcentajeProcesado < 100:
								procesoActual.porcentajeProcesado += 100
								self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":procesoActual.porcentajeProcesado})
								time.sleep(0.05)
							#quitarlo de pendientes
							self.quitarDeTablaPendientes.emit([1,procesoActual.id])
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
						elif procesoActual.id == 2 and procesoActual.porcentajeProcesado == 0:#la primera vez que se entra el procesamiento del proceso 2
							#procesamos el proceso
							while procesoActual.porcentajeProcesado < 50:
								procesoActual.porcentajeProcesado += 1
								self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":procesoActual.porcentajeProcesado})
								time.sleep(0.05)
							self.procesosEnMemoria.append(procesoActual)
							self.semaforoManejador[0] = True
							
						elif procesoActual.id == 2 and procesoActual.porcentajeProcesado != 0 and len(self.procesosEnMemoria)==0:
							#procesamos el proceso
							while procesoActual.porcentajeProcesado < 100:
								procesoActual.porcentajeProcesado += 1
								self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":procesoActual.porcentajeProcesado})
								time.sleep(0.05)
							#quitarlo de pendientes
							self.quitarDeTablaPendientes.emit([1,procesoActual.id])
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