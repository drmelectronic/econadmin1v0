#! /usr/bin/python
# -*- coding: utf-8 -*-
# To change this template, choose Tools | Templates
# and open the template in the editor.
import time
import gtk
import threading

__author__="econain"
__date__ ="$05/08/2011 11:26:40 AM$"

class WindowMain:
	def __init__(self):
		self.w = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.w.set_default_size(200,200)
		vbox_main = gtk.VBox(False,0)
		self.w.add(vbox_main)
		tag_negrita= gtk.TextTag('negrita')
		tag_negrita.set_property('weight',700)
		tag_table = gtk.TextTagTable()
		tag_table.add(tag_negrita)
		self.buffer = gtk.TextBuffer(tag_table)
		self.temp = gtk.TextView(self.buffer)
		vbox_main.pack_start(self.temp)
		self.entry = gtk.Entry()
		vbox_main.pack_start(self.entry)
		self.but_copiar= gtk.Button("Copiar")
		self.but_copiar.connect('clicked',self.copiar)
		vbox_main.pack_start(self.but_copiar)
		self.a = True
		self.but_format= gtk.Button("formatear")
		self.but_format.connect('clicked',self.format)
		vbox_main.pack_start(self.but_format)
		self.w.show_all()
		self.format(None)

	def copiar(self, widget):
		inicio = self.buffer.get_start_iter()
		fin = self.buffer.get_end_iter()
		texto = self.buffer.get_text(inicio,fin,True)
		print texto

	def format(self, widget):
		with open('/home/danielypamela/Escritorio/Documento.html','r') as archivo:
			html = archivo.read()
			lineas = html.split('</tr><tr')
			i = 0
			for linea in lineas:
				if i == 0:
					col = linea.split('<b>')
					linea = col[1].split('</b>')
					texto = linea[0]
				else:
					col = linea.split('</td>')
					if len(col) == 2:
						linea = col[0].split('3>')
						texto = linea[1].split('<')[0]
					if len(col) == 3:
						linea = col[1].split('2>')
						texto = ' - '+linea[1]
					if len(col) == 4:
						col1 = col[1].split('>')[1]
						col2 = col[2].split('>')[1]
						texto = ' '+col1+' '+col2
				print texto
				i += 1

if __name__ == "__main__":
	gtk.gdk.threads_init()
	w = WindowMain()
	gtk.main()