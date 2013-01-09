#! /usr/bin/python
#! -*- encoding: utf8 -*-
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="danielypamela"
__date__ ="$07-nov-2011 18:07:53$"

import gtk
import Estilos
import gobject

class Ventana(gtk.Window):
	def __init__(self,consulta):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = consulta.cursor
		self.set_title("Proveedores")
		vbox_main = gtk.VBox(False,0)
		self.add(vbox_main)
		tabla_controles = gtk.Table(4,5,False)
		vbox_main.pack_start(tabla_controles)
		label_buscar = gtk.Label("Buscar:")
		tabla_controles.attach(label_buscar,0,1,0,1)
		self.entry_buscar = gtk.Entry()
		tabla_controles.attach(self.entry_buscar,1,2,0,1)
		but_editar= Estilos.MiBoton("../images/PNG-16/Modify.png","Modificar")
		tabla_controles.attach(but_editar,2,3,0,1)
		but_delete = Estilos.MiBoton("../images/PNG-16/Delete.png","Eliminar")
		tabla_controles.attach(but_delete,3,4,0,1)
		but_nuevo = Estilos.MiBoton("../images/PNG-16/Add.png","Nuevo")
		tabla_controles.attach(but_nuevo,4,5,0,1)
		columnas = ("RAZON","COMERCIAL","TELEFONO","CORREO","WEB")
		self.model = gtk.ListStore(str,str,str,str,str,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name,renderer,text=i)
			self.treeview.append_column(column)
			if i<2:
				renderer.set_property('width-chars',20)
			elif i>2:
				renderer.set_property('width-chars',15)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(700,300)
		vbox_main.pack_start(sw)
		sw.add(self.treeview)
		self.show_all()

		self.entry_buscar.connect('changed',self.buscar)
		but_editar.connect('clicked',self.editar)
		self.treeview.connect('row-activated',self.on_row_activated)
		but_delete.connect('clicked',self.delete)
		but_nuevo.connect('clicked',self.nuevo)

		self.buscar()
		self.treeview.set_cursor(0)


	def buscar(self,widget=None):
		self.model.clear()
		texto = self.entry_buscar.get_text()
		if texto == "":
			sql = "SELECT NOMBRE,COMERCIAL,TELEFONO,CORREO,WEB,ID FROM proveedores ORDER BY NOMBRE ASC"
		else:
			sql = "SELECT NOMBRE,COMERCIAL,TELEFONO,CORREO,WEB,ID FROM proveedores WHERE NOMBRE LIKE '%s'OR COMERCIAL LIKE '%s' OR DIRECCION LIKE '%s' OR RUC LIKE '%s' ORDER BY NOMBRE ASC"%('%'+texto+'%','%'+texto+'%','%'+texto+'%','%'+texto+'%')
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
			self.model.append(item)

	def on_row_activated(self,widget,path,column):
		codigo = self.model[path][0]
		self.editar(codigo)

	def delete(self,codigo):
		path, column = self.treeview.get_cursor()
		dialog = Estilos.DialogoSN('¡Atención!','¿Está seguro de borrar el proveedor?')
		if dialog.run() == gtk.RESPONSE_OK:
			sql = "DELETE FROM proveedores WHERE ID=%d"%self.model[path][5]
			self.cursor.execute(sql)
			self.buscar()
		dialog.cerrar()

	def editar(self,widget):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[path][5])
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.actualizar()
			self.buscar()
		nueva.cerrar()

	def nuevo(self,widget):
		nueva = Nueva(self.cursor)
		if nueva.run() == gtk.RESPONSE_OK:
			nueva.guardar()
			self.buscar()
		nueva.cerrar()

