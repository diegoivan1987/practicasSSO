#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtWidgets
from PyQt5 import uic
from Manejador import Manejador
from PyQt5.QtGui import  QColor

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
		self.semaforoManejador  =[False]
			
		self.btnI.clicked.connect(self.correr)

	def correr(self):
		self.productor = Productor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria)
		self.productor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.productor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.consumidor = Consumidor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria,self.semaforoManejador)
		self.consumidor.actualizarBarra.connect(self.socketBarra)
		self.consumidor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.consumidor.quitarDeTablaPendientes.connect(self.socketQuitarDeTablaPendientes)
		self.consumidor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.consumidor.agregarATerminados.connect(self.socketAgregarATerminados)
		#self.manejador = Manejador(self.semaforoManejador,self.semaforoConsumidor)
		#self.manejador.pintarLabel.connect(self.socketPintarLabel)
		self.productor.start()
		self.consumidor.start()
		#self.manejador.start()
		
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
		#se hace hardcodeado porque si me pongo a remover por el id del proceso, por algun motivo al obtener el texto de la celda me da error
		if senial[0] == 1:
			if senial[1] == 1 or senial[1] == 2:
				self.tablaPendientes.removeRow(0)
			else:
				self.tablaPendientes.removeRow(1)
				
	def socketAgregarATerminados(self,senial):
		self.tablaTerminados.insertRow(self.tablaTerminados.rowCount())
		id = QtWidgets.QTableWidgetItem(str(senial))
		self.tablaTerminados.setItem(self.tablaTerminados.rowCount()-1,0,id)

	def socketPintarLabel(self,senial):
		color = QColor(150,60,150)
		if senial == 1:
			self.lbManejador.setStyleSheet("foreground-color: red")

#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())