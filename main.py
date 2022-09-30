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
		time.sleep(0.01)#para que se alcancen a reflejar los cambios en la interfaz
		#no se termina hasta que se hayan terminado todos los pr
		# ocesos
		while contadorProcesosFinalizados < len(self.colaProcesosSJF):
			#recorremos el arreglo de procesos
			for i in range(len(self.colaProcesosSJF)):
				if randint(1,10)==1:
					agregar = Proceso(len(self.colaProcesosSJF)+1,randint(1,10))
					print("Se creo el proceso "+str(agregar.id))
					self.colaProcesosSJF.append(agregar)
					self.ordenaProcesos(self.colaProcesosSJF)
					self.senialActualizarOrden.emit(1)
					time.sleep(0.01)#para que se alcancen a reflejar los cambios en la interfaz

				if self.colaProcesosSJF[i].banderaTerminado == False:#si aun no termina, sigue trabajando con el proceso
					for j in range(self.colaProcesosSJF[i].tiempoEstimado):#mientras no se haya terminado el proceso o la cota de tiempo
						time.sleep(1)
						self.colaProcesosSJF[i].tiempoEstimado-=1#disminuimos su tiempo
						if self.colaProcesosSJF[i].tiempoEstimado == 0:#si se completo durante este ciclo
							self.colaProcesosSJF[i].banderaTerminado = True#lo marcamos como terminado
							contadorProcesosFinalizados += 1#aumentamos el contador de procesos terminados
							self.senialActualizarTiempo.emit(i)
							time.sleep(0.01)#para que se alcancen a reflejar los cambios en la interfaz
							break#interrumpimos la duracion de la cota de tiempo
						self.senialActualizarTiempo.emit(i)		
		print("se termino el procesamiento SJF")#ayuda para saber si termino el bucle
		self.quit()

	def ordenaProcesos(self,colaProcesosSJF=[]):
		for j in range(len(colaProcesosSJF)-1):
			for i in range(len(colaProcesosSJF)-1):
				if colaProcesosSJF[i].tiempoEstimado>colaProcesosSJF[i+1].tiempoEstimado:
					temp = colaProcesosSJF[i]
					colaProcesosSJF[i] = self.colaProcesosSJF[i+1]
					colaProcesosSJF[i+1] = temp

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
		contadorFCFS = 0
		#no se termina hasta que se hayan terminado todos los procesos
		while contadorProcesosFinalizados <(len(self.colaProcesosRR)):
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
							time.sleep(0.005)#para que se alcancen a reflejar los cambios en la interfaz
							break#interrumpimos la duracion de la cota de tiempo
						self.senialActualizarRR.emit(i)
						if(i>0 and randint(1,3)==2):
							print("bloqueo en "+str(self.colaProcesosRR[i].id))
							if contadorFCFS == 0:
								while (self.colaProcesosFCFS[0].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[0].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(0)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								while (self.colaProcesosFCFS[1].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[1].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(1)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								while (self.colaProcesosFCFS[2].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[2].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(2)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								contadorFCFS = 1
							elif contadorFCFS == 1:
								while (self.colaProcesosFCFS[3].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[3].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(3)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								while (self.colaProcesosFCFS[4].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[4].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(4)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								while (self.colaProcesosFCFS[5].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[5].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(5)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								contadorFCFS = 2
							elif contadorFCFS == 2:
								while (self.colaProcesosFCFS[6].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[6].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(6)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								while (self.colaProcesosFCFS[7].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[7].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(7)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								while (self.colaProcesosFCFS[8].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[8].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(8)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)	
								contadorFCFS = 3
							elif contadorFCFS == 3:
								while (self.colaProcesosFCFS[9].porcentajeProcesado<100):#mientras no se haya terminado el proceso
									self.colaProcesosFCFS[9].porcentajeProcesado+=1#aumentamos su porcentaje
									self.senialActualizarFCFS.emit(9)#aqui no se hace primero porque no hay un cambio de indides en la lista
									time.sleep(0.01)
									contadorFCFS = 4	
								print("se termino el procesamiento de FCFS")#ayuda para saber si termino el bucle
							#contador = 0
							#for ax in range(len(self.colaProcesosFCFS)):
							#	if self.colaProcesosFCFS[ax].banderaTerminado == False and contador < 3:
							#		self.colaProcesosFCFS[ax].banderaTerminado = True
							#		self.colaProcesosFCFS[ax].porcentajeProcesado = 100
							#		self.senialActualizarFCFS.emit(ax)
							#		contador +=1
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
			agregar2 = Proceso(i+1,randint(1,10))
			agregar3 = Proceso(i+1,randint(1,10))
			self.colaProcesosFCFS.append(agregar)
			self.colaProcesosRR.append(agregar2)
			self.colaProcesosSJF.append(agregar3)

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