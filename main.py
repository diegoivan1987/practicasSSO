#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from re import I
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtGui import  QColor
from PyQt5 import uic
import sys, time
import math

class Productor(QtCore.QThread):
	actualizaTablaPaginas = QtCore.pyqtSignal(dict)
	pintarTablaMemoria = QtCore.pyqtSignal(dict)#

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
					procesoActual = self.procesosPendientes[0]
					tamanio = procesoActual.tamanio
					if ((self.paginasDisponibles[0]*8)/tamanio)<1:#si ya no hay espacion disponible en la memoria fisica sale
						self.semaforoProductor[0] = False
						self.semaforoConsumidor[0] = True
					else:#si aun hay espacio en la memoria fisica
						procesoActual = self.procesosPendientes.pop(0)
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
						tamanioAuxiliar = procesoActual.tamanio
						color = QColor(procesoActual.color[0],procesoActual.color[1],procesoActual.color[2])
						for i in range(self.tablaPaginas.rowCount()):	
							if self.tablaPaginas.item(i,0).text()==str(procesoActual.id):
									posicionMarco = int(self.tablaPaginas.item(i,2).text())
									for j in range(8):
										if tamanioAuxiliar>0:
											columna = QtWidgets.QTableWidgetItem("")
											columna.setBackground(color)
											self.pintarTablaMemoria.emit({"fila":posicionMarco,"columna":j,"item":columna})
											time.sleep(0.05)
											tamanioAuxiliar-=1

class Consumidor(QtCore.QThread):
	actualizaTablaPaginas = QtCore.pyqtSignal(dict)
	pintarTablaMemoria = QtCore.pyqtSignal(dict)
	actualizarBarra = QtCore.pyqtSignal(dict)

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
				print("Entro consumidor")
				if len(self.procesosEnMemoria)>0:
					procesoActual = self.procesosEnMemoria.pop(0)
					tamanio = procesoActual.tamanio
					rangoAumento = math.floor(100/tamanio)
					porcentajeActual = 0
					numeroAumentos = 0
					while numeroAumentos < tamanio:
						porcentajeActual += rangoAumento
						self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":porcentajeActual})
						numeroAumentos += 1
						time.sleep(0.1)
					if(porcentajeActual<100):
						self.actualizarBarra.emit({"idProceso":procesoActual.id,"porcentajeBarra":100})
						time.sleep(0.1)
				else:
					self.semaforoConsumidor[0]=False
					self.semaforoProductor[0]=False
					#sobreescribir tabla de paginas
					#quitarlo de la memoria
					#añadirlo a procesos terminados
					#cambiar semaforos




#dependiendo de la opcion pasada en los parametros sera si es productor o consumidor
class ProductorConsumidor(QtCore.QThread):
	senial = QtCore.pyqtSignal(list)#señal que indica si quita o agrega al arreglo de procesos y que proceso es
	senialQuitar = QtCore.pyqtSignal(int)#para quitar procesos de la tabla de pendientes al cargarlo al buffer(producir)
	senialAgregar = QtCore.pyqtSignal(int)#para agregar procesos de la tabla de terminados al quitarlo del buffer(consumir)

	def __init__(self,mutex,dato,ocupados,opcion,repeticiones,banderaProductor,banderaConsumidor):
		super(ProductorConsumidor, self).__init__(None)
		self.mutex = mutex
		self.dato = dato
		self.opcion = opcion#indicara si es productor o consumidor
		self.repeticiones = repeticiones#numero total de veces que se ha consumido un proceso
		self.banderaProductor = banderaProductor#bandera para hacer trabajar al productor
		self.banderaConsumidor = banderaConsumidor#bandera para hacer trabajar al consumidor
		self.ocupados = ocupados#espacios ocupados en el buffer
		
	#se inicia o continua el proceso
	def run(self):
		while self.repeticiones[0]<20:
			self.mutex.lock()
			#print("repeticion "+str(self.repeticiones[0]))
			if self.opcion == 1:#productor
				if self.banderaProductor[0] == 1:
					if self.repeticiones[0] < 20:
						self.producir(self.dato,self.ocupados,self.repeticiones,self.banderaProductor,self.banderaConsumidor,self.senial)
						self.senialQuitar.emit(0)
			elif self.opcion == 2:#consumidor
				if self.banderaConsumidor[0] == 1:
					self.consumir(self.dato,self.ocupados,self.repeticiones,self.banderaProductor,self.banderaConsumidor,self.senial)
					self.senialAgregar.emit(0)
			self.mutex.unlock()
	

	def producir(self,dato,ocupado,repeticiones,banderaProductor,banderaConsumidor,senial):
		dato[0]+= 1
		#print("Produce "+str(dato[0]))
		senial.emit([dato[0]-1,1])
		time.sleep(0.1)
		ocupado[0] +=1 
		if ocupado[0] == 10:
			banderaProductor[0] = 0
			banderaConsumidor[0] = 1

	def consumir(self,dato,ocupado,repeticiones,banderaProductor,banderaConsumidor,senial):
		dato[0] -= 1
		#print("Consume "+str(dato[0]))
		senial.emit([dato[0],2])
		time.sleep(0.1)
		repeticiones[0] +=1
		ocupado[0] -= 1
		if ocupado[0] == 0:
			banderaProductor[0] = 1
			banderaConsumidor[0] = 0

class Proceso():
		id = 0
		tamanio = 0
		color = []


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
		self.matrizTablaPendientes = []
		self.matrizTablaTerminados = []
		self.matrizMemoria = []
		self.matrizTablaPaginas = []

		#inicializamos los arreglos de procesos y sus datos
		for i in range(20):
			agregar = Proceso(i+1,randint(1,24),[randint(0,255),randint(0,255),randint(0,255)])
			self.procesosPendientes.append(agregar)


		#llenamos la tabla de pendientes
		for i in range(20):
			self.tablaPendientes.insertRow(self.tablaPendientes.rowCount())
			id = QtWidgets.QTableWidgetItem(str(self.procesosPendientes[i].id))
			tamanio = QtWidgets.QTableWidgetItem(str(self.procesosPendientes[i].tamanio))
			self.tablaPendientes.setItem(i,0,id)
			self.tablaPendientes.setItem(i,1,tamanio)

		self.paginasDisponibles = [10]
		self.semaforoProductor = [True]
		self.semaforoConsumidor  =[False]
			
		self.btnI.clicked.connect(self.correr)

	def correr(self):
		self.productor = Productor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria)
		self.productor.actualizaTablaPaginas.connect(self.socketActualizaTablaPaginas)
		self.productor.pintarTablaMemoria.connect(self.socketPintarTablaMemoria)
		self.consumidor = Consumidor(self.semaforoProductor,self.semaforoConsumidor,self.procesosPendientes,self.paginasDisponibles,self.tablaPaginas,self.tablaMemoria,self.procesosEnMemoria)
		self.consumidor.actualizarBarra.connect(self.socketBarra)
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


			
	def quitaDeTabla(self,senial):
		self.tablaPendientes.removeRow(senial)
		agregar = self.colaPendientes.pop(senial)
		self.colaTerminados.append(agregar)

	def aniadirATabla(self,senial):
		self.tablaTerminados.insertRow(self.tablaTerminados.rowCount())
		proceso = self.colaTerminados.pop(senial)
		print("Se agrego "+str(proceso.id))
		agregar = QtWidgets.QTableWidgetItem("Proceso "+str(proceso.id))
		self.tablaTerminados.setItem(self.tablaTerminados.rowCount()-1,0,agregar)

#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())