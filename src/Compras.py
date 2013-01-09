#! /usr/bin/python
#! -*- encoding: utf8 -*-
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="danielypamela"
__date__ ="$07-nov-2011 18:07:53$"

import gtk
import Estilos
import gobject
import Proveedores
from decimal import Decimal

class Ventana(gtk.Window):
	def __init__(self,consulta):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = consulta.cursor
		self.set_title("Compras")
		vbox_main = gtk.VBox(False,0)
		self.add(vbox_main)
		tabla_controles = gtk.Table(8,5,False)
		vbox_main.pack_start(tabla_controles)
		label_buscar = gtk.Label("Buscar:")
		tabla_controles.attach(label_buscar,0,1,0,1)
		self.entry_buscar = gtk.Entry()
		tabla_controles.attach(self.entry_buscar,1,2,0,1)
		label_periodo = gtk.Label("Periodo:")
		tabla_controles.attach(label_periodo,2,3,0,1)
		self.entry_periodo = Estilos.EntryPeriodo()
		tabla_controles.attach(self.entry_periodo,3,4,0,1)
		but_editar= Estilos.MiBoton("../images/PNG-16/Modify.png","Modificar")
		tabla_controles.attach(but_editar,4,5,0,1)
		but_delete = Estilos.MiBoton("../images/PNG-16/Delete.png","Eliminar")
		tabla_controles.attach(but_delete,5,6,0,1)
		but_nuevo = Estilos.MiBoton("../images/PNG-16/Add.png","Nuevo")
		tabla_controles.attach(but_nuevo,6,7,0,1)
		but_buscar = Estilos.MiBoton("../images/PNG-16/Search.png","Buscar")
		tabla_controles.attach(but_buscar,7,8,0,1)
		columnas = ("ID","FECHA","SERIE","COMERCIAL","PRECIO")
		self.model = gtk.ListStore(int,str,str,str,str,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name,renderer,text=i)
			self.treeview.append_column(column)
			if i==3:
				renderer.set_property('width-chars',30)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(700,300)
		vbox_main.pack_start(sw)
		sw.add(self.treeview)
		self.show_all()

		self.entry_buscar.connect('changed',self.buscar)
		self.entry_periodo.entry.connect('changed',self.buscar)
		but_editar.connect('clicked',self.editar)
		self.treeview.connect('row-activated',self.on_row_activated)
		but_delete.connect('clicked',self.delete)
		but_nuevo.connect('clicked',self.nuevo)
		but_buscar.connect('clicked',self.consulta)
		self.buscar()
		self.treeview.set_cursor(0)

	def consulta(self,widget):
		nueva = Consulta(self.cursor)

	def buscar(self,widget=None):
		self.model.clear()
		texto = self.entry_buscar.get_text()
		periodo = self.entry_periodo.get_text()
		if texto == "":
			sql = "SELECT compras.IDP,compras.DIA,CONCAT(compras.SERIE,'-',compras.NUM),proveedores.COMERCIAL,compras.TOTAL,compras.ID FROM compras JOIN proveedores ON proveedores.RUC=compras.RUC WHERE compras.MES='%s' ORDER BY compras.ID ASC"%(periodo)
		else:
			sql = "SELECT compras.IDP,compras.DIA,CONCAT(compras.SERIE,'-',compras.NUM),proveedores.COMERCIAL,compras.TOTAL,compras.ID FROM compras JOIN proveedores ON proveedores.RUC=compras.RUC JOIN comprasitems ON compras.ID=comprasitems.FACTURA WHERE (proveedores.COMERCIAL LIKE '%s' OR proveedores.RAZON LIKE '%s' OR comprasitems.DESCRIPCION LIKE '%s') AND compras.MES='%s' ORDER BY compras.ID ASC"%('%'+texto+'%','%'+texto+'%','%'+texto+'%',periodo)
		print sql
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
			self.model.append(item)

	def on_row_activated(self,widget,path,column):
		codigo = self.model[path][0]
		self.editar(codigo)

	def delete(self,codigo):
		path, column = self.treeview.get_cursor()
		dialog = Estilos.DialogoSN('¡Atención!','¿Está seguro de borrar la factura?')
		if dialog.run() == gtk.RESPONSE_OK:
			sql = "DELETE FROM compras WHERE ID=%d"%self.model[path][5]
			self.cursor.execute(sql)
			self.buscar()
		dialog.cerrar()

	def editar(self,widget):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[path][5])
		if nueva.run() == gtk.RESPONSE_OK:
			if self.contra():
				return
			nueva.actualizar()
			self.buscar()
		nueva.cerrar()

	def nuevo(self,widget):
		if self.contra():
			return
		nueva = Nueva(self.cursor)
		while True:
			if nueva.run() == gtk.RESPONSE_OK:
				nueva.guardar()
				self.buscar()
				nueva.redibujar()
			else:
				break
		nueva.cerrar()

	def contra(self):
		psw = Estilos.Contra()
		if psw.run() == gtk.RESPONSE_OK:
			sql = "SELECT FINANZAS FROM personal WHERE PASS='%s'"%psw.psw
			self.cursor.execute(sql)
			if self.cursor.rowcount == 0:
				alerta = Estilos.Alerta('Error','Contraseña equivocada.')
				if alerta.run() == gtk.RESPONSE_OK:
					pass
				alerta.destroy()
				psw.destroy()
				return True
			elif not self.cursor.fetchone()[0]:
				psw.destroy()
				alerta = Estilos.Alerta('Error','No tiene los privilegios para\nhacer esta tarea.')
				if alerta.run() == gtk.RESPONSE_OK:
					pass
				alerta.destroy()
				psw.destroy()
				return True
		psw.destroy()

