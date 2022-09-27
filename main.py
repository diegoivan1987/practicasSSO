#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5 import uic
import sys, time

class HiloSJF(QtCore.QThread):
	senialActualizarTiempo = QtCore.pyqtSignal(int)
	senialActualizarOrden = QtCore.pyqtSignal(int)
	def __init__(self, colaProcesosSJF = []):
		super(HiloSJF, self).__init__(None)
		self.colaProcesosSJF = colaProcesosSJF
	
	#se inicia o continua el proceso
	def run(self):
		contadorProcesosFinalizados = 0
		self.ordenaProcesos(self.colaProcesosSJF)
		self.senialActualizarOrden.emit(1)
		time.sleep(0.005)#para que se alcancen a reflejar los cambios en la interfaz
		#no se termina hasta que se hayan terminado todos los pr
		# ocesos
		while contadorProcesosFinalizados < len(self.colaProcesosSJF):
			#recorremos el arreglo de procesos
			for i in range(len(self.colaProcesosSJF)):
				if randint(1,10)==1:
					agregar = Proceso(len(self.colaProcesosSJF)+1,randint(1,10))
					self.colaProcesosSJF.append(agregar)
					self.ordenaProcesos(self.colaProcesosSJF)
					self.senialActualizarOrden.emit(1)
					time.sleep(0.005)#para que se alcancen a reflejar los cambios en la interfaz

				if self.colaProcesosSJF[i].banderaTerminado == False:#si aun no termina, sigue trabajando con el proceso
					for j in range(self.colaProcesosSJF[i].tiempoEstimado):#mientras no se haya terminado el proceso o la cota de tiempo
						time.sleep(1)
						self.colaProcesosSJF[i].tiempoEstimado-=1#disminuimos su tiempo
						if self.colaProcesosSJF[i].tiempoEstimado == 0:#si se completo durante este ciclo
							self.colaProcesosSJF[i].banderaTerminado = True#lo marcamos como terminado
							contadorProcesosFinalizados += 1#aumentamos el contador de procesos terminados
							self.senialActualizarTiempo.emit(i)
							time.sleep(0.001)#para que se alcancen a reflejar los cambios en la interfaz
							break#interrumpimos la duracion de la cota de tiempo
						self.senialActualizarTiempo.emit(i)		
		print("se termino el procesamiento")#ayuda para saber si termino el bucle
		self.quit()

	def ordenaProcesos(self,colaProcesosSJF=[]):
		for j in range(len(colaProcesosSJF)-1):
			for i in range(len(colaProcesosSJF)-1):
				if colaProcesosSJF[i].tiempoEstimado>colaProcesosSJF[i+1].tiempoEstimado:
					temp = colaProcesosSJF[i]
					colaProcesosSJF[i] = self.colaProcesosSJF[i+1]
					colaProcesosSJF[i+1] = temp

