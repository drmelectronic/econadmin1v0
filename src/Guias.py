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
		self.set_title("Guías de Salida")
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
		but_print = Estilos.MiBoton('../images/PNG-16/Print.png','Imprimir')
		but_enviar = Estilos.MiBoton('../images/PNG-16/Email.png','Enviar')
		self.but_ver = Estilos.MiBoton('../images/PNG-16/Search.png','Ver')
		self.but_guia = Estilos.MiBoton('../images/PNG-16/Next.png','Guía de Sal.')
		self.but_factura = Estilos.MiBoton('../images/PNG-16/Modify.png','Facturar')
		hbox_www.pack_start(but_print)
		hbox_www.pack_start(but_enviar)
		hbox_www.pack_start(self.but_ver)
		hbox_www.pack_start(self.but_guia)
		hbox_www.pack_start(self.but_factura)
		but_print.connect('clicked',self.imprimir)
		but_enviar.connect('clicked',self.enviar)
		self.but_ver.connect('clicked',self.ver)
		self.but_guia.connect('clicked',self.guia)
#		self.but_factura.connect('clicked',self.factura)
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
		columnas = ("CÓDIGO","FECHA","EMPRESA","DESCRIPCIÓN")
		self.model = gtk.ListStore(str,str,str,str,int,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name,renderer,markup=i)
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
			enviado = self.model[path][5]
		except:
			self.but_editar.set_sensitive(False)
		else:
			self.but_editar.set_sensitive(True)
			if enviado:
			  self.but_editar.label.set_text('Copiar')
				
			else:
			  self.but_editar.label.set_text('Editar')
			print enviado
		url = 'http://%s/econadmin/images/guia.jpg'%(self.host)
		self.www.open(url)

	def buscar(self,widget=None):
		self.model.clear()
		texto = self.entry_buscar.get_text()
		if texto == "":
			sql = "SELECT CONCAT(guias.SERIE,'-',guias.NUMERO) AS CORR,guias.FECHA,clientes.COMERCIAL,guias.NOMBRE,guias.ID,guias.IMPRESO FROM guias JOIN clientes ON clientes.ID=guias.EMPRESA ORDER BY CORR DESC LIMIT 100"
		else:
			sql = "SELECT CONCAT(guias.SERIE,'-',guias.NUMERO) AS CORR,guias.FECHA,clientes.COMERCIAL,guias.NOMBRE,guias.ID,guias.IMPRESO FROM guias JOIN clientes ON clientes.ID=guias.EMPRESA WHERE guias.NOMBRE LIKE '%s'OR clientes.COMERCIAL LIKE '%s' ORDER BY CORR DESC"%('%'+texto+'%','%'+texto+'%')
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
			if not item[5]:
				item = ('<b>'+str(item[0])+'</b>','<b>'+str(item[1])+'</b>','<b>'+item[2]+'</b>','<b>'+item[3]+'</b>',item[4],item[5])
			self.model.append(item)

	def on_editar(self,widget):
		path, column = self.treeview.get_cursor()
		self.on_row_activated(widget,int(path[0]),column)

	def on_row_activated(self,widget,path,column):
		enviado = self.model[path][5]
		self.abrir(enviado)

	def abrir(self,enviado):
		if enviado:
			self.copiar()
		else:
			self.editar()

	def guia(self,widget):
                print 'guia'
		path, column = self.treeview.get_cursor()
		try:
			path = int(path[0])
		except:
			return

	def ver(self,widget):
		path, column = self.treeview.get_cursor()
		try:
			path = int(path[0])
		except:
			return
		guia = Impresion.Guias(self.cursor,self.model[path][4])
		guia.convertir()
		guia.ver()
		url = 'http://%s/econadmin/images/guia.jpg'%(self.host)
		self.www.open(url)

	def imprimir(self,widget):
		path, column = self.treeview.get_cursor()
		try:
			path = int(path[0])
		except:
			return
		guia = Impresion.Guias(self.cursor,self.model[path][4])
		guia.imprimir()


	def enviar(self,widget):
		operation = gtk.PrintOperation()
		action = gtk.PRINT_OPERATION_ACTION_EXPORT
		operation.set_export_filename('../cotizacion.pdf')
		self.www_frame.print_full(operation,action)
		path, column = self.treeview.get_cursor()
		id = self.model[int(path[0])][5]
		sql = "SELECT ATENCION,CC,CCO,NOMBRE,CONCAT(YEAR(FECHA),'-',CORR) FROM cotizaciones WHERE ID = %d"%id
		self.cursor.execute(sql)
		ateid,ccid,ccoid,nombre,corr = self.cursor.fetchone()
		sql = "UPDATE cotizaciones SET ENVIADO=1 WHERE ID=%d"%id
		self.cursor.execute(sql)
		corr = corr[2:]
		ventas_id = 2
		to = self.get_mails(ateid)
		cc = self.get_mails(ccid)
		cco = self.get_mails(ccoid)
		if cco=='':
			cco = 'webmaster@econain.com'
		else:
			cco += ',webmaster@econain.com'
		subject = 'Cotización %s: %s'%(corr,nombre)
		body = 'Saludos cordiales,\nLe hacemos entrega de nuestra cotización por <b>%s</b>'%nombre
		path = os.getcwd()
		attach = os.path.join(path,'../cotizacion.pdf')
		os.system("evince '%s'"%attach)
		comm = """thunderbird -compose "to='%s',cc='%s',bcc='%s',subject='%s',body='%s',attachment='%s',preselectid='id%d'" """%(to,cc,cco,subject,body,attach,ventas_id)
		self.buscar()

	def get_mails(self,text):
		ids = text.split(',')
		l = len(ids)
		where = ''
		for i,id in enumerate(ids):
			where += 'ID=%s'%id
			if l!=i+1:
				where += ' or '
		sql = "SELECT CORREO FROM contactos WHERE %s"%where
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		l = len(items)
		mails = ''
		for i,row in enumerate(items):
			mails += row[0]
			if l!=i+1:
				where += ','
		return mails

	def copiar(self):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[int(path[0])][4])
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
		nueva.cerrar()
		self.buscar()

	def editar(self):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[int(path[0])][4])
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.actualizar()
		nueva.cerrar()
		self.buscar()

	def nuevo(self,widget):
		nueva = Nueva(self.cursor)
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
		nueva.cerrar()
		self.buscar()

