import gtk
import os
import subprocess as sp
import time
import threading
import socket
import SocketServer
import Queue
import MySQLdb
import sys
import webkit
from decimal import *
gtk.gdk.threads_init()
#gobject.threads_init()
hilo = True
texto1 = ""
DEFAULT_URL = 'http://localhost/GPS/index.php'
class MainWin:

	def __init__(self):
		w = gtk.Window()
		w.set_default_size(1050, 620)
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(230,230)
		self.entrada = gtk.TextView()
		self.buffer = self.entrada.get_buffer()
		sw.add(self.entrada)
		hbox = gtk.HBox(False,0)
		sw2 = gtk.ScrolledWindow()
		self.webview = webkit.WebView()
		sw2.add(self.webview)
		hbox.pack_start(sw2)
		
		vbox = gtk.VBox(False, 0)
		vbox.pack_start(sw, True, True,0)
		hbox.pack_end(vbox, False, False, 0)
		box = gtk.HBox(False, 0)
		self.btn_start = gtk.Button("Start")
		self.btn_start.connect("clicked", self.btn_start_click)
		box.pack_start(self.btn_start)
		btn_test = gtk.Button("Test")
		btn_test.connect("clicked", self.btn_test_click)
		box.pack_end(btn_test)
		
		self.btn_stop = gtk.Button("Stop")
		self.btn_stop.connect("clicked", self.btn_stop_click)
		
		self.btn_stop.set_sensitive(False)
		box.pack_end(self.btn_stop)
		
		
		vbox.pack_end(box, False, False, 0)
		box3 = gtk.VBox(True, 0)
		
		self.entry_lat = gtk.Entry(10)
		self.entry_lat.set_editable(False)
		box3.pack_start(self.entry_lat)
		
		self.entry_long = gtk.Entry(10)
		self.entry_long.set_editable(False)
		box3.pack_start(self.entry_long)
		
		vbox.pack_end(box3, False, False, 0)
		
		box4 = gtk.HBox(True,0)
		self.seguir = gtk.CheckButton("Seguir", True)
		self.seguir.set_active(True)
		self.seguir.connect("toggled", self.seguir_toggle)
		box4.pack_start(self.seguir)
		box3.pack_start(box4)
		


		w.add(hbox)
		w.show_all()
		w.connect("destroy", self.quit)

	def get_popen(self, cmd):
		return sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
	
	def exec_cmd(self):
		global texto1
		print "Soy el hilo"
		self.miSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.miSocket.bind(("192.168.1.2", 4545))
		self.miSocket.settimeout(1)
		self.miSocket.listen(2)
		print("Esperando conexion")
		while hilo:
			try:
				self.channel, details = self.miSocket.accept()
			except:
				pass
			else:
				self.channel.settimeout(1)
				self.channel.send("OK\n")
				print "OK enviado"
				print "Esperando recibir, hilo = ",hilo
				while hilo:
					try:
						texto1 = self.channel.recv(1024)
					except:
						pass
					else:
						self.entry_lat.set_text("Leyendo")
						self.entry_long.set_text("posicion")
						self.new_thread(self.guardar)
						self.buffer.insert_at_cursor("Recibido :"+texto1+"\n")
						print time.localtime(time.time())
						print "recibido", texto1
						if texto1 == "quit":
							break
		print "Cerrando el socket"
		self.miSocket.shutdown(self.miSocket)
		self.miSocket.close()
		
	def terminate(self):
		self.btn_stop.set_sensitive(False)
		self.btn_start.set_sensitive(True)
		global hilo
		hilo = False
		print hilo
		print "Terminate threads"

	def quit(self, widget):
		gtk.main_quit()
		self.terminate()

	def btn_test_click(self, widget):
		print "gtkMain thread"
		a = "-17.110203"
		b = "-11.236441"
		self.entry_lat.set_text(a)
		self.entry_long.set_text(b)
		db = MySQLdb.connect(host='localhost',user='root',passwd='menorah', db='GPS')
		cursor = db.cursor()
		print str(a)+"  "+str(b)
		sql = 'INSERT INTO  `GPS`.`Prueba` (`ID` ,`Hora` ,`Latitud` ,`Longitud`) VALUES (NULL , CURRENT_TIMESTAMP , %s,  %s);' % (a, b)
		cursor.execute(sql)
						

	def btn_stop_click(self, widget):
		self.terminate()

	def new_thread(self, method):
		t = threading.Thread(target=method, args=())
		t.start()

	def btn_start_click(self, widget):
		print "Start threads"
		global hilo
		hilo = True
		self.btn_stop.set_sensitive(True)
		widget.set_sensitive(False)
		self.new_thread(self.exec_cmd)

	def new_thread_args(self, method, arg):
		t = threading.Thread(target=method, args=(arg))
		t.start()
	
	def guardar(self):
		global texto1
		print texto1
		coor = texto1.split(",")
		if coor[0] == "POS":
			if coor[2] == 'N':
				latsign = 1
			else:
				latsign = -1
			lat = Decimal(coor[1])*latsign/100
			if coor[4] == 'E':
				lonsign = 1
			else:
				lonsign = -1
			long = Decimal(coor[3])*lonsign/100
			self.entry_lat.set_text(str(lat))
			self.entry_long.set_text(str(long))
			db = MySQLdb.connect(host='localhost',user='root',passwd='menorah', db='GPS')
			cursor = db.cursor()
			sql = 'INSERT INTO  `GPS`.`Prueba` (`ID` ,`Hora` ,`Latitud` ,`Longitud`) VALUES (NULL , CURRENT_TIMESTAMP , %s,  %s);' % (lat, long)
			cursor.execute(sql)

	def load(self, url):
		self.webview.open(url)
		self.webview.show

	def open(self, url):
		self.load(url)
	


	def seguir_toggle(self, widget):
		check = self.seguir.get_active()
		if check:
			url = 'http://localhost/GPS/index.php'
		else:
			url = 'http://localhost/GPS/index2.php'
		self.open(url)
		

if __name__ == "__main__":
	gtk.gdk.threads_init()
	gui = MainWin()
	gui.open(DEFAULT_URL)
	gtk.main()