class HiloFCFS(QtCore.QThread):
	senialBloqueo = QtCore.pyqtSignal(int)
	senialActualizar = QtCore.pyqtSignal(int)
	def __init__(self, colaProcesosFCFS = []):
		super(HiloFCFS, self).__init__(None)
		self.colaProcesosFCFS = colaProcesosFCFS
	
	#se inicia o continua el proceso
	def run(self):
		contadorProcesosFinalizados = 0
		#no se termina hasta que se hayan terminado todos los procesos
		while contadorProcesosFinalizados <10:
			#recorremos el arreglo de procesos
			for i in range(10):
				if self.colaProcesosFCFS[i].banderaTerminado == False:#si aun no termina, sigue trabajando con el proceso
					while (self.colaProcesosFCFS[i].porcentajeProcesado<100):#mientras no se haya terminado el proceso
						if randint(1,5)==5 and i>0:#interrumpimos un proceso con un 20% de probabilidad, simulando una bloqueo por E/S
							#primero mandamos la señal para que haya un cambio en la interfaz y luego procesamos la lista, ya que hay un cambio de indices
							self.senialBloqueo.emit(i)
							time.sleep(0.008)#para que se puedan terminar los cambios en la interfaz
							self.agregar = self.colaProcesosFCFS[i]
							self.colaProcesosFCFS.append(self.agregar)#lo pasamos al final de la fila
							del self.colaProcesosFCFS[i]#lo eliminamos de la posicion original que ocupaba
							i-=1#regresamos el indice para no saltarnos el siguiente proceso al que se elimino
						else:#si no hubo un bloqueo
							#actualizamos el porcentaje en la tabla
							self.colaProcesosFCFS[i].porcentajeProcesado+=1#aumentamos su porcentaje
							if self.colaProcesosFCFS[i].porcentajeProcesado == 100:#si se completo durante este ciclo
								self.colaProcesosFCFS[i].banderaTerminado = True#lo marcamos como terminado
								contadorProcesosFinalizados += 1#aumentamos el contador de procesos terminados
							self.senialActualizar.emit(i)#aqui no se hace primero porque no hay un cambio de indides en la lista
							time.sleep(0.01)				
		print("se termino el procesamiento")#ayuda para saber si termino el bucle

class HiloRR(QtCore.QThread):
	senialActualizarRR = QtCore.pyqtSignal(int)
	senialBloqueoRR = QtCore.pyqtSignal(int)
	senialActualizarFCFS = QtCore.pyqtSignal(int)
	senialBloqueoFCFS = QtCore.pyqtSignal(int)
	def __init__(self, colaProcesosRR,colaProcesosFCFS):
		super(HiloRR, self).__init__(None)
		self.colaProcesosRR = colaProcesosRR
		self.colaProcesosFCFS = colaProcesosFCFS
	#se inicia o continua el proceso
	def run(self):
		contadorProcesosFinalizados = 0
		#no se termina hasta que se hayan terminado todos los procesos
		while contadorProcesosFinalizados <(len(self.colaProcesosFCFS)+len(self.colaProcesosRR)):
			#recorremos el arreglo de procesos
			for i in range(len(self.colaProcesosRR)):
				if self.colaProcesosRR[i].banderaTerminado == False:#si aun no termina, sigue trabajando con el proceso
					for j in range(5):#mientras no se haya terminado el proceso o la cota de tiempo
						time.sleep(1)
						self.colaProcesosRR[i].tiempoEstimado-=1#disminuimos su tiempo
						if self.colaProcesosRR[i].tiempoEstimado == 0:#si se completo durante este ciclo
							self.colaProcesosRR[i].banderaTerminado = True#lo marcamos como terminado
							contadorProcesosFinalizados += 1#aumentamos el contador de procesos terminados
							self.senialActualizarRR.emit(i)
							time.sleep(0.001)#para que se alcancen a reflejar los cambios en la interfaz
							break#interrumpimos la duracion de la cota de tiempo
						self.senialActualizarRR.emit(i)
						if(i>0 and randint(1,3)==2):
							print("bloqueo en "+str(self.colaProcesosRR[i].id))
							#primero mandamos la señal para que haya un cambio en la interfaz y luego procesamos la lista, ya que hay un cambio de indices
							self.senialBloqueoRR.emit(i)
							time.sleep(0.008)#para que se puedan terminar los cambios en la interfaz
							self.agregar = self.colaProcesosRR[i]
							self.colaProcesosRR.append(self.agregar)#lo pasamos al final de la fila
							del self.colaProcesosRR[i]#lo eliminamos de la posicion original que ocupaba
							i-=1#regresamos el indice para no saltarnos el siguiente proceso al que se elimino
							cuentaTiempoDeFCFS = 0
							while cuentaTiempoDeFCFS <300:
								#recorremos el arreglo de procesos
								for x in range(len(self.colaProcesosFCFS)):
									print(str(x)+" "+str(cuentaTiempoDeFCFS))
									if self.colaProcesosFCFS[x].banderaTerminado == False and cuentaTiempoDeFCFS <300:#si aun no termina, sigue trabajando con el proceso
										while (self.colaProcesosFCFS[x].porcentajeProcesado<100):#mientras no se haya terminado el proceso
											#actualizamos el porcentaje en la tabla
											self.colaProcesosFCFS[x].porcentajeProcesado+=1#aumentamos su porcentaje
											cuentaTiempoDeFCFS +=1
											if self.colaProcesosFCFS[x].porcentajeProcesado == 100:#si se completo durante este ciclo
												self.colaProcesosFCFS[x].banderaTerminado = True#lo marcamos como terminado
												contadorProcesosFinalizados += 1#aumentamos el contador de procesos terminados
												print("Termino proceso "+str(self.colaProcesosFCFS[x].id)+" "+str(self.colaProcesosFCFS[x].porcentajeProcesado))
											self.senialActualizarFCFS.emit(x)#aqui no se hace primero porque no hay un cambio de indides en la lista
											time.sleep(0.01)
							break;
							
										
		print("se termino el procesamiento de RR")#ayuda para saber si termino el bucle

