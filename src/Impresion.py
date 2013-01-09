#! /usr/bin/python
# -*- coding: utf-8 -*-
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, BaseDocTemplate,Frame,PageTemplate,PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, PropertySet
from reportlab.lib import colors
from reportlab.lib.units import cm
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_RIGHT,TA_CENTER
from reportlab.lib.fonts import addMapping
import reportlab.rl_config
from decimal import Decimal
import string
trans = string.maketrans('áéíóúñ','ÁÉÍÓÚÑ')
reportlab.rl_config.warnOnMissingFontGlyphs = 0
ruta = '../fonts/'
#ruta = '/usr/share/fonts/truetype/ubuntu-font-family/'
pdfmetrics.registerFont(TTFont('Ubuntu', ruta+'Ubuntu-R.ttf'))
pdfmetrics.registerFont(TTFont('UbuntuB', ruta+'Ubuntu-B.ttf'))
pdfmetrics.registerFont(TTFont('UbuntuBI', ruta+'Ubuntu-BI.ttf'))
pdfmetrics.registerFont(TTFont('UbuntuRI', ruta+'Ubuntu-RI.ttf'))
pdfmetrics.registerFontFamily('Ubuntu',normal='Ubuntu',bold='UbuntuB',italic='UbuntuRI',boldItalic='UbuntuBI',)
pdfmetrics.registerFont(TTFont('Calibri', ruta+'CALIBRI.TTF'))
pdfmetrics.registerFont(TTFont('CalibriB', ruta+'CALIBRIB.TTF'))
pdfmetrics.registerFont(TTFont('CalibriBI', ruta+'CALIBRIZ.TTF'))
pdfmetrics.registerFont(TTFont('CalibriRI', ruta+'CALIBRII.TTF'))
pdfmetrics.registerFontFamily('Calibri',normal='Calibri',bold='CalibriB',italic='CalibriRI',boldItalic='CalibriBI',)
pdfmetrics.registerFont(TTFont('Consolas', ruta+'CONSOLA.TTF'))
pdfmetrics.registerFont(TTFont('ConsolasB', ruta+'CONSOLAB.TTF'))
pdfmetrics.registerFont(TTFont('ComsolasBI', ruta+'CONSOLAZ.TTF'))
pdfmetrics.registerFont(TTFont('ConsolasRI', ruta+'CONSOLAI.TTF'))
pdfmetrics.registerFontFamily('Consolas',normal='Consolas',bold='CalibriB',italic='CalibriRI',boldItalic='CalibriBI',)
__author__="econain"
__date__ ="$11/11/2011 10:53:44 AM$"
UNIDADES = ( '', 'UN ', 'DOS ', 'TRES ', 'CUATRO ', 'CINCO ', 'SEIS ', 'SIETE ', 'OCHO ', 'NUEVE ', 'DIEZ ', 'ONCE ', 'DOCE ', 'TRECE ', 'CATORCE ', 'QUINCE ', 'DIECISEIS ', 'DIECISIETE ', 'DIECIOCHO ', 'DIECINUEVE ', 'VEINTE ')
DECENAS = ('VENTI', 'TREINTA ', 'CUARENTA ', 'CINCUENTA ', 'SESENTA ', 'SETENTA ', 'OCHENTA ', 'NOVENTA ', 'CIEN ')
CENTENAS = ('CIENTO ', 'DOSCIENTOS ', 'TRESCIENTOS ', 'CUATROCIENTOS ', 'QUINIENTOS ', 'SEISCIENTOS ', 'SETECIENTOS ', 'OCHOCIENTOS ', 'NOVECIENTOS '  )

def num_a_letras(number_in):
    convertido = ''
    number_str = str(number_in) if (type(number_in) != 'str') else number_in
    number_str =  number_str.zfill(9)
    millones, miles, cientos = number_str[:3], number_str[3:6], number_str[6:]
    if(millones):
        if(millones == '001'):
            convertido += 'UN MILLON '
        elif(int(millones) > 0):
            convertido += '%sMILLONES ' % __convertNumber(millones)
    if(miles):
        if(miles == '001'):
            convertido += 'MIL '
        elif(int(miles) > 0):
            convertido += '%sMIL ' % __convertNumber(miles)
    if(cientos):
        if(cientos == '001'):
            convertido += 'UN '
        elif(int(cientos) > 0):
            convertido += '%s ' % __convertNumber(cientos)
    return convertido

