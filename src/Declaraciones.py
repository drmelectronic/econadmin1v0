#! /usr/bin/python
# -*- coding: utf-8 -*-

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
		self.set_title("Declaraciones")
		vbox_main = gtk.VBox(False,0)
		self.add(vbox_main)


if __name__ == "__main__":
    print "Hello World";
