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
        self.set_title("Facturas")
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
#       self.but_factura.connect('clicked',self.factura)
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
        self.model = gtk.ListStore(str,str,str,str,int,int,int)
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
        self.treeview.connect('key-release-event',self.on_key)
        but_nuevo.connect('clicked',self.nuevo)
        self.but_editar.connect('clicked',self.on_editar)
        self.buscar()
        self.treeview.set_cursor(0)


    def on_key(self,widget,event):
        if event.keyval == 65535: #Delete
            path, column = self.treeview.get_cursor()
            try:
                id = self.model[path][4]
                anulado = self.model[path][6]
            except:
                pass
            else:
                anulado = not anulado
                sql = "UPDATE facturas SET ANULADO=%d WHERE ID=%d"%(anulado,id)
                self.cursor.execute(sql)
                print sql
                self.buscar()

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
        url = 'http://%s/econadmin/images/factura.png'%(self.host)
        self.www.open(url)

    def buscar(self,widget=None):
        self.model.clear()
        texto = self.entry_buscar.get_text()
        if texto == "":
            sql = "SELECT CONCAT(facturas.SERIE,'-',facturas.NUMERO) AS CORR,facturas.FECHA,clientes.COMERCIAL,facturas.NOMBRE,facturas.ID,facturas.IMPRESO,facturas.ANULADO FROM facturas JOIN clientes ON clientes.ID=facturas.EMPRESA ORDER BY CORR DESC LIMIT 100"
        else:
            sql = "SELECT CONCAT(facturas.SERIE,'-',facturas.NUMERO) AS CORR,facturas.FECHA,clientes.COMERCIAL,facturas.NOMBRE,facturas.ID,facturas.IMPRESO,facturas.ANULADO FROM facturas JOIN clientes ON clientes.ID=facturas.EMPRESA WHERE cotizaciones.NOMBRE LIKE '%s'OR clientes.COMERCIAL LIKE '%s' ORDER BY CORR DESC"%('%'+texto+'%','%'+texto+'%')
        print sql
        self.cursor.execute(sql)
        items = self.cursor.fetchall()
        for item in items:
            if item[6]:
                item = ('<b>'+str(item[0])+'</b>',str(item[1]),item[2],item[3],item[4],item[5], item[6])
            elif not item[5]:
                item = ('<b>'+str(item[0])+'</b>','<b>'+str(item[1])+'</b>','<b>'+item[2]+'</b>','<b>'+item[3]+'</b>',item[4],item[5], item[6])
            self.model.append(item)

    def on_editar(self,widget):
        path, column = self.treeview.get_cursor()
        self.on_row_activated(widget,int(path[0]),column)

    def on_row_activated(self,widget,path,column):
        impreso = self.model[path][5]
        self.abrir(impreso)

    def abrir(self,impreso):
        if impreso:
            self.copiar()
        else:
            self.editar()

    def guia(self,widget):
        path, column = self.treeview.get_cursor()
        try:
            path = int(path[0])
        except:
            return

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
        if nueva.run() == gtk.RESPONSE_OK:
            oc = nueva.entry_cod.get_text()
            file = nueva.entry_file.get_text()
            sql = "UPDATE cotizaciones SET OC='%s',OCFILE='%s' WHERE ID=%d"%(oc,file,self.model[path][5])
            self.cursor.execute(sql)
        nueva.cerrar()

    def imprimir(self,widget):
        path, column = self.treeview.get_cursor()
        try:
            path = int(path[0])
        except:
            return
        fact = Impresion.Facturas(self.cursor,self.model[path][4])
        fact.imprimir()
        self.buscar()


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
        print comm
        print os.system(comm)
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
        self.cursor.execute("SELECT NUMERO FROM facturas WHERE SERIE=%s ORDER BY NUMERO DESC LIMIT 1"%(nueva.entry_serie.get_text()))
        try:
            corr = self.cursor.fetchone()[0]+1
        except:
            corr = 1
        nueva.entry_numero.set_text(str(corr))
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
        self.impreso = False
        self.cursor = cursor
        self.set_title("Nueva Factura")
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
        self.cursor.execute("SELECT NUMERO FROM facturas WHERE SERIE=%s ORDER BY NUMERO DESC LIMIT 1"%(self.entry_serie.get_text()))
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
        label_moneda = gtk.Label('Moneda:')
        tabla_datos.attach(label_moneda,0,1,3,4)
        self.combo_moneda = Estilos.ComboButton(self.cursor)
        self.combo_moneda.sql("SELECT ID,NOMBRE FROM monedas",0)
        tabla_datos.attach(self.combo_moneda,1,3,3,4)
        columnas = ("CANT","DESCRIPCIÓN","PRECIO")
        self.model = gtk.ListStore(str,str,str,int)
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
        tabla_cond = gtk.Table(2,3,False)
        self.vbox.pack_start(tabla_cond)
        label_guia = gtk.Label("Guía:")
        tabla_cond.attach(label_guia,0,1,0,1)
        self.entry_guia = gtk.Entry()
        tabla_cond.attach(self.entry_guia,1,2,0,1)
        label_compra = gtk.Label("O. Compra:")
        tabla_cond.attach(label_compra,0,1,1,2)
        self.entry_compra = gtk.Entry()
        tabla_cond.attach(self.entry_compra,1,2,1,2)
        label_pago = gtk.Label("Pago:")
        tabla_cond.attach(label_pago,0,1,2,3)
        self.entry_pago = Estilos.Completion(self.cursor,"pagos")
        tabla_cond.attach(self.entry_pago,1,2,2,3)
        self.but_guardar = Estilos.MiBoton("../images/PNG-16/Save.png","Guardar")
        but_mas.connect('clicked',self.mas)
        but_cop.connect('clicked',self.cop)
        but_editar.connect('clicked',self.but_editar)
        but_eliminar.connect('clicked',self.eliminar)
        self.treeview.connect('row-activated',self.on_row_activated)
        self.add_action_widget(self.but_guardar,gtk.RESPONSE_OK)
        self.combo_empresa.connect('changed',self.cambio_empresa)
        self.cotiz = 0
        self.show_all()

    def on_row_activated(self,widget,path,column):
        self.editar(path)

    def cotizacion(self,id):
        self.cotiz = id
        sql = "SELECT EMPRESA,OC,PAGO,GUIA,MONEDA FROM cotizaciones WHERE ID=%d"%self.cotiz
        self.cursor.execute(sql)
        empresa,oc,pago,guia,moneda = self.cursor.fetchone()
        self.entry_compra.set_text(oc)
        self.combo_empresa.set_id(empresa)
        self.combo_empresa.set_sensitive(False)
        self.entry_pago.set_id(pago)
        if guia != 0:
          sql = "SELECT CONCAT(SERIE,'-',NUMERO) FROM guias WHERE ID=%d"%guia
          print guia
          self.cursor.execute(sql)
          guia = self.cursor.fetchone()[0]
          self.entry_guia.set_text(guia)
        self.combo_moneda.set_id(moneda)
        self.combo_moneda.set_sensitive(False)
        sql = "SELECT CANT,TXT,PRECIO,ID FROM cotitems WHERE COTIZ=%d"%self.cotiz
        self.cursor.execute(sql)
        items = self.cursor.fetchall()
        for row in items:
            self.model.append(row)

    def guardar(self):
        #guardar cotizacion
        serie = self.entry_serie.get_text()
        numero = self.entry_numero.get_text()
        fecha = self.but_fecha.get_date()
        empresa = self.combo_empresa.get_id()
        compra = self.entry_compra.get_text()
        guia = self.entry_guia.get_text()
        pago = self.entry_pago.get_id()
        igv = 18
        moneda = self.combo_moneda.get_id()
        precio = Decimal('0.00').quantize(Decimal('0.00'))
        for row in self.model:
            precio += (Decimal(row[2])*Decimal(row[0])).quantize(Decimal('0.00'))
        nombre = self.model[0][1].split('\n')[0]
        columnas = "SERIE,NUMERO,FECHA, EMPRESA,COTIZ,OC, GUIA,PAGO,IMPRESO, IGV,MONEDA,NOMBRE, PRECIO"
        valores = "%s,%s,'%s', %d,%d,'%s', '%s',%d,0, %d,%d,'%s','%s'"%(serie,numero,fecha, empresa,self.cotiz,compra, guia,pago, igv,moneda,nombre,precio)
        sql = "INSERT INTO facturas (%s) VALUES (%s)"%(columnas,valores)
        self.cursor.execute(sql)
        #guardar items
        self.cursor.execute("SELECT ID FROM facturas ORDER BY ID DESC LIMIT 1")
        self.id = self.cursor.fetchone()[0]
        for row in self.model:
            valores = "%d,'%s','%s','%s'"%(self.id,row[0],row[1],row[2])
            self.cursor.execute("INSERT INTO factitems (FACTURA,CANT,DESCRIPCION,PRECIO) VALUES (%s)"%valores)


    def actualizar(self):
        fecha = str(datetime.date.today())
        empresa = self.combo_empresa.get_id()
        moneda = self.combo_moneda.get_id()
        pago = self.entry_pago.get_id()
        precio = Decimal('0.00').quantize(Decimal('0.00'))
        for row in self.model:
            precio += (Decimal(row[2])*Decimal(row[0])).quantize(Decimal('0.00'))
        nombre = self.model[0][1][0:32]
        guia = self.entry_guia.get_text()
        oc = self.entry_compra.get_text()
        valores = (fecha,empresa,moneda, pago,precio,nombre, guia,oc,self.id)
        sql = "UPDATE facturas SET FECHA='%s',EMPRESA=%d,MONEDA=%d,PAGO=%d,PRECIO='%s',NOMBRE='%s',GUIA='%s',OC='%s' WHERE ID=%d"%valores
        print sql
        self.cursor.execute(sql)
        for row in self.model:
            if row[3]==0:
                valores = (self.id,row[0],row[1],row[2])
                self.cursor.execute("INSERT INTO factitems (FACTURA,CANT,DESCRIPCION,PRECIO) VALUES (%d,'%s','%s','%s')"%valores)
            else:
                valores = (self.id,row[0],row[1],row[2],row[3])
                self.cursor.execute("UPDATE factitems SET FACTURA=%d,CANT='%s',DESCRIPCION='%s',PRECIO='%s' WHERE ID=%d"%valores)

    def copiar(self,id):
        self.id = id
        sql = "SELECT CANT,DESCRIPCION,PRECIO,ID FROM factitems WHERE FACTURA = %d"%id
        self.cursor.execute(sql)
        items = self.cursor.fetchall()
        sql = "SELECT FECHA,SERIE,NUMERO,EMPRESA,COTIZ,OC,PAGO,MONEDA FROM facturas WHERE ID=%d"%id
        print sql
        self.cursor.execute(sql)
        fecha,serie,numero,empresa,cotiz,compra,pago,moneda = self.cursor.fetchone()
        self.combo_empresa.set_id(empresa)
        self.but_fecha.set_date(fecha)
        self.entry_serie.set_text(str(serie))
        self.entry_numero.set_text(str(numero))
        self.cursor.execute("SELECT NUMERO FROM facturas WHERE SERIE=%s ORDER BY NUMERO DESC LIMIT 1"%(self.entry_serie.get_text()))
        try:
            corr = self.cursor.fetchone()[0]+1
        except:
            corr = 1
        self.entry_numero.set_text(str(corr))
        self.cotiz = cotiz
        self.entry_compra.set_text(compra)
        self.entry_pago.set_id(pago)
        self.combo_moneda.set_id(moneda)
        self.model.clear()
        for row in items:
            self.model.append(row)
        self.treeview.set_cursor(0)

    def leer(self,id):
        self.id = id
        sql = "SELECT CANT,DESCRIPCION,PRECIO,ID FROM factitems WHERE FACTURA = %d"%id
        self.cursor.execute(sql)
        items = self.cursor.fetchall()
        sql = "SELECT FECHA,SERIE,NUMERO,EMPRESA,COTIZ,OC,PAGO,MONEDA,GUIA FROM facturas WHERE ID=%d"%id
        print sql
        self.cursor.execute(sql)
        fecha,serie,numero,empresa,cotiz,compra,pago,moneda,guia = self.cursor.fetchone()
        self.combo_empresa.set_id(empresa)
        self.but_fecha.set_date(fecha)
        self.entry_serie.set_text(str(serie))
        self.entry_numero.set_text(str(numero))
        self.cotiz = cotiz
        self.entry_compra.set_text(compra)
        self.entry_guia.set_text(guia)
        self.entry_pago.set_id(pago)
        self.combo_moneda.set_id(moneda)
        self.model.clear()
        for row in items:
            self.model.append(row)
        self.treeview.set_cursor(0)

    def cambio_empresa(self,widget):
        if self.combo_empresa.get_sensitive():
            id = widget.get_id()
            self.cursor.execute("SELECT MONEDA,PAGO FROM clientes WHERE ID = %d"%id)
            moneda,pago = self.cursor.fetchone()
            self.combo_moneda.set_id(moneda)
            self.entry_pago.set_id(pago)
        
    def mas(self,widget):
        item = Item()
        if item.run() == gtk.RESPONSE_OK:
            row = item.guardar()
            self.model.append((row[0],row[1],row[2],0))
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
            self.model[path][2] = row[2]
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
        self.set_title("Facturas por Cotización")
        self.impreso = False
        self.cursor = cursor
        self.cotiz = id
        columnas = ("FACTURA","ANULADO","PAGADO")
        self.model = gtk.ListStore(str,int,int,int,int)
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
        sql = "SELECT CONCAT(SERIE,'-',NUMERO),ANULADO,PAGADO,IMPRESO,ID FROM facturas WHERE COTIZ=%d ORDER BY SERIE DESC,NUMERO DESC"%self.cotiz
        self.cursor.execute(sql)
        items = self.cursor.fetchall()
        self.model.clear()
        for row in items:
            self.model.append(row)

    def abrir(self,widget):
        nueva = Nueva(self.cursor)
        if self.impreso:
            nueva.copiar(self.model[0][4])
        else:
            nueva.leer(self.model[0][4])
        if nueva.run() == gtk.RESPONSE_OK:
            if self.impreso:
                nueva.guardar()
            else:
                nueva.actualizar()
        nueva.cerrar()

    def on_cursor(self,widget):
        path, column = self.treeview.get_cursor()
        try:
            self.impreso = self.model[path][3]
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
        factura = self.model[path][4]
        fact = Impresion.Facturas(self.cursor,factura)
        fact.imprimir()

    def guardar(self):
        i = 0
        b = True
        for row in self.model:
            sql = "UPDATE facturas SET ANULADO=%d, PAGADO=%d WHERE ID=%d"%(row[1],row[2],row[4])
            self.cursor.execute(sql)
            if not row[1]:
              i += 1
              id = row[4]
              b = b and row[2]
        if i>0:
            sql = "UPDATE cotizaciones SET FACTURA=%d, PAGADO=%d WHERE ID=%d"%(id,b,self.cotiz)
            print sql
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
        self.entry_precio.set_text(row[2])

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
