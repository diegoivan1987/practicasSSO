#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtGui import  QColor
from PyQt5 import uic
import sys, time

class ProductorConsumidor(QtCore.QThread):
	senial = QtCore.pyqtSignal(list)

	def __init__(self,mutex,dato,ocupados,opcion,repeticiones,banderaProductor,banderaConsumidor):
		super(ProductorConsumidor, self).__init__(None)
		self.mutex = mutex
		self.dato = dato
		self.opcion = opcion
		self.repeticiones = repeticiones
		self.banderaProductor = banderaProductor
		self.banderaConsumidor = banderaConsumidor
		self.ocupados = ocupados
		
	#se inicia o continua el proceso
	def run(self):
		while self.repeticiones[0]<20:
			self.mutex.lock()
			print("repeticion "+str(self.repeticiones[0]))
			if self.opcion == 1:
				if self.banderaProductor[0] == 1:
					if self.repeticiones[0] < 20:
						self.producir(self.dato,self.ocupados,self.repeticiones,self.banderaProductor,self.banderaConsumidor,self.senial)
			elif self.opcion == 2:
				if self.banderaConsumidor[0] == 1:
					self.consumir(self.dato,self.ocupados,self.repeticiones,self.banderaProductor,self.banderaConsumidor,self.senial)
			self.mutex.unlock()
	

	def producir(self,dato,ocupado,repeticiones,banderaProductor,banderaConsumidor,senial):
		dato[0]+= 1
		print("Produce "+str(dato[0]))
		senial.emit([dato[0]-1,1])
		time.sleep(0.1)
		ocupado[0] +=1 
		if ocupado[0] == 10:
			banderaProductor[0] = 0
			banderaConsumidor[0] = 1

	def consumir(self,dato,ocupado,repeticiones,banderaProductor,banderaConsumidor,senial):
		dato[0] -= 1
		print("Consume "+str(dato[0]))
		senial.emit([dato[0],2])
		time.sleep(0.1)
		repeticiones[0] +=1
		ocupado[0] -= 1
		if ocupado[0] == 0:
			banderaProductor[0] = 1
			banderaConsumidor[0] = 0

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

		#inicializamos los arreglos de procesos y sus datos
		for i in range(20):
			agregar = Proceso(i+1,randint(1,10))
			self.colaProcesosFCFS.append(agregar)

		#inicializamos los datos de las tablas
		for i in range(10):
			columna = QtWidgets.QTableWidgetItem("")
			color = QColor(124,252,0)
			columna.setBackground(color)
			self.tablaProcesos.setItem(0,i,columna)

		for i in range(20):
			self.tablaPendientes.addRow()
			agregar = QtGui.QTableWidgetItem("Proceso "+str(self.colaProcesosFCFS[i]))
			
		self.btnI.clicked.connect(self.correr)

	def correr(self):
		self.dato = [0]
		self.repeticiones = [0]
		self.banderaProductor = [1]
		self.banderaConsumidor = [0]
		self.ocupados = [0]
		self.mutex = QtCore.QMutex()
		self.productor = ProductorConsumidor(self.mutex,self.dato,self.ocupados,1,self.repeticiones,self.banderaProductor,self.banderaConsumidor)
		self.consumidor = ProductorConsumidor(self.mutex,self.dato,self.ocupados,2,self.repeticiones,self.banderaProductor,self.banderaConsumidor)
		self.productor.senial.connect(self.socketPintaSector)
		self.consumidor.senial.connect(self.socketPintaSector)
		self.productor.start()
		self.consumidor.start()
		
	def socketPintaSector(self,senial):
		columna = QtWidgets.QTableWidgetItem("")
		if senial[1] == 1:
			color = QColor(238, 75, 43)
		elif senial[1] == 2:
			color = QColor(124,252,0)
		columna.setBackground(color)
		self.tablaProcesos.setItem(0,senial[0],columna)
			
	

#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())