class Nueva(gtk.Dialog):
	def __init__(self,cursor):
		gtk.Dialog.__init__(self)
		self.cursor = cursor
		self.set_title("Nueva Guía")
		tabla_datos = gtk.Table(3,5,False)
		self.vbox.pack_start(tabla_datos)
		label_corr = gtk.Label("Código:")
		tabla_datos.attach(label_corr,0,1,0,1)
		self.entry_serie= gtk.Entry()
		self.entry_serie.set_text('1')
		self.entry_serie.set_sensitive(False)
		tabla_datos.attach(self.entry_serie,1,2,0,1)
		self.entry_numero= gtk.Entry()
		tabla_datos.attach(self.entry_numero,2,3,0,1)
		label_fecha = gtk.Label('Fecha:')
		tabla_datos.attach(label_fecha,0,1,1,2)
		self.but_fecha = Estilos.Fecha(label_fecha.get_window())
		self.but_fecha.set_date(datetime.date.today())
		tabla_datos.attach(self.but_fecha,1,3,1,2)
		self.cursor.execute("SELECT NUMERO FROM guias WHERE SERIE=%s ORDER BY NUMERO DESC LIMIT 1"%(self.entry_serie.get_text()))
		try:
			corr = self.cursor.fetchone()[0]+1
		except:
			corr = 1
		self.entry_numero.set_text(str(corr))
		label_empresa = gtk.Label("Empresa:")
		tabla_datos.attach(label_empresa,0,1,2,3)
		self.combo_empresa = Estilos.ComboButton(self.cursor)
		self.combo_empresa.sql("SELECT ID,COMERCIAL FROM clientes",0)
		tabla_datos.attach(self.combo_empresa,1,3,2,3)
		label_llegada = gtk.Label("P. Llegada:")
		tabla_datos.attach(label_llegada,0,1,4,5)
		self.combo_llegada = Estilos.ComboButton(self.cursor)
		tabla_datos.attach(self.combo_llegada,1,3,4,5)
		columnas = ("CANT","DESCRIPCIÓN")
		self.model = gtk.ListStore(str,str,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			if i==1:
				renderer.set_property('width-chars',50)
			column = gtk.TreeViewColumn(name,renderer,text=i)
			self.treeview.append_column(column)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_size_request(600,300)
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self.vbox.pack_start(sw)
		sw.add(self.treeview)
		hbox_but = gtk.HBox()
		self.vbox.pack_start(hbox_but)
		but_mas = Estilos.MiBoton("../images/PNG-16/Add.png","Añadir")
		hbox_but.pack_start(but_mas)
		but_cop = Estilos.MiBoton("../images/PNG-16/Load.png","Copiar")
		hbox_but.pack_start(but_cop)
		but_editar = Estilos.MiBoton("../images/PNG-16/Modify.png","Editar")
		hbox_but.pack_start(but_editar)
		but_eliminar = Estilos.MiBoton("../images/PNG-16/Delete.png","Eliminar")
		hbox_but.pack_start(but_eliminar)
		tabla_cond = gtk.Table(4,5,False)
		self.vbox.pack_start(tabla_cond)
		label_motivo = gtk.Label("Motivo:")
		tabla_cond.attach(label_motivo,0,1,0,1)
		self.entry_motivo = Estilos.Completion(self.cursor,"motivos")
		tabla_cond.attach(self.entry_motivo,1,2,0,1)
		label_compra = gtk.Label("O. Compra:")
		tabla_cond.attach(label_compra,2,3,0,1)
		self.entry_compra = gtk.Entry()
		tabla_cond.attach(self.entry_compra,3,4,0,1)
		label_transportista = gtk.Label("Transportista:")
		tabla_cond.attach(label_transportista,0,1,2,3)
		self.entry_transportista = Estilos.Completion(self.cursor,"transportistas")
		tabla_cond.attach(self.entry_transportista,1,2,2,3)
		label_dni = gtk.Label("DNI:")
		tabla_cond.attach(label_dni,2,3,2,3)
		self.entry_dni = gtk.Entry()
		tabla_cond.attach(self.entry_dni,3,4,2,3)
		label_vehiculo = gtk.Label("Vehiculo:")
		tabla_cond.attach(label_vehiculo,0,1,3,4)
		self.entry_vehiculo = Estilos.CompletionVehiculo(self.cursor,"vehiculos")
		hbox_vehiculo = gtk.HBox(False,0)
		hbox_vehiculo.pack_start(self.entry_vehiculo,False,False,0)
		self.toggle_vehiculo = gtk.CheckButton('ECO')
		hbox_vehiculo.pack_start(self.toggle_vehiculo)
		tabla_cond.attach(hbox_vehiculo,1,2,3,4)
		label_licencia = gtk.Label("Licencia:")
		tabla_cond.attach(label_licencia,2,3,3,4)
		self.entry_licencia = gtk.Entry()
		tabla_cond.attach(self.entry_licencia,3,4,3,4)
		label_observ = gtk.Label("Observaciones:")
		tabla_cond.attach(label_observ,0,1,4,5)
		self.entry_observ = gtk.TextView()
		tabla_cond.attach(self.entry_observ,1,4,4,5)
		self.but_guardar = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		but_mas.connect('clicked',self.mas)
		but_cop.connect('clicked',self.cop)
		but_editar.connect('clicked',self.but_editar)
		but_eliminar.connect('clicked',self.eliminar)
		self.entry_transportista.connect('nuevo',self.nuevo_transportista)
		self.entry_transportista.connect('antiguo',self.antiguo_transportista)
		self.treeview.connect('row-activated',self.on_row_activated)
		self.add_action_widget(self.but_guardar,gtk.RESPONSE_OK)
		self.combo_empresa.connect('changed',self.cambio_empresa)
		self.entry_dni.set_sensitive(False)
		self.entry_licencia.set_sensitive(False)
		self.cotiz = 0
		self.show_all()

	def nuevo_transportista(self,widget):
		self.entry_dni.set_sensitive(True)
		self.entry_licencia.set_sensitive(True)
		self.entry_vehiculo.set_sensitive(True)

	def antiguo_transportista(self,widget):
		self.entry_dni.set_sensitive(False)
		self.entry_licencia.set_sensitive(False)
		sql = "SELECT DNI,LICENCIA FROM transportistas WHERE ID=%d"%widget.get_id()
		self.cursor.execute(sql)
		dni,licencia = self.cursor.fetchone()
		self.entry_dni.set_text(dni)
		self.entry_licencia.set_text(licencia)
		if licencia == '':
			self.entry_vehiculo.set_sensitive(False)
		else:
			self.entry_vehiculo.set_sensitive(True)


	def on_row_activated(self,widget,path,column):
		self.editar(path)

	def cotizacion(self,id):
		self.cotiz = id
		sql = "SELECT EMPRESA,OC FROM cotizaciones WHERE ID=%d"%self.cotiz
		self.cursor.execute(sql)
		empresa,oc = self.cursor.fetchone()
		self.entry_compra.set_text(oc)
		self.combo_empresa.set_id(empresa)
		self.combo_empresa.set_sensitive(False)
		sql = "SELECT CANT,TXT,ID FROM cotitems WHERE COTIZ=%d"%self.cotiz
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for row in items:
			self.model.append(row)

	def guardar(self):
		serie = self.entry_serie.get_text()
		numero = self.entry_numero.get_text()
		fecha = self.but_fecha.get_date()
		empresa = self.combo_empresa.get_id()
		nombre = self.model[0][1].split('\n')[0]
		llegada = self.combo_llegada.get_id()
		motivo = self.entry_motivo.get_id(False)
		compra = self.entry_compra.get_text()
		transportista = self.entry_transportista.get_id()
		if self.toggle_vehiculo:
		  empresav = 0
		else:
		  empresav = empresa
		vehiculo = self.entry_vehiculo.get_id(1,empresav)
		buffer = self.entry_observ.get_buffer()
		inicio = buffer.get_start_iter()
		fin = buffer.get_end_iter()
		observaciones = buffer.get_text(inicio,fin,False)
		columnas = "SERIE,NUMERO,FECHA, EMPRESA,NOMBRE,LLEGADA, MOTIVO,COTIZ,OC, TRANSP,VEHICULO,IMPRESO, OBSERV"
		valores = "%s,%s,'%s', %d,'%s',%d, '%s',%d,'%s', %d,%d,0, '%s'"%(serie,numero,fecha, empresa,nombre,llegada, motivo,self.cotiz,compra, transportista,vehiculo, observaciones)
		sql = "INSERT INTO guias (%s) VALUES (%s)"%(columnas,valores)
		self.cursor.execute(sql)
		#guardar items
		self.cursor.execute("SELECT ID FROM guias ORDER BY ID DESC LIMIT 1")
		id = self.cursor.fetchone()[0]
		for row in self.model:
			valores = "%d,%d,'%s','%s'"%(row[2],id,row[0],row[1])
			self.cursor.execute("INSERT INTO guiasitems (ID,GUIA,CANT,TXT) VALUES (%s)"%valores)

	def actualizar(self):
		serie = self.entry_serie.get_text()
		numero = self.entry_numero.get_text()
		fecha = self.but_fecha.get_date()
		empresa = self.combo_empresa.get_id()
		nombre = self.model[0][1].split('\n')[0]
		llegada = self.combo_llegada.get_id()
		motivo = self.entry_motivo.get_id(False)
		compra = self.entry_compra.get_text()
		transportista = self.entry_transportista.get_id()
		if self.toggle_vehiculo:
		  empresav = 0
		else:
		  empresav = empresa
		vehiculo = self.entry_vehiculo.get_id(1,empresav)
		buffer = self.entry_observ.get_buffer()
		inicio = buffer.get_start_iter()
		fin = buffer.get_end_iter()
		observaciones = buffer.get_text(inicio,fin,False)
		valores = (serie,numero,fecha, empresa,nombre,llegada, motivo,self.cotiz,compra, transportista,vehiculo, observaciones,self.id)
		sql = "UPDATE guias SET SERIE=%s,NUMERO=%s,FECHA='%s', EMPRESA=%d,NOMBRE='%s',LLEGADA=%d, MOTIVO='%s',COTIZ=%d,OC='%s', TRANSP=%d,VEHICULO=%d, OBSERV='%s' WHERE ID=%d"%valores
		for row in self.model:
			valores = (self.id,row[0],row[1],row[2])
			self.cursor.execute("UPDATE guiasitems SET GUIA=%d,CANT=%s,TXT='%s' WHERE ID=%d"%valores)
			print row[1]
		
	def copiar(self,id):
		self.id = id
		sql = "SELECT CANT,TXT FROM guiasitems WHERE GUIA = %d"%id
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		sql = "SELECT EMPRESA,LLEGADA,MOTIVO,COTIZ,OC,TRANSP,VEHICULO,OBSERV FROM guias WHERE ID=%d"%id
		self.cursor.execute(sql)
		empresa,llegada,motivo,cotiz,compra,transp,vehiculo,observ = self.cursor.fetchone()
		self.combo_empresa.set_id(empresa)
		self.combo_empresa.set_sensitive(False)
		self.combo_llegada.set_id(llegada)
		try:
			mot = int(motivo)
		except:
			self.entry_motivo.set_text(motivo)
		else:
			if mot==0:
				motivo = 'Venta'
			elif mot==1:
				motivo = 'Venta sujeta a confirmar'
			elif mot==2:
				motivo = 'Reparación'
			elif mot==3:
				motivo = 'Devolución'
			self.entry_motivo.set_text(motivo)
		self.cotiz = cotiz
		self.entry_compra.set_text(compra)
		self.entry_transportista.set_id(transp)
		self.entry_vehiculo.set_id(vehiculo)
		self.entry_observ.get_buffer().set_text(observ)
		self.model.clear()
		for row in items:
			self.model.append((row[0],row[1],0))
		self.treeview.set_cursor(0)

	def leer(self,id):
		self.id = id
		sql = "SELECT CANT,TXT FROM guiasitems WHERE GUIA = %d"%id
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		sql = "SELECT FECHA,SERIE,NUMERO,EMPRESA,LLEGADA,MOTIVO,COTIZ,OC,TRANSP,VEHICULO,OBSERV FROM guias WHERE ID=%d"%id
		self.cursor.execute(sql)
		fecha,serie,numero,empresa,llegada,motivo,cotiz,compra,transp,vehiculo,observ = self.cursor.fetchone()
		self.combo_empresa.set_id(empresa)
		self.combo_empresa.set_sensitive(False)
		self.combo_llegada.set_id(llegada)
		try:
			mot = int(motivo)
		except:
			self.entry_motivo.set_text(motivo)
		else:
			if mot==0:
				motivo = 'Venta'
			elif mot==1:
				motivo = 'Venta sujeta a confirmar'
			elif mot==2:
				motivo = 'Reparación'
			elif mot==3:
				motivo = 'Devolución'
			self.entry_motivo.set_text(motivo)
		self.but_fecha.set_date(fecha)
		self.entry_serie.set_text(str(serie))
		self.entry_numero.set_text(str(numero))
		self.cotizacion = cotiz
		self.entry_compra.set_text(compra)
		self.entry_transportista.set_id(transp)
		self.entry_vehiculo.set_id(vehiculo)
		self.entry_observ.get_buffer().set_text(observ)
		self.model.clear()
		for row in items:
			self.model.append((row[0],row[1],0))
		self.treeview.set_cursor(0)

	def cambio_empresa(self,widget):
		id = widget.get_id()
		self.combo_llegada.sql("SELECT ID,NOMBRE FROM direcciones WHERE EMPRESA=%d"%id,True)
		self.cursor.execute("SELECT MONEDA,PAGO,RESPONSABLE FROM clientes WHERE ID = %d"%id)
		self.entry_transportista.filtrar('EMPRESA',id,True)
		self.entry_vehiculo.filtrar('EMPRESA',id,True)
		
	def mas(self,widget):
		item = Item()
		if item.run() == gtk.RESPONSE_OK:
			row = item.guardar()
			self.model.append((row[0],row[1],0))
		item.cerrar()

	def cop(self,widget):
		lista = Lista(self.cursor)
		if lista.run() == gtk.RESPONSE_OK:
			row = lista.abrir()
			self.model.append(row)
		lista.cerrar()

	def but_editar(self,widget):
		path,column = self.treeview.get_cursor()
		path = int(path[0])
		self.editar(path)

	def editar(self,path):
		item = Item()
		item.leer(self.model[path])
		if item.run() == gtk.RESPONSE_OK:
			row = item.guardar()
			self.model[path][0] = row[0]
			self.model[path][1] = row[1]
		item.cerrar()

	def eliminar(self,widget):
		path,column = self.treeview.get_cursor()
		path = int(path[0])
		iter = self.treeview.get_model().get_iter(path)
		self.model.remove(iter)

	def cerrar(self):
		self.destroy()

class Cotizacion(gtk.Dialog):
	def __init__(self,cursor,id):
		gtk.Dialog.__init__(self)
		self.set_title("Guias por Cotización")
		self.cursor = cursor
                self.cotiz = id
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
		self.but_nueva = Estilos.MiBoton("../images/PNG-16/Add.png","_Nueva")
		self.action_area.pack_start(self.but_nueva,False,False,0)
                self.but_nueva.connect('clicked',self.abrir)
                self.but_imprimir = Estilos.MiBoton("../images/PNG-16/Print.png","_Imprimir")
		self.action_area.pack_start(self.but_imprimir,False,False,0)
		self.but_imprimir.connect('clicked',self.imprimir)
                self.but_guardar = Estilos.MiBoton("../images/PNG-16/Save.png","_Guardar")
		self.add_action_widget(self.but_guardar,gtk.RESPONSE_OK)
		self.treeview.connect('cursor-changed',self.on_cursor)
		self.show_all()
                self.actualizar()

        def actualizar(self):
          sql = "SELECT CONCAT(SERIE,'-',NUMERO),ANULADO,IMPRESO,ID FROM guias WHERE COTIZ=%d ORDER BY SERIE DESC,NUMERO DESC"%self.cotiz
          self.cursor.execute(sql)
          items = self.cursor.fetchall()
          self.model.clear()
          for row in items:
            self.model.append(row)

        def abrir(self,widget):
          nueva = Nueva(self.cursor)
          if self.impreso:
            print 'copiar'
            nueva.copiar(self.model[0][3])
          else:
            nueva.leer(self.model[0][3])
          if nueva.run() == gtk.RESPONSE_OK:
            if self.impreso:
              nueva.guardar()
            else:
              nueva.actualizar()
          nueva.cerrar()

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
				self.but_nueva.label.set_text('_Copiar')
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
                Impresion.Guias(self.cursor,guia)
                sql = "UPDATE guias SET IMPRESO=1 WHERE ID=%d"%(guia)
                self.cursor.execute(sql)
                self.actualizar()

        def guardar(self):
          i = 0
          for row in self.model:
            sql = "UPDATE guias SET ANULADO=%d WHERE ID=%d"%(row[1],row[3])
            self.cursor.execute(sql)
            if not row[1]:
              i += 1
              id = row[3]
          if i==1:
            sql = "UPDATE cotizaciones SET GUIA=%d WHERE ID=%d"%(id,self.cotiz)
            self.cursor.execute(sql)

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
		item = (cantidad,descripcion)
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
