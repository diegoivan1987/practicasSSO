#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtGui import  QColor
from PyQt5 import uic
import sys, time

from matplotlib.pyplot import text

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

class lectorEscritor(QtCore.QThread):
	palabraLectura = QtCore.pyqtSignal(str)#mandara una palabra al cuadro de lectura

	def __init__(self,texto,argumentos,cuadroDeEscritura):
		super(lectorEscritor, self).__init__(None)
		self.texto = texto
		self.argumentos = argumentos
		self.cuadroDeEscritura = cuadroDeEscritura
		
	#se inicia o continua el proceso
	def run(self):
		if self.argumentos["opcion"] == "lector":
			palabras = str.split(self.texto[0],"\n")
			for palabra in palabras:
				#self.palabraLectura.emit([palabra,self.argumentos["indice"]])
				self.palabraLectura.emit(palabra)
				time.sleep(1)
		elif self.argumentos["opcion"] == "escritor":
			self.cuadroDeEscritura.setEnabled(True)
			
	
	def stop(self):
		self.texto[0] = self.cuadroDeEscritura.toPlainText()
		self.cuadroDeEscritura.setEnabled(False)
		self.quit()

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

		self.texto = ["Autómata\nSalvajes\nArtificio\nHipócritas\nClon\nPrimitivos\nEntelequia\nRacistas\nAnatema\nIntolerantes\n"]

		self.txtE1.setPlainText(self.texto[0])
		self.txtE2.setPlainText(self.texto[0])

		self.txtE1.setEnabled(False)
		self.txtE2.setEnabled(False)
		self.txtL1.setEnabled(False)
		self.txtL2.setEnabled(False)
			
		self.btnIL1.clicked.connect(self.inicioLector1)
		self.btnIL2.clicked.connect(self.inicioLector2)
		self.btnIE1.clicked.connect(self.inicioEscritor1)
		self.btnPE1.clicked.connect(self.pararEscritor1)
		self.btnIE2.clicked.connect(self.inicioEscritor1)
		self.btnPE2.clicked.connect(self.pararEscritor1)

		self.argumentosEscritor = {"opcion":"escritor"}
		self.hiloEscritor1 = lectorEscritor(self.texto,self.argumentosEscritor,self.txtE1)
		self.hiloEscritor2 = lectorEscritor(self.texto,self.argumentosEscritor,self.txtE2)

	def inicioEscritor1(self):
		self.hiloEscritor1.start()
	
	def pararEscritor1(self):
		self.hiloEscritor1.stop()

	def inicioEscritor2(self):
		self.hiloEscritor2.start()
	
	def pararEscritor2(self):
		self.hiloEscritor2.stop()

	def inicioLector1(self):
		self.argumentos = {"opcion":"lector"}
		self.hiloLector = lectorEscritor(self.texto,self.argumentos,self.txtE1)
		self.hiloLector.palabraLectura.connect(self.socketLector1)
		self.hiloLector.start()
	
	def socketLector1(self,senial):
		self.txtL1.setPlainText("")
		self.escribir = self.txtL1.toPlainText()
		self.escribir = self.escribir + "\n"+ senial
		self.txtL1.setPlainText(self.escribir)

	def inicioLector2(self):
		self.argumentos = {"opcion":"lector"}
		self.hiloLector = lectorEscritor(self.texto,self.argumentos,self.txtE1)
		self.hiloLector.palabraLectura.connect(self.socketLector2)
		self.hiloLector.start()
	
	def socketLector2(self,senial):
		self.txtL2.setPlainText("")
		self.escribir = self.txtL2.toPlainText()
		self.escribir = self.escribir + "\n"+ senial
		self.txtL2.setPlainText(self.escribir)


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
		self.productor.senialQuitar.connect(self.quitaDeTabla)
		self.consumidor.senial.connect(self.socketPintaSector)
		self.consumidor.senialAgregar.connect(self.aniadirATabla)
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