def __convertNumber(n):
    output = ''
    if(n == '100'):
        output = "CIEN "
    elif(n[0] != '0'):
        output = CENTENAS[int(n[0])-1]
    k = int(n[1:])
    if(k <= 20):
        output += UNIDADES[k]
    else:
        if((k > 30) & (n[2] != '0')):
            output += '%sY %s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])
        else:
            output += '%s%s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])
    return output

class Membrete(BaseDocTemplate):
	def __init__(self,filename,**kw):
		self.estilos ={'texto':
			ParagraphStyle(name='texto',
				alignment = TA_JUSTIFY,
				fontName = 'Ubuntu',
				fontSize = 10,
				leading = 14,
				firstLineIndent = 20,
				),
				'titulo':
				ParagraphStyle(name='titulo',
				alignment = TA_RIGHT,
				fontName = 'Ubuntu',
				fontSize = 11,
				leading = 14,
				textColor = '#0000CC',
				),
				'pie':
				ParagraphStyle(name='pie',
				alignment = TA_CENTER,
				fontName = 'Calibri',
				fontSize = 9,
				leading = 14,
				textColor = '#0000CC',
				),
				}
		apply(BaseDocTemplate.__init__,(self,filename))
		self.mostrar = 0
		self.allowSplitting = 1
		self.showBoundary = self.mostrar
		self.MARGEN = 1.5*cm
		ruta_logo = os.path.join('../images/header.png')
		self.logo = Image(ruta_logo,width=2.00*cm*1.7,height=1.15*cm*1.7)
		self.logo.hAlign = 'CENTER'
		self.logocAlign = 'TOP'
		frameDatos = Frame(self.MARGEN,3.8*cm,A4[0]-(self.MARGEN*2),23*cm,id='datos',showBoundary=self.mostrar)
		template = PageTemplate('pagina_normal',[frameDatos],self.formato)
		self.addPageTemplates(template)
						
	def cabecera(self,canvas):
		origen = Frame(self.MARGEN,A4[1]-2*cm,A4[0]-(2*self.MARGEN),1*cm,id='cabecera',showBoundary=self.mostrar)
		story = []
		story.append(Paragraph("Don Quijote",self.estilos['titulo']))
		origen.addFromList(story,canvas)
		canvas.line(x1=self.MARGEN,y1=A4[1]-2*cm,x2=A4[0]-(2*self.MARGEN),y2=A4[1]-2*cm)

	def formato(self,canvas,doc):
		canvas.saveState()
		self.cabecera(canvas)
		canvas.restoreState()

#		estiloHoja = getSampleStyleSheet()
#		story = []
#		logo = Image(os.path.realpath('../images/encabezado-nuevo.png'),400,100)
#		story.append(logo)
#		t = Titulo('p')
#		story.append(t)
#
#		doc = SimpleDocTemplate('../ejemplo1.pdf',pagesize=A4,showBoundary=1)
#		doc.build(story)

class Titulo(PropertySet):
	defaults = {
		'fontName':'Times-Roman',
		'fontSize':10,
		'leading':12,
		'leftIndent':0,
		'rightIndent':0,
		'firstLineIndent':0,
		'alignment':TA_LEFT,
		'spaceBefore':0,
		'spaceAfter':0,
		'bulletFontName':'Times-Roman',
		'bulletFontSize':10,
		'bulletIndent':0,
		'textColor': '#000000',
		'backColor':None,
		'wordWrap':None,
		'borderWidth': 0,
		'borderPadding': 0,
		'borderColor': None,
		'borderRadius': None,
		'allowWidows': 1,
		'allowOrphans': 0,
	}

class NumberedCanvas(canvas.Canvas):
	def __init__(self,*args,**kwargs):
		canvas.Canvas.__init__(self,*args,**kwargs)
		self._saved_page_states = []

	def showPage(self):
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()

	def save(self):
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self.draw_page_number(num_pages)
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)

	def draw_page_number(self,page_count):
		self.setFont('Helvetica', 10)
		self.drawString(10*cm,1*cm,"{0} de {1}".format(self._pageNumber,page_count))

class NormalCanvas(canvas.Canvas):
	def __init__(self,*args,**kwargs):
		canvas.Canvas.__init__(self,*args,**kwargs)
		self._saved_page_states = []

	def showPage(self):
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()

	def save(self):
		for state in self._saved_page_states:
			self.__dict__.update(state)
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)