class Consulta(gtk.Window):
	def __init__(self,cursor):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = cursor
		self.set_title("Detalle de Compras")
		vbox_main = gtk.VBox(False,0)
		self.add(vbox_main)
		tabla_controles = gtk.Table(2,1,False)
		vbox_main.pack_start(tabla_controles)
		label_buscar = gtk.Label("Buscar:")
		tabla_controles.attach(label_buscar,0,1,0,1)
		self.entry_buscar = gtk.Entry()
		tabla_controles.attach(self.entry_buscar,1,2,0,1)
		columnas = ("PERIODO","ID","FECHA","DESCRIPCION","PRECIO")
		self.model = gtk.ListStore(str,int,str,str,str,int)
		self.treeview = gtk.TreeView(self.model)
		i = 0
		for name in columnas:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(name,renderer,text=i)
			self.treeview.append_column(column)
			if i==3:
				renderer.set_property('width-chars',30)
			i+=1
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(700,300)
		vbox_main.pack_start(sw)
		sw.add(self.treeview)
		self.show_all()

		self.entry_buscar.connect('changed',self.buscar)
		self.treeview.connect('row-activated',self.on_row_activated)
		self.buscar()
		self.treeview.set_cursor(0)

	def buscar(self,widget=None):
		self.model.clear()
		texto = self.entry_buscar.get_text()
		if texto == "":
			sql = "SELECT compras.MES,compras.IDp,compras.DIA,comprasitems.DESCRIPCION,comprasitems.PRECIO,compras.ID FROM comprasitems JOIN compras ON compras.ID = comprasitems.FACTURA ORDER BY comprasitems.ID DESC LIMIT 200"
		else:
			sql = "SELECT compras.MES,compras.IDp,compras.DIA,comprasitems.DESCRIPCION,comprasitems.PRECIO,compras.ID FROM comprasitems JOIN compras ON compras.ID = comprasitems.FACTURA WHERE comprasitems.DESCRIPCION LIKE '%s' ORDER BY comprasitems.ID DESC LIMIT 200"%('%'+texto+'%')
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		for item in items:
			self.model.append(item)

	def on_row_activated(self,widget,path,column):
		codigo = self.model[path][0]
		self.editar(codigo)

	def delete(self,codigo):
		path, column = self.treeview.get_cursor()
		dialog = Estilos.DialogoSN('¡Atención!','¿Está seguro de borrar la factura?')
		if dialog.run() == gtk.RESPONSE_OK:
			sql = "DELETE FROM compras WHERE ID=%d"%self.model[path][5]
			self.cursor.execute(sql)
			self.buscar()
		dialog.cerrar()

	def editar(self,widget):
		path, column = self.treeview.get_cursor()
		nueva = Nueva(self.cursor)
		nueva.leer(self.model[path][5])
		if nueva.run() == gtk.RESPONSE_OK:
			if self.contra():
				return
			nueva.actualizar()
			self.buscar()
		nueva.cerrar()

	def nuevo(self,widget):
		if self.contra():
			return
		nueva = Nueva(self.cursor)
		while True:
			if nueva.run() == gtk.RESPONSE_OK:
				nueva.guardar()
				self.buscar()
				nueva.redibujar()
			else:
				break
		nueva.cerrar()

	def contra(self):
		psw = Estilos.Contra()
		if psw.run() == gtk.RESPONSE_OK:
			sql = "SELECT FINANZAS FROM personal WHERE PASS='%s'"%psw.psw
			self.cursor.execute(sql)
			if self.cursor.rowcount == 0:
				alerta = Estilos.Alerta('Error','Contraseña equivocada.')
				if alerta.run() == gtk.RESPONSE_OK:
					pass
				alerta.destroy()
				psw.destroy()
				return True
			elif not self.cursor.fetchone()[0]:
				psw.destroy()
				alerta = Estilos.Alerta('Error','No tiene los privilegios para\nhacer esta tarea.')
				if alerta.run() == gtk.RESPONSE_OK:
					pass
				alerta.destroy()
				psw.destroy()
				return True
		psw.destroy()


