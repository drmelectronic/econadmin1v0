#! /usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import Contactos
import Estilos
import gobject
import Consultas
import xlwt
from decimal import Decimal
import os

__author__="danielypamela"
__date__ ="$26/10/2011 05:53:37 PM$"

class Ventana(gtk.Window):
	""" Clase Ventana Principal """
	def __init__ (self,consulta):
		""" Class initialiser """
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.cursor = consulta.cursor
		self.set_title("Declaraciones")
		vbox_main = gtk.VBox(False,0)
		self.add(vbox_main)
		hbox_control = gtk.HBox(False,0)
		vbox_main.pack_start(hbox_control,False,False,0)
		label_periodo = gtk.Label("Periodo:")
		hbox_control.pack_start(label_periodo,False,False,0)
		self.entry_periodo = Estilos.EntryPeriodo()
		hbox_control.pack_start(self.entry_periodo,False,False,0)
		but_calcular = Estilos.MiBoton("../images/PNG-16/Modify.png","_Calcular")
		hbox_control.pack_start(but_calcular,False,False,0)
		but_print = Estilos.MiBoton("../images/PNG-16/Print.png","Im_primir")
		hbox_control.pack_start(but_print,False,False,0)
		frame_id = gtk.Frame('Identificación')
		vbox_main.pack_start(frame_id)
		tabla_id = gtk.Table(4,2)
		frame_id.add(tabla_id)
		tabla_id.attach(gtk.Label('RUC:'),0,1,0,1)
		tabla_id.attach(gtk.Label('20516318547'),1,2,0,1)
		tabla_id.attach(gtk.Label('Razón Social:'),2,3,0,1)
		tabla_id.attach(gtk.Label('ECONAIN S.A.C.'),3,4,0,1)
		tabla_id.attach(gtk.Label('Periodo:'),0,1,1,2)
		self.label_periodo = gtk.Label()
		tabla_id.attach(self.label_periodo,1,2,1,2)
		tabla_id.attach(gtk.Label('Régimen de Renta:'),2,3,1,2)
		tabla_id.attach(gtk.Label('General'),3,4,1,2)
		frame_op = gtk.Frame('Opciones')
		vbox_main.pack_start(frame_op)
		tabla_op = gtk.Table(6,2)
		frame_op.add(tabla_op)
		tabla_op.attach(gtk.Label('Ventas no\nGravadas'),0,1,0,1)
		tabla_op.attach(gtk.Label('Percepciones'),1,2,0,1)
		tabla_op.attach(gtk.Label('Retenciones'),2,3,0,1)
		tabla_op.attach(gtk.Label('IVAP'),3,4,0,1)
		tabla_op.attach(gtk.Label('Retenciones 3ra\nCategoría'),4,5,0,1)
		tabla_op.attach(gtk.Label('Exonerado\nIGV'),5,6,0,1)
		tabla_op.attach(gtk.Label('NO'),0,1,1,2)
		self.label_perc =gtk.Label()
		tabla_op.attach(self.label_perc,1,2,1,2)
		self.label_ret =gtk.Label()
		tabla_op.attach(self.label_ret,2,3,1,2)
		tabla_op.attach(gtk.Label('NO'),3,4,1,2)
		tabla_op.attach(gtk.Label('NO'),4,5,1,2)
		tabla_op.attach(gtk.Label('NO'),5,6,1,2)
		frame_ventas = gtk.Frame('Ventas')
		vbox_main.pack_start(frame_ventas)
		tabla_ventas = gtk.Table(3,4)
		frame_ventas.add(tabla_ventas)
		tabla_ventas.attach(gtk.Label('Ventas Netas'),0,1,1,2)
		tabla_ventas.attach(gtk.Label('Export Facturadas'),0,1,2,3)
		tabla_ventas.attach(gtk.Label('BASE'),1,2,0,1)
		tabla_ventas.attach(gtk.Label('TRIBUTO'),2,3,0,1)
		tabla_ventas.attach(gtk.Label('TOTAL'),1,2,3,4)
		self.label_ventasn = gtk.Label()
		tabla_ventas.attach(self.label_ventasn,1,2,1,2)
		self.label_ventasn_trib = gtk.Label()
		tabla_ventas.attach(self.label_ventasn_trib,2,3,1,2)
		self.label_export = gtk.Label()
		tabla_ventas.attach(self.label_export,1,2,2,3)
		self.label_export_trib = gtk.Label()
		tabla_ventas.attach(self.label_export_trib,2,3,2,3)
		self.label_trib_ventas = gtk.Label()
		tabla_ventas.attach(self.label_trib_ventas,2,3,3,4)
		frame_compras = gtk.Frame('Compras')
		vbox_main.pack_start(frame_compras)
		tabla_compras = gtk.Table(3,5)
		frame_compras.add(tabla_compras)
		tabla_compras.attach(gtk.Label('Compras'),0,1,1,2)
		tabla_compras.attach(gtk.Label('No Gravadas'),0,1,2,3)
		tabla_compras.attach(gtk.Label('Importaciones'),0,1,3,4)
		tabla_compras.attach(gtk.Label('BASE'),1,2,0,1)
		tabla_compras.attach(gtk.Label('TRIBUTO'),2,3,0,1)
		tabla_compras.attach(gtk.Label('TOTAL'),1,2,4,5)
		self.label_compras = gtk.Label()
		self.label_compras_trib = gtk.Label()
		self.label_nograv =  gtk.Label()
		self.label_import = gtk.Label()
		self.label_import_trib = gtk.Label()
		self.label_trib_compras = gtk.Label()
		tabla_compras.attach(self.label_compras,1,2,1,2)
		tabla_compras.attach(self.label_compras_trib,2,3,1,2)
		tabla_compras.attach(self.label_nograv,1,2,2,3)
		tabla_compras.attach(self.label_import,1,2,3,4)
		tabla_compras.attach(self.label_import_trib,2,3,3,4)
		tabla_compras.attach(self.label_trib_compras,2,3,4,5)
		frame_renta = gtk.Frame('Renta')
		vbox_main.pack_start(frame_renta)
		tabla_renta = gtk.Table(3,3)
		frame_renta.add(tabla_renta)
		tabla_renta.attach(gtk.Label('Sistema B (%)'),0,2,0,1)
		self.label_rentaporc = gtk.Label()
		tabla_renta.attach(self.label_rentaporc,2,3,0,1)
		tabla_renta.attach(gtk.Label('INGRESO NETO'),0,1,2,3)
		tabla_renta.attach(gtk.Label('BASE'),1,2,1,2)
		tabla_renta.attach(gtk.Label('TRIBUTO'),2,3,1,2)
		self.label_renta_base = gtk.Label()
		self.label_renta_trib = gtk.Label()
		tabla_renta.attach(self.label_renta_base,1,2,2,3)
		tabla_renta.attach(self.label_renta_trib,2,3,2,3)
		frame_deuda = gtk.Frame('Deuda')
		vbox_main.pack_start(frame_deuda)
		tabla_deuda = gtk.Table(3,13)
		frame_deuda.add(tabla_deuda)
		tabla_deuda.attach(gtk.Label('Impuesto Resultante o Saldo a Favor'),0,1,1,2)
		tabla_deuda.attach(gtk.Label('Saldo a Favor del Periodo Anterior'),0,1,2,3)
		tabla_deuda.attach(gtk.Label('Tributo a Pagar o Saldo a Favor'),0,1,3,4)
		tabla_deuda.attach(gtk.Label('Retenciones declaradas el Periodo'),0,1,5,6)
		tabla_deuda.attach(gtk.Label('Retenciones declaradas en Periodos anteriores'),0,1,6,7)
		tabla_deuda.attach(gtk.Label('Total de Deuda Tributaria'),0,1,8,9)
		tabla_deuda.attach(gtk.Label('Percepciones'),0,1,9,10)
		tabla_deuda.attach(gtk.Label('Percepciones Anteriores'),0,1,10,11)
		tabla_deuda.attach(gtk.Label('Importe a Pagar'),0,1,11,12)
		tabla_deuda.attach(gtk.Label('Pago'),0,1,12,13)
		tabla_deuda.attach(gtk.Label('Deuda Pendiente'),0,1,13,14)
		self.label_igv = gtk.Label()
		self.label_renta = gtk.Label()
		self.label_anterior = gtk.Label()
		self.label_tributo = gtk.Label()
		self.label_retenciones = gtk.Label()
		self.label_retenciones_ant = gtk.Label()
		self.label_total = gtk.Label()
		self.label_renta2 = gtk.Label()
		self.label_percepciones = gtk.Label('0')
		self.label_percepcionesant = gtk.Label('0')
		self.label_importe_igv = gtk.Label()
		self.label_pago_igv = gtk.Label()
		self.label_deuda_igv = gtk.Label()
		self.label_importe_renta = gtk.Label()
		self.label_pago_renta = gtk.Label()
		self.label_deuda_renta = gtk.Label()
		tabla_deuda.attach(self.label_igv,1,2,1,2)
		tabla_deuda.attach(self.label_renta,2,3,1,2)
		tabla_deuda.attach(self.label_anterior,1,2,2,3)
		tabla_deuda.attach(self.label_tributo,1,2,3,4)
		tabla_deuda.attach(self.label_retenciones,1,2,5,6)
		tabla_deuda.attach(self.label_retenciones_ant,1,2,6,7)
		tabla_deuda.attach(self.label_total,1,2,8,9)
		tabla_deuda.attach(self.label_renta2,2,3,8,9)
		tabla_deuda.attach(self.label_percepciones,1,2,9,10)
		tabla_deuda.attach(self.label_percepcionesant,1,2,10,11)
		tabla_deuda.attach(self.label_importe_igv,1,2,11,12)
		tabla_deuda.attach(self.label_pago_igv,1,2,12,13)
		tabla_deuda.attach(self.label_deuda_igv,1,2,13,14)
		tabla_deuda.attach(self.label_importe_renta,2,3,11,12)
		tabla_deuda.attach(self.label_pago_renta,2,3,12,13)
		tabla_deuda.attach(self.label_deuda_renta,2,3,13,14)
		self.entry_periodo.entry.connect('changed',self.leer)
		but_calcular.connect('clicked',self.calcular)
		but_print.connect('clicked',self.imprimir)
		
		self.show_all()
	
	def leer(self,widget):
	  periodo = widget.get_text()
	  igv = Decimal('0.18')
	  sql = "SELECT VENTAS,EXPORTACIONES,COMPRAS,COMPRASTRIB,NGRAVADAS,IMPORTACIONES,RENTAPORC,SUBTOTAL,ANTERIOR,RETENCIONES,RETENCIONESANT,PERCEPCIONES,PERCEPCIONESANT,PAGOIGV,DEUDAIGV,PAGORENTA,DEUDARENTA FROM balances WHERE PERIODO='%s'"%periodo
	  self.cursor.execute(sql)
	  if self.cursor.rowcount == 0:
	    return
	  else:
	    ventas,exportaciones,compras,comprastrib,ngravadas,importaciones,rentaporc,subtotal,anterior,retenciones,retencionesant,percepciones,percepcionesant,pagoigv,deudaigv,pagorenta,deudarenta = self.cursor.fetchone()
	    self.label_ventasn.set_text(str(ventas))
	    tributo1 = int(round(ventas*igv))
	    self.label_ventasn_trib.set_text(str(tributo1))
	    self.label_export.set_text(str(exportaciones))
	    tributo2 = int(round(exportaciones*igv))
	    self.label_export_trib.set_text(str(tributo2))
	    self.label_trib_ventas.set_text(str(tributo1+tributo2))
	    self.label_compras.set_text(str(compras))
	    self.label_compras_trib.set_text(str(comprastrib))
	    self.label_nograv.set_text(str(ngravadas))
	    self.label_import.set_text(str(importaciones))
	    tributo3 = int(round(importaciones*igv))
	    self.label_import_trib.set_text(str(tributo3))
	    self.label_trib_compras.set_text(str(tributo3+comprastrib))
	    self.label_rentaporc.set_text(str(rentaporc))
	    renta_base = ventas+exportaciones
	    self.label_renta_base.set_text(str(renta_base))
	    renta = int(round(renta_base*rentaporc/100))
	    self.label_renta_trib.set_text(str(renta))
	    suma = tributo1+tributo2-comprastrib-tributo3
	    self.label_igv.set_text(str(suma))
	    self.label_anterior.set_text(str(anterior))
	    self.label_tributo.set_text(str(suma+anterior))
	    self.label_retenciones.set_text(str(retenciones))
	    self.label_retenciones_ant.set_text(str(retencionesant))
	    total = suma+anterior-retenciones-retencionesant
	    self.label_total.set_text(str(total))
	    self.label_percepciones.set_text(str(percepciones))
	    self.label_percepcionesant.set_text(str(percepcionesant))
	    self.label_importe_igv.set_text(str(total-percepciones-percepcionesant))
	    self.label_importe_renta.set_text(str(renta))
	    self.label_renta.set_text(str(renta))
	    self.label_pago_igv.set_text(str(pagoigv))
	    self.label_pago_renta.set_text(str(pagorenta))
	    self.label_deuda_igv.set_text(str(deudaigv))
	    self.label_deuda_renta.set_text(str(deudarenta))
	    if suma != subtotal:
	      alerta = Estilos.Alerta('Error','Vuelva a Calcular')
	      print suma,subtotal
	      if alerta.run() == gtk.RESPONSE_OK:
		alerta.destroy()

	def calcular(self,widget):
	  periodo = self.entry_periodo.get_text()
	  igv = Decimal('0.18')
	  sql = "SELECT SUM(IF(facturas.MONEDA=2,facturas.PRECIO*cambio.VALOR,facturas.PRECIO)) AS SOLES FROM facturas JOIN cambio ON cambio.DIA=facturas.FECHA WHERE facturas.FECHA LIKE '%s' AND facturas.ANULADO=0"%(periodo+'-%')
	  self.cursor.execute(sql)
	  v = self.cursor.fetchone()
	  if v[0] is None:
	  	ventas = 0
	  else:
	  	ventas = int(v[0])
	  sql = """SELECT  f.FECHA, CONCAT(f.SERIE,'-',f.NUMERO) AS DOC,e.COMERCIAL,e.RUC,
IF(f.MONEDA=1,f.PRECIO,f.PRECIO*c.VALOR) AS NETO,
IF(f.MONEDA=1,f.PRECIO*0.18,f.PRECIO*0.18*c.VALOR) AS IGV,
IF(f.MONEDA=1,f.PRECIO*1.18,f.PRECIO*1.18*c.VALOR) AS TOTAL, ANULADO
FROM facturas AS f
JOIN clientes AS e ON e.ID = f.EMPRESA
JOIN cambio AS c ON c.DIA = f.FECHA
WHERE FECHA LIKE  '%s'""" % (periodo+'-%')
	  self.cursor.execute(sql)
	  queryventas = self.cursor.fetchall()
	  wb = xlwt.Workbook()
	  ws = wb.add_sheet('Ventas', cell_overwrite_ok=True)
	  x = 0
	  y = 0
	  stylefecha = xlwt.easyxf('', num_format_str='DD-MM-YY')
	  stylebold = xlwt.easyxf('font: name Ubuntu, colour red, bold on')
	  sumaneto = 0
	  sumaigv = 0
	  sumatotal = 0
	  for fila in queryventas:
	      for celda in fila:
	          if x == 0:
	              ws.write(y, x, celda, stylefecha)
	          else:
	              ws.write(y, x, celda)
	          if x == 4 and not fila[7]:
	              sumaneto += celda
	          elif x == 5 and not fila[7]:
	              sumaigv += celda
	          elif x == 6 and not fila[7]:
	              sumatotal += celda
	          x += 1
	      y += 1
	      x = 0
	  ws.write(y, 4, sumaneto, stylebold)
	  ws.write(y, 5, sumaigv, stylebold)
	  ws.write(y, 6, sumatotal, stylebold)
	  sql = """SELECT c.IDP, c.DIA, c.TIPO, c.SERIE, c.NUM, c.RUC, p.NOMBRE,
IF(c.MONEDA=1,c.NETO,c.NETO*c.TK) AS NETO,
IF(c.MONEDA=1,c.NGRAVADA,c.NGRAVADA*c.TK) AS NGRAV,
IF(c.MONEDA=1,c.GRAVADA,c.GRAVADA*c.TK) AS GRAVADA,
IF(c.MONEDA=1,c.IGV,c.IGV*c.TK) AS IGV,
IF(c.MONEDA=1,c.TOTAL,c.TOTAL*c.TK) AS TOTAL
FROM compras AS c
JOIN proveedores AS p ON p.ruc = c.RUC
WHERE  `MES` =  '%s'""" % (periodo)
	  self.cursor.execute(sql)
	  queryventas = self.cursor.fetchall()
	  ws = wb.add_sheet('Compras', cell_overwrite_ok=True)
	  x = 0
	  y = 0
	  stylefecha = xlwt.easyxf('', num_format_str='DD-MM-YY')
	  stylebold = xlwt.easyxf('font: name Ubuntu, colour red, bold on')
	  suma7 = 0
	  suma8 = 0
	  suma9 = 0
	  suma10 = 0
	  suma11 = 0
	  for fila in queryventas:
	      for celda in fila:
	          if x == 1:
	              ws.write(y, x, celda, stylefecha)
	          else:
	              ws.write(y, x, celda)
	          if x == 7:
	              suma7 += celda
	          elif x == 8:
	              suma8 += celda
	          elif x == 9:
	              suma9 += celda
	          elif x == 10:
	              suma10 += celda
	          elif x == 11:
	              suma11 += celda
	          x += 1
	      y += 1
	      x = 0
	  ws.write(y, 7, suma7, stylebold)
	  ws.write(y, 8, suma8, stylebold)
	  ws.write(y, 9, suma9, stylebold)
	  ws.write(y, 10, suma10, stylebold)
	  ws.write(y, 11, suma11, stylebold)
	  y += 1
	  ws.write(y, 7, 'NETO', stylebold)
	  ws.write(y, 8, 'NGRAVADA', stylebold)
	  ws.write(y, 9, 'GRAVADA', stylebold)
	  ws.write(y, 10, 'IGV', stylebold)
	  ws.write(y, 11, 'TOTAL', stylebold)
	  wb.save('balance.xls')
	  os.system("gnome-open 'balance.xls'")
	  igvventas = round(ventas*igv)
	  print 'Ventas:',ventas
	  print 'IGV Ventas:',igvventas
	  sql = "SELECT sum(IF(compras.MONEDA=2,compras.GRAVADA*cambio.VALOR,compras.GRAVADA)) AS GRAVADA, sum(IF(compras.MONEDA=2,compras.NGRAVADA*cambio.VALOR,compras.NGRAVADA)) AS NGRAVADA, sum(IF(compras.MONEDA=2,compras.IGV*cambio.VALOR,compras.IGV)) AS IGV, sum(IF(compras.MONEDA=2,(GRAVADA*0.18-IGV)*cambio.VALOR,GRAVADA*0.18-IGV)) AS DIF FROM compras JOIN cambio ON cambio.DIA=compras.DIA WHERE compras.MES = '%s'"%periodo
	  self.cursor.execute(sql)
	  gravada,ngravada,igvcomp,dif = self.cursor.fetchone()
	  igvcompras = round(round(gravada)*0.18)
	  gravada = round(gravada)
	  ngravada = round(ngravada)
	  igvcomp = round(igvcomp)
	  print 'Compras:',gravada
	  print 'NGravada:',ngravada
	  print 'IGV:',igvcomp,igvcompras#real,calculado
	  print 'DIF:',dif
	  sql = "SELECT sum(IF(compras.MONEDA=2,(IGV-GRAVADA*0.18)*cambio.VALOR,IGV-GRAVADA*0.18)) AS DIF FROM compras JOIN cambio ON cambio.DIA=compras.DIA WHERE compras.MES = '%s' AND compras.CALCULO=5"%periodo
	  self.cursor.execute(sql)
	  igvimport = self.cursor.fetchone()[0]
	  if igvimport == None:
	    igvimport = 0
	  importaciones = int(round(igvimport/igv))
	  print 'Importaciones =', importaciones
	  print 'IGV import = ', igvimport
	  compras = igvcomp+int(igvimport)
	  rentaporc = Decimal('2.03')
	  renta = int(round(ventas*rentaporc/100))
	  subtotal = igvventas-igvcompras-round(igvimport)
	  export = 0
	  sql = "SELECT SUBTOTAL,ANTERIOR,RETENCIONES,RETENCIONESANT,PERCEPCIONES,PERCEPCIONESANT FROM balances WHERE PERIODO<'%s' ORDER BY PERIODO DESC LIMIT 1"%periodo
	  self.cursor.execute(sql)
          print sql
	  if self.cursor.rowcount == 0:
	    anterior,retencionesant,percepcionesant = (0,0,0)
	  else:
	    sub,ant,ret,retant,perp,perpant = self.cursor.fetchone()
	    anterior = sub+ant
            #falta calcular mejor
	    if anterior > 0:
	      anterior = 0
              retencionesant = 0
              percepcionesant = 0
            else:
              retencionesant = ret+retant
              percepcionesant = perp+perpant
              print perp+perpant
	  tributo = subtotal+anterior
	  retenciones = 0
	  total = tributo-retenciones
	  if total<0:
	    total = 0
	  percepciones = 0
	  importe = total-percepciones-percepcionesant
	  sql = "DELETE FROM balances WHERE PERIODO='%s'"%periodo
	  self.cursor.execute(sql)
	  columnas = "PERIODO,VENTAS,EXPORTACIONES,COMPRAS, COMPRASTRIB,NGRAVADAS,IMPORTACIONES, RENTAPORC,SUBTOTAL,ANTERIOR, RETENCIONES,RETENCIONESANT,PERCEPCIONES,PERCEPCIONESANT, PAGOIGV,DEUDAIGV,PAGORENTA,DEUDARENTA"
	  valores  = (columnas,periodo,ventas,export,gravada, igvcompras,ngravada,importaciones, rentaporc,subtotal,anterior, retenciones,retencionesant,percepciones,percepcionesant, 0,importe,0,renta)
	  sql = "INSERT INTO balances (%s) VALUES ('%s',%d,%d,%d, %d,%d,%d, %s,%d,%d, %d,%d,%d,%d, %d,%d,%d,%d)"%valores
	  print sql
	  self.cursor.execute(sql)
	  self.leer(self.entry_periodo)


	def imprimir(self,widget):
	  return

if __name__ == "__main__":
    consulta = Consultas.Conectar()
    Ventana(consulta)
    gtk.main()
