#!/usr/bin/env python
#! -*- encoding: utf8 -*-
import gtk
import Estilos
import Consultas
import datetime
import gobject
from decimal import Decimal
import webkit
import os
import Impresion

class Ventana(gtk.Window):
	""" Clase Ventana Principal """
	def __init__ (self,consulta):
		""" Class initialiser """
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = consulta.cursor
		self.host = consulta.www
		self.set_title("Cheques")
		hbox_main = gtk.HBox(True,0)
		vbox_main = gtk.VBox(False,0)
		hbox_main.pack_start(vbox_main)
		self.vbox_www = gtk.VBox()
		hbox_main.pack_start(self.vbox_www)
		sw_www = gtk.ScrolledWindow()
		sw_www.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		sw_www.set_size_request(300,500)
		hbox_www = gtk.HBox()
		self.vbox_www.pack_start(hbox_www)
		self.but_print = Estilos.MiBoton('../images/PNG-16/Print.png','Imprimir')
                self.combo_cuenta = Estilos.ComboButton(self.cursor)
                self.combo_cuenta.sql("SELECT cuentascorr.ID,CONCAT(BANCO,'/',monedas.NOMBRE) FROM cuentascorr JOIN monedas ON monedas.ID = cuentascorr.MONEDA",1)
                self.combo_cuenta.set_id(0)
		hbox_www.pack_start(self.but_print)
                hbox_www.pack_start(self.combo_cuenta)
		self.but_print.connect('clicked',self.imprimir)
		self.combo_cuenta.connect('changed',self.buscar)
		self.vbox_www.pack_start(sw_www)
		self.www = webkit.WebView()
		self.www_frame = self.www.get_main_frame()
		sw_www.add(self.www)
		self.add(hbox_main)
		tabla_controles = gtk.Table(4,5,False)
		vbox_main.pack_start(tabla_controles,False,False,0)
		label_buscar = gtk.Label("Buscar:")
		tabla_controles.attach(label_buscar,0,1,0,1)
		self.entry_buscar = gtk.Entry()
		tabla_controles.attach(self.entry_buscar,1,2,0,1)
		self.but_editar = Estilos.MiBoton("../images/PNG-16/Load.png","Editar")
		tabla_controles.attach(self.but_editar,3,4,0,1)
		but_nuevo = Estilos.MiBoton("../images/PNG-16/Add.png","Nuevo")
		tabla_controles.attach(but_nuevo,4,5,0,1)
		columnas = ("CÓDIGO","GIRO","DESDE","MONTO","NOMBRE")#id, anulado,color,IMPRESO
		self.model = gtk.ListStore(str,str,str,str,str,int,int,str,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name)
                        column.pack_start(renderer,True)
                        column.set_attributes(renderer,markup=i,cell_background=7)
			self.treeview.append_column(column)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(550,300)
		vbox_main.pack_start(sw)
		sw.add(self.treeview)
		self.show_all()

		self.entry_buscar.connect('changed',self.buscar)
		self.treeview.connect('row-activated',self.on_row_activated)
		self.treeview.connect('cursor_changed',self.on_cursor)
		but_nuevo.connect('clicked',self.nuevo)
		self.but_editar.connect('clicked',self.on_editar)

		self.buscar()
		self.treeview.set_cursor(0)

	def on_cursor(self,widget):
		path, column = self.treeview.get_cursor()
		try:
			enviado = self.model[path][8]
		except:
			self.but_editar.set_sensitive(False)
		else:
			self.but_editar.set_sensitive(True)
			if enviado:
				self.but_editar.label.set_text('Copiar')
                                self.but_print.set_sensitive(False)
                        else:
				self.but_editar.label.set_text('Editar')
                                self.but_print.set_sensitive(True)
		url = 'http://%s/econadmin/images/factura.png'%(self.host)
		self.www.open(url)

	def buscar(self,widget=None):
		self.model.clear()
		texto = self.entry_buscar.get_text()
                cuenta = self.combo_cuenta.get_id()
		if texto == "":
                  if cuenta != 0:
                    txt = "WHERE CUENTA=%d"%cuenta
                  else:
                    txt = ''
                  sql = "SELECT CODIGO,GIRO,DESDE,MONTO,NOMBRE,ID,ANULADO,IMPRESO FROM cheques %s ORDER BY CODIGO DESC LIMIT 100"%txt
		else:
                  if cuenta != 0:
                    txt = "AND CUENTA=%d"%cuenta
                  else:
                    txt = ''
                  sql = "SELECT CODIGO,GIRO,DESDE,MONTO,NOMBRE,ID,ANULADO,IMPRESO FROM cheques WHERE NOMBRE='%s' %s ORDER BY CODIGO DESC LIMIT 100"%('%'+texto+'%',txt)
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
                  if item[6]:
                    color = '#88FFFF'
                  else:
                    color = '#FFFFFF'
                  if not item[7]:#impreso
                    item = ('<b>'+str(item[0])+'</b>','<b>'+str(item[1])+'</b>','<b>'+str(item[2])+'</b>','<b>'+str(item[3])+'</b>','<b>'+str(item[4])+'</b>',item[5],item[6],color,item[7])
                  else:
                    item = (str(item[0]),str(item[1]),str(item[2]),str(item[3]),item[4],item[5],item[6],color,item[7])
                  self.model.append(item)
                        
	def on_editar(self,widget):
		path, column = self.treeview.get_cursor()
		self.on_row_activated(widget,int(path[0]),column)

	def on_row_activated(self,widget,path,column):
		impreso = self.model[path][8]
		self.abrir(impreso)

	def abrir(self,enviado):
		if enviado:
			self.copiar()
		else:
			self.editar()

	def imprimir(self,widget):
		path, column = self.treeview.get_cursor()
		try:
			path = int(path[0])
		except:
			return
		Impresion.Cheques(self.cursor,self.model[path][5])
                self.buscar()

	def copiar(self):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor,self.combo_cuenta.get_id())
		nueva.leer(self.model[int(path[0])][5])
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
		nueva.cerrar()
		self.buscar()

	def editar(self):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor,self.combo_cuenta.get_id())
		nueva.leer(self.model[int(path[0])][5])
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.actualizar()
		nueva.cerrar()
		self.buscar()

	def nuevo(self,widget):
		nueva = Nueva(self.cursor,self.combo_cuenta.get_id())
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
		nueva.cerrar()
		self.buscar()