class Proceso():
		id = 0
		porcentajeProcesado = 0
		banderaBloqueo = False
		tiempoEstimado = 0
		banderaTerminado = False


		def __init__(self,id,tiempoEstimado):
				self.id = id
				self.tiempoEstimado = tiempoEstimado

class VentanaPrincipal(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.ui = uic.loadUi('prueba.ui',self)#Se carga la interfaz grafica

		self.colaProcesosFCFS = []
		self.colaProcesosRR = []
		self.colaProcesosSJF = []

		#inicializamos los arreglos de procesos y sus datos
		for i in range(10):
			agregar = Proceso(i+1,randint(1,10))
			self.colaProcesosFCFS.append(agregar)
			self.colaProcesosRR.append(agregar)
			self.colaProcesosSJF.append(agregar)

		#inicializamos los datos de las tablas
		for i in range(10):
			self.tablaFCFS.insertRow(self.tablaFCFS.rowCount())
			tablaId = QtWidgets.QTableWidgetItem(str(self.colaProcesosFCFS[i].id))
			tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.colaProcesosFCFS[i].porcentajeProcesado))
			self.tablaFCFS.setItem(i,0,tablaId)
			self.tablaFCFS.setItem(i,1,tablaPorcentaje)

			self.tablaRR.insertRow(self.tablaRR.rowCount())
			tablaId = QtWidgets.QTableWidgetItem(str(self.colaProcesosRR[i].id))
			tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.colaProcesosRR[i].tiempoEstimado))
			self.tablaRR.setItem(i,0,tablaId)
			self.tablaRR.setItem(i,1,tablaPorcentaje)

			self.tablaSJF.insertRow(self.tablaSJF.rowCount())
			tablaId = QtWidgets.QTableWidgetItem(str(self.colaProcesosSJF[i].id))
			tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.colaProcesosSJF[i].tiempoEstimado))
			self.tablaSJF.setItem(i,0,tablaId)
			self.tablaSJF.setItem(i,1,tablaPorcentaje)

		self.btnI1.clicked.connect(self.iniciaFCFS)
		self.btnI2.clicked.connect(self.iniciaRR)
		self.btnI3.clicked.connect(self.iniciaSJF)

	#para reordenar la tabla como si fuera una fila
	def reordenarTablaFCFS(self,senial):
		self.agregar = self.colaProcesosFCFS[senial]
		tablaId = QtWidgets.QTableWidgetItem(str(self.agregar.id))
		tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.agregar.porcentajeProcesado))
		self.tablaFCFS.insertRow(self.tablaFCFS.rowCount())
		self.tablaFCFS.setItem(self.tablaFCFS.rowCount()-1,0,tablaId)
		self.tablaFCFS.setItem(self.tablaFCFS.rowCount()-1,1,tablaPorcentaje)
		self.tablaFCFS.removeRow(senial)

	#para reordenar la tabla como si fuera una fila
	def reordenarTablaRR(self,senial):
		self.agregar = self.colaProcesosRR[senial]
		tablaId = QtWidgets.QTableWidgetItem(str(self.agregar.id))
		tablaTiempo = QtWidgets.QTableWidgetItem(str(self.agregar.tiempoEstimado))
		self.tablaRR.insertRow(self.tablaRR.rowCount())
		self.tablaRR.setItem(self.tablaRR.rowCount()-1,0,tablaId)
		self.tablaRR.setItem(self.tablaRR.rowCount()-1,1,tablaTiempo)
		self.tablaRR.removeRow(senial)
			

	#para actualizar el porcentaje de los procesos
	def actualizarOrdenTablaSJF(self,senial):
		if senial ==1:
			self.tablaSJF.setRowCount(0)
			for i in range(len(self.colaProcesosSJF)):
				self.agregar = self.colaProcesosSJF[i]
				tablaId = QtWidgets.QTableWidgetItem(str(self.agregar.id))
				tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.agregar.tiempoEstimado))
				self.tablaSJF.insertRow(self.tablaSJF.rowCount())
				self.tablaSJF.setItem(i,0,tablaId)
				self.tablaSJF.setItem(i,1,tablaPorcentaje)
	
	def actualizarTablaFCFS(self,senial):
		self.agregar = self.colaProcesosFCFS[senial]
		tablaId = QtWidgets.QTableWidgetItem(str(self.agregar.id))
		tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.agregar.porcentajeProcesado))
		self.tablaFCFS.setItem(senial,0,tablaId)
		self.tablaFCFS.setItem(senial,1,tablaPorcentaje)
			
	def iniciaFCFS(self):
		self.primerHilo = HiloFCFS(self.colaProcesosFCFS)
		self.primerHilo.senialBloqueo.connect(self.reordenarTablaFCFS)
		self.primerHilo.senialActualizar.connect(self.actualizarTablaFCFS)
		self.primerHilo.start()

	#para actualizar el tiempo restante de los procesos
	def actualizarTiempoTablaSJF(self,senial):
		self.agregar = self.colaProcesosSJF[senial]
		tablaId = QtWidgets.QTableWidgetItem(str(self.agregar.id))
		tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.agregar.tiempoEstimado))
		self.tablaSJF.setItem(senial,0,tablaId)
		self.tablaSJF.setItem(senial,1,tablaPorcentaje)

	#para actualizar el tiempo restante de los procesos
	def actualizarTablaRR(self,senial):
		self.agregar = self.colaProcesosRR[senial]
		tablaId = QtWidgets.QTableWidgetItem(str(self.agregar.id))
		tablaPorcentaje = QtWidgets.QTableWidgetItem(str(self.agregar.tiempoEstimado))
		self.tablaRR.setItem(senial,0,tablaId)
		self.tablaRR.setItem(senial,1,tablaPorcentaje)

	def iniciaRR(self):
		self.segundoHilo = HiloRR(self.colaProcesosRR,self.colaProcesosFCFS)
		self.segundoHilo.senialActualizarRR.connect(self.actualizarTablaRR)
		self.segundoHilo.senialBloqueoRR.connect(self.reordenarTablaRR)
		self.segundoHilo.senialBloqueoFCFS.connect(self.reordenarTablaFCFS)
		self.segundoHilo.senialActualizarFCFS.connect(self.actualizarTablaFCFS)
		self.segundoHilo.start()

	def iniciaSJF(self):
		self.tercerHilo = HiloSJF(self.colaProcesosSJF)
		self.tercerHilo.senialActualizarOrden.connect(self.actualizarOrdenTablaSJF)
		self.tercerHilo.senialActualizarTiempo.connect(self.actualizarTiempoTablaSJF)
		self.tercerHilo.start()

#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())