class Nueva(gtk.Dialog):
	def __init__(self,cursor):
		gtk.Dialog.__init__(self)
		self.cursor = cursor
		self.set_title("Nueva Factura de Compra")
		frame_p = gtk.Frame()
		frame_p.set_border_width(2)
		self.vbox.pack_start(frame_p)
		tabla_datos = gtk.Table(4,9,False)
		frame_p.add(tabla_datos)
		label_periodo = gtk.Label("Periodo:")
		tabla_datos.attach(label_periodo,0,1,0,1,gtk.SHRINK,gtk.SHRINK)
		self.entry_periodo = Estilos.EntryPeriodo()
		tabla_datos.attach(self.entry_periodo,1,2,0,1)
		self.entry_idp = gtk.Entry()
		self.entry_idp.set_sensitive(False)
		self.entry_idp.set_size_request(100,27)
		tabla_datos.attach(self.entry_idp,2,3,0,1,gtk.SHRINK,gtk.SHRINK)
		self.combo_personal = Estilos.ComboButton(self.cursor)
		self.combo_personal.sql("SELECT ID,NOMBRE FROM personal",1)
		tabla_datos.attach(self.combo_personal,3,4,0,1)
		label_ruc = gtk.Label("RUC:")
		tabla_datos.attach(label_ruc,0,1,1,2,gtk.SHRINK,gtk.SHRINK)
		self.entry_ruc = Estilos.EntryRUC(self.cursor)
		self.entry_ruc.connect('ok',self.leer_ruc)
		self.entry_ruc.set_size_request(100,27)
		tabla_datos.attach(self.entry_ruc,1,2,1,2)
		self.label_razon = gtk.Label("--")
		tabla_datos.attach(self.label_razon,2,4,1,2,gtk.SHRINK,gtk.SHRINK)
		label_tipo = gtk.Label("Tipo:")
		tabla_datos.attach(label_tipo,0,1,2,3,gtk.SHRINK,gtk.SHRINK)
		self.combo_tipo = Estilos.ComboButton(self.cursor)
		self.combo_tipo.items(((1,"Factura"),(2,"Boleta"),(3,"Nota de Crédito"),(4,"Nota de Contabilidad")))
		self.combo_tipo.set_id(1)
		self.combo_tipo.set_size_request(100,30)
		tabla_datos.attach(self.combo_tipo,1,2,2,3)
		self.entry_serie = gtk.Entry()
		self.entry_serie.set_size_request(100,27)
		tabla_datos.attach(self.entry_serie,2,3,2,3)
		self.entry_serie.connect('activate',lambda e: self.do_move_focus(self,gtk.DIR_TAB_FORWARD))
		self.entry_numero = gtk.Entry()
		self.entry_numero.set_size_request(100,27)
		self.entry_numero.connect('activate',lambda e: self.do_move_focus(self,gtk.DIR_TAB_FORWARD))
		tabla_datos.attach(self.entry_numero,3,4,2,3)
		label_dia = gtk.Label("Día:")
		tabla_datos.attach(label_dia,0,1,3,4,gtk.SHRINK,gtk.SHRINK)
		self.entry_dia = Estilos.EntryDia(self.cursor,self.entry_periodo)
		self.entry_dia.connect('focus-out-event',self.leer_dia)
		self.entry_dia.set_size_request(100,27)
		tabla_datos.attach(self.entry_dia,1,2,3,4)
		self.label_dia = gtk.Label()
		tabla_datos.attach(self.label_dia,2,3,3,4)
		self.label_tk = gtk.Label()
		tabla_datos.attach(self.label_tk,3,4,3,4)
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		sw.set_size_request(400,100)
		self.model = gtk.ListStore(int,str,str,str,str,str,int)
		columnas = ("ITEM","CANT","DESCRIPCIÓN","P.UNIT","P.TOTAL","TRABAJO")
		self.treeview = gtk.TreeView(self.model)
		self.model_cot = gtk.ListStore(int,str)
		sql = "SELECT ID,NOMBRE FROM cotizaciones WHERE PAGADO=0"
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		self.diccionario = {}
		for row in items:
			self.model_cot.append(row)
			self.diccionario[row[1]]=row[0]
		for i,nombre in enumerate(columnas):
			renderer = gtk.CellRendererText()
			if i==0 or i==4:
				renderer.set_property('editable',False)
			elif i==5:
				renderer = gtk.CellRendererCombo()
				renderer.set_property('model',self.model_cot)
				renderer.set_property('text-column',1)
				renderer.set_property('editable',True)
				renderer.set_property('width-chars',10)
				renderer.connect('edited',self.edited_combo,self.model_cot,i)
			else:
				renderer.set_property('editable',True)
				renderer.connect('edited',self.edited_cell,i)
			column = gtk.TreeViewColumn(nombre,renderer,text=i)
			self.treeview.append_column(column)
		sw.add(self.treeview)
		tabla_datos.attach(sw,0,4,4,5,gtk.EXPAND,gtk.SHRINK)
		hbox_sw = gtk.HBox(False,0)
		self.but_mas = Estilos.MiBoton('../images/PNG-16/Add.png','Añadir')
		self.but_borrar = Estilos.MiBoton('../images/PNG-16/Delete.png','Eliminar')
		self.but_borrar.set_sensitive(False)
		self.but_mas.connect('clicked',self.mas)
		self.but_borrar.connect('clicked',self.borrar)
		hbox_sw.pack_start(self.but_mas)
		hbox_sw.pack_start(self.but_borrar)
		tabla_datos.attach(hbox_sw,0,4,5,6,gtk.SHRINK,gtk.SHRINK)
		label_neto = gtk.Label("Neto:")
		tabla_datos.attach(label_neto,0,1,6,7,gtk.SHRINK,gtk.SHRINK)
		self.entry_neto = gtk.Entry()
		self.entry_neto.set_size_request(100,27)
		tabla_datos.attach(self.entry_neto,1,2,6,7)
		label_ngravado = gtk.Label("No gravado:")
		tabla_datos.attach(label_ngravado,2,3,6,7,gtk.SHRINK,gtk.SHRINK)
		self.entry_ngravado = gtk.Entry()
		self.entry_ngravado.set_size_request(100,27)
		tabla_datos.attach(self.entry_ngravado,3,4,6,7)
		label_gravado = gtk.Label("Gravado:")
		tabla_datos.attach(label_gravado,0,1,7,8,gtk.SHRINK,gtk.SHRINK)
		self.entry_gravado = gtk.Entry()
		self.entry_gravado.set_size_request(100,27)
		tabla_datos.attach(self.entry_gravado,1,2,7,8)
		label_igv= gtk.Label("IGV:")
		tabla_datos.attach(label_igv,2,3,7,8,gtk.SHRINK,gtk.SHRINK)
		self.entry_igv = gtk.Entry()
		self.entry_igv.set_size_request(100,27)
		tabla_datos.attach(self.entry_igv,3,4,7,8)
		label_total= gtk.Label("Total:")
		tabla_datos.attach(label_total,0,1,8,9,gtk.SHRINK,gtk.SHRINK)
		self.entry_total = gtk.Entry()
		self.entry_total.set_size_request(100,27)
		tabla_datos.attach(self.entry_total,1,2,8,9)
		label_moneda= gtk.Label("Moneda:")
		tabla_datos.attach(label_moneda,2,3,8,9,gtk.SHRINK,gtk.SHRINK)
		self.combo_moneda = Estilos.ComboButton(self.cursor)
		self.combo_moneda.sql("SELECT ID,NOMBRE FROM monedas",0)
		self.combo_moneda.set_id(1)
		tabla_datos.attach(self.combo_moneda,3,4,8,9)
		self.but_tipo = Estilos.ComboButton(self.cursor)
		self.but_tipo.items(((1,"Neto"),(2,"Total"),(3,"N-NG"),(4,"Tot-NG"),(5,"Aduana"),(6,"Selva")))
		self.but_tipo.set_id(1)
		self.but_ok = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		but_cancel = Estilos.MiBoton("../images/PNG-16/Exit.png","Cancelar")
		self.action_area.pack_start(self.but_tipo)
		self.add_action_widget(self.but_ok,gtk.RESPONSE_OK)
		self.add_action_widget(but_cancel,gtk.RESPONSE_CANCEL)
		self.but_tipo.connect('changed',self.cambiar_tipo)
		self.entry_neto.connect('key-release-event',self.leer_neto)
		self.entry_ngravado.connect('key-release-event',self.leer_ngravado)
		self.entry_periodo.entry.connect('changed',self.redibujar)
		self.combo_tipo.connect('changed',self.cambio_doc)
		self.tipo = 0
		self.redibujar()
		self.show_all()

	def mas(self,widget):
		for row in self.model:
			i = row[0]
		self.model.append((i+1,1,'','0','0',0))
		self.but_borrar.set_sensitive(True)

	def borrar(self,widget):
		path,column = self.treeview.get_cursor()
		model = self.treeview.get_model()
		iter = model.get_iter(path)
		self.model.remove(iter)
		if len(self.model)==1:
			self.but_borrar.set_sensitive(False)

	def edited_combo(self,cell,path,iter,model,column):
		text = u'%s'%iter
		try:
			self.model[path][6] = self.diccionario[text]
			self.model[path][5] = text
		except:
			self.model[path][6] = 0
			self.model[path][5] = 'Ninguno'
			
	def cambio_doc(self,widget):
	  tipo = widget.get_id()
	  if tipo == 2:
	    self.tipo = 6
	  self.leer_tipo()
	  self.cambiar_tipo(None)


	def edited_cell(self,cell,path,new_text,column):
		if self.tipo == 0:
			return
		self.model[path][column] = new_text
		if column==3:
			total = (Decimal(new_text)*Decimal(self.model[path][1])).quantize(Decimal('0.01'))
			self.model[path][4] = str(total)
			total = Decimal('0.00')
			for row in self.model:
				total += Decimal(row[4])
			self.valor = total
			if self.tipo == 1:# solo neto
				self.entry_neto.set_text(str(self.valor))
				self.leer_neto(self.entry_neto)
			elif self.tipo == 2:# solo total
				self.entry_total.set_text(str(self.valor))
				self.leer_total(self.entry_total)
			elif self.tipo == 3:# Neto - Ngravado
				self.entry_neto.set_text(str(self.valor))
				self.leer_neto(self.entry_neto)
			elif self.tipo == 4:# Total - Ngravado
				self.entry_total.set_text(str(self.valor))
				self.leer_total(self.entry_total)
			elif self.tipo == 6:# Selva
				self.entry_neto.set_text(str(self.valor))
				self.entry_ngravado.set_text(str(self.valor))
				self.entry_total.set_text(str(self.valor))
		elif column==1:
			total = (Decimal(new_text)*Decimal(self.model[path][3])).quantize(Decimal('0.01'))
			self.model[path][4] = str(total)
			total = Decimal('0.00')
			for row in self.model:
				total += Decimal(row[4])
			self.valor = total
			if self.tipo == 1:# solo neto
				self.entry_neto.set_text(str(self.valor))
				self.leer_neto(self.entry_neto)
			elif self.tipo == 2:# solo total
				self.entry_total.set_text(str(self.valor))
				self.leer_total(self.entry_total)
			elif self.tipo == 3:# Neto - Ngravado
				self.entry_neto.set_text(str(self.valor))
				self.leer_neto(self.entry_neto)
			elif self.tipo == 4:# Total - Ngravado
				self.entry_total.set_text(str(self.valor))
				self.leer_total(self.entry_total)
			elif self.tipo == 6:# Selva
				self.entry_neto.set_text(str(self.valor))
				self.entry_ngravado.set_text(str(self.valor))
				self.entry_total.set_text(str(self.valor))
				self.entry_igv.set_text('0.00')

	def cambiar_tipo(self,widget):
	  if self.combo_tipo.get_id() == 1:
	    	self.tipo = self.but_tipo.get_id()
		self.entry_ruc.tipo = self.tipo
		self.leer_ruc(self.entry_ruc)
		if self.tipo == 1:#sólo Neto
			self.entry_neto.set_text(str(self.valor))
			self.leer_neto(self.entry_neto)
		elif self.tipo == 2:# sólo Total
			self.entry_total.set_text(str(self.valor))
			self.leer_total(self.entry_total)
		elif self.tipo == 3:# Neto - Ngravado
			self.entry_neto.set_text(str(self.valor))
			self.leer_neto(self.entry_neto)
		elif self.tipo == 4:# Total - Ngravado
			self.entry_total.set_text(str(self.valor))
			self.leer_total(self.entry_total)
		elif self.tipo == 6:# Selva
			self.entry_neto.set_text(str(self.valor))
			self.entry_ngravado.set_text(str(self.valor))
			self.entry_total.set_text(str(self.valor))
			self.entry_gravado.set_text('0.00')
			self.entry.igv.set_text('0.00')
			
		

	def leer_ngravado(self,widget,event=None):
		texto = widget.get_text()
		try:
			valor = Decimal(texto)
		except:
			widget.set_text('')
		else:
			if self.tipo == 3: #NETO - NGRAVADO
				ngravado  = Decimal(self.entry_ngravado.get_text())
				neto = Decimal(self.entry_neto.get_text())
				gravado = neto-valor
				igv = (gravado*Decimal('0.18')).quantize(Decimal('0.01'))
				self.entry_gravado.set_text(str(gravado))
				self.entry_igv.set_text(str(igv))
				total = neto+igv
				self.entry_total.set_text(str(total))
			if self.tipo ==4:#Total - ngravado
				total = Decimal(self.entry_total.get_text())
				gravadoyigv = total-valor
				gravado = (gravadoyigv/Decimal('1.18')).quantize(Decimal('0.01'))
				igv = gravadoyigv-gravado
				neto = valor+gravado
				self.entry_neto.set_text(str(neto))
				self.entry_gravado.set_text(str(gravado))
				self.entry_igv.set_text(str(igv))

	def leer_total(self,widget,event=None):
		texto = widget.get_text()
		try:
			valor = Decimal(texto)
		except:
			widget.set_text('')
		else:
			if self.tipo == 2:
				neto = (valor/Decimal('1.18')).quantize(Decimal('0.01'))
				igv = valor-neto
				self.entry_neto.set_text(str(neto))
				self.entry_gravado.set_text(str(neto))
				self.entry_igv.set_text(str(igv))
			if self.tipo ==4:#Total - ngravado
				ngravado = Decimal(self.entry_ngravado.get_text())
				gravadoyigv = valor - ngravado
				gravado = (gravadoyigv/Decimal('1.18')).quantize(Decimal('0.01'))
				igv = gravadoyigv-gravado
				neto = ngravado + gravado
				self.entry_neto.set_text(str(neto))
				self.entry_gravado.set_text(str(gravado))
				self.entry_igv.set_text(str(igv))

	def leer_neto(self,widget,event=None):
		texto = widget.get_text()
		try:
			valor = Decimal(texto)
		except:
			widget.set_text('')
		else:
			if self.tipo == 1:#solo neto
				self.entry_gravado.set_text(texto)
				igv = (valor*Decimal('0.18')).quantize(Decimal('0.01'))
				self.entry_igv.set_text(str(igv))
				self.entry_total.set_text(str(igv+valor))
			elif self.tipo == 3:#neto - ngravado
				ngravado = Decimal(self.entry_ngravado.get_text())
				gravado = valor-ngravado
				self.entry_gravado.set_text(str(gravado))
				igv = (gravado*Decimal('0.18')).quantize(Decimal('0.01'))
				self.entry_igv.set_text(str(igv))
				self.entry_total.set_text(str(igv+valor))
			elif self.tipo == 5:#aduana
				self.entry_gravado.set_text(texto)
				igv = (valor*Decimal('0.18')).quantize(Decimal('0.01'))+self.valor
				self.entry_igv.set_text(str(igv))
				self.entry_total.set_text(str(igv+valor))


	def leer_ruc(self,widget):
		self.label_razon.set_text(widget.razon)
		self.but_tipo.set_id(widget.tipo)
		if self.combo_tipo.get_id() == 1:
		  self.tipo = widget.tipo
		self.combo_moneda.set_id(widget.moneda)
		self.but_mas.set_sensitive(True)
		self.leer_tipo()
		
	def leer_tipo(self):
		if self.tipo == 0:
			self.entry_neto.set_sensitive(False)
			self.entry_ngravado.set_sensitive(False)
			self.entry_gravado.set_sensitive(False)
			self.entry_igv.set_sensitive(False)
			self.entry_total.set_sensitive(False)
		elif self.tipo == 1 or self.tipo == 2:#sólo Neto, sólo Total
			self.entry_neto.set_sensitive(False)
			self.entry_ngravado.set_sensitive(False)
			self.entry_gravado.set_sensitive(False)
			self.entry_igv.set_sensitive(False)
			self.entry_total.set_sensitive(False)
			self.entry_ngravado.set_text('0.00')
		elif self.tipo == 3: #NETO - Ngravado
			self.entry_neto.set_sensitive(False)
			self.entry_ngravado.set_sensitive(True)
			self.entry_gravado.set_sensitive(False)
			self.entry_igv.set_sensitive(False)
			self.entry_total.set_sensitive(False)
		elif self.tipo == 4: #TOTAL - Ngravado
			self.entry_neto.set_sensitive(False)
			self.entry_ngravado.set_sensitive(True)
			self.entry_gravado.set_sensitive(False)
			self.entry_igv.set_sensitive(False)
			self.entry_total.set_sensitive(False)
		elif self.tipo == 5: #Aduana
			self.model[0][3] = 'Reintegro de Derechos'
			self.but_mas.set_sensitive(False)
			self.entry_neto.set_sensitive(True)
			self.entry_ngravado.set_sensitive(False)
			self.entry_gravado.set_sensitive(False)
			self.entry_igv.set_sensitive(False)
			self.entry_total.set_sensitive(False)
		elif self.tipo == 6: #Selva
			self.but_mas.set_sensitive(True)
			self.entry_neto.set_sensitive(False)
			self.entry_ngravado.set_sensitive(False)
			self.entry_gravado.set_sensitive(False)
			self.entry_igv.set_sensitive(False)
			self.entry_total.set_sensitive(False)

	def redibujar(self,widget=None):
		self.entry_neto.set_text('0.00')
		self.entry_ngravado.set_text('0.00')
		self.entry_gravado.set_text('0.00')
		self.entry_igv.set_text('0.00')
		self.entry_total.set_text('0.00')
		self.entry_neto.set_sensitive(False)
		self.entry_ngravado.set_sensitive(False)
		self.entry_gravado.set_sensitive(False)
		self.entry_igv.set_sensitive(False)
		self.entry_total.set_sensitive(False)
		self.valor = Decimal('0.00')
		self.model.clear()
		self.model.append((1,1,'','0','0','Ninguno',0))
		self.treeview.set_cursor_on_cell(0)
		sql = "SELECT IDP FROM compras WHERE mes='%s' ORDER BY IDP DESC LIMIT 1"%self.entry_periodo.get_text()
		self.cursor.execute(sql)
		if self.cursor.rowcount == 0:
			idp = 1
		else:
			idp = self.cursor.fetchone()[0]+1
		self.entry_idp.set_text(str(idp))
		self.set_focus(self.entry_ruc)
		self.entry_serie.set_text('')
		self.entry_numero.set_text('')
		self.entry_dia.set_text('')

	def leer_dia(self,widget,event):
		self.label_dia.set_text(widget.fecha)
		self.label_tk.set_text(str(widget.tk))

	def guardar(self):
		idp = self.entry_idp.get_text()
		mes = self.entry_periodo.get_text()
		ruc = self.entry_ruc.get_text()
		dia = self.label_dia.get_text()
		doc = self.combo_tipo.get_id()
		serie = self.entry_serie.get_text()
		num = self.entry_numero.get_text()
		moneda = self.combo_moneda.get_id()
		if moneda == 2:
			tk = self.label_tk.get_text()
		else:
			tk = '1.0'
		valor = self.entry_neto.get_text()
		ngravada = self.entry_ngravado.get_text()
		gravada = self.entry_gravado.get_text()
		igv = self.entry_igv.get_text()
		total = self.entry_total.get_text()
		personal = self.combo_personal.get_id()
		tipo = self.but_tipo.get_id()
		valores = idp,mes,ruc,dia,doc,serie,num,moneda,tk,valor,ngravada,gravada,igv,total,tipo,personal
		sql = "INSERT INTO compras (IDP,MES,RUC,DIA,TIPO,SERIE,NUM,MONEDA,TK,NETO,NGRAVADA,GRAVADA,IGV,TOTAL,CALCULO,PERSONAL) VALUES (%s,'%s',%s,'%s',%d,'%s','%s',%d,%s,%s,%s,%s,%s,%s,%d,%d)"%valores
		self.cursor.execute(sql)
		sql = "UPDATE proveedores SET TIPO=%d, MONEDA=%d WHERE RUC=%s"%(tipo,moneda,self.entry_ruc.get_text())
		self.cursor.execute(sql)
		sql = "SELECT ID FROM compras ORDER BY ID DESC LIMIT 1"
		self.cursor.execute(sql)
		id = self.cursor.fetchone()[0]
		for row in self.model:
			valores = id,row[1],row[2],row[3],row[6]
			sql = "INSERT INTO comprasitems (FACTURA,CANTIDAD,DESCRIPCION,PRECIO,COT) VALUES (%d,%s,'%s',%s,%d)"%valores
			self.cursor.execute(sql)
		nombre = self.label_razon.get_text()[:15]+' '+serie.zfill(3)+'-'+num.zfill(6)
		sql = "INSERT INTO cuentas (NOMBRE,MONTO,PERSONAL,FACTURA) VALUES ('%s',%s,%d,%d)"%(nombre,self.valor,personal,id)
		self.cursor.execute(sql)

	def actualizar(self):
		idp = self.entry_idp.get_text()
		mes = self.entry_periodo.get_text()
		ruc = self.entry_ruc.get_text()
		dia = self.label_dia.get_text()
		tipo = self.combo_tipo.get_id()
		serie = self.entry_serie.get_text()
		num = self.entry_numero.get_text()
		moneda = self.combo_moneda.get_id()
		if moneda == 2:
			tk = self.label_tk.get_text()
		else:
			tk = '1.0'
		valor = self.entry_neto.get_text()
		ngravada = self.entry_ngravado.get_text()
		gravada = self.entry_gravado.get_text()
		igv = self.entry_igv.get_text()
		total = self.entry_total.get_text()
		personal = self.combo_personal.get_id()
		valores = idp,mes,ruc,dia,tipo,serie,num,moneda,tk,valor,ngravada,gravada,igv,total,self.tipo,personal,self.id
		sql = "UPDATE compras SET IDP=%s,MES='%s',RUC=%s,DIA='%s',TIPO=%d,SERIE='%s',NUM='%s',MONEDA=%d,TK=%s,NETO=%s,NGRAVADA=%s,GRAVADA=%s,IGV=%s,TOTAL=%s,CALCULO=%d,PERSONAL=%d WHERE ID=%d"%valores
		self.cursor.execute(sql)
		sql = "UPDATE proveedores SET TIPO=%d, MONEDA=%d WHERE RUC=%s"%(self.tipo,moneda,self.entry_ruc.get_text())
		self.cursor.execute(sql)
		sql = "DELETE FROM comprasitems WHERE FACTURA=%d"%self.id
		self.cursor.execute(sql)
		for row in self.model:
			valores = self.id,row[1],row[2],row[3],row[6]
			sql = "INSERT INTO comprasitems (FACTURA,CANTIDAD,DESCRIPCION,PRECIO,COT) VALUES (%d,%s,'%s',%s,%d)"%valores
			self.cursor.execute(sql)
		nombre = self.label_razon.get_text()[:15]+' '+serie.zfill(3)+'-'+num.zfill(6)
		sql = "UPDATE cuentas SET NOMBRE='%s',MONTO=%s,PERSONAL=%d WHERE FACTURA=%d"%(nombre,self.valor,personal,self.id)
		self.cursor.execute(sql)

	def leer(self,id):
		self.id = id
		sql = "SELECT IDP,MES,RUC,DIA,TIPO,SERIE,NUM,MONEDA,TK,NETO,NGRAVADA,GRAVADA,IGV,TOTAL,CALCULO,PERSONAL FROM compras WHERE ID=%d"%id
		self.cursor.execute(sql)
		idp,mes,ruc,dia,tipo,serie,num,moneda,tk,valor,ngravada,gravada,igv,total,calculo,personal = self.cursor.fetchone()
		self.tipo = calculo
		self.entry_periodo.set_text(mes)
		self.entry_ruc.set_text(str(ruc))
		self.entry_ruc.teclas(self.entry_ruc,None)
		self.entry_dia.set_text(dia.strftime("%d-%m-%Y"))
		self.combo_tipo.set_id(tipo)
		self.entry_serie.set_text(serie)
		self.entry_numero.set_text(num)
		self.combo_moneda.set_id(moneda)
		self.entry_neto.set_text(str(valor))
		self.entry_ngravado.set_text(str(ngravada))
		self.entry_gravado.set_text(str(gravada))
		self.entry_igv.set_text(str(igv))
		self.entry_total.set_text(str(total))
		self.combo_personal.set_id(personal)
		self.entry_dia.teclas(self.entry_dia,None)
		self.leer_dia(self.entry_dia,None)
		self.entry_idp.set_text(str(idp))
		self.model.clear()
		sql = "SELECT comprasitems.CANTIDAD,comprasitems.DESCRIPCION,comprasitems.PRECIO,cotizaciones.NOMBRE,comprasitems.COT FROM comprasitems JOIN cotizaciones ON comprasitems.COT = cotizaciones.ID WHERE comprasitems.FACTURA=%d"%self.id
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		self.valor = Decimal('0.00')
		for i,row in enumerate(items):
			total = (Decimal(row[0])*Decimal(row[2])).quantize(Decimal('0.01'))
			self.model.append((i+1,row[0],row[1],row[2],str(total),row[3],row[4]))
			self.valor += total

	def cerrar(self):
		self.destroy()

if __name__ == '__main__':
	import Consultas
	consultas = Consultas.Conectar()
	v = Ventana(consultas)
	gtk.main()
