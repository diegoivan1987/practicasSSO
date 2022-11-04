#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtWidgets
from PyQt5 import uic

from Productor import Productor
from Consumidor import Consumidor

import sys

class Proceso():
		id = 0
		tamanio = 0
		color = []
		colorVirtual = []

		def __init__(self,id,tamanio,color,colorVirtual):
				self.id = id
				self.tamanio = tamanio
				self.color = color
				self.colorVirtual = colorVirtual

class VentanaPrincipal(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.ui = uic.loadUi('prueba.ui',self)#Se carga la interfaz grafica

		self.procesosPendientes = []
		self.procesosEnMemoria = []
		self.indiceMarcoActual = 0

		#inicializamos los arreglos de procesos y sus datos
		for i in range(10):
			color1 = randint(50,255)
			color2 = randint(50,255)
			color3 = randint(50,255)
			agregar = Proceso(i+1,randint(1,24),[color1,color2,color3],[color1-50,color2-50,color3-50])
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

		self.numeroMarcoFisico = [0] #serviran para llenar la tabla de paginas
		self.numeroMarcoVirtual = [0] #serviran para llenar la tabla de paginas
			
		self.btnI.clicked.connect(self.correr)

	def correr(self):
		self.productor = Productor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria,self.numeroMarcoFisico,self.numeroMarcoVirtual)
		self.productor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.productor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.productor.pintarTablaMemoriaVirtual.connect(self.socketPintarTablaMemoriaVirtual)

		#self.consumidor = Consumidor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria,self.indiceMarcoActual)
		#self.consumidor.actualizarBarra.connect(self.socketBarra)
		#self.consumidor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		#self.consumidor.quitarDeTablaPendientes.connect(self.socketQuitarDeTablaPendientes)
		#self.consumidor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		#self.consumidor.agregarATerminados.connect(self.socketAgregarATerminados)
		self.productor.start()
		#self.consumidor.start()
		
	def socketActualizaTablaPaginas(self,senial):
		proceso = QtWidgets.QTableWidgetItem(str(senial["proceso"]))
		indice = QtWidgets.QTableWidgetItem(str(senial["indice"]))
		numeroMarco = QtWidgets.QTableWidgetItem(str(senial["numeroMarco"]))
		enRAM = QtWidgets.QTableWidgetItem(str(senial["RAM"]))
		if senial["funcion"] == "agregar":
			self.tablaPaginas.insertRow(self.tablaPaginas.rowCount())
			self.tablaPaginas.setItem(self.tablaPaginas.rowCount()-1,0,proceso)
			self.tablaPaginas.setItem(self.tablaPaginas.rowCount()-1,1,indice)
			self.tablaPaginas.setItem(self.tablaPaginas.rowCount()-1,2,numeroMarco)
			self.tablaPaginas.setItem(self.tablaPaginas.rowCount()-1,3,enRAM)

	def socketPintarTablaMemoria(self,senial):
		if senial["RAM"]==1:
			self.tablaMemoria.setItem(senial["fila"],senial["columna"],senial["item"])
	
	def socketPintarTablaMemoriaVirtual(self,senial):
		if senial["RAM"]==0:
			print("jodete")
			print("Proceso "+str(senial["id"])+" marco "+str(senial["fila"])+" columna "+str(senial["columna"]))
			self.tablaVirtual.setItem(senial["fila"],senial["columna"],senial["item"])

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