class Nueva(gtk.Dialog):
	def __init__(self,cursor,cuenta):
		gtk.Dialog.__init__(self)
		self.cursor = cursor
		self.set_title("Nuevo Cheque")
		tabla_datos = gtk.Table(3,6,False)
		self.vbox.pack_start(tabla_datos)
                label_cuenta = gtk.Label("Cuenta:")
		tabla_datos.attach(label_cuenta,0,1,0,1)
		self.combo_cuenta= Estilos.ComboButton(self.cursor)
		self.combo_cuenta.sql("SELECT cuentascorr.ID,CONCAT(BANCO,'/',monedas.NOMBRE) FROM cuentascorr JOIN monedas ON monedas.ID = cuentascorr.MONEDA",0)
		tabla_datos.attach(self.combo_cuenta,1,3,0,1)
                if cuenta != 0:
                  self.combo_cuenta.set_id(cuenta)
		label_cod = gtk.Label("Código:")
		tabla_datos.attach(label_cod,0,1,1,2)
		self.entry_cod= gtk.Entry()
		self.entry_cod.set_text('1')
		tabla_datos.attach(self.entry_cod,1,3,1,2)
		label_fecha = gtk.Label('Fecha:')
		tabla_datos.attach(label_fecha,0,1,2,3)
		self.but_giro = Estilos.Fecha(label_fecha.get_window())
		self.but_giro.set_date(datetime.date.today())
		tabla_datos.attach(self.but_giro,1,2,2,3)
                self.but_desde = Estilos.Fecha(label_fecha.get_window())
		self.but_desde.set_date(datetime.date.today())
		tabla_datos.attach(self.but_desde,2,3,2,3)
                self.cursor.execute("SELECT CODIGO FROM cheques WHERE CUENTA=%d ORDER BY CODIGO DESC LIMIT 1"%cuenta)
		try:
			cod = self.cursor.fetchone()[0]+1
		except:
			cod = 1
		self.entry_cod.set_text(str(cod))
		label_tipo = gtk.Label("Tipo:")
		tabla_datos.attach(label_tipo,0,1,3,4)
		self.combo_tipo = Estilos.ComboButton(self.cursor)
		self.combo_tipo.items(((1,'Personal'),(2,'Contacto'),(3,'Proveedor')))
		tabla_datos.attach(self.combo_tipo,1,3,3,4)
                label_nombre = gtk.Label('Nombre:')
                tabla_datos.attach(label_nombre,0,1,4,5)
                self.combo_nombre = Estilos.Completion(self.cursor, 'personal')
                tabla_datos.attach(self.combo_nombre,1,3,4,5)
                label_monto = gtk.Label("Monto")
                tabla_datos.attach(label_monto,0,1,5,6)
                self.entry_monto = gtk.Entry()
                tabla_datos.attach(self.entry_monto,1,3,5,6)
                self.but_guardar = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		self.add_action_widget(self.but_guardar,gtk.RESPONSE_OK)
		self.combo_cuenta.connect('changed',self.cambio_cuenta)
                self.combo_tipo.connect('changed',self.cambio_tipo)
                self.but_giro.connect('cambio',self.cambio_giro)
                self.but_desde.connect('cambio',self.cambio_desde)
		self.cotiz = 0
		self.show_all()


	def guardar(self):
		#guardar cotizacion
		cod = self.entry_cod.get_text()
		cuenta = self.combo_cuenta.get_id()
		giro = self.but_giro.get_date()
                desde= self.but_desde.get_date()
		tipo = self.combo_tipo.get_id()
		idtipo = self.combo_nombre.get_id()
                sql = "SELECT NOMBRE FROM "
                nombre = self.combo_nombre.get_text()
                monto = self.entry_monto.get_text()
		columnas = "CODIGO,CUENTA,GIRO, DESDE,TIPO,IDTIPO, NOMBRE,MONTO,ANULADO"
		valores = "%s,%d,'%s', '%s',%d,%d, '%s','%s',0"%(cod,cuenta,giro, desde,tipo,idtipo, nombre,monto)
		sql = "INSERT INTO cheques (%s) VALUES (%s)"%(columnas,valores)
		self.cursor.execute(sql)

	def actualizar(self):
		cod = self.entry_cod.get_text()
		cuenta = self.combo_cuenta.get_id()
		giro = self.but_giro.get_date()
                desde= self.but_desde.get_date()
		tipo = self.combo_tipo.get_id()
		idtipo = self.combo_nombre.get_id()
                nombre = self.combo_nombre.get_text()
                monto = self.entry_monto.get_text()
		valores = (cod,cuenta,giro, desde,tipo,idtipo, nombre,monto,self.id)
		sql = "UPDATE cheques SET CODIGO=%s,CUENTA=%d,GIRO='%s',DESDE='%s',TIPO=%d,IDTIPO=%d,NOMBRE='%s',MONTO='%s' WHERE ID=%d"%valores
		print sql
		self.cursor.execute(sql)
		
	def copiar(self,id):
		self.id = id
                self.cursor.execute("SELECT CODIGO FROM cheques WHERE CUENTA=%d ORDER BY NUMERO DESC LIMIT 1"%cuenta)
		try:
			cod = self.cursor.fetchone()[0]+1
		except:
			cod = 1
		self.entry_cod.set_text(str(cod))
		sql = "SELECT CODIGO,CUENTA,GIRO, DESDE,TIPO,IDTIPO, NOMBRE,MONTO FROM cheques WHERE ID=%d"%id
		self.cursor.execute(sql)
		cod,cuenta,giro,desde,tipo,idtipo,nombre,monto = self.cursor.fetchone()
		self.entry_cod.set_text(str(cod))
                self.combo_cuenta.set_id(cuenta)
                self.but_giro.set_date(giro)
                self.but_desde.set_date(desde)
                self.combo_tipo.set_id(tipo)
                self.combo_nombre.set_id(idtipo)
                self.entry_monto.set_text(str(monto))

	def leer(self,id):
          	self.id = id
		sql = "SELECT CODIGO,CUENTA,GIRO, DESDE,TIPO,IDTIPO, NOMBRE,MONTO FROM cheques WHERE ID=%d"%id
		self.cursor.execute(sql)
		cod,cuenta,giro,desde,tipo,idtipo,nombre,monto = self.cursor.fetchone()
                self.combo_cuenta.set_id(cuenta)
                self.but_giro.set_date(giro)
                self.but_desde.set_date(desde)
                self.combo_tipo.set_id(tipo)
                self.combo_nombre.set_id(idtipo)
                self.entry_monto.set_text(str(monto))
		self.entry_cod.set_text(str(cod))

	def cambio_cuenta(self,widget):
            cuenta = widget.get_id()
            self.cursor.execute("SELECT CODIGO FROM cheques WHERE CUENTA=%d ORDER BY CODIGO DESC LIMIT 1"%cuenta)
            try:
		cod = self.cursor.fetchone()[0]+1
            except:
		cod = 1
            self.entry_cod.set_text(str(cod))
		
	def cambio_tipo(self,widget):
            id = widget.get_id()
            if id == 1:#personal
              self.combo_nombre.cambiar_tabla("personal")
            elif id ==2:#contacto
              self.combo_nombre.cambiar_tabla("contactos")
            elif id ==3:#proveedores
              self.combo_nombre.cambiar_tabla("proveedores")
        
        def cambio_giro(self,widget):
          print 'giro'
          giro = widget.get_date()
          desde = self.but_desde.get_date()
          if giro>desde:
            self.but_desde.set_date(giro)
        
        def cambio_desde(self,widget):
          print 'desde'
          desde = widget.get_date()
          giro = self.but_giro.get_date()
          if giro>desde:
            self.but_giro.set_date(desde)
        
	def cerrar(self):
		self.destroy()

