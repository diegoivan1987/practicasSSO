"""en este programa varios lectores pueden leer una variable al mismo tiempo, pero solo un escritor puede escribir al
mismo tiempo
Si se esta leyendo, todos los escritores deben esperar
si se esta escribiendo, todos los lectores y escritores que no sean el que esta realizando la accion deben esperar"""
from random import randint
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtGui import  QColor
from PyQt5 import uic
import sys, time

class lectorEscritor(QtCore.QThread):
	palabraLectura = QtCore.pyqtSignal(str)#mandara una palabra al cuadro de lectura
	senialMensajeEscritor = QtCore.pyqtSignal(str)#mandara un mensaje cuando no se pueda entrar a un escritor

	def __init__(self,texto,argumentos,cuadroDeTexto,mutex,semaforoEscritor,contadorLectores,escritorActivo):
		super(lectorEscritor, self).__init__(None)
		self.texto = texto#texto que se va a leer o a sobreescribir
		self.argumentos = argumentos #argumentos independientes de cada hilo
		self.cuadroDeTexto = cuadroDeTexto #cuadro de texto que se verá afectado
		self.mutex = mutex #mutex global
		self.semaforoEscritor =semaforoEscritor #semaforo para el escritor, global
		self.contadorLectores = contadorLectores #contador de los lectores activos,global
		self.escritorActivo = escritorActivo #indicador de escritor activo, solo se usa para dar mensajes a los lectores, global
		
	#proceso principal
	def run(self):
		if self.argumentos["opcion"] == "lector":
			if self.escritorActivo[0] == False:
				self.lectura()
			else:	
				self.palabraLectura.emit("Escritor activo, esperar")
		elif self.argumentos["opcion"] == "escritor":
			if self.semaforoEscritor[0] == True:#si el semaforo de escritor esta prendido entra
				self.cuadroDeTexto.setEnabled(True)#habilitamos el cuadro de texto para que pueda escribir
				self.semaforoEscritor[0] = False#volvemos a apagar el semaforo para que el otro escritor no pueda entrar
				print("Se apago el semaforo del escritor")
				self.escritorActivo[0] = True#indicador para mensajes hacia los lectores
			else:
				self.senialMensajeEscritor.emit("Hay otro escritor o lector activo, espere")

	def lectura(self):#usa las variables utilizadas por lectores, a su vez que puede prender el semaforo del escritor
		self.mutex.lock()#bloquemoas porque varios lectores pueden intentar alterar esto
		print("Se bloqueo lector,1 parte")
		self.contadorLectores[0] += 1
		if self.contadorLectores[0] == 1:
			self.semaforoEscritor[0] = False
		self.mutex.unlock()
		print("Se desbloqueo lector,1 parte")
		palabras = str.split(self.texto[0],"\n")#aqui se realiza el proceso de lectura, esto no tiene problema si se bloquea o no
		for palabra in palabras:
			#self.palabraLectura.emit([palabra,self.argumentos["indice"]])
			self.palabraLectura.emit(palabra)
			time.sleep(1)
		self.mutex.lock()#bloquemoas porque varios lectores pueden intentar alterar esto
		print("Se bloqueo lector,2 parte")
		self.contadorLectores[0] -= 1
		if self.contadorLectores[0] == 0:
			self.semaforoEscritor[0] = True
		self.mutex.unlock()
		print("Se desbloqueo lector,1 parte")

	#aqui es donde realmente se altera la variable de texto que leeran los lectores, tambien se prende el semaforo de escritor para dejarlo disponible para otro
	def stop(self):
		self.texto[0] = self.cuadroDeTexto.toPlainText()
		self.cuadroDeTexto.setEnabled(False)
		self.semaforoEscritor[0] = True
		print("Se prendio el semaforo del escritor")
		self.escritorActivo[0] = False
		self.quit()

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
		self.semaforoEscritor=[True]
		self.contadorLectores = [0] #numero de lectores activos al mismo tiempo
		self.mutexLectores = QtCore.QMutex()
		self.escritorActivo = [False]
		self.hiloEscritor1 = lectorEscritor(self.texto,self.argumentosEscritor,self.txtE1,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)
		self.hiloEscritor2 = lectorEscritor(self.texto,self.argumentosEscritor,self.txtE2,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)

	def inicioEscritor1(self):
		self.txtE1.setPlainText(self.texto[0])
		self.hiloEscritor1.senialMensajeEscritor.connect(self.socketMensajeEscritor1)
		self.hiloEscritor1.start()
	
	def pararEscritor1(self):
		self.hiloEscritor1.stop()

	def inicioEscritor2(self):
		self.txtE2.setPlainText(self.texto[0])
		self.hiloEscritor2.senialMensajeEscritor.connect(self.socketMensajeEscritor2)
		self.hiloEscritor2.start()
	
	def pararEscritor2(self):
		self.hiloEscritor2.stop()

	def inicioLector1(self):
		self.txtL1.setPlainText("")
		self.argumentos = {"opcion":"lector"}
		self.hiloLector = lectorEscritor(self.texto,self.argumentos,self.txtL1,self.mutexLectores,self.semaforoEscritor,self.contadorLectores,self.escritorActivo)
		self.hiloLector.palabraLectura.connect(self.socketLector1)
		self.hiloLector.start()
	
	def socketLector1(self,senial):
		self.escribir = self.txtL1.toPlainText()
		self.escribir = self.escribir + "\n"+ senial
		self.txtL1.setPlainText(self.escribir)

	def inicioLector2(self):
		self.txtL2.setPlainText("")
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

#Iniciamos la aplicacion en bucle
app = QtWidgets.QApplication(sys.argv)
mainWindow = VentanaPrincipal()
mainWindow.show()
sys.exit(app.exec_())