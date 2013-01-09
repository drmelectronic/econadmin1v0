#! /usr/bin/python
# -*- encoding: utf8 -*-

import sys
import gtk
import appindicator
import Cotizaciones
import Clientes
import Contactos
import Consultas
import Cambio
import Proveedores
import Facturas
import Guias
import Compras
import Cheques
import Balances
import Stock
import threading
import os

class Applet:
	def __init__(self):
		self.consulta = Consultas.Conectar()
		#icono en /usr/share/icons/Humanity/categories/64
		self.ind = appindicator.Indicator("EconAdmin","package_office",appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)
		self.ind.set_attention_icon("new-messages-red")
		self.menu_setup()
		self.ind.set_menu(self.menu)

	def menu_setup(self):
		self.menu = gtk.Menu()
		nombres = ("Clientes","Contactos","Cotizaciones","Facturas","Guías",None,"Tipo de Cambio","Proveedores","Compras","Stock","Cheques",None,"Balances","Refrescar")
		funciones = (self.clientes,self.contactos,self.cotizaciones,self.facturas,self.guias,None,self.cambio,self.proveedores,self.compras,self.stock,self.cheques,None,self.balances,self.refrescar)
		for i in range(len(nombres)):
			if nombres[i] == None:
				item = gtk.SeparatorMenuItem()
			else:
				item = gtk.MenuItem(nombres[i])
				item.connect('activate',funciones[i])
			self.menu.append(item)
		self.menu.show_all()

	def clientes(self,widget):
		Clientes.Ventana(self.consulta)

	def contactos(self,widget):
		Contactos.Ventana(self.consulta)

	def cotizaciones(self,widget):
		Cotizaciones.Ventana(self.consulta)
                
        def facturas(self,widget):
          Facturas.Ventana(self.consulta)
        
        def guias(self,widget):
          Guias.Ventana(self.consulta)

	def cambio(self,widget):
		Cambio.Ventana(self.consulta)

	def proveedores(self,widget):
		Proveedores.Ventana(self.consulta)

	def compras(self,widget):
		Compras.Ventana(self.consulta)
        
        def stock(self,widget):
		Stock.Ventana(self.consulta)
        
        def cheques(self,widget):
                Cheques.Ventana(self.consulta)
		
	def balances(self,widget):
		Balances.Ventana(self.consulta)

	def refrescar(self,widget):
                comm = "cp -R /home/daniel/Documentos/Python/EconAdmin/src/ ../"
		command = os.popen(comm)
		read = command.read()
		self.consulta = Consultas.Conectar()
		reload(Cotizaciones)
		reload(Clientes)
		reload(Contactos)
                reload(Facturas)
                reload(Guias)
		reload(Consultas)
		reload(Cambio)
		reload(Cheques)
		reload(Balances)
		reload(Proveedores)
		reload(Compras)

	def salir(self, widget):
		sys.exit(0)


if __name__ == "__main__":
		indicator = Applet()
		gtk.main()
