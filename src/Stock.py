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

class Ventana(gtk.Window):
  """ Clase Ventana Principal """
  def __init__ (self,consulta):
    """ Class initialiser """
    gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
    self.consulta = consulta
    self.cursor = consulta.cursor
    self.host = consulta.www
    self.set_title("Stock")
    hbox_main = gtk.HBox(True,0)
    vbox_main = gtk.VBox(False,0)
    hbox_main.pack_start(vbox_main)
    self.vbox_www = gtk.VBox()
    hbox_main.pack_start(self.vbox_www)
    sw_www = gtk.ScrolledWindow()
    sw_www.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    sw_www.set_size_request(595,500)
    hbox_www = gtk.HBox()
    self.vbox_www.pack_start(hbox_www)
    but_print = Estilos.MiBoton('../images/PNG-16/Print.png','Imprimir')
    but_enviar = Estilos.MiBoton('../images/PNG-16/Email.png','Enviar')
    self.but_oc = Estilos.MiBoton('../images/PNG-16/Save.png','O.C.')
    self.but_guia = Estilos.MiBoton('../images/PNG-16/Next.png','Guía de Sal.')
    self.but_factura = Estilos.MiBoton('../images/PNG-16/Modify.png','Facturar')
    hbox_www.pack_start(but_print)
    hbox_www.pack_start(but_enviar)
    hbox_www.pack_start(self.but_oc)
    hbox_www.pack_start(self.but_guia)
    hbox_www.pack_start(self.but_factura)
    but_print.connect('clicked',self.imprimir)
    but_enviar.connect('clicked',self.enviar)
    self.but_oc.connect('clicked',self.orden)
    self.but_guia.connect('clicked',self.guia)
    self.but_factura.connect('clicked',self.factura)
    self.vbox_www.pack_start(sw_www)
    self.www = webkit.WebView()
    self.www_frame = self.www.get_main_frame()
    sw_www.add(self.www)
    self.add(hbox_main)
    tabla_controles = gtk.Table(6,1,False)
    vbox_main.pack_start(tabla_controles,False,False,0)
    label_buscar = gtk.Label("Buscar:")
    tabla_controles.attach(label_buscar,0,1,0,1)
    self.entry_buscar = gtk.Entry()
    tabla_controles.attach(self.entry_buscar,1,2,0,1)
    self.but_editar = Estilos.MiBoton("../images/PNG-16/Load.png","Editar")
    tabla_controles.attach(self.but_editar,2,3,0,1)
    but_nuevo = Estilos.MiBoton("../images/PNG-16/Add.png","Nuevo")
    tabla_controles.attach(but_nuevo,3,4,0,1)
    self.check_anulados = gtk.CheckButton("Anulados")
    tabla_controles.attach(self.check_anulados,4,5,0,1)
    self.check_pagados = gtk.CheckButton("Pagados")
    tabla_controles.attach(self.check_pagados,5,6,0,1)
    columnas = ("CÓDIGO","FECHA","EMPRESA","PRECIO","DESCRIPCIÓN")#id,enviado,color,anulado
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
    self.check_anulados.connect('toggled',self.buscar)
    self.check_pagados.connect('toggled',self.buscar)
    self.entry_buscar.connect('changed',self.buscar)
    self.treeview.connect('row-activated',self.on_row_activated)
    self.treeview.connect('cursor_changed',self.on_cursor)
    self.treeview.connect('key-release-event',self.on_key)
    but_nuevo.connect('clicked',self.nuevo)
    self.but_editar.connect('clicked',self.on_editar)

    self.buscar()
    self.treeview.set_cursor(0)
  

  def on_key(self,widget,event):
    if event.keyval == 65535: #Delete
      path, column = self.treeview.get_cursor()
    try:
      id = self.model[path][5]
      anulado = self.model[path][8]
    except:
      pass
    else:
      anulado = not anulado
      sql = "UPDATE cotizaciones SET ANULADO=%d WHERE ID=%d"%(anulado,id)
      self.cursor.execute(sql)
      self.buscar()
  
  def on_cursor(self,widget):
    path, column = self.treeview.get_cursor()
    try:
      enviado = self.model[path][6]
    except:
      self.but_editar.set_sensitive(False)
    else:
      self.but_editar.set_sensitive(True)
      if enviado:
        self.but_editar.label.set_text('Copiar')
        self.but_editar.label.set_text('Editar')
    url = 'http://%s/econadmin/documentos/cotizaciones.php?id=%d'%(self.host,self.model[path][5])
    self.www.open(url)

  def buscar(self,widget=None):
    self.model.clear()
    texto = self.entry_buscar.get_text()
    if texto == "":
      if self.check_anulados.get_active():# ver anulados
        txt = ''
        if not self.check_pagados.get_active(): #solo impagos
          txt = 'WHERE cotizaciones.PAGADO=0'
      else:
        txt = 'WHERE cotizaciones.ANULADO=0'
        if not self.check_pagados.get_active(): #solo impagos
          txt += ' AND cotizaciones.PAGADO=0'
      sql = "SELECT cotizaciones.CORR,cotizaciones.FECHA, clientes.COMERCIAL, CONCAT(IF(cotizaciones.MONEDA=1,'S/. ','$ '),cotizaciones.PRECIO), cotizaciones.NOMBRE, cotizaciones.ID, cotizaciones.ENVIADO,cotizaciones.OC,cotizaciones.ANULADO,cotizaciones.FACTURA,cotizaciones.PAGADO FROM cotizaciones JOIN clientes ON clientes.ID=cotizaciones.EMPRESA %s ORDER BY YEAR(cotizaciones.FECHA) DESC, cotizaciones.CORR DESC"%txt
    else:
      if self.check_anulados.get_active():
        txt = ''
        if not self.check_pagados.get_active(): #solo impagos
          txt = 'AND cotizaciones.PAGADO=0'
      else:
        txt = 'AND cotizaciones.ANULADO=0'
        if not self.check_pagados.get_active(): #solo impagos
          txt += ' AND cotizaciones.PAGADO=0'
      sql = "SELECT cotizaciones.CORR,cotizaciones.FECHA, clientes.COMERCIAL, CONCAT(IF(cotizaciones.MONEDA=1,'S/. ','$ '),cotizaciones.PRECIO), cotizaciones.NOMBRE, cotizaciones.ID, cotizaciones.ENVIADO,cotizaciones.OC,cotizaciones.ANULADO,cotizaciones.FACTURA,cotizaciones.PAGADO FROM cotizaciones JOIN clientes ON clientes.ID=cotizaciones.EMPRESA WHERE (cotizaciones.NOMBRE LIKE '%s'OR clientes.COMERCIAL LIKE '%s') %s ORDER BY YEAR(cotizaciones.FECHA) DESC, cotizaciones.CORR DESC"%('%'+texto+'%','%'+texto+'%',txt)
    self.cursor.execute(sql)
    items = self.cursor.fetchall()
    for item in items:
      color = '#FFFFFF'#blanco
      if item[10] == 0 :# sin pago
        color = '#A9F5BC'#verde
        if item[9] == 0 :# sin factura
          color = '#F2F5A9'
          if item[7]=='':#sin oc
            color = '#FF8888'
            if item[8]:#anulado
              color = '#FF4444'
      
      if not item[6]:
        item = ('<b>'+str(item[0])+'</b>','<b>'+str(item[1])+'</b>','<b>'+item[2]+'</b>','<b>'+str(item[3])+'</b>','<b>'+str(item[4])+'</b>',item[5],item[6],color,item[8])
      else:
        item = (str(item[0]),str(item[1]),item[2],str(item[3]),str(item[4]),item[5],item[6],color,item[8])
      self.model.append(item)

  def on_editar(self,widget):
    path, column = self.treeview.get_cursor()
    self.on_row_activated(widget,int(path[0]),column)

  def on_row_activated(self,widget,path,column):
    enviado = self.model[path][6]
    self.abrir(enviado)

  def abrir(self,enviado):
    if enviado:
      self.copiar()
    else:
      self.editar()

  def guia(self,widget):
    path, column = self.treeview.get_cursor()
    try:
      path = int(path[0])
    except:
      return
    id = self.model[path][5]
    sql = "SELECT ID FROM guias WHERE COTIZ=%d"%id
    self.cursor.execute(sql)
    guia = self.cursor.fetchone()
    guias = Guias.Cotizacion(self.cursor,id)
    if guia == None:
      nueva = Guias.Nueva(self.cursor)
      nueva.cotizacion(id)
      if nueva.run() == gtk.RESPONSE_OK:
        nueva.guardar()
        guia.actualizar()
      nueva.cerrar()
    if guias.run() == gtk.RESPONSE_OK:
      guias.guardar()
      self.buscar()
    guias.cerrar()
    
      

  def factura(self,widget):
    path, column = self.treeview.get_cursor()
    try:
      path = int(path[0])
    except:
      return
    id = self.model[path][5]
    sql = "SELECT ID FROM facturas WHERE COTIZ=%d"%id
    self.cursor.execute(sql)
    factura = self.cursor.fetchone()
    facturas = Facturas.Cotizacion(self.cursor,id)
    if factura == None:
      nueva = Facturas.Nueva(self.cursor)
      nueva.cotizacion(id)
      if nueva.run() == gtk.RESPONSE_OK:
        nueva.guardar()
        facturas.actualizar()
      nueva.cerrar()
    if facturas.run() == gtk.RESPONSE_OK:
      facturas.guardar()
      self.buscar()
      print 'buscar'
    facturas.cerrar()


  def orden(self,widget):
    path, column = self.treeview.get_cursor()
    try:
      path = int(path[0])
    except:
      return
    nueva = Estilos.DialogOC()
    sql = "SELECT OC,OCFILE FROM cotizaciones WHERE ID=%d"%self.model[path][5]
    self.cursor.execute(sql)
    oc,oc_file = self.cursor.fetchone()
    nueva.entry_cod.set_text(oc)
    nueva.entry_file.set_text(oc_file)
    os.system("""gnome-open '%s'"""%(oc_file))
    if nueva.run() == gtk.RESPONSE_OK:
      oc = nueva.entry_cod.get_text()
      file = nueva.entry_file.get_text()
      ext = file.split('.')[-1]
      comm = """mv '%s' '/home/econain/EconAdmin/ordenes/%d.%s'"""%(file,self.model[path][5],ext)
      command = os.popen(comm)
      read = command.read()
      file = '/home/econain/EconAdmin/ordenes/%d.%s'%(self.model[path][5],ext)
      sql = "UPDATE cotizaciones SET OC='%s',OCFILE='%s' WHERE ID=%d"%(oc,file,self.model[path][5])
      self.cursor.execute(sql)
    nueva.cerrar()

  def imprimir(self,widget):
    operation = gtk.PrintOperation()
    action = gtk.PRINT_OPERATION_ACTION_PRINT
    self.www_frame.print_full(operation,action)

  def enviar(self,widget):
    operation = gtk.PrintOperation()
    action = gtk.PRINT_OPERATION_ACTION_EXPORT
    path, column = self.treeview.get_cursor()
    id = self.model[int(path[0])][5]
    sql = "SELECT ATENCION,CC,CCO,NOMBRE,CONCAT(YEAR(FECHA),'-',CORR) FROM cotizaciones WHERE ID = %d"%id
    self.cursor.execute(sql)
    ateid,ccid,ccoid,nombre,corr = self.cursor.fetchone()	
    corr = corr[2:]
    name = corr
    operation.set_export_filename('/home/econain/EconAdmin/cotizaciones/'+corr+'.pdf')
    self.www_frame.print_full(operation,action)
    ventas_id = 2
    to = self.get_mails(ateid)
    cc = self.get_mails(ccid)
    cco = self.get_mails(ccoid)
    subject = 'Cotización %s: %s'%(corr,nombre)
    body = 'Saludos cordiales,\nLe hacemos entrega de nuestra cotización por <b>%s</b>'%nombre
    path = os.getcwd()
    attach = ('/home/econain/EconAdmin/cotizaciones/'+corr+'.pdf')
    comm = """thunderbird -compose "to='%s',cc='%s,%s',bcc='webmaster@econain.com',subject='%s',body='%s',attachment='%s',preselectid='id%d'" """%(to,cc,cco,subject,body,attach,ventas_id)
    command = os.popen(comm)
    read = command.read()
    confirm = Estilos.DialogSN('Consulta','¿Marcar como enviado?')
    if confirm.run()==gtk.RESPONSE_OK:
      sql = "UPDATE cotizaciones SET ENVIADO=1 WHERE ID=%d"%id
      self.cursor.execute(sql)
    else:
      print 'no se envió'
    confirm.destroy()
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
    nueva = Nueva(self.cursor,self)
    nueva.leer(self.model[int(path[0])][5])
    if nueva.run() == gtk.RESPONSE_OK:
      nueva.guardar()
    nueva.cerrar()
    self.buscar()

  def editar(self):
    path, column = self.treeview.get_cursor()
    nueva = Nueva(self.cursor,self)
    nueva.leer(self.model[int(path[0])][5])
    if nueva.run() == gtk.RESPONSE_OK:
      nueva.actualizar()
    nueva.cerrar()
    self.buscar()

  def nuevo(self,widget):
    nueva = Nueva(self.cursor,self)
    if nueva.run() == gtk.RESPONSE_OK:
      nueva.guardar()
    nueva.cerrar()
    self.buscar()