class Cotizacion(gtk.Dialog):
	def __init__(self,cursor,id):
		gtk.Dialog.__init__(self)
		self.set_title("Guias por Cotización")
		self.cursor = cursor
		sql = "SELECT CONCAT(SERIE,'-',NUMERO),ANULADO,IMPRESO,ID FROM guias WHERE COTIZ=%d ORDER BY SERIE DESC,NUMERO DESC"%id
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		columnas = ("GUIA","ANULADO")
		self.model = gtk.ListStore(str,int,int,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			if i==0:
				renderer = gtk.CellRendererText()
				column = gtk.TreeViewColumn(name,renderer,text=i)
				column.set_min_width(200)
				self.treeview.append_column(column)
			else:
				renderer = gtk.CellRendererToggle()
				renderer.set_radio(True)
				renderer.set_activatable(True)
				renderer.connect('toggled',self.on_toggled,i)
				column = gtk.TreeViewColumn(name,renderer,active=i)
				column.set_max_width(40)
				self.treeview.append_column(column)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_size_request(600,300)
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self.vbox.pack_start(sw)
		sw.add(self.treeview)
		for row in items:
			self.model.append(row)
		self.but_imprimir = Estilos.MiBoton("../images/PNG-16/Print.png","_Imprimir")
		self.action_area.pack_start(self.but_imprimir,False,False,0)
		self.but_imprimir.connect('clicked',self.imprimir)
		self.but_nueva = Estilos.MiBoton("../images/PNG-16/Add.png","_Nueva")
		self.add_action_widget(self.but_nueva,gtk.RESPONSE_OK)
		self.treeview.connect('cursor-changed',self.on_cursor)
		self.show_all()

	def on_cursor(self,widget):
		path, column = self.treeview.get_cursor()
		try:
			self.impreso = self.model[path][2]
		except:
			self.but_nueva.label.set_text('_Nuevo')
			self.but_nueva.label.set_use_underline(True)
			self.but_imprimir.set_sensitive(False)
		else:
			if self.impreso:
				self.but_nueva.label.set_text('_Nuevo')
				self.but_nueva.label.set_use_underline(True)
				self.but_imprimir.set_sensitive(False)
			else:
				self.but_nueva.label.set_text('_Editar')
				self.but_nueva.label.set_use_underline(True)
				self.but_imprimir.set_sensitive(True)

	def on_toggled(self,cell,path,i):
		b = self.model[path][i]
		self.model[path][i] = not b

	def imprimir(self,widget):
		path, column = self.treeview.get_cursor()
		guia = self.model[path][3]


	def cerrar(self):
		self.destroy()

class Item(gtk.Dialog):
	def __init__(self):
		gtk.Dialog.__init__(self)
		self.set_title("Nuevo Item")
		hbox_cant = gtk.HBox()
		self.vbox.pack_start(hbox_cant)
		label_cant = gtk.Label("Cantidad:")
		hbox_cant.pack_start(label_cant)
		self.entry_cant = gtk.Entry()
		hbox_cant.pack_start(self.entry_cant)
                label_precio = gtk.Label("Precio:")
		hbox_cant.pack_start(label_precio)
		self.entry_precio = gtk.Entry()
		hbox_cant.pack_start(self.entry_precio)
		frame_desc = gtk.Frame("Descripción")
		self.vbox.pack_start(frame_desc)
		self.text_desc = Estilos.TextHTML()
		self.buffer = self.text_desc.buffer
		frame_desc.add(self.text_desc)
		frame_desc.set_size_request(400,200)
		self.but_ok = Estilos.MiBoton("../images/PNG-16/Check.png","OK")
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.entry_cant.connect('changed',self.numero)
		self.show_all()

	def numero(self,widget):
		try:
			dec = Decimal('0'+widget.get_text())
		except:
			widget.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse('#ffa89f'))
			self.but_ok.set_sensitive(False)
		else:
			widget.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse('#FFFFFF'))
			self.but_ok.set_sensitive(True)

	def guardar(self):
		cantidad = self.entry_cant.get_text()
		inicio = self.buffer.get_start_iter()
		fin = self.buffer.get_end_iter()
		descripcion = self.buffer.get_text(inicio,fin,False)
                precio = self.entry_precio.get_text()
		item = (cantidad,descripcion,precio)
		return item

	def leer(self,row):
		self.entry_cant.set_text(row[0])
		self.text_desc.buffer.set_text(row[1])

	def cerrar(self):
		self.destroy()

