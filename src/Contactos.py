#! /usr/bin/python
#! -*- encoding: utf8 -*-

import gtk
import Consultas
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
		self.set_title("Contactos")
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
		columnas = ("NOMBRE","AREA","CELULAR","TELEFONO","CORREO","EMPRESA")
		self.model = gtk.ListStore(str,str,str,str,str,str,int)
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
			sql = "SELECT contactos.NOMBRE,contactos.AREA,contactos.CELULAR,IF(contactos.TELF='',clientes.TELEFONO,CONCAT(clientes.TELEFONO,' Anexo ',contactos.TELF)),contactos.CORREO,clientes.COMERCIAL,contactos.ID FROM contactos JOIN clientes ON clientes.ID = contactos.EMPRESA ORDER BY clientes.COMERCIAL ASC,contactos.NOMBRE ASC"
		else:
			sql = "SELECT contactos.NOMBRE,contactos.AREA,contactos.CELULAR,IF(contactos.TELF='',clientes.TELEFONO,CONCAT(clientes.TELEFONO,' Anexo ',contactos.TELF)),contactos.CORREO,clientes.COMERCIAL,contactos.ID FROM contactos JOIN clientes ON clientes.ID = contactos.EMPRESA WHERE contactos.NOMBRE LIKE '%s' OR clientes.COMERCIAL LIKE '%s' OR clientes.NOMBRE LIKE '%s' ORDER BY clientes.COMERCIAL ASC,contactos.NOMBRE ASC"%('%'+texto+'%','%'+texto+'%','%'+texto+'%')
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
			self.model.append(item)

	def on_row_activated(self,widget,path,column):
		codigo = self.model[path][0]
		self.abrir(codigo)

	def delete(self,codigo):
		path, column = self.treeview.get_cursor()
		dialog = Estilos.DialogoSN('¡Atención!','¿Está seguro de borrar el contacto?')
		if dialog.run() == gtk.RESPONSE_OK:
			sql = "DELETE FROM contactos WHERE ID=%d"%self.model[path][6]
			self.cursor.execute(sql)
			self.buscar()
		dialog.cerrar()

	def editar(self,widget):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[path][6])
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
		self.set_title("Nueva Contacto")
		frame_p = gtk.Frame()
		frame_p.set_border_width(2)
		self.vbox.pack_start(frame_p)
		tabla_datos = gtk.Table(4,7,False)
		frame_p.add(tabla_datos)
		label_cargo = gtk.Label("Nombre Formal:")
		tabla_datos.attach(label_cargo,0,1,0,1,gtk.SHRINK,gtk.SHRINK)
                self.entry_cargo = gtk.Entry()
		tabla_datos.attach(self.entry_cargo,1,4,0,1)
                label_nombre =  gtk.Label("Nombre Completo:")
		tabla_datos.attach(label_nombre,0,1,1,2,gtk.SHRINK,gtk.SHRINK)
                self.entry_nombre = gtk.Entry()
		tabla_datos.attach(self.entry_nombre,1,4,1,2)
		label_area = gtk.Label("Área:")
		label_area.set_size_request(120,25)
		tabla_datos.attach(label_area,0,1,2,3,gtk.SHRINK,gtk.SHRINK)
		self.entry_area = gtk.Entry()
		tabla_datos.attach(self.entry_area,1,4,2,3)
		label_telf = gtk.Label("Celular:")
		tabla_datos.attach(label_telf,0,1,3,4,gtk.SHRINK,gtk.SHRINK)
		self.entry_telf = gtk.Entry()
		tabla_datos.attach(self.entry_telf,1,2,3,4)
		label_anexo = gtk.Label("Anexo:")
		tabla_datos.attach(label_anexo,2,3,3,4,gtk.SHRINK,gtk.SHRINK)
		self.entry_anexo = gtk.Entry()
		tabla_datos.attach(self.entry_anexo,3,4,3,4)
		label_correo= gtk.Label("Correo:")
		tabla_datos.attach(label_correo,0,1,4,5,gtk.SHRINK,gtk.SHRINK)
		self.entry_correo = gtk.Entry()
		tabla_datos.attach(self.entry_correo,1,4,4,5)
		label_empresa = gtk.Label("Empresa:")
		tabla_datos.attach(label_empresa,0,1,5,6,gtk.SHRINK,gtk.SHRINK)
		self.combo_empresa = Estilos.ComboButton(self.cursor)
		tabla_datos.attach(self.combo_empresa,1,4,5,6)
		hbox_checks = gtk.HBox(True,0)
		tabla_datos.attach(hbox_checks,0,4,6,7)
		self.check_ate = gtk.RadioButton(None,'Atención:')
		hbox_checks.pack_start(self.check_ate)
		self.check_cc = gtk.RadioButton(self.check_ate,'C.C.:')
		hbox_checks.pack_start(self.check_cc)
		self.check_cco = gtk.RadioButton(self.check_ate,'C.C.O.:')
		hbox_checks.pack_start(self.check_cco)
		self.check_fact = gtk.CheckButton('Factura:')
		hbox_checks.pack_start(self.check_fact)
		self.combo_empresa.sql("SELECT ID,COMERCIAL FROM clientes",0)
		self.but_ok = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		but_cancel = Estilos.MiBoton("../images/PNG-16/Exit.png","Cancelar")
                self.entry_cargo.connect('focus-out-event', self.copiar_nombre)
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.add_action_widget(but_cancel,gtk.RESPONSE_CANCEL)
		self.show_all()
        
        def copiar_nombre(self,widget,event):
          self.entry_nombre.set_text(widget.get_text())

	def guardar(self):
		nombre = self.entry_nombre.get_text()
                cargo = self.entry_cargo.get_text()
		area= self.entry_area.get_text()
		telf = self.entry_telf.get_text()
		anexo = self.entry_anexo.get_text()
		correo = self.entry_correo.get_text()
		empresa = self.combo_empresa.get_id()
		ate = self.check_ate.get_active()
		cc = self.check_cc.get_active()
		cco = self.check_cco.get_active()
		fact = self.check_fact.get_active()
		sql = "INSERT INTO contactos (NOMBRE,CARGO,AREA,CELULAR,TELF,CORREO,EMPRESA,ATE,CC,CCO,FACT) VALUES ('%s','%s','%s','%s','%s','%s',%d,%d,%d,%d,%d)"%(nombre,cargo,area,telf,anexo,correo,empresa,ate,cc,cco,fact)
		self.cursor.execute(sql)
		self.cerrar()

	def actualizar(self):
		nombre = self.entry_nombre.get_text()
                cargo = self.entry_cargo.get_text()
		area= self.entry_area.get_text()
		telf = self.entry_telf.get_text()
		anexo = self.entry_anexo.get_text()
		correo = self.entry_correo.get_text()
		empresa = self.combo_empresa.get_id()
		ate = self.check_ate.get_active()
		cc = self.check_cc.get_active()
		cco = self.check_cco.get_active()
		fact = self.check_fact.get_active()
		sql = "UPDATE contactos SET NOMBRE='%s',CARGO='%s',AREA='%s',CELULAR='%s',TELF='%s',CORREO='%s',EMPRESA=%d,ATE=%d,CC=%d,CCO=%d,FACT=%d WHERE ID=%d"%(nombre,cargo,area,telf,anexo,correo,empresa,ate,cc,cco,fact,self.id)
		self.cursor.execute(sql)
		self.cerrar()

	def leer(self,id):
		self.id = id
		sql = "SELECT NOMBRE,CARGO,AREA,CELULAR,TELF,CORREO,EMPRESA,ATE,CC,CCO,FACT FROM contactos WHERE ID=%d"%id
		self.cursor.execute(sql)
		nombre,cargo,area,celular,telf,correo,empresa,ate,cc,cco,fact = self.cursor.fetchone()
		self.entry_nombre.set_text(nombre)
                self.entry_cargo.set_text(cargo)
		self.entry_area.set_text(area)
		self.entry_telf.set_text(celular)
		self.entry_anexo.set_text(telf)
		self.entry_correo.set_text(correo)
		self.combo_empresa.set_id(empresa)
		self.check_ate.set_active(ate)
		self.check_cc.set_active(cc)
		self.check_cco.set_active(cco)
		self.check_fact.set_active(fact)

	def set_empresa(self,id_empresa):
		self.combo_empresa.set_id(id_empresa)

	def cerrar(self):
		self.destroy()


if __name__ == '__main__':
	consulta = Consultas.Conectar()
	v = Ventana(consulta)
	gtk.main()

