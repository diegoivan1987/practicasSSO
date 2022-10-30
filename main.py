#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtWidgets
from PyQt5 import uic

from Productor import Productor
from Consumidor import Consumidor

import sys

class Proceso():
		id = 0
		tamanio = 0 #solo para cuestiones graficas
		porcentajeProcesado = 0
		color = []
		marcos = []#marcos en memoria fisica que ocupa

		def __init__(self,id,tamanio,color):
				self.id = id
				self.tamanio = tamanio
				self.color = color

class VentanaPrincipal(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.ui = uic.loadUi('prueba.ui',self)#Se carga la interfaz grafica

		self.procesosPendientes = []
		self.procesosEnMemoria = []

		#inicializamos los arreglos de procesos y sus datos
		for i in range(5):
			agregar = Proceso(i+1,randint(9,14),[randint(0,255),randint(0,255),randint(0,255)])
			self.procesosPendientes.append(agregar)


		#llenamos la tabla de pendientes
		for i in range(len(self.procesosPendientes)):
			self.tablaPendientes.insertRow(self.tablaPendientes.rowCount())
			id = QtWidgets.QTableWidgetItem(str(self.procesosPendientes[i].id))
			tamanio = QtWidgets.QTableWidgetItem(str(self.procesosPendientes[i].tamanio))
			self.tablaPendientes.setItem(i,0,id)
			self.tablaPendientes.setItem(i,1,tamanio)

		self.paginasDisponibles = [10]#tamanio total de la tabla de paginas
		self.semaforoProductor = [True]
		self.semaforoConsumidor  =[False]
			
		self.btnI.clicked.connect(self.correr)

	def correr(self):
		self.productor = Productor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria)
		self.productor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.productor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.consumidor = Consumidor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria)
		self.consumidor.actualizarBarra.connect(self.socketBarra)
		self.consumidor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.consumidor.quitarDeTablaPendientes.connect(self.socketQuitarDeTablaPendientes)
		self.consumidor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.consumidor.agregarATerminados.connect(self.socketAgregarATerminados)
		self.productor.start()
		self.consumidor.start()
		
	def socketActualizaTablaPaginas(self,senial):
		proceso = QtWidgets.QTableWidgetItem(str(senial["proceso"]))
		indice = QtWidgets.QTableWidgetItem(str(senial["indice"]))
		self.tablaPaginas.setItem(senial["fila"],0,proceso)
		self.tablaPaginas.setItem(senial["fila"],1,indice)

	def socketPintarTablaMemoria(self,senial):
		self.tablaMemoria.setItem(senial["fila"],senial["columna"],senial["item"])

	def socketBarra(self,senial):
		self.label_3.setText("Proceso: "+str(senial["idProceso"]))
		self.barra.setValue(senial["porcentajeBarra"])

	def socketQuitarDeTablaPendientes(self,senial):
		if senial == 1:
			self.tablaPendientes.removeRow(0)#como usamos una lista FIFO, siempre se va a terminar el primer proceso en la lista, por lo tanto, siempre quitamos el primero de la tabla
				
	def socketAgregarATerminados(self,senial):
		self.tablaTerminados.insertRow(self.tablaTerminados.rowCount())
		id = QtWidgets.QTableWidgetItem(str(senial))
		self.tablaTerminados.setItem(self.tablaTerminados.rowCount()-1,0,id)

#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())