class Nueva(gtk.Dialog):
	def __init__(self,cursor,padre):
		gtk.Dialog.__init__(self,"Nueva Cotización",padre,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		self.cursor = cursor
		tabla_datos = gtk.Table(2,5,False)
		self.vbox.pack_start(tabla_datos)
		label_corr = gtk.Label('Correlativo:')
		tabla_datos.attach(label_corr,0,1,0,1)
		self.entry_corr = gtk.Entry()
		tabla_datos.attach(self.entry_corr,1,2,0,1)
		label_fecha = gtk.Label('Fecha:')
		tabla_datos.attach(label_fecha,0,1,1,2)
		self.but_fecha = Estilos.Fecha(label_fecha.get_window())
		self.but_fecha.set_date(datetime.date.today())
		fecha = self.but_fecha.get_date()
		self.cursor.execute("SELECT CORR FROM cotizaciones WHERE YEAR(FECHA)=%d ORDER BY YEAR(FECHA) DESC, CORR DESC LIMIT 1"%fecha.year)
		try:
			corr = self.cursor.fetchone()[0]+1
		except:
			corr = 1
		self.entry_corr.set_text(str(corr))
		tabla_datos.attach(self.but_fecha,1,2,1,2)
		label_empresa = gtk.Label("Empresa:")
		tabla_datos.attach(label_empresa,0,1,2,3)
		self.combo_empresa = Estilos.ComboButton(self.cursor)
		self.combo_empresa.sql("SELECT ID,COMERCIAL FROM clientes",0)
		tabla_datos.attach(self.combo_empresa,1,2,2,3)
		sw_atencion = gtk.ScrolledWindow()
		sw_atencion.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		columnas = ("NOMBRE","ATE","CC","CCO")
		self.model_atencion = gtk.ListStore(str,bool,bool,bool,int)
		self.treeview_atencion = gtk.TreeView(self.model_atencion)
		i = 0
		for name in columnas:
			if i==0:
				renderer = gtk.CellRendererText()
				column = gtk.TreeViewColumn(name,renderer,text=i)
				column.set_min_width(200)
				self.treeview_atencion.append_column(column)
			else:
				renderer = gtk.CellRendererToggle()
				renderer.set_radio(True)
				renderer.set_activatable(True)
				renderer.connect('toggled',self.on_toggled,i)
				column = gtk.TreeViewColumn(name,renderer,active=i)
				column.set_max_width(40)
				self.treeview_atencion.append_column(column)
			i+=1
		sw_atencion.add(self.treeview_atencion)
		sw_atencion.set_size_request(300,80)
		tabla_datos.attach(sw_atencion,0,2,3,4)
		label_moneda = gtk.Label("Moneda.:")
		tabla_datos.attach(label_moneda,0,1,4,5)
		self.combo_moneda = Estilos.ComboButton(self.cursor)
		tabla_datos.attach(self.combo_moneda,1,2,4,5)
		columnas = ("CANT","DESCRIPCIÓN","PRECIO")
		self.model = gtk.ListStore(str,str,str,str,int)
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
		tabla_cond = gtk.Table(2,6,False)
		self.vbox.pack_start(tabla_cond)
		label_plazo = gtk.Label("Plazo:")
		tabla_cond.attach(label_plazo,0,1,0,1)
		self.entry_plazo = Estilos.Completion(self.cursor,"plazos")
		tabla_cond.attach(self.entry_plazo,1,2,0,1)
		label_garantia = gtk.Label("Garantía:")
		tabla_cond.attach(label_garantia,0,1,1,2)
		self.entry_garantia = Estilos.Completion(self.cursor,"garantias")
		tabla_cond.attach(self.entry_garantia,1,2,1,2)
		label_pago = gtk.Label("Forma de pago:")
		tabla_cond.attach(label_pago,0,1,2,3)
		self.entry_pago = Estilos.Completion(self.cursor,"pagos")
		tabla_cond.attach(self.entry_pago,1,2,2,3)
		label_validez = gtk.Label("Validez de la Oferta:")
		tabla_cond.attach(label_validez,0,1,3,4)
		self.entry_validez = Estilos.Completion(self.cursor,"validez")
		tabla_cond.attach(self.entry_validez,1,2,3,4)
		label_observ = gtk.Label("Observaciones:")
		tabla_cond.attach(label_observ,0,1,4,5)
		self.entry_observ = gtk.TextView()
		tabla_cond.attach(self.entry_observ,1,2,4,5)
		label_responsable = gtk.Label("Responsable:")
		tabla_cond.attach(label_responsable,0,1,5,6)
		self.combo_responsable = Estilos.ComboButton(self.cursor)
		self.combo_responsable.sql("SELECT ID,TITULO FROM personal WHERE COT=1 ORDER BY ID",0)
		self.combo_moneda.sql("SELECT ID,NOMBRE FROM monedas",0)
		tabla_cond.attach(self.combo_responsable,1,2,5,6)
		self.but_guardar = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
		but_mas.connect('clicked',self.mas)
		but_cop.connect('clicked',self.cop)
		but_editar.connect('clicked',self.but_editar)
		but_eliminar.connect('clicked',self.eliminar)
		self.treeview.connect('row-activated',self.on_row_activated)
		self.add_action_widget(self.but_guardar,gtk.RESPONSE_OK)
		self.combo_empresa.connect('changed',self.cambio_empresa)
		self.show_all()

	def on_row_activated(self,widget,path,column):
		self.editar(path)

	def on_toggled(self,cell,path,i):
		b = self.model_atencion[path][i]
		self.model_atencion[path][i] = not b
		if b == False:
			if i==1:			
				self.model_atencion[path][2] = b
				self.model_atencion[path][3] = b
			elif i==2:
				self.model_atencion[path][1] = b
				self.model_atencion[path][3] = b
			elif i==3:
				self.model_atencion[path][1] = b
				self.model_atencion[path][2] = b
		b = 0
		for row in self.model_atencion:
			b = b or row[1] or row[2] or row[3]
		self.but_guardar.set_sensitive(b)

	def guardar(self):
		#guardar cotizacion
		try:
			corr = int(self.entry_corr.get_text())
		except:
			return
		fecha = self.but_fecha.get_date()
		empresa = self.combo_empresa.get_id()
		atencion = '0'
		cc = '0'
		cco = '0'
		for row in self.model_atencion:
			if row[1]:
				atencion += str(row[4])+',0'
			elif row[2]:
				cc += str(row[4])+',0'
			elif row[3]:
				cco += str(row[4])+',0'
		moneda = self.combo_moneda.get_id()
		plazo = self.entry_plazo.get_id()
		garantia = self.entry_garantia.get_id()
		pago = self.entry_pago.get_id()
		validez = self.entry_validez.get_id()
		responsable = self.combo_responsable.get_id()
		buffer = self.entry_observ.get_buffer()
		inicio = buffer.get_start_iter()
		fin = buffer.get_end_iter()
		observ = buffer.get_text(inicio,fin,0)
		precio = Decimal('0.00').quantize(Decimal('0.00'))
		for row in self.model:
			precio += (Decimal(row[2])*Decimal(row[0])).quantize(Decimal('0.00'))
		nombre = self.model[0][1].split('\n')[0]
		columnas = "CORR,FECHA,EMPRESA, ATENCION,CC,CCO,MONEDA, PLAZO,GARANTIA,PAGO, VALIDEZ,RESPONSABLE,PRECIO,NOMBRE,OBSERV"
		valores = "%d,'%s',%d, '%s','%s','%s',%d, %d,%d,%d, %d,%d,'%s','%s','%s'"%(corr,fecha,empresa, atencion,cc,cco,moneda, plazo,garantia,pago, validez,responsable,precio,nombre,observ)
		sql = "INSERT INTO cotizaciones (%s) VALUES (%s)"%(columnas,valores)
		self.cursor.execute(sql)
		#guardar items
		self.cursor.execute("SELECT ID FROM cotizaciones ORDER BY ID DESC LIMIT 1")
		id = self.cursor.fetchone()[0]
		for row in self.model:
			valores = "%d,'%s','%s','%s','%s'"%(id,row[0],row[1],row[2],row[3])
			self.cursor.execute("INSERT INTO cotitems (COTIZ,CANT,TXT,PRECIO,HTML) VALUES (%s)"%valores)

	def actualizar(self):
		fecha = str(datetime.date.today())
		empresa = self.combo_empresa.get_id()
		atencion = '0'
		cc = '0'
		cco = '0'
		for row in self.model_atencion:
			if row[1]:
				atencion += str(row[4])+',0'
			elif row[2]:
				cc += str(row[4])+',0'
			elif row[3]:
				cco += str(row[4])+',0'
		print atencion,cc,cco
		moneda = self.combo_moneda.get_id()
		plazo = self.entry_plazo.get_id()
		garantia = self.entry_garantia.get_id()
		pago = self.entry_pago.get_id()
		validez = self.entry_validez.get_id()
		responsable = self.combo_responsable.get_id()
		buffer = self.entry_observ.get_buffer()
		inicio = buffer.get_start_iter()
		fin = buffer.get_end_iter()
		observ = buffer.get_text(inicio,fin,0)
		precio = Decimal('0.00').quantize(Decimal('0.00'))
		for row in self.model:
			precio += (Decimal(row[2])*Decimal(row[0])).quantize(Decimal('0.00'))
		nombre = self.model[0][1].split('\n')[0]
		valores = (fecha,empresa, atencion,cc,cco,moneda, plazo,garantia,pago, validez,responsable,precio,nombre,observ,self.id)
		sql = "UPDATE cotizaciones SET FECHA='%s',EMPRESA=%d,ATENCION='%s',CC='%s',CCO='%s',MONEDA=%d,PLAZO=%d,GARANTIA=%d,PAGO=%d,VALIDEZ=%d,RESPONSABLE=%d,PRECIO=%d,NOMBRE='%s',OBSERV='%s' WHERE ID=%d"%valores
		print sql
		self.cursor.execute(sql)
		for row in self.model:
			if row[4]==0:
				valores = (self.id,row[0],row[1],row[2],row[3])
				self.cursor.execute("INSERT INTO cotitems (COTIZ,CANT,TXT,PRECIO,HTML) VALUES (%d,'%s','%s','%s','%s')"%valores)
			else:
				valores = (self.id,row[0],row[1],row[2],row[3],row[4])
				self.cursor.execute("UPDATE cotitems SET COTIZ=%d,CANT='%s',TXT='%s',PRECIO='%s',HTML='%s' WHERE ID=%d"%valores)

	def leer(self,id):
		self.id = id
		sql = "SELECT CANT,TXT,PRECIO,HTML,ID FROM cotitems WHERE COTIZ=%d"%id
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		sql = "SELECT EMPRESA,FECHA,ATENCION,CC,CCO, MONEDA,PLAZO,GARANTIA, PAGO,VALIDEZ,RESPONSABLE,OBSERV,CORR FROM cotizaciones WHERE ID = %d"%id
		self.cursor.execute(sql)
		empresa,fecha,atencion,cc,cco,moneda,plazo,garantia,pago,validez,responsable,observ,corr = self.cursor.fetchone()
		self.but_fecha.set_date(fecha)
		self.combo_empresa.set_id(empresa)
		self.combo_moneda.set_id(moneda)
		self.entry_plazo.set_id(plazo)
		self.entry_garantia.set_id(garantia)
		self.entry_pago.set_id(pago)
		self.entry_validez.set_id(validez)
		self.combo_responsable.set_id(responsable)
		self.entry_observ.get_buffer().set_text(observ)
                self.entry_corr.set_text(str(corr))
		ids = (atencion.split(','),cc.split(','),cco.split(','))
		sql = "SELECT NOMBRE,ID FROM contactos WHERE EMPRESA=%d"%empresa
		self.cursor.execute(sql)
		contactos = self.cursor.fetchall()
		self.model_atencion.clear()
		self.model.clear()
		print ids
		print contactos
		for row in contactos:
			bools = [False,False,False]
			b = False
			i = 0
			for tipos in ids:
				for id in tipos:
					if int(id) == row[1]:
						bools[i] = True
						b = True
						break
				i +=1
				if b:
					break

			print 'fila',(row[0],bools[0],bools[1],bools[2],row[1])
			self.model_atencion.append((row[0],bools[0],bools[1],bools[2],row[1]))
		for row in items:
			self.model.append(row)
		self.treeview.set_cursor(0)

	def cambio_empresa(self,widget):
		id = widget.get_id()
		self.cursor.execute("SELECT NOMBRE,ATE,CC,CCO,ID FROM contactos WHERE EMPRESA=%d"%id)
		atencion = self.cursor.fetchall()
		self.model_atencion.clear()
		for row in atencion:
			self.model_atencion.append(row)
		self.cursor.execute("SELECT MONEDA,PAGO,RESPONSABLE FROM clientes WHERE ID = %d"%id)
		moneda,pago,responsable = self.cursor.fetchone()
		self.combo_moneda.set_id(moneda)
		self.entry_pago.set_id(pago)
		print self.combo_responsable.diccionario
		print 'responsable',responsable
		self.combo_responsable.set_id(responsable)

	def mas(self,widget):
		item = Item(self)
		if item.run() == gtk.RESPONSE_OK:
			row = item.guardar()
			self.model.append((row[0],row[1],row[2],row[3],0))
		item.cerrar()

	def cop(self,widget):
		lista = Lista(self.cursor,self)
		if lista.run() == gtk.RESPONSE_OK:
			row = lista.abrir()
			self.model.append(row)
		lista.cerrar()

	def but_editar(self,widget):
		path,column = self.treeview.get_cursor()
		path = int(path[0])
		self.editar(path)

	def editar(self,path):
		item = Item(self)
		item.leer(self.model[path])
		if item.run() == gtk.RESPONSE_OK:
			row = item.guardar()
			self.model[path][0] = row[0]
			self.model[path][1] = row[1]
			self.model[path][2] = row[2]
			self.model[path][3] = row[3]
		item.cerrar()

	def eliminar(self,widget):
		path,column = self.treeview.get_cursor()
		path = int(path[0])
		iter = self.treeview.get_model().get_iter(path)
		self.model.remove(iter)

	def cerrar(self):
		self.destroy()

class Item(gtk.Dialog):
	def __init__(self,padre):
		gtk.Dialog.__init__(self,"Nuevo Item",padre,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
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
		self.entry_precio.connect('changed',self.numero)
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
		html = self.text_desc.codificar()
		precio = self.entry_precio.get_text()
		item = (cantidad,descripcion,precio,html)
		return item

	def leer(self,row):
		self.entry_cant.set_text(row[0])
		self.entry_precio.set_text(row[2])
		self.text_desc.decodificar(row[3])
	
	def cerrar(self):
		self.destroy()

class Lista(gtk.Dialog):
	""" Clase Ventana Principal """
	def __init__ (self,cursor,padre):
		""" Class initialiser """
		gtk.Dialog.__init__(self,"Items Cotizaciones",padre,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		self.cursor = cursor
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
