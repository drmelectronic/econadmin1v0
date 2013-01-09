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

	def copiar(self, widget):
		inicio = self.buffer.get_start_iter()
		fin = self.buffer.get_end_iter()
		texto = self.buffer.get_text(inicio,fin,True)
		print texto

	def format(self, widget):
		with open('/home/danielypamela/Escritorio/Documento.html','w') as archivo:
			texto = """<table width=65 cellpadding=4 cellspacing=0 border=0><col width=><col><col>"""
			lineas = self.buffer.get_line_count()
			for i in range(lineas):
				inicio = self.buffer.get_iter_at_line(i)
				if i == lineas-1:
					fin = self.buffer.get_end_iter()
				else:
					fin = self.buffer.get_iter_at_line(i+1)
				linea = str(self.buffer.get_text(inicio,fin,False))
				if i == 0:
					texto = texto+"""<tr valign=top><td colspan=3><b>%s</b></td></tr></tr>"""%linea[:-1]
				elif " " == linea[0]:
					linea = linea[1:]
					if "-" == linea[0]:
						linea = linea[2:]
						texto = texto+"""<tr><td>-</td><td colspan=2>%s</td></tr>"""%linea[:-1]
					else:
						tabs = linea.split(':')
						if len(tabs) == 2:
							print tabs
							texto = texto+"""<tr><td></td><td>%s:</td><td>%s</td></tr>"""%(tabs[0],tabs[1][1:-1])
						else:
							texto = texto+"""<tr><td></td><td colspan=2>%s</td></tr>"""%tabs[:-1]
				else:
					if i == lineas-1:
						texto = texto+"""<tr valign=top><td colspan=3>%s</td></tr>"""%linea
					else:
						texto = texto+"""<tr valign=top><td colspan=3>%s</td></tr>"""%linea[:-1]

			print texto
			archivo.write(texto)

if __name__ == "__main__":
	gtk.gdk.threads_init()
	w = WindowMain()
	gtk.main()
	def format(self, widget):
		with open('/home/danielypamela/Escritorio/Documento.html','w') as archivo:
			texto = """<table width=65 cellpadding=4 cellspacing=0 border=0><col width=><col><col>"""
			lineas = self.buffer.get_line_count()
			for i in range(lineas):
				inicio = self.buffer.get_iter_at_line(i)
				if i == lineas-1:
					fin = self.buffer.get_end_iter()
				else:
					fin = self.buffer.get_iter_at_line(i+1)
				linea = str(self.buffer.get_text(inicio,fin,False))
				if i == 0:
					texto = texto+"""<tr valign=top><td colspan=3><b>%s</b></td></tr></tr>"""%linea[:-1]
				elif " " == linea[0]:
					linea = linea[1:]
					if "-" == linea[0]:
						linea = linea[2:]
						texto = texto+"""<tr><td>-</td><td colspan=2>%s</td></tr>"""%linea[:-1]
					else:
						tabs = linea.split(':')
						if len(tabs) == 2:
							print tabs
							texto = texto+"""<tr><td></td><td>%s:</td><td>%s</td></tr>"""%(tabs[0],tabs[1][1:-1])
						else:
							texto = texto+"""<tr><td></td><td colspan=2>%s</td></tr>"""%tabs[:-1]
				else:
					if i == lineas-1:
						texto = texto+"""<tr valign=top><td colspan=3>%s</td></tr>"""%linea
					else:
						texto = texto+"""<tr valign=top><td colspan=3>%s</td></tr>"""%linea[:-1]

			print texto
			archivo.write(texto)

if __name__ == "__main__":
	gtk.gdk.threads_init()
	w = WindowMain()
	gtk.main()