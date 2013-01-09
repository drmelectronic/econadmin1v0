#!/usr/bin/env python
#! -*- encoding: utf8 -*-

import gtk
import Contactos
import Estilos
import gobject

__author__="danielypamela"
__date__ ="$26/10/2011 05:53:37 PM$"

class Ventana(gtk.Window):
	""" Clase Ventana Principal """
	def __init__ (self,consulta):
		""" Class initialiser """
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = consulta.cursor
		self.set_title("Clientes")
		vbox_main = gtk.VBox(False,0)
		self.add(vbox_main)
		tabla_controles = gtk.Table(4,5,False)
		vbox_main.pack_start(tabla_controles)
		label_buscar = gtk.Label("Buscar:")
		tabla_controles.attach(label_buscar,0,1,0,1)
		self.entry_buscar = gtk.Entry()
		tabla_controles.attach(self.entry_buscar,1,2,0,1)
		self.but_editar= Estilos.MiBoton("../images/PNG-16/Modify.png","Modificar")
		tabla_controles.attach(self.but_editar,2,3,0,1)
		self.but_delete = Estilos.MiBoton("../images/PNG-16/Delete.png","Eliminar")
		tabla_controles.attach(self.but_delete,3,4,0,1)
		but_nuevo = Estilos.MiBoton("../images/PNG-16/Add.png","Nuevo")
		tabla_controles.attach(but_nuevo,4,5,0,1)
		columnas = ("EMPRESA","RUC","TELEFONO","DIRECCIÓN")
		self.model = gtk.ListStore(str,gobject.TYPE_INT64,str,str,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name,renderer,text=i)
			self.treeview.append_column(column)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(700,300)
		vbox_main.pack_start(sw)
		sw.add(self.treeview)
		self.show_all()

		self.entry_buscar.connect('changed',self.buscar)
		self.but_editar.connect('clicked',self.editar)
		self.treeview.connect('row-activated',self.on_row_activated)
		self.treeview.connect('cursor-changed',self.on_cursor)
		self.but_delete.connect('clicked',self.delete)
		but_nuevo.connect('clicked',self.nuevo)

		self.buscar()
		self.but_editar.set_sensitive(False)
		self.but_delete.set_sensitive(False)
		self.treeview.set_cursor(0)

	def on_cursor(self,widget):
		try:
			path, column = self.treeview.get_cursor()
			int(path[0])
		except:
			self.but_delete.set_sensitive(False)
			self.but_editar.set_sensitive(False)
		else:
			self.but_delete.set_sensitive(True)
			self.but_editar.set_sensitive(True)

	def buscar(self,widget=None):
		self.model.clear()
		texto = self.entry_buscar.get_text()
		if texto == "":
			sql = "SELECT COMERCIAL,RUC,TELEFONO,DIRECCION,ID FROM clientes ORDER BY COMERCIAL ASC"
		else:
			sql = "SELECT COMERCIAL,RUC,TELEFONO,DIRECCION,ID FROM clientes WHERE NOMBRE LIKE '%s' OR COMERCIAL LIKE '%s' ORDER BY COMERCIAL ASC"%('%'+texto+'%','%'+texto+'%')
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
			self.model.append(item)

	def on_row_activated(self,widget,path,column):
		self.editar(None)

	def delete(self,codigo):
		path, column = self.treeview.get_cursor()
		id = self.model[path][4]
		dialog = Estilos.DialogoSN('¡Atención!','¿Está seguro de borrar la empresa?')
		if dialog.run() == gtk.RESPONSE_OK:
			sql = "DELETE FROM clientes WHERE ID=%d"%id
			self.cursor.execute(sql)
			self.buscar()
			dialog.cerrar()
			dialog = Estilos.DialogoSN('¡Atención!','¿Desea borrar los contactos de la empresa?')
			if dialog.run() == gtk.RESPONSE_OK:
				sql = "DELETE FROM contactos WHERE EMPRESA=%d"%id
				self.cursor.execute(sql)
		dialog.cerrar()

	def editar(self,widget):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[path][4])
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
			self.buscar()
		nueva.cerrar()
		self.treeview.set_cursor(path)

	def nuevo(self,widget):
		nueva = Nueva(self.cursor)
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
			self.buscar()
			self.treeview.set_cursor(0)
		nueva.cerrar()