class Lista(gtk.Dialog):
	""" Clase Ventana Principal """
	def __init__ (self,cursor):
		""" Class initialiser """
		gtk.Dialog.__init__(self)
		self.cursor = cursor
		self.set_title("Items Cotizaciones")
		tabla_controles = gtk.Table(4,5,False)
		self.vbox.pack_start(tabla_controles)
		label_buscar = gtk.Label("Buscar:")
		tabla_controles.attach(label_buscar,0,1,0,1)
		entry_buscar = gtk.Entry()
		tabla_controles.attach(entry_buscar,1,2,0,1)
		columnas = ("COTIZ","EMPRESA","DESCRIPCIÓN","PRECIO")
		self.model = gtk.ListStore(str,str,str,str,str)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name,renderer,text=i)
			self.treeview.append_column(column)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(450,450)
		self.vbox.pack_start(sw)
		sw.add(self.treeview)
		self.show_all()
		self.but_abrir = Estilos.MiBoton('../images/PNG-16/Load.png','Abrir')
		entry_buscar.connect('activate',self.buscar)
		self.treeview.connect('row-activated',self.on_row_activated)
		self.add_action_widget(self.but_abrir,gtk.RESPONSE_OK)
		self.buscar(entry_buscar)
		self.treeview.set_cursor(0)


	def buscar(self,widget):
		texto = widget.get_text()
		if texto == "":
			sql = "SELECT CONCAT(YEAR(cotizaciones.FECHA),'-',cotizaciones.CORR) as corre,cotitems.CANT,cotitems.TXT,cotitems.PRECIO,cotitems.HTML FROM cotitems JOIN cotizaciones ON cotizaciones.ID = cotitems.COTIZ ORDER BY corre DESC"
		else:
			sql = "SELECT CONCAT(YEAR(cotizaciones.FECHA),'-',cotizaciones.CORR) as corre,cotitems.CANT,cotitems.TXT,cotitems.PRECIO,cotitems.HTML FROM cotitems JOIN cotizaciones ON cotizaciones.ID = cotitems.COTIZ JOIN clientes ON clientes.ID = cotizaciones.EMPRESA WHERE cotitems.TXT LIKE '%s' OR clientes.COMERCIAL LIKE '%s' OR clientes.NOMBRE LIKE '%s' ORDER BY corr DESC"%('%'+texto+'%','%'+texto+'%','%'+texto+'%')
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		self.model.clear()
		for item in items:
			self.model.append(item)

	def abrir(self):
		try:
			path, column = self.treeview.get_cursor()
		except:
			path = 0
		return self.model[path][1],self.model[path][2],self.model[path][3],self.model[path][4],0

	def on_row_activated(self,widget,path,column):
		codigo = self.model[path][0]
		self.but_abrir.clicked()

	def cerrar(self):
		self.destroy()

if __name__ == '__main__':
	import Consultas
	consultas = Consultas.Conectar()
	v = Ventana(consultas)
	gtk.main()
