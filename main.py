#ejecutar desde la carpeta, para que detecte el archivo de la interfaz grafica
from random import randint
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtGui import  QColor
from PyQt5 import uic
import sys, time

from matplotlib.pyplot import text

class lectorEscritor(QtCore.QThread):
	palabraLectura = QtCore.pyqtSignal(str)#mandara una palabra al cuadro de lectura
	senialMensajeEscritor = QtCore.pyqtSignal(str)#mandara un mensaje cuando no se pueda entrar a un escritor

	def __init__(self,texto,argumentos,cuadroDeTexto,mutex,semaforoEscritor,contadorLectores,escritorActivo):
		super(lectorEscritor, self).__init__(None)
		self.texto = texto
		self.argumentos = argumentos
		self.cuadroDeTexto = cuadroDeTexto
		self.mutex = mutex
		self.semaforoEscritor =semaforoEscritor
		self.contadorLectores = contadorLectores
		self.escritorActivo = escritorActivo
		
	#se inicia o continua el proceso
	def run(self):
		if self.argumentos["opcion"] == "lector":
			if self.escritorActivo[0] == False:
				self.lectura()
			else:	
				self.palabraLectura.emit("Escritor activo, esperar")
		elif self.argumentos["opcion"] == "escritor":
			if self.semaforoEscritor[0] == True:
				self.cuadroDeTexto.setEnabled(True)
				self.semaforoEscritor[0] = False
				print("Se apago el semaforo del escritor")
				self.escritorActivo[0] = True
			else:
				self.senialMensajeEscritor.emit("Hay otro escritor o lector activo, espere")

	def lectura(self):
		#self.cuadroDeTexto.setPlainText("")
		self.mutex.lock()
		print("Se bloqueo lector,1 parte")
		self.contadorLectores[0] += 1
		if self.contadorLectores[0] == 1:
			self.semaforoEscritor[0] = False
		self.mutex.unlock()
		print("Se desbloqueo lector,1 parte")
		palabras = str.split(self.texto[0],"\n")
		for palabra in palabras:
			#self.palabraLectura.emit([palabra,self.argumentos["indice"]])
			self.palabraLectura.emit(palabra)
			time.sleep(1)
		self.mutex.lock()
		print("Se bloqueo lector,2 parte")
		self.contadorLectores[0] -= 1
		if self.contadorLectores[0] == 0:
			self.semaforoEscritor[0] = True
		self.mutex.unlock()
		print("Se desbloqueo lector,1 parte")

			
	
	def stop(self):
		self.texto[0] = self.cuadroDeTexto.toPlainText()
		self.cuadroDeTexto.setEnabled(False)
		self.semaforoEscritor[0] = True
		print("Se prendio el semaforo del escritor")
		self.escritorActivo[0] = False
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

		self.txtL1.setPlainText("")
		self.txtL2.setPlainText("")

		self.txtE1.setEnabled(False)
		self.txtE2.setEnabled(False)
		self.txtL1.setEnabled(False)
		self.txtL2.setEnabled(False)
			
		self.btnIL1.clicked.connect(self.inicioLector1)
		self.btnIL2.clicked.connect(self.inicioLector2)
		self.btnIE1.clicked.connect(self.inicioEscritor1)
		self.btnPE1.clicked.connect(self.pararEscritor1)
		self.btnIE2.clicked.connect(self.inicioEscritor2)
		self.btnPE2.clicked.connect(self.pararEscritor2)

		self.argumentosEscritor = {"opcion":"escritor"}
		#self.argumentosEscritor = {"seEscribio":False}
		self.semaforoEscritor=[True]
		self.contadorLectores = [0]
		self.mutexLectores = QtCore.QMutex()
		self.escritorActivo = [False]
		self.hiloEscritor1 = lectorEscritor(self.texto,self.argumentosEscritor,self.txtE1,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)
		self.hiloEscritor2 = lectorEscritor(self.texto,self.argumentosEscritor,self.txtE2,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)

	def inicioEscritor1(self):
		self.hiloEscritor1.senialMensajeEscritor.connect(self.socketMensajeEscritor1)
		self.hiloEscritor1.start()
	
	def pararEscritor1(self):
		self.hiloEscritor1.stop()

	def inicioEscritor2(self):
		self.hiloEscritor2.senialMensajeEscritor.connect(self.socketMensajeEscritor2)
		self.hiloEscritor2.start()
	
	def pararEscritor2(self):
		self.hiloEscritor2.stop()

	def inicioLector1(self):
		self.argumentos = {"opcion":"lector"}
		self.hiloLector = lectorEscritor(self.texto,self.argumentos,self.txtL1,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)
		self.hiloLector.palabraLectura.connect(self.socketLector1)
		self.hiloLector.start()
	
	def socketLector1(self,senial):
		self.escribir = self.txtL1.toPlainText()
		self.escribir = self.escribir + "\n"+ senial
		self.txtL1.setPlainText(self.escribir)

	def inicioLector2(self):
		self.argumentos = {"opcion":"lector"}
		self.hiloLector = lectorEscritor(self.texto,self.argumentos,self.txtL2,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)
		self.hiloLector.palabraLectura.connect(self.socketLector2)
		self.hiloLector.start()
	
	def socketLector2(self,senial):
		self.escribir = self.txtL2.toPlainText()
		self.escribir = self.escribir + "\n"+ senial
		self.txtL2.setPlainText(self.escribir)

	def socketMensajeEscritor1(self,signal):
		self.txtE1.setPlainText(signal)

	def socketMensajeEscritor2(self,signal):
		self.txtE2.setPlainText(signal)


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