class Facturas:
	def __init__(self,cursor,id):
		self.id = id
		self.cursor = cursor
		sql = "SELECT DAY(FECHA),meses.NOMBRE,YEAR(FECHA),CONCAT(SERIE,'-',NUMERO),EMPRESA,COTIZ,OC,GUIA,pagos.NOMBRE,facturas.MONEDA,facturas.IGV FROM facturas JOIN pagos ON pagos.ID = facturas.PAGO JOIN meses ON meses.MES=MONTH(facturas.FECHA) WHERE facturas.ID=%d"%id
		cursor.execute(sql)
		dia,mes,year,corr,empresa,cotiz,compra,guia,pago,moneda,igv = cursor.fetchone()
		sql = "SELECT CANT,DESCRIPCION,PRECIO FROM factitems WHERE FACTURA=%d"%id
                cursor.execute(sql)
		rows = cursor.fetchall()
                sql = "SELECT NOMBRE,DIRECCION,RUC FROM clientes WHERE ID=%d"%empresa
		cursor.execute(sql)
		razon,direcc,ruc = cursor.fetchone()
                self.path = "../outs/factura.pdf"
		pdf = canvas.Canvas(self.path)
		pdf.setFont("Consolas",8)
		margen = (10,45)
		#posicion = 2.25x(distancia en mm)
                fecha = str(dia)+' de '+mes+' de '+str(year)
		pdf.drawString(445+margen[0],830-95-margen[1],corr)
		pdf.drawString(80+margen[0],830-150-margen[1],fecha)
		pdf.drawString(95+margen[0],830-170-margen[1],razon)
		pdf.drawString(310+margen[0],830-150-margen[1],direcc)
		pdf.drawString(450+margen[0],830-170-margen[1],str(ruc))
                pdf.drawString(280+margen[0],830-410-margen[1],guia)
		pdf.drawString(280+margen[0],830-427-margen[1],compra)
		pdf.drawString(280+margen[0],830-444-margen[1],pago)
                if moneda == 1:
                  simb = 'S/.'
                  denom = 'NUEVOS SOLES'
                else:
                  simb = '$'
                  denom = 'DÓLARES AMERICANOS'
		x,y,p = (56,205,10) #posicion
                valor = Decimal('0.00')
		for i,row in enumerate(rows):
			pdf.drawString(x+margen[0],830-y-margen[1],str(i+1).zfill(2))
			pdf.drawString(x+margen[0]+21,830-y-margen[1],str(row[0].quantize(Decimal('0.001'))).zfill(2))
                        pdf.drawString(x+margen[0]+385,830-y-margen[1],simb)
                        pdf.drawString(x+margen[0]+401,830-y-margen[1],str(row[2].quantize(Decimal('0.01'))))
                        total = row[0]*row[2]
                        total = total.quantize(Decimal('0.01'))
                        pdf.drawString(x+margen[0]+455,830-y-margen[1],simb)
                        pdf.drawString(x+margen[0]+471,830-y-margen[1],str(total).zfill(2))
                        valor += total
                        renglones = row[1].split('\n')
                        for linea in renglones:
                            while len(linea) > 80:
                                   palabras = linea.split(' ')
                                   c = 0
                                   ls = ''
                                   for pal in palabras:
                                       c += len(pal) + 1
                                       if c >= 80:
                                           break
                                       ls += pal + ' '
                                   pdf.drawString(x+margen[0]+55,830-y-margen[1],ls)
                                   linea = linea[len(ls):]
                                   y += p
                            pdf.drawString(x+margen[0]+55,830-y-margen[1],linea)
                            y += p
                pdf.drawString(margen[0]+510,830-408-margen[1],simb)
                pdf.drawString(margen[0]+530,830-408-margen[1],str(valor))
                pdf.drawString(margen[0]+475,830-428-margen[1],str(igv))
                impuesto = (valor*igv/100).quantize(Decimal('0.01'))
                pdf.drawString(margen[0]+510,830-428-margen[1],simb)
                pdf.drawString(margen[0]+530,830-428-margen[1],str(impuesto))
                total = impuesto + valor
                pdf.drawString(margen[0]+510,830-448-margen[1],simb)
                pdf.drawString(margen[0]+530,830-448-margen[1],str(total))
                num = int(total)
                letras = num_a_letras(num)
                decim = int((total - num)*100)
                texto = letras+'CON %s/100 %s'%(str(decim).zfill(2),denom)
                pdf.drawString(margen[0]+95,830-390-margen[1],texto)
                pdf.showPage()
		pdf.save()
		
	def imprimir(self):
		os.system("gtklp -P Panasonic-KX-P1123 -C %s"%self.path)
		sql = "UPDATE facturas SET IMPRESO=1 WHERE ID=%d"%self.id
		print sql
		self.cursor.execute(sql)
		
	def ver(self):
		os.system("evince %s"%self.path)

	def convertir(self):
		os.system("cp %s /home/econain/www/econadmin/images/factura.pdf"%self.path)
		os.system("cd /home/econain/www/econadmin/images/")
		os.system("convert -scale 1200x900 factura.pdf factura.jpg")
		