class Nueva(gtk.Dialog):
	def __init__(self,cursor):
		gtk.Dialog.__init__(self)
		self.cursor = cursor
		self.set_title("Nueva Empresa")
		frame_p = gtk.Frame()
		frame_p.set_border_width(2)
		self.vbox.pack_start(frame_p)
		tabla_datos = gtk.Table(2,5,False)
		frame_p.add(tabla_datos)
		label_razon = gtk.Label("R. SOCIAL:")
		tabla_datos.attach(label_razon,0,1,0,1,gtk.SHRINK,gtk.SHRINK)
		self.entry_razon = gtk.Entry()
		tabla_datos.attach(self.entry_razon,1,2,0,1)
		label_comercial = gtk.Label("N. COMERCIAL")
		label_comercial.set_size_request(120,25)
		tabla_datos.attach(label_comercial,0,1,1,2,gtk.SHRINK,gtk.SHRINK)
		self.entry_comercial = gtk.Entry()
		tabla_datos.attach(self.entry_comercial,1,2,1,2)
		label_ruc = gtk.Label("RUC:")
		tabla_datos.attach(label_ruc,0,1,2,3,gtk.SHRINK,gtk.SHRINK)
		self.entry_ruc = gtk.Entry()
		tabla_datos.attach(self.entry_ruc,1,2,2,3)
		label_dir = gtk.Label("Dirección:")
		tabla_datos.attach(label_dir,0,1,3,4,gtk.SHRINK,gtk.SHRINK)
		self.entry_dir = gtk.Entry()
		tabla_datos.attach(self.entry_dir,1,2,3,4)
		label_telefono = gtk.Label("Teléfono:")
		tabla_datos.attach(label_telefono,0,1,4,5,gtk.SHRINK,gtk.SHRINK)
		self.entry_tele = gtk.Entry()
		tabla_datos.attach(self.entry_tele,1,2,4,5)
		frame_s = gtk.Frame()
		frame_s.set_border_width(2)
		self.vbox.pack_start(frame_s)
		tabla_s = gtk.Table(2,3)
		frame_s.add(tabla_s)

		label_moneda = gtk.Label("Moneda:")
		label_moneda.set_size_request(120,20)
		tabla_s.attach(label_moneda,0,1,1,2,gtk.SHRINK,gtk.SHRINK)
		self.combo_moneda = Estilos.ComboButton(self.cursor)
		tabla_s.attach(self.combo_moneda,1,2,1,2)
		label_pago = gtk.Label("F. PAGO:")
		tabla_s.attach(label_pago,0,1,2,3,gtk.SHRINK,gtk.SHRINK)
		self.entry_pago = Estilos.Completion(self.cursor,"pagos")
		tabla_s.attach(self.entry_pago,1,2,2,3)
		label_responsable = gtk.Label("Responsable:")
		tabla_s.attach(label_responsable,0,1,3,4,gtk.SHRINK,gtk.SHRINK)
		self.combo_responsable = Estilos.ComboButton(self.cursor)
		tabla_s.attach(self.combo_responsable,1,2,3,4)
		self.combo_responsable.sql("SELECT ID,NOMBRE FROM personal WHERE COT=1 ORDER BY ID",0)
		self.combo_moneda.sql("SELECT ID,NOMBRE FROM monedas",0)
		self.frame_t = gtk.Frame()
		self.frame_t.set_border_width(2)
		sw = gtk.ScrolledWindow()
                sw.set_size_request(350,150)
		sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		vbox = gtk.VBox()
		but_mas = Estilos.MiBoton('../images/PNG-16/Add.png','Añadir Contacto')
		but_mas.connect('clicked',self.mas)
		vbox.pack_start(sw)
		vbox.pack_start(but_mas)
		self.frame_t.add(vbox)
		columnas = ("NOMBRE","ATE","CC","CCO","FACT")
		self.model = gtk.ListStore(str,bool,bool,bool,bool,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			if i==0:
				renderer = gtk.CellRendererText()
				column = gtk.TreeViewColumn(name,renderer,text=i)
				column.set_min_width(180)
				self.treeview.append_column(column)
			else:
				renderer = gtk.CellRendererToggle()
				if i == 4:
					renderer.set_radio(False)
				else:
					renderer.set_radio(True)
				renderer.set_activatable(True)
				renderer.connect('toggled',self.on_toggled,i)
				column = gtk.TreeViewColumn(name,renderer,active=i)
				column.set_max_width(40)
				self.treeview.append_column(column)
			i+=1
		sw.add(self.treeview)
		self.but_crear = Estilos.MiBoton("../images/PNG-16/Next.png","Siguiente")
		self.action_area.pack_start(self.but_crear)
		self.but_ok = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		but_cancel = Estilos.MiBoton("../images/PNG-16/Exit.png","Cancelar")
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.add_action_widget(but_cancel,gtk.RESPONSE_CANCEL)
		self.but_crear.connect('clicked',self.crear)
		self.but_ok.set_sensitive(False)
		self.show_all()

	def on_toggled(self,cell,path,i):
		self.model[path][i] = not self.model[path][i]
		if self.model[path][i]:
			if i == 1:
				self.model[path][2] = 0
				self.model[path][3] = 0
			elif i == 2:
				self.model[path][1] = 0
				self.model[path][3] = 0
			elif i == 3:
				self.model[path][1] = 0
				self.model[path][2] = 0
		cot = False
		fact = False
		for row in self.model:
			cot = cot or row[1] or row[2] or row[3]
			fact = fact or row[4]
		b = cot and fact
		self.but_ok.set_sensitive(b)

	def mas(self,widget):
		nuevo = Contactos.Nueva(self.cursor)
		nuevo.set_empresa(self.id)
		if nuevo.run() == gtk.RESPONSE_OK:
			nuevo.guardar()
			self.actualizar_contactos()
		nuevo.cerrar()

	def actualizar_contactos(self):
		sql = "SELECT NOMBRE,ATE,CC,CCO,FACT,ID FROM contactos WHERE EMPRESA=%d ORDER BY NOMBRE"%self.id
                self.cursor.execute(sql)
		contactos = self.cursor.fetchall()
		self.model.clear()
		cot = False
		fact = False
		for row in contactos:
			self.model.append(row)
		for row in self.model:
			cot = cot or row[1] or row[2] or row[3]
			fact = fact or row[4]
		b = cot and fact
		self.but_ok.set_sensitive(b)

	def guardar(self):
		razon = self.entry_razon.get_text()
		comercial = self.entry_comercial.get_text()
		ruc = self.entry_ruc.get_text()
		direccion = self.entry_dir.get_text()
		telefono = self.entry_tele.get_text()
		moneda = self.combo_moneda.get_id()
		pago = self.entry_pago.get_id()
		responsable = self.combo_responsable.get_id()
		sql = "UPDATE clientes SET NOMBRE='%s',COMERCIAL='%s',RUC=%s,DIRECCION='%s',TELEFONO='%s',MONEDA=%d,PAGO=%d,RESPONSABLE=%d WHERE ID=%d"%(razon,comercial,ruc,direccion,telefono,moneda,pago,responsable,self.id)
		self.cursor.execute(sql)
		for row in self.model:
			sql = "UPDATE contactos SET ATE=%d,CC=%d,CCO=%d,FACT=%d WHERE ID=%d"%(row[1],row[2],row[3],row[4],row[5])
			self.cursor.execute(sql)
		self.cerrar()

	def crear(self,widget):
		ruc = self.entry_ruc.get_text()
		comercial = self.entry_comercial.get_text()
		razon = self.entry_razon.get_text()
		direccion = self.entry_dir.get_text()
		tele = self.entry_tele.get_text()
		moneda = self.combo_moneda.get_id()
		pago = self.entry_pago.get_id()
		print pago
		responsable = self.combo_responsable.get_id()
		sql = "INSERT INTO clientes (RUC,COMERCIAL,NOMBRE,DIRECCION,TELEFONO,MONEDA,PAGO,RESPONSABLE) VALUES ('%s','%s','%s','%s','%s',%d,%d,%d)"%(ruc,comercial,razon,direccion,tele,moneda,pago,responsable)
		self.cursor.execute(sql)
		sql = "SELECT ID FROM clientes WHERE RUC=%s"%ruc
		self.cursor.execute(sql)
		self.id = self.cursor.fetchone()[0]
		self.vbox.pack_start(self.frame_t)
		self.frame_t.show_all()
		self.but_crear.hide()
		self.but_ok.set_sensitive(True)

	def leer(self,id):
		self.id = id
		sql = "SELECT NOMBRE,COMERCIAL,RUC,DIRECCION,TELEFONO,MONEDA,PAGO,RESPONSABLE FROM clientes WHERE ID=%d"%id
		self.cursor.execute(sql)
		razon,comercial,ruc,direccion,telefono,moneda,pago,responsable = self.cursor.fetchone()
		self.entry_razon.set_text(razon)
		self.entry_comercial.set_text(comercial)
		self.entry_ruc.set_text(str(ruc))
		self.entry_dir.set_text(direccion)
		self.entry_tele.set_text(telefono)
		self.combo_moneda.set_id(moneda)
		self.entry_pago.set_id(pago)
		self.combo_responsable.set_id(responsable)
		self.vbox.pack_start(self.frame_t)
		self.frame_t.show_all()
                
		self.but_crear.hide()
		self.but_ok.set_sensitive(True)
		self.actualizar_contactos()


	def cerrar(self):
		self.destroy()


if __name__ == '__main__':
	import Consultas
	consultas = Consultas.Conectar()
	v = Ventana(consultas)
	gtk.main()
