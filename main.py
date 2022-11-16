#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
#pseudocodigo
"""crear 5 procesos aleatorio que se cargen en memoria
hacer su procesamiento normalmente
uno de esos procesos va a tener una interrupcion, lo que hara que se pase a procesar el siguiente proceso
esa interrupcion activara al manejador, el manejador mandara una señal al controlador del dispositivo simulado, 
un disco duro, el manejador tambien quedara en espera
el disco duro hace su proceso de busqueda, simple, con una barra de carga para que sea grafico
una vez que el disco termine, manda una señal al manejador, que vuelve a encenderse
el manejador agrega 2 bloques de memoria al marco del proceso que quedo pendiente
el manejador se apaga
se continua el procesamiento del proceso pendiente
una vez termina, se vuelve a llamar una interrupcion, que enciende el manejador
el manejador manda informacion al controlador del disco
el manejador se apaga
el disco simula la escritura con una barra de carga
una vez termina la barra de carga
en caso de que haya mas procesos pendientes, se continua con ellos"""
from random import randint
from PyQt5 import QtWidgets
from PyQt5 import uic
from Controlador import Controlador
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
			agregar = Proceso(i+1,randint(11,16),[randint(0,255),randint(0,255),randint(0,255)])
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
		self.semaforoControlador = [False]
			
		self.btnI.clicked.connect(self.correr)

	def correr(self):
		self.productor = Productor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria)
		self.productor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.productor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.productor.pintarTablaBufferRam.connect(self.socketPintarTablaBufferRam)
		self.consumidor = Consumidor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria,self.semaforoManejador)
		self.consumidor.actualizarBarra.connect(self.socketBarra)
		self.consumidor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.consumidor.quitarDeTablaPendientes.connect(self.socketQuitarDeTablaPendientes)
		self.consumidor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.consumidor.agregarATerminados.connect(self.socketAgregarATerminados)
		self.manejador = Manejador(self.semaforoManejador,self.semaforoControlador,self.procesosEnMemoria)
		self.manejador.pintarLabel.connect(self.socketPintarLabel)
		self.manejador.aniadirInfo.connect(self.socketAniadirInfo)
		self.manejador.cambiarLabelInstruccion.connect(self.socketCambiarLabelInstruccion)
		self.manejador.pintarTablaBufferRam.connect(self.socketPintarTablaBufferRam)
		self.manejador.pintarTablaBufferControlador.connect(self.socketPintarTablaBufferControlador)
		self.controlador = Controlador(self.semaforoControlador,self.semaforoManejador)
		self.controlador.aumentarControlador.connect(self.socketAumentarControlador)
		self.controlador.cambiarLabelInstruccion.connect(self.socketCambiarLabelInstruccion)
		self.productor.start()
		self.consumidor.start()
		self.manejador.start()
		self.controlador.start()
		
	def socketActualizaTablaPaginas(self,senial):
		proceso = QtWidgets.QTableWidgetItem(str(senial["proceso"]))
		indice = QtWidgets.QTableWidgetItem(str(senial["indice"]))
		self.tablaPaginas.setItem(senial["fila"],0,proceso)
		self.tablaPaginas.setItem(senial["fila"],1,indice)

	def socketPintarTablaMemoria(self,senial):
		self.tablaMemoria.setItem(senial["fila"],senial["columna"],senial["item"])
		
	def socketPintarTablaBufferRam(self,senial):
		self.tablaBufferRam.setItem(senial["fila"],senial["columna"],senial["item"])

	def socketPintarTablaBufferControlador(self,senial):
		self.tablaBufferControlador.setItem(senial["fila"],senial["columna"],senial["item"])


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
			self.lbManejador.setStyleSheet("background-color: green")
		else:
			self.lbManejador.setStyleSheet("background-color: red")

	def socketAumentarControlador(self,senial):
		self.barraControlador.setValue(senial)

	def socketAniadirInfo(self,senial):
		columna = QtWidgets.QTableWidgetItem("")
		columna.setBackground(senial["color"])
		self.tablaMemoria.setItem(2,senial["columna"],columna)

	def socketCambiarLabelInstruccion(self,senial):
		self.lbInstruccion.setText(senial)


#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())