class Nueva(gtk.Dialog):
	def __init__(self,cursor):
		gtk.Dialog.__init__(self)
		self.cursor = cursor
		self.set_title("Nuevo Proveedor")
		frame_p = gtk.Frame()
		frame_p.set_border_width(2)
		self.vbox.pack_start(frame_p)
		tabla_datos = gtk.Table(2,10,False)
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
		label_celular = gtk.Label("Celular:")
		tabla_datos.attach(label_celular,0,1,5,6,gtk.SHRINK,gtk.SHRINK)
		self.entry_cel = gtk.Entry()
		tabla_datos.attach(self.entry_cel,1,2,5,6)
		label_correo = gtk.Label("Correo:")
		tabla_datos.attach(label_correo,0,1,6,7,gtk.SHRINK,gtk.SHRINK)
		self.entry_correo = gtk.Entry()
		tabla_datos.attach(self.entry_correo,1,2,6,7)
		label_web= gtk.Label("Web:")
		tabla_datos.attach(label_web,0,1,7,8,gtk.SHRINK,gtk.SHRINK)
		self.entry_web = gtk.Entry()
		tabla_datos.attach(self.entry_web,1,2,7,8)
		label_tipo= gtk.Label("Tipo:")
		tabla_datos.attach(label_tipo,0,1,8,9,gtk.SHRINK,gtk.SHRINK)
		self.entry_tipo = Estilos.ComboButton(self.cursor)
		self.entry_tipo.items(((1,"Neto"),(2,"Total"),(3,"N-NG"),(4,"Tot-NG"),(5,"Aduana"),(6,"Selva")))
		self.entry_tipo.set_id(1)
		tabla_datos.attach(self.entry_tipo,1,2,8,9)
		label_moneda = gtk.Label("Moneda:")
		tabla_datos.attach(label_moneda,0,1,9,10)
		self.combo_moneda = Estilos.ComboButton(self.cursor)
		self.combo_moneda.sql("SELECT ID,NOMBRE FROM monedas",0)
		self.combo_moneda.set_id(1)
		tabla_datos.attach(self.combo_moneda,1,2,9,10)
		self.but_ok = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		but_cancel = Estilos.MiBoton("../images/PNG-16/Exit.png","Cancelar")
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.add_action_widget(but_cancel,gtk.RESPONSE_CANCEL)
		self.show_all()

	def guardar(self):
		razon = self.entry_razon.get_text()
		comercial = self.entry_comercial.get_text()
		ruc = self.entry_ruc.get_text()
		direccion = self.entry_dir.get_text()
		telefono = self.entry_tele.get_text()
		celular = self.entry_cel.get_text()
		correo = self.entry_correo.get_text()
		web = self.entry_web.get_text()
		tipo = self.entry_tipo.get_id()
		moneda = self.combo_moneda.get_id()
		sql = "INSERT INTO proveedores (NOMBRE,COMERCIAL,RUC,DIRECCION,TELEFONO,CELULAR,CORREO,WEB,TIPO,MONEDA) VALUES ('%s','%s',%s,'%s','%s','%s','%s','%s',%d,%d)"%(razon,comercial,ruc,direccion,telefono,celular,correo,web,tipo,moneda)
		self.cursor.execute(sql)
		self.cerrar()

	def actualizar(self):
		razon = self.entry_razon.get_text()
		comercial = self.entry_comercial.get_text()
		ruc = self.entry_ruc.get_text()
		direccion = self.entry_dir.get_text()
		telefono = self.entry_tele.get_text()
		celular = self.entry_cel.get_text()
		correo = self.entry_correo.get_text()
		web = self.entry_web.get_text()
		tipo = self.entry_tipo.get_id()
		moneda = self.combo_moneda.get_id()
		sql = "UPDATE proveedores SET NOMBRE='%s',COMERCIAL='%s',RUC=%s,DIRECCION='%s',TELEFONO='%s',CELULAR='%s',CORREO='%s',WEB='%s',TIPO=%d,MONEDA=%d WHERE ID=%d"%(razon,comercial,ruc,direccion,telefono,celular,correo,web,tipo,moneda,self.id)
		self.cursor.execute(sql)
		self.cerrar()

	def leer(self,id):
		self.id = id
		sql = "SELECT NOMBRE,COMERCIAL,RUC,DIRECCION,TELEFONO,CELULAR,CORREO,WEB,TIPO FROM proveedores WHERE ID=%d"%id
		self.cursor.execute(sql)
		razon,comercial,ruc,direccion,telefono,celular,correo,web,tipo = self.cursor.fetchone()
		self.entry_razon.set_text(razon)
		self.entry_comercial.set_text(comercial)
		self.entry_ruc.set_text(str(ruc))
		self.entry_dir.set_text(direccion)
		self.entry_tele.set_text(telefono)
		self.entry_cel.set_text(celular)
		self.entry_web.set_text(web)
		self.entry_tipo.set_id(tipo)

	def cerrar(self):
		self.destroy()


if __name__ == '__main__':
	import Consultas
	consultas = Consultas.Conectar()
	v = Ventana(consultas)
	gtk.main()
