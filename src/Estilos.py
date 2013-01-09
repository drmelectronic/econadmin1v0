#! /usr/bin/python
# -*- encoding: utf8 -*-

# To change this template, choose Tools | Templates
# and open the template in the editor.
import gtk
import time
import datetime
import calendar
from weakref import *
import inspect
from decimal import Decimal
import threading
from reportlab.pdfgen import canvas
import pygst
import sys, gst, gobject
import os
import Proveedores
import pynotify
pynotify.init('pynotify')

__author__="econain"
__date__ ="$01/06/2011 12:22:02 PM$"

def notify(title,text):
		notify = pynotify.Notification(title,text,"pynotify")
		notify.set_urgency(pynotify.URGENCY_NORMAL)
		notify.set_timeout(5000)
		notify.show()

class DialogOC(gtk.Dialog):
	def __init__(self):
		gtk.Dialog.__init__(self)
		self.set_title('Nueva Orden de Compra')
		tabla = gtk.Table(3,2)
		self.vbox.pack_start(tabla)
		label = gtk.Label('Archivo')
		tabla.attach(label,0,1,0,1)
		label = gtk.Label('Código')
		tabla.attach(label,0,1,1,2)
		self.entry_cod = gtk.Entry()
		tabla.attach(self.entry_cod,1,3,1,2)
		self.entry_file = gtk.Entry()
		self.entry_file.set_editable(False)
		tabla.attach(self.entry_file,1,2,0,1)
		self.but_ex = MiBoton('../images/PNG-16/Search.png',None)
		tabla.attach(self.but_ex,2,3,0,1)
		self.but_ex.connect('clicked',self.examinar)
		self.but_ok = MiBoton('../images/PNG-16/Check.png','OK')
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.show_all()

	def examinar(self,widget):
		dialog = gtk.FileChooserDialog("Open..",
                               self,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.gif")
		filter.add_pattern("*.tif")
		filter.add_pattern("*.xpm")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("PDF")
		filter.add_pattern("*.pdf")
		filter.add_pattern("*.ps")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			path = dialog.get_filename()
			self.entry_file.set_text(path)
                        os.system("""gnome-open '%s'"""%(path))
		dialog.destroy()

	def cerrar(self):
		self.destroy()

class Alerta(gtk.Dialog):
	def __init__(self,titulo,mensaje):
		gtk.Dialog.__init__(self)
		self.set_title(titulo)
		label = gtk.Label(mensaje)
		self.vbox.pack_start(label)
		self.but_ok = MiBoton('../images/PNG-16/Check.png','OK')
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.show_all()

class Contra(gtk.Dialog):
	def __init__(self):
		gtk.Dialog.__init__(self)
		self.set_title('Autenticación de Usuario')
		label = gtk.Label("Ingrese su contraseña")
		self.vbox.pack_start(label)
		self.entry = gtk.Entry()
		self.vbox.pack_start(self.entry)
		self.entry.set_property('caps-lock-warning',True)
		self.entry.set_property('visibility',False)
		self.but_ok = gtk.Button()
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.entry.connect('activate',self.enter)
		self.show_all()
		self.but_ok.hide()

	def enter(self,widget):
		self.psw = self.entry.get_text()
		self.but_ok.clicked()

class EntryRUC(gtk.Entry):
	__gsignals__ = {
		"nuevo": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		"ok" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}
	def __init__(self,cursor):
		gtk.Entry.__init__(self)
		self.cursor = cursor
		self.connect('key-release-event',self.teclas)
		self.razon = "Error"
		self.id = 0
		self.tipo = 0

	def teclas(self,widget=None,event=None):
		if len(self.get_text())==11:
			try:
				ruc = int(self.get_text())
			except:
				self.set_text('')
			else:
				sql = "SELECT COMERCIAL,ID,TIPO,MONEDA FROM proveedores WHERE RUC=%d"%ruc
				self.cursor.execute(sql)
				if self.cursor.rowcount == 0:
					nueva = Proveedores.Nueva(self.cursor)
					nueva.entry_ruc.set_text(str(ruc))
					if nueva.run() == gtk.RESPONSE_OK:
						nueva.guardar()
						window.do_move_focus(window,gtk.DIR_TAB_FORWARD)
						window.do_move_focus(window,gtk.DIR_TAB_FORWARD)
						self.emit('ok')
					else:
						self.set_text('')
					nueva.cerrar()
				else:
					self.razon,self.id,self.tipo,self.moneda = self.cursor.fetchone()
					window = self.get_toplevel()
					window.do_move_focus(window,gtk.DIR_TAB_FORWARD)
					window.do_move_focus(window,gtk.DIR_TAB_FORWARD)
					self.emit('ok')

class EntryDia(gtk.Entry):
	def __init__(self,cursor,entry):
		gtk.Entry.__init__(self)
		self.cursor = cursor
		self.connect('key-release-event',self.teclas)
		self.connect('activate',self.enter)
		self.entry = entry
		self.fecha = datetime.date.today().strftime("%Y-%m-%d")
		sql = "SELECT VALOR FROM cambio WHERE DIA='%s'"%self.fecha
		self.cursor.execute(sql)
		if self.cursor.rowcount==0:
			self.tk = 'Error'
		else:
			self.tk = self.cursor.fetchone()[0]

	def teclas(self,widget,event):
		periodo = self.entry.get_text()
		self.year = int(periodo.split('-')[0])
		self.mes = int(periodo.split('-')[1])
		texto = widget.get_text()
		partes = texto.split('-')
		if len(partes) == 1:
			try:
				dia = int(texto)
			except:
				return
			else:
				self.fecha = datetime.date(self.year,self.mes,dia).strftime("%Y-%m-%d")
		elif len(partes) == 2:
			try:
				dia = int(partes[0])
				mes = int(partes[1])
			except:
				return
			else:
				self.fecha = datetime.date(self.year,mes,dia).strftime("%Y-%m-%d")
		elif len(partes) == 3:
			try:
				dia = int(partes[0])
				mes = int(partes[1])
				year = int(partes[2])
			except:
				return
			else:
				if year <= 1900:
					year+=2000
				self.fecha = datetime.date(year,mes,dia).strftime("%Y-%m-%d")
		sql = "SELECT VALOR FROM cambio WHERE DIA='%s'"%self.fecha
		self.cursor.execute(sql)
		if self.cursor.rowcount==0:
			self.tk = 'Error'
		else:
			self.tk = self.cursor.fetchone()[0]

	def enter(self,widget):
		window = self.get_toplevel()
		window.do_move_focus(window,gtk.DIR_TAB_FORWARD)

class EntryPeriodo(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__ (self, False, 2)
		self.entry = gtk.Entry()
		self.entry.set_size_request(70,25)
		dia = datetime.date.today()
		self.entry.set_text(dia.strftime("%Y-%m"))
		self.entry.set_editable(False)
		adjustment_year = gtk.Adjustment(datetime.date.today().year,2011,2020,1,1,0)
		self.spin_y = gtk.SpinButton(adjustment_year)
		adjustment_mes = gtk.Adjustment(datetime.date.today().month,1,12,1,1,0)
		self.spin_m = gtk.SpinButton(adjustment_mes)
		self.spin_m.set_wrap (True)
		self.pack_start(self.entry, False, False, 0)
		self.spin_m.connect('wrapped',self.wrap_mes)
		self.entry.connect('scroll-event',self.spin_mouse)
		self.entry.connect('activate',self.on_enter)
		self.entry.connect_after('key-press-event',self.key_press)
		self.entry.connect_after('key-release-event',self.spin_key)
		self.entry.select_region(5,7)
		self.posicion = 5

	def on_enter(self,widget):
		value = widget.get_text()
		lst = value.split ('-')
		self.spin_m.set_value (int(lst[1]))
		self.spin_y.set_value (int(lst[0]))

	def key_press(self,widget,event):
		if event.keyval == 65362 or event.keyval == 65364:
			return True

	def spin_key(self,widget,event):
		if event.keyval == 65361: #izquierda
			widget.select_region(0,4)
			return True
		elif event.keyval == 65363: #derecha
			widget.select_region(5,7)
			return True
		elif event.keyval == 65362: #arriba
			self.posicion = self.entry.get_property('cursor-position')
			if self.posicion>4:
				self.spin_m.spin(gtk.SPIN_STEP_FORWARD)
			else:
				self.spin_y.spin(gtk.SPIN_STEP_FORWARD)
			self.update()
			return True
		elif event.keyval == 65364: #abajo
			self.posicion = self.entry.get_property('cursor-position')
			if self.posicion>4:
				self.spin_m.spin(gtk.SPIN_STEP_BACKWARD)
			else:
				self.spin_y.spin(gtk.SPIN_STEP_BACKWARD)
			self.update()
			return True
		elif 48<=event.keyval and event.keyval<=57: #numeros
				self.on_enter(widget)

	def spin_mouse(self,widget,event):
		if event.direction== gtk.gdk.SCROLL_UP:
			self.spin_m.spin(gtk.SPIN_STEP_FORWARD)
			self.update()
		elif event.direction== gtk.gdk.SCROLL_DOWN:
			self.spin_m.spin(gtk.SPIN_STEP_BACKWARD)
			self.update()

	def update(self):
		self.entry.set_text(str(self.spin_y.get_value_as_int())+'-'+str(self.spin_m.get_value_as_int()).zfill(2))
		if self.posicion>4:
			self.entry.select_region(5,7)
		else:
			self.entry.select_region(0,4)

	def wrap_mes(self,spin):
		if self.spin_m.get_value_as_int() == 1:
			self.spin_y.spin(gtk.SPIN_STEP_FORWARD)
		else:
			self.spin_y.spin(gtk.SPIN_STEP_BACKWARD)

	def set_text(self, value):
		lst = value.split ('-')
		self.spin_m.set_value (float(lst[1]))
		self.spin_y.set_value (float(lst[0]))
		self.update()

	def get_text(self):
		return self.entry.get_text()

	def set_periodo(self, value):
		value = value.strftime("%Y-%m")
		lst = value.split ('-')
		self.spin_m.set_value (float(lst[1]))
		self.spin_y.set_value (float(lst[0]))
		self.update()

	def get_time(self):
		return datetime.timedelta(0,(self.spin_h.get_value_as_int()*60+self.spin_m.get_value_as_int())*60)

class MiBoton(gtk.Button):
	def __init__(self, file, string):
		gtk.Button.__init__(self)
		hbox = gtk.HBox(False, 0)
		imagen = gtk.Image()
		imagen.set_from_file(file)
		hbox.pack_start(imagen)
		self.label = gtk.Label()
		if not string == None:
			self.label.set_text(string)
			self.label.set_use_underline(True)
			hbox.pack_start(self.label)
		self.add(hbox)

class ToggleBoton(gtk.ToggleButton):
	def __init__(self, file, string):
		gtk.ToggleButton.__init__(self)
		hbox = gtk.HBox(False, 0)
		imagen = gtk.Image()
		imagen.set_from_file(file)
		hbox.pack_start(imagen)
		self.label = gtk.Label()
		if not string == None:
			self.label.set_text(string)
			self.label.set_use_underline(True)
			hbox.pack_start(self.label)
		self.add(hbox)

class ComboButton(gtk.ComboBox):
	def __init__(self, cursor):
		self.cursor = cursor
		self.lista = gtk.ListStore(int,str)
		self.lista.append((0,''))
		gtk.ComboBox.__init__(self,self.lista)
		cell = gtk.CellRendererText()
		self.pack_start(cell,True)
		self.add_attribute(cell,'text',1)
		self.set_size_request(75,30)
		item = self.lista.get_iter(0)
		self.set_active_iter(item)

	def items(self,lista):
		self.diccionario = {}
		self.lista.clear()
		i = 0
		for item in lista:
			self.diccionario[item[0]] = i
			self.lista.append(item)
			i += 1

	def sql(self,sql,espacio=True):
		self.diccionario = {}
		self.cursor.execute(sql)
		lista =self.cursor.fetchall()
		self.lista.clear()
		i = 0
		if espacio:
			self.diccionario[0]=i
			self.lista.append((0,''))
			i += 1
			self.set_id(0)
		for item in lista:
			self.diccionario[item[0]] = i
			self.lista.append(item)
			i+= 1

	def set_id(self,id):
		path = self.diccionario[id]
		self.set_active(path)

	def get_id(self):
		path = self.get_active()
		return self.lista[path][0]

	def get_text(self):
		path = self.get_active()
		return self.lista[path][1]

class DialogSN(gtk.Dialog):
	def __init__(self, titulo, mensaje):
		gtk.Dialog.__init__(self)
		self.set_default_size(120,80)
		self.set_title(titulo)
		self.set_position(gtk.WIN_POS_CENTER)
		label = gtk.Label(mensaje)
		self.vbox.pack_start(label)
		but_si = MiBoton("../images/PNG-24/Check.png","_Sí")
		but_no = MiBoton("../images/PNG-24/Delete.png","_No")
                self.add_action_widget(but_si,gtk.RESPONSE_OK)
                self.add_action_widget(but_no,gtk.RESPONSE_CANCEL)
		self.show_all()

class Completion(gtk.Entry):
	__gsignals__ = {
		'nuevo'	:	(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'antiguo'	:	(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}

	def __init__(self,cursor,tabla):
		gtk.Entry.__init__(self)
		lista = gtk.ListStore(int,str)
		self.tabla = tabla
		self.cursor = cursor
		cursor.execute("SELECT ID,NOMBRE FROM %s"%self.tabla)
		result = cursor.fetchall()
		self.diccionario = {'':0}
		self.antidiccionario = {0:''}
		for row in result:
			self.diccionario[str(row[1])] = row[0]
			self.antidiccionario[row[0]] = str(row[1])
			lista.append(row)
		self.completion = gtk.EntryCompletion()
                self.completion.set_match_func(self.funcion_completion)
		self.completion.set_model(lista)
		self.completion.set_minimum_key_length(2)
		self.completion.set_text_column(1)
		self.set_completion(self.completion)
		self.connect('changed',self.consultar)
		self.nuevo = False
                
        def funcion_completion(self,completion,string,iter):
          model = completion.get_model()
          texto = model[iter][1].lower()
          result = texto.find(string)
          if result==-1:
            return False
          return True
                  
        def cambiar_tabla(self,tabla):
                self.cursor.execute("SELECT ID,NOMBRE FROM %s"%tabla)
		lista = gtk.ListStore(int,str)
		result = self.cursor.fetchall()
		self.diccionario = {'':0}
		self.antidiccionario = {0:''}
		for row in result:
			self.diccionario[str(row[1])] = row[0]
			self.antidiccionario[row[0]] = str(row[1])
			lista.append(row)
		self.completion.set_model(lista)
                
	def filtrar(self,columna,id,default=False):
		lista = gtk.ListStore(int,str)
		sql = "SELECT ID,NOMBRE FROM %s WHERE %s=%d"%(self.tabla,columna,id)
		if default:
			sql += ' OR %s=0'%columna
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		self.diccionario = {'':0}
		self.antidiccionario = {0:''}
		for row in result:
			self.diccionario[str(row[1])] = row[0]
			self.antidiccionario[row[0]] = str(row[1])
			lista.append(row)
		self.completion.set_model(lista)
		self.set_completion(self.completion)

	def consultar(self,widget):
		texto = self.get_text()
		try:
			id = self.diccionario[texto]
		except:
			self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse('#CCCCCC'))
			self.nuevo = True
			self.emit('nuevo')
		else:
			self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse('#FFFFFF'))
			self.nuevo = False
			self.emit('antiguo')

	def set_id(self,id):
		texto = self.antidiccionario[id]
		self.set_text(texto)

	def get_id(self,save=True):
		texto = self.get_text()
		if not save:
			return texto
		if self.nuevo:
			print "INSERT INTO %s (NOMBRE) VALUES (%s)"%(self.tabla,texto)
			self.cursor.execute("INSERT INTO %s (NOMBRE) VALUES ('%s')"%(self.tabla,texto))
			self.cursor.execute("SELECT ID FROM %s ORDER BY ID DESC"%self.tabla)
			id = self.cursor.fetchone()[0]
		else:
			id = self.diccionario[texto]
		return id
	      
class CompletionVehiculo(Completion):
      def get_id(self,save,empresa):
		texto = self.get_text()
		if not save:
			return texto
		if self.nuevo:
			self.cursor.execute("INSERT INTO %s (NOMBRE,EMPRESA) VALUES ('%s',%d)"%(self.tabla,texto,empresa))
			self.cursor.execute("SELECT ID FROM %s ORDER BY ID DESC"%self.tabla)
			id = self.cursor.fetchone()[0]
		else:
			id = self.diccionario[texto]
		return id

class Fecha (gtk.Button):
	__gsignals__ = {
			"changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
		"cambio" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}
	def __init__ (self,w):
		gtk.Button.__init__ (self)
		self.calendar = gtk.Calendar()
		self.set_size_request(90,30)
		self.cwindow = gtk.Dialog()
		self.ok = gtk.Button()
		self.cwindow.add_action_widget(self.ok,gtk.RESPONSE_OK)
		self.cwindow.set_position (gtk.WIN_POS_MOUSE)
		self.cwindow.set_decorated (False)
		self.cwindow.set_modal (False)
		self.eb = gtk.EventBox()
		self.eb.add(self.calendar)
		self.cwindow.vbox.pack_start(self.eb)
		self.currentDate = datetime.date.today()
		y,self.month,day = self.calendar.get_date()
		self.__connect_signals ()
		self.day = 0
		self.entro = False
		self.update_entry ()

	def __connect_signals (self):
		self.day_selected_handle = self.calendar.connect ("day-selected", self.day_selected)
		self.clicked_handle = self.connect ("clicked", self.show_widget)

	def day_selected(self,widget):
		year,month,day = self.calendar.get_date()
		if month == self.month:
			self.month = month
			self.ok.clicked()
		else:
			self.month = month

	def get_text (self):
		return self.get_label()

	def close(self,widget,context):
		year,month,day = self.calendar.get_date ()
		if day != self.day:
			self.hide_widget()
		self.day = day
		self.emit ("changed", self.currentDate)

	def update_entry (self, *args):
		year,month,day = self.calendar.get_date ()
		month = month +1;
		self.currentDate = datetime.date(year, month, day)
		text = self.currentDate.strftime ("%d/%m/%Y")
		self.set_label(text)
                self.emit ("cambio")

	def get_date (self):
		return self.currentDate

	def set_date(self,date):
		self.set_label(date.strftime("%d/%m/%Y"))

	def show_widget (self, *args):
		self.cwindow.show_all()
		self.ok.hide()
		if self.cwindow.run() == gtk.RESPONSE_OK:
			self.update_entry()
		self.hide_widget()

	def hide_widget (self, *args):
		self.cwindow.hide_all()

	def focus_out_event (self, widget, event):
		self.hide_widget()

class Hora(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__ (self, False, 2)
		self.hora = gtk.Entry()
		self.hora.set_size_request(45,25)
		self.hora.set_text('00:00')
		self.spin_h = gtk.SpinButton (digits=0)
		self.spin_m = gtk.SpinButton (digits=0)
		self.spin_h.set_range (0, 23)
		self.spin_m.set_range (0, 59)
		self.spin_h.set_increments (1, 2)
		self.spin_m.set_increments (1, 2)
		self.spin_h.set_wrap (True)
		self.spin_m.set_wrap (True)
		self.pack_start (self.hora, False, False, 0)
		self.spin_m.connect('wrapped',self.wrap_min)
		self.hora.connect('scroll-event',self.spin_mouse)
		self.hora.connect('activate',self.on_enter)
		self.hora.connect_after('key-press-event',self.key_press)
		self.hora.connect_after('key-release-event',self.spin_key)
		self.hora.select_region(3,5)
		self.posicion = 5

	def on_enter(self,widget):
		value = widget.get_text()
		lst = value.split (':')
		self.spin_m.set_value (float(lst[1]))
		self.spin_h.set_value (float(lst[0]))

	def key_press(self,widget,event):
		if event.keyval == 65362 or event.keyval == 65364:
			return True

	def spin_key(self,widget,event):
		if event.keyval == 65361:
			widget.select_region(0,2)
			return True
		elif event.keyval == 65363:
			widget.select_region(3,5)
			return True
		elif event.keyval == 65362:
			self.posicion = self.hora.get_property('cursor-position')
			if self.posicion>2:
				self.spin_m.spin(gtk.SPIN_STEP_FORWARD)
			else:
				self.spin_h.spin(gtk.SPIN_STEP_FORWARD)
			self.update()
			return True
		elif event.keyval == 65364:
			self.posicion = self.hora.get_property('cursor-position')
			if self.posicion>2:
				self.spin_m.spin(gtk.SPIN_STEP_BACKWARD)
			else:
				self.spin_h.spin(gtk.SPIN_STEP_BACKWARD)
			self.update()
			return True
		elif 48<=event.keyval and event.keyval<=57:
				self.on_enter(widget)

	def spin_mouse(self,widget,event):
		if event.direction== gtk.gdk.SCROLL_UP:
			self.spin_m.spin(gtk.SPIN_STEP_FORWARD)
			self.update()
		elif event.direction== gtk.gdk.SCROLL_DOWN:
			self.spin_m.spin(gtk.SPIN_STEP_BACKWARD)
			self.update()

	def update(self):
		self.hora.set_text(str(self.spin_h.get_value_as_int()).zfill(2)+':'+str(self.spin_m.get_value_as_int()).zfill(2))
		if self.posicion>2:
			self.hora.select_region(3,5)
		else:
			self.hora.select_region(0,2)

	def wrap_min(self,spin):
		if self.spin_m.get_value_as_int() == 0:
			self.spin_h.spin(gtk.SPIN_STEP_FORWARD)
		else:
			self.spin_h.spin(gtk.SPIN_STEP_BACKWARD)

	def set_text(self, value):
		lst = value.split (':')
		self.spin_m.set_value (float(lst[1]))
		self.spin_h.set_value (float(lst[0]))
		self.update()

	def get_text(self):
		return self.hora.get_text()

	def set_time(self, value):
		value = str(value)
		lst = value.split (':')
		self.spin_m.set_value (float(lst[1]))
		self.spin_h.set_value (float(lst[0]))
		self.update()

	def get_time(self):
		return datetime.timedelta(0,(self.spin_h.get_value_as_int()*60+self.spin_m.get_value_as_int())*60)

class TextHTML(gtk.TextView):
	def __init__(self):
		gtk.TextView.__init__(self)
		self.buffer = self.get_buffer()

	def codificar(self):
		texto = """<table class="item"><col width= 5><col width= 5><col>"""
		lineas = self.buffer.get_line_count()
		for i in range(lineas):
			inicio = self.buffer.get_iter_at_line(i)
			if i == lineas-1:
				fin = self.buffer.get_end_iter()
			else:
				fin = self.buffer.get_iter_at_line(i+1)
			linea = str(self.buffer.get_text(inicio,fin,False))
			if i != lineas-1:
				linea = linea[:-1]
			if i == 0:
				texto = texto+"""<tr valign=top><td colspan=3><b>%s</b></td></tr></tr>"""%linea
			else:
				try:
					p = linea[0]
				except:
					texto = texto+'<tr><td colspan=3></td></tr>'
				else:
					if linea[0]==' ':
						while linea[0]==' ':
							linea = linea[1:]
						if "-" == linea[0]:
							linea = linea[1:]
							while linea[0]==' ':
								linea = linea[1:]
							texto = texto+"""<tr><td>-</td><td colspan=2>%s</td></tr>"""%linea
						else:
							tabs = linea.split(':')
							if len(tabs) == 2:
								texto = texto+"""<tr><td></td><td>%s:</td><td>%s</td></tr>"""%(tabs[0],tabs[1])
							else:
								texto = texto+"""<tr><td></td><td colspan=2>%s</td></tr>"""%tabs
					else:
							texto = texto+"""<tr valign=top><td colspan=3>%s</td></tr>"""%linea
		return texto+'</table>'

	def decodificar(self,html):
		lineas = html.split('</tr><tr')
		i = 0
		t = ""
		for linea in lineas:
			if i == 0:
				col = linea.split('<b>')
				linea = col[1].split('</b>')
				texto = linea[0]
			else:
				col = linea.split('</td>')
				if len(col) == 2:
					linea = col[0].split('3>')
					texto = linea[1].split('<')[0]
				if len(col) == 3:
					linea = col[1].split('2>')
					texto = ' - '+linea[1]
				if len(col) == 4:
					col1 = col[1].split('>')[1]
					col2 = col[2].split('>')[1]
					texto = ' '+col1+' '+col2
			t = t+texto+'\n'
			i += 1
		self.buffer.set_text(t[:-1])
			
class DialogoSN(gtk.Dialog):
	def __init__(self,titulo,mensaje):
		gtk.Dialog.__init__(self)
		self.set_title(titulo)
		self.vbox.pack_start(gtk.Label(mensaje))
		but_ok = MiBoton('../images/PNG-16/Check.png','Sí')
		but_cancel = MiBoton('../images/PNG-16/Exit.png','No')
		self.add_action_widget(but_ok,gtk.RESPONSE_OK)
		self.add_action_widget(but_cancel,gtk.RESPONSE_CANCEL)
		self.show_all()

	def cerrar(self):
		self.destroy()
		del self

if __name__ == '__main__':
	c = TextHTML()
	t = """Mantenimiento de Microcentrífuga Refrigerada de Laboratorio
 Marca: EPPENDORF
 Modelo: 5415R
 - Mantenimiento Integral.
 - Fabricación de retén inoxidable del eje de motor.
 - Niquelado de base de soporte de motor.
 - Reanodizado de rotor."""
	c.buffer.set_text(t)
	c.codificar()
	gtk.main()