class Guias:
	def __init__(self,cursor,id):
		self.id = id
		sql = "SELECT CANT,TXT FROM guiasitems WHERE GUIA = %d"%id
		cursor.execute(sql)
		items = cursor.fetchall()
		sql = "SELECT FECHA,CONCAT(SERIE,'-',NUMERO),EMPRESA,LLEGADA,MOTIVO,COTIZ,OC,TRANSP,VEHICULO,OBSERV FROM guias WHERE ID=%d"%id
		cursor.execute(sql)
		fecha,corr,empresa,llegada,motivo,cotiz,compra,transp,vehiculo,observ = cursor.fetchone()
		sql = "SELECT NOMBRE,DIRECCION,RUC FROM clientes WHERE ID=%d"%empresa
		cursor.execute(sql)
		razon,direcc,ruc = cursor.fetchone()
		sql = "SELECT NOMBRE,DNI,LICENCIA FROM transportistas WHERE ID=%d"%transp
		cursor.execute(sql)
		nombre,dni,licencia = cursor.fetchone()
                placa = ''
                if vehiculo != 0:
                  sql = "SELECT NOMBRE FROM vehiculos WHERE ID=%d"%vehiculo
                  cursor.execute(sql)
                  placa= cursor.fetchone()[0]
                if llegada==0:
                    lugar = direcc
                else:
                    sql = "SELECT NOMBRE FROM direcciones WHERE ID=%d"%llegada
                    cursor.execute(sql)
                    lugar = cursor.fetchone()[0]
		self.path = "../outs/guia.pdf"
		pdf = canvas.Canvas(self.path)
		pdf.setFont("Consolas",8)
		margen = (20,22)
		#posicion = 2.25x(distancia en mm)
		pdf.drawString(420+margen[0],830-108-margen[1],corr)
		pdf.drawString(90+margen[0],830-157-margen[1],razon)
		pdf.drawString(90+margen[0],830-167-margen[1],direcc)
		pdf.drawString(90+margen[0],830-177-margen[1],str(ruc))
		pdf.drawString(160+margen[0],830-177-margen[1],compra)
		pdf.drawString(275+margen[0],830-177-margen[1],str(fecha))
		pdf.drawString(97+margen[0],830-187-margen[1],'Ca Tritón Mz 183 Lt 12 - Urb SMP - Los Olivos')
		pdf.drawString(97+margen[0],830-197-margen[1],lugar)

		pdf.drawString(385+margen[0],830-157-margen[1],nombre)
		pdf.drawString(385+margen[0],830-167-margen[1],placa)
		pdf.drawString(385+margen[0],830-177-margen[1],licencia)
		pdf.drawString(385+margen[0],830-187-margen[1],observ)
		if motivo=='Venta':
			pdf.drawString(157+margen[0],830-405-margen[1],'X')
		elif motivo=='Venta sujeta a confirmar':
			pdf.drawString(257+margen[0],830-405-margen[1],'X')
		elif motivo=='Reparación':
			pdf.drawString(320+margen[0],830-405-margen[1],'X')
		elif motivo=='Devolución':
			pdf.drawString(383+margen[0],830-405-margen[1],'X')
		else:
			pdf.drawString(419+margen[0],830-405-margen[1],motivo)
			pdf.drawString(518+margen[0],830-405-margen[1],'X')
		sql = "SELECT CANT,TXT FROM guiasitems WHERE GUIA=%d"%id
		cursor.execute(sql)
		rows = cursor.fetchall()
		x,y,p = (62,230,10) #posicion
		for i,row in enumerate(rows):
			pdf.drawString(x+margen[0],830-y-margen[1],str(i+1).zfill(2))
			pdf.drawString(x+margen[0]+23,830-y-margen[1],str(row[0]).zfill(2))
                        renglones = row[1].split('\n')
                        for linea in renglones:
                          if len(linea) > 87:
                           pass
                          else:
                           pdf.drawString(x+margen[0]+56,830-y-margen[1],linea)
                           y +=p
			  print linea
			y += p

		pdf.showPage()
		pdf.save()
	
	def imprimir(self):
                os.system("gtklp -P Panasonic-KX-P1123 -C %s"%self.path)
		sql = "UPDATE guias SET IMPRESO=1 WHERE ID=%"%self.id
		print sql
		self.cursor.execute(sql)

	def convertir(self):
		comm = "cp %s /home/econain/www/econadmin/images/guia.pdf"%self.path
		command = os.popen(comm)
		read = command.read()
		print comm
		comm ="cd /home/econain/www/econadmin/images/"
		command = os.popen(comm)
		read = command.read()
		print comm
		comm = "convert -scale 1600x1200 guia.pdf guia.jpg"
		command = os.popen(comm)
		read = command.read()
		print comm
		
	def ver(self):
	  os.system("gnome-open %s"%self.path)

