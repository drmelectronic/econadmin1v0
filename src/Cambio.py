#! /usr/bin/python
#! -*- encoding: utf8 -*-

import gtk
import Consultas
import datetime
from decimal import Decimal
import Estilos

__author__="danielypamela"
__date__ ="$07-nov-2011 15:16:07$"


class Ventana(gtk.Window):
	def __init__(self,consulta):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = consulta.cursor
		self.set_title("Tipos de Cambio")
		self.vbox_main = gtk.VBox(False,0)
		self.add(self.vbox_main)
		hbox_main = gtk.HBox(False,0)
		self.vbox_main.pack_start(hbox_main)
		label_year = gtk.Label('Año:')
		hbox_main.pack_start(label_year)
		adjustment_year = gtk.Adjustment(datetime.date.today().year,2011,2020,1,1,0)
		self.spin_year = gtk.SpinButton(adjustment_year)
		hbox_main.pack_start(self.spin_year)
		label_mes = gtk.Label('Mes:')
		hbox_main.pack_start(label_mes)
		adjustment_mes = gtk.Adjustment(datetime.date.today().month-1,1,12,1,1,0)
		self.spin_mes = gtk.SpinButton(adjustment_mes)
		self.spin_mes.set_wrap(True)
		self.spin_mes.connect('wrapped',self.mes_wrap)
		self.spin_year.connect('value-changed',self.spin_change)
		self.spin_mes.connect('value-changed',self.spin_change)
		hbox_main.pack_start(self.spin_mes)
		self.tabla = gtk.Table(7,6,True)
		self.vbox_main.pack_start(self.tabla)
		self.dias_mes = (31,28,31,30,31,30,31,31,30,31,30,31)
		self.spin_change()
		self.show_all()

	def spin_change(self,spin=None):
		self.vbox_main.remove(self.tabla)
		self.tabla = gtk.Table(7,7,True)
		self.mes = self.spin_mes.get_value_as_int()
		self.year = self.spin_year.get_value_as_int()
		dias = ('Lunes', 'Martes','Miércoles','Jueves','Viernes','Sábado','Domingo')
		for dia in enumerate(dias):
			eb = gtk.EventBox()
			eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
			eb.set_size_request(80,25)
			label = gtk.Label()
			label.set_markup("<span foreground='#FFFFFF'><b>%s</b></span>"%dia[1])
			eb.add(label)
			self.tabla.attach(eb,dia[0],dia[0]+1,0,1)
		self.dias = self.dias_mes[self.mes-1]
		if self.year%4 == 0 and self.mes == 2:
			self.dias = 29
		y = 1
		self.entry_dia = [None]*self.dias
		for dia in range(self.dias):
			d = datetime.date(self.year,self.mes,dia+1)
			x = d.weekday()
			vbox = gtk.VBox(True,0)
			label = gtk.Label()
			vbox.pack_start(label)
			self.entry_dia[dia] = gtk.Entry(5)
			self.entry_dia[dia].set_size_request(80,25)
			self.entry_dia[dia].connect('activate',self.enter,dia+1,x)
			fecha = datetime.date(self.year,self.mes,dia+1)
			sql = "SELECT VALOR FROM cambio WHERE DIA='%s'"%fecha
			self.cursor.execute(sql)
			if self.cursor.rowcount != 0:
				valor = self.cursor.fetchone()
				self.entry_dia[dia].set_text(str(valor[0]))
			vbox.pack_start(self.entry_dia[dia])
			if x == 6 or x == 0:
				label.set_markup("<span foreground='#FF0000'><b>%d</b></span>"%(dia+1))
				self.entry_dia[dia].set_sensitive(False)
				if dia == 0 or dia == 1:
				  anterior = self.mes-1
				  if anterior == 0:
				    p = str(self.year-1)+'-12-%'
				  else:
				    p = str(self.year)+'-'+str(anterior).zfill(2)+'-%'
				  sql = "SELECT VALOR FROM cambio WHERE DIA LIKE '%s' ORDER BY DIA DESC LIMIT 1"%p
				  print sql
				  self.cursor.execute(sql)
				  valor = self.cursor.fetchone()[0]
				  self.entry_dia[dia].set_text(str(valor))
			else:
				label.set_markup("<span foreground='#0000FF'><b>%d</b></span>"%(dia+1))
				self.ultimo = dia+1
			self.tabla.attach(vbox,x,x+1,y,y+1)
			if x == 6:
				y +=1
		self.vbox_main.pack_start(self.tabla)
		self.tabla.show_all()
		self.set_focus(self.entry_dia[0])

	def enter(self,widget,dia,x):
		texto = widget.get_text()
		try:
			cambio = Decimal(texto)
		except:
			widget.set_text('')
		else:
			print self.ultimo
			print dia
			if x == 5:
				try:
					self.entry_dia[dia].set_text(texto)
					self.entry_dia[dia+1].set_text(texto)
				except:
					pass
			if self.ultimo == dia:
				self.guardar()
			else:
				self.do_move_focus(self,gtk.DIR_TAB_FORWARD)

	def guardar(self):
		sql = "DELETE FROM cambio WHERE YEAR(DIA)=%d AND MONTH(DIA)= %d"%(self.year,self.mes)
		self.cursor.execute(sql)
		for i,entry in enumerate(self.entry_dia):
			dia = i+1
			fecha = datetime.date(self.year,self.mes,dia)
			sql = "INSERT INTO cambio (DIA,VALOR) VALUES('%s',%s)"%(fecha,entry.get_text())
			self.cursor.execute(sql)
		Estilos.Alerta('Mes Guardado','El tipo de cambio ha sido guardado\ncorrectamente.')

	def mes_wrap(self,spin):
		if spin.get_value_as_int() == 1:
			self.spin_year.spin(gtk.SPIN_STEP_FORWARD,1)
		else:
			self.spin_year.spin(gtk.SPIN_STEP_BACKWARD,1)

if __name__ == '__main__':
	consulta = Consultas.Conectar()
	v = Ventana(consulta)
	gtk.main()
