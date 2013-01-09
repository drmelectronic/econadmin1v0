#! /usr/bin/python
# -*- coding: utf-8 -*-

# To change this template, choose Tools | Templates
# and open the template in the editor.
import MySQLdb
from xml.dom import minidom
import gtk
import gobject

__author__="econain"
__date__ ="$02/06/2011 10:45:40 AM$"

class Conectar():
	def __init__(self):
		xmldoc = minidom.parse("../config.xml")
		host = getXML(xmldoc, "host")
		user = getXML(xmldoc, "user")
		passwd = getXML(xmldoc, "passwd")
		db = getXML(xmldoc, "db")
		charset = getXML(xmldoc, "charset")
		init_command = getXML(xmldoc, "init_command")
		www = getXML(xmldoc, "www")
		try:
			DB = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset=charset, init_command=init_command)
		except:
			DB = MySQLdb.connect(host=www, user=user, passwd=passwd, db=db, charset=charset, init_command=init_command)
		self.cursor = DB.cursor()
		self.www = www

	def apertura(self, dia, mes, ano, ruta, lado, listmodel, column_names):
		self.cursor.execute(("""SELECT FECHA, PRIMERA, ULTIMA, FRECUENCIA, CANTIDAD, RUTA, LADO FROM apertura ORDER BY FECHA DESC"""))
		items = self.cursor.fetchall()
		treeview, treemodel = self.create_model(column_names, items, listmodel)
		return treeview, treemodel


	def salidas(self, dia, ruta, lado, listmodel, column_names):
		self.cursor.execute(("""SELECT PADRON, HORA, FRECUENCIA FROM salidas WHERE DIA = "%s" AND ESTADO = 1""")% (dia))
		items = self.cursor.fetchall()
		treeview, treemodel = self.create_model(column_names, items, listmodel)
		return treeview, treemodel

	def disponibles(self, dia, ruta, lado, listmodel, column_names):
		self.cursor.execute(("""SELECT PADRON, HORA, FRECUENCIA, ID FROM salidas WHERE DIA = "%s" AND ESTADO = 0""")% (dia))
		items = self.cursor.fetchall()
		treeview, treemodel = self.create_model(column_names, items, listmodel)
		return treeview, treemodel

	def excluidos(self, dia, ruta, lado, listmodel, column_names):
		self.cursor.execute(("""SELECT PADRON, HORA, FRECUENCIA FROM salidas WHERE DIA = "%s" AND ESTADO = 2""")% (dia))
		items = self.cursor.fetchall()
		treeview, treemodel = self.create_model(column_names, items, listmodel)
		return treeview, treemodel

	def vueltas_padron(self, dia, mes, ano, padron, listmodel, column_names):
		if padron == "":
			padron = "0"
		sql = ("""SELECT `salidas`.`LADO`, `salidas`.`HORA`, `mcontroles`.`HORA` FROM `salidas` JOIN `mcontroles` ON `salidas`.`ID` = `mcontroles`.`SALIDA` WHERE `salidas`.`PADRON` = %s AND `salidas`.`DIA` = "%s-%s-%s" """)% (padron, ano, mes, dia)
		self.cursor.execute(sql)
		items = self.cursor.fetchall()
		treeview, treemodel = self.create_model(column_names, items, listmodel)
		return treeview, treemodel

	def create_model(self, column_names, items, listmodel):
		treemodel = gtk.TreeModelSort(listmodel)
		treemodel.set_sort_column_id(0, gtk.SORT_ASCENDING)
		treeview = gtk.TreeView(treemodel)
		for i in range(len(column_names)):
			cell_text = gtk.CellRendererText()
			tvcolumn = gtk.TreeViewColumn(column_names[i])
			tvcolumn.pack_start(cell_text, True)
			tvcolumn.set_attributes(cell_text, text=i)
			treeview.append_column(tvcolumn)
		treeview.set_reorderable(True)
		for item in items:
			listmodel.append(item)
		return  treeview, treemodel
		
	
	def actualizar_model(self, column_names, items, listmodel, treemodel, treeview):
		for item in items:
			listmodel.append(item)
		return  treeview, treemodel
		

	def salidas_act(self, dia, ruta, lado, listmodel):
		self.cursor.execute(("""SELECT PADRON, HORA, FRECUENCIA FROM salidas WHERE DIA = "%s" AND ESTADO = 1""")% (dia))
		items = self.cursor.fetchall()
		for item in items:
			listmodel.append(item)

	def disponibles_act(self, dia, ruta, lado, listmodel):
		self.cursor.execute(("""SELECT PADRON, HORA, FRECUENCIA FROM salidas WHERE DIA = "%s" AND ESTADO = 0""")% (dia))
		items = self.cursor.fetchall()
		for item in items:
			listmodel.append(item)

	def excluidos_act(self, dia, ruta, lado, listmodel):
		self.cursor.execute(("""SELECT PADRON, HORA, FRECUENCIA FROM salidas WHERE DIA = "%s" AND ESTADO = 2""")% (dia))
		items = self.cursor.fetchall()
		for item in items:
			listmodel.append(item)


def getXML(xml, etiqueta):
	reflist = xml.getElementsByTagName(etiqueta)
	ref = reflist[0]
	nodelist = ref.childNodes
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)

if __name__ == "__main__":
	w = Conectar()
	w.rutas()