class Cheques:
	def __init__(self,cursor,id):
		self.id = id
		sql = "SELECT CUENTA,GIRO,DESDE,NOMBRE,MONTO FROM cheques WHERE ID=%d"%id
                print sql
                cursor.execute(sql)
                cuenta,giro,desde,nombre,monto = cursor.fetchone()
                self.path = "../outs/cheque.pdf"
		pdf = canvas.Canvas(self.path)
		margen = (3,-20)
                num = int(monto)
                letras = num_a_letras(num)
                decim = int((monto - num)*100)
                texto = letras+'CON %s/100'%(str(decim).zfill(2))
                nombre = str(nombre).translate(trans).upper()
		#posicion = 2.25x(distancia en mm)
                if cuenta < 3:#BBVA
                  pdf.setFont("Ubuntu",12)
                  y,m,d = str(giro).split('-')
                  pdf.drawString(200+margen[0],830-80-margen[1],d)
                  pdf.drawString(220+margen[0],830-80-margen[1],m)
                  pdf.drawString(240+margen[0],830-80-margen[1],y[2:])
                  y,m,d = str(desde).split('-')
                  pdf.drawString(275+margen[0],830-80-margen[1],d)
                  pdf.drawString(295+margen[0],830-80-margen[1],m)
                  pdf.drawString(315+margen[0],830-80-margen[1],y[2:])
                  pdf.setFont("UbuntuB",12)
                  pdf.drawString(370+margen[0],830-80-margen[1],str(monto))
                  pdf.drawString(80+margen[0],830-120-margen[1],nombre)
                  pdf.setFont("Ubuntu",12)
                  pdf.drawString(80+margen[0],830-140-margen[1],texto)
                else:#Interbank
                  pdf.setFont("Ubuntu",10)
                  y,m,d = str(giro).split('-')
                  pdf.drawString(198+margen[0],830-65-margen[1],d)
                  pdf.drawString(214+margen[0],830-65-margen[1],m)
                  pdf.drawString(230+margen[0],830-65-margen[1],y[2:])
                  y,m,d = str(desde).split('-')
                  pdf.drawString(250+margen[0],830-65-margen[1],d)
                  pdf.drawString(266+margen[0],830-65-margen[1],m)
                  pdf.drawString(282+margen[0],830-65-margen[1],y[2:])
                  pdf.setFont("UbuntuB",12)
                  pdf.drawString(340+margen[0],830-80-margen[1],str(monto))
                  pdf.drawString(80+margen[0],830-120-margen[1],nombre)
                  pdf.setFont("Ubuntu",12)
                  pdf.drawString(80+margen[0],830-140-margen[1],texto)
                pdf.showPage()
		pdf.save()
		os.system("gtklp -P Panasonic-KX-P1123 -C %s"%self.path)
                sql = "UPDATE cheques SET IMPRESO=1 WHERE ID=%d"%id
                cursor.execute(sql)


if __name__ == "__mai__":
    from reportlab.lib.pagesizes import A4
    #story = []
    #story.append(PageBreak())
    #s =" 2"
    #doc = Membrete('../out.pdf')
    #story.append(Paragraph(s,doc.estilos['titulo']))
    #normal = NormalCanvas
    #numerado = NumberedCanvas
    #doc.build(story,canvasmaker= normal)
    print A4
    path = "../outs/guia.pdf"
    pdf = canvas.Canvas(path)
    pdf.setFont("Consolas",6)
    margen = (0,0)
    x,y = (0,0)
    p = 20
    for i in range(50):
        for j in range(50):
            pdf.drawString(x+margen[0],841-y-margen[1],'.%d,%d'%(x,y))
            y += p
        y = 0
        x+=p
    pdf.showPage()
    pdf.save()
    os.system("evince %s"%path)

if __name__ == '__main__':
  import Consultas
  consulta = Consultas.Conectar()
  guia = Guias(consulta.cursor,57)
  guia.convertir()
  guia.ver()
