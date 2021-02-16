#########################################################################
#Mooring simulator, 2014                                                #
#Edited by Arnaud Le Fur, IFREMER                                       #
#########################################################################

from PyQt5 import QtGui, QtWidgets
from os import startfile,rename,remove
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import mm as cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

import time



class Report_wind(QtWidgets.QWidget):
    """Cette classe permet de generer automatiquement le rapport pdf """

        
    def __init__(self):
        """initialisation de la fenetre et des boutons """
        super(Report_wind, self).__init__()
        
        self.grid_unit = QtWidgets.QGridLayout()
        self.grid_unit.setSpacing(6)
       
        self.setLayout(self.grid_unit)
       
        btn2 = QtWidgets.QPushButton('Generate report', self)
        self.label_1=QtWidgets.QLabel("Title")
        self.label_2=QtWidgets.QLabel("Author")                      
        self.Qline_1=QtWidgets.QLineEdit("Default")
        self.Qline_2=QtWidgets.QLineEdit("Arnaud Le Fur")    
        
        self.grid_unit.addWidget(self.label_1,0,0)
        self.grid_unit.addWidget(self.label_2,1,0)
        self.grid_unit.addWidget(self.Qline_1,0,1)
        self.grid_unit.addWidget(self.Qline_2,1,1)
        self.grid_unit.addWidget(btn2,2,0)
        btn2.clicked.connect(self.generate_report)                         
        self.resize(400,201)         
    def generate_report(self):
        """Fonction appele lorsque lutilisateur clique sur le bouton generate report """
        self.Title=str(self.Qline_1.text())
        self.go()
        btn = QtWidgets.QPushButton('Read report', self)   
        btn.clicked.connect(self.read_report)   
        self.grid_unit.addWidget(btn,3,0)                                    #On ajoute un bouton permettant de lire le rapport venant detre genere
        QtWidgets.QMessageBox.information(self,'Message',"Report generated")

    def read_report(self):
        """Demarre le fichier pdf avec le programme defini par defaut sur windows"""
        startfile(self.mypath+'\Report'+'\\'+str(self.Qline_1.text())+'.pdf')
        
    def coord(self, x, y, unit=1):
        """Fonction recupere dun exemple"""
        x, y = x * unit, y * unit
        return x, y    

    def go(self):
        """Cette fonction permet de structurer et de remplir le rapport """
        #PAGE 1#
        self.c = canvas.Canvas(self.Title+'.pdf')
        self.page_width=defaultPageSize[0]
        self.page_height=defaultPageSize[1]
        #Bandeau de bas de page#
        self.c.drawString(x=20, y=25, text="Mooring Simulator")
        self.c.drawRightString(x=self.page_width-20, y=25, text=str(self.Qline_2.text())+"        "+time.strftime('%d/%m/%y %H:%M',time.localtime())+"        "+str(self.c.getPageNumber()))
        self.c.setFont('Times-Bold',14)
        self.c.drawCentredString(x=((self.page_width)/2), y=45,text=str(self.Qline_1.text()))
        self.c.setFont('Times-Roman',12)
        
        h1=0
        off=0
        bool_width=0
       
        if self.mooring_image_width[0]<=765:           #Classiquement sur la largeur dune page on peut faire tenir 2 largeur dimage
            bool_width=1                                                    #si limage es trop large on en met une seule par page dou le booleen bool_width
            
        for i in range(len(self.mooring_image_height)):                     #On parcourt lensemble des images
            if h1+0.4*self.mooring_image_height[i]>=self.page_height-100:   #si il ne nous reste plus suffisamment de place pour placer limage suivante
                if off==0 and bool_width==1:
                    h1=0                                                    #on met la suite en haut de la feuille a droite
                    off=self.page_width/2
                else:                                                       #La feuille est pleine
                    off=0
                    h1=0
                    self.c.showPage()                                       #On passe a la feuille suivante
                    #Bandeau de bas de page#
                    self.c.drawString(x=20, y=25, text="Mooring Simulator")
                    self.c.drawRightString(x=self.page_width-20, y=25, text=str(self.Qline_2.text())+"        "+time.strftime('%d/%m/%y %H:%M',time.localtime())+"        "+str(self.c.getPageNumber()))
                    self.c.setFont('Times-Bold',14)
                    self.c.drawCentredString(x=((self.page_width)/2), y=45,text=str(self.Qline_1.text()))
                    self.c.setFont('Times-Roman',12)
                    #
            w,h=self.c.drawImage(self.mypath+'\Report\Pictures\img'+str(i)+'.png', -0.27*self.mooring_image_width[i]+off ,
                                 self.page_height-self.mooring_image_height[i]*0.4-h1-20, width=None, height=self.mooring_image_height[i]*0.4, mask=None, preserveAspectRatio=True, anchor='c')
            h1=h1+0.4*h

        
        self.c.showPage()                                                  #Changement de page

        #Affichage des quatres graphiques#
        w,h=self.c.drawImage(self.mypath+'\Report\Pictures\Fig1.png', -200 , self.page_height/2+20, width=None, height=(self.page_height-90)/2, mask=None, preserveAspectRatio=True, anchor='c')
        w,h=self.c.drawImage(self.mypath+'\Report\Pictures\Fig2.png', -200+self.page_width/2-50 , self.page_height/2+20, width=None, height=(self.page_height-90)/2, mask=None, preserveAspectRatio=True, anchor='c')
        w,h=self.c.drawImage(self.mypath+'\Report\Pictures\Fig3.png', -200 , 60, width=None, height=(self.page_height-90)/2, mask=None, preserveAspectRatio=True, anchor='c')
        w,h=self.c.drawImage(self.mypath+'\Report\Pictures\Fig4.png', -200+self.page_width/2-40 , 60, width=None, height=(self.page_height-90)/2, mask=None, preserveAspectRatio=True, anchor='c')
        #Bandeau de bas de page#
        self.c.drawString(x=20, y=25, text="Mooring Simulator")
        self.c.drawRightString(x=self.page_width-20, y=25, text=str(self.Qline_2.text())+"        "+time.strftime('%d/%m/%y %H:%M',time.localtime())+"        "+str(self.c.getPageNumber()))
        self.c.setFont('Times-Bold',14)
        self.c.drawCentredString(x=((self.page_width)/2), y=45,text=str(self.Qline_1.text()))
        self.c.setFont('Times-Roman',12)
        self.c.showPage()                                                #Changement de page


        #Affichage du tableau recapitulatif#


        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]
        styleN.alignment = TA_LEFT
        styleBH = styles["Normal"]
        styleBH.alignment = TA_CENTER
        taille_lim=34                                                   #Nombre de ligne limite que peut contenir la page                                                  
        count=0
        #Headers
        inter=[]
        final=[]
        mytable=[]
        mysize=[]
        colWidths=[4.6* cm, 1.3*cm, 3.5*cm, 1.3*cm, 1.2*cm, 0.8*cm, 0.8*cm, 1.2*cm, 1.4*cm, 1.3*cm, 2.5*cm]  #Largeur des colonnes du tableau
        for i in range(len(self.Tab_report[0])):
            description = Paragraph('<b>'+str(self.Tab_report[0][i])+'</b>', styleBH)                        #Titre des categories en gras 
            inter.append(description)
        final.append(inter)
        
        for i in range(1,len(self.Tab_report)):
            inter=[]
            count=count+1                                                                                    #On incremente count a chaque ligne
            if len(str(self.Tab_report[i][0]))>24 or len(str(self.Tab_report[i][2]))>16:                     #Si le nom ou les profondeur tiennent sur 2 lignes on reincremente count
                count=count+1
            if count%taille_lim==0:                                                                          #On atteint la taille limite
                mytable.append(final)
                mysize.append(count)
                count=0
                final=[]
            for j in range(len(self.Tab_report[i])):
                description = Paragraph(str(self.Tab_report[i][j]), styleBH)                                 #On remplit les cases du tableau
                inter.append(description)
            final.append(inter)
        mytable.append(final)
        mysize.append(count)
        #Bandeau en haut de page (uniquement pour la premiere)#
        self.c.drawString(x=20, y=self.page_height-60, text="Safe Anchor's WET weight (kg) : ")
        self.c.drawString(x=300, y=self.page_height-60, text=str(self.anchor_value[0]))
        self.c.drawString(x=20, y=self.page_height-80, text="Selected Anchor's WET weight(kg) : ")
        self.c.drawString(x=300, y=self.page_height-80, text=str(self.anchor_value[1]))
        self.c.drawString(x=20, y=self.page_height-100, text="Max Launch Tension / Breaking Strength (%) : ")
        self.c.drawString(x=300, y=self.page_height-100, text=str(self.anchor_value[2]))
        #Instanciation du tableau#
        table = Table(mytable[0], colWidths)
        Taille_tab=cm*(1.4+0.6*mysize[0])

        table.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           ]))

        table.wrapOn(self.c, self.page_width, self.page_height)
        table.drawOn(self.c, *self.coord(20, (self.page_height-Taille_tab-150)))
        #Bandeau de bas de page#
        self.c.drawString(x=20, y=25, text="Mooring Simulator")
        self.c.drawRightString(x=self.page_width-20, y=25, text=str(self.Qline_2.text())+"        "+time.strftime('%d/%m/%y %H:%M',time.localtime())+"        "+str(self.c.getPageNumber()))
        self.c.setFont('Times-Bold',14)
        self.c.drawCentredString(x=((self.page_width)/2), y=45,text=str(self.Qline_1.text()))
        self.c.setFont('Times-Roman',12)
        self.c.showPage()                                                           #Page suivante
        for i in range(1,len(mytable)):                                             #Si on avait atteint la taille limite on recreer un tableau sur la page suivante
        #Instanciation des tableau#
            table = Table(mytable[i], colWidths)
            Taille_tab=cm*(1.4+0.6*(mysize[i]))
            table.setStyle(TableStyle([
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ]))

            table.wrapOn(self.c, self.page_width, self.page_height)
            table.drawOn(self.c, *self.coord(20, (self.page_height-20-Taille_tab)))
        #Bandeau de bas de page#
            self.c.drawString(x=20, y=25, text="Mooring Simulator")
            self.c.drawRightString(x=self.page_width-20, y=25, text=str(self.Qline_2.text())+"        "+time.strftime('%d/%m/%y %H:%M',time.localtime())+"        "+str(self.c.getPageNumber()))
            self.c.setFont('Times-Bold',14)
            self.c.drawCentredString(x=((self.page_width)/2), y=45,text=str(self.Qline_1.text()))
            self.c.setFont('Times-Roman',12)
            self.c.showPage()                                                       #Page suivante

        #PAGE Inventaire#
        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]
        styleN.alignment = TA_LEFT
        styleBH = styles["Normal"]
        styleBH.alignment = TA_CENTER
        #Headers
        inter=[]
        final=[]
        colWidths=[6.9* cm, 3*cm]
        for i in range(len(self.inventory[0])):                                        #Nom des categories en gras
            description = Paragraph('<b>'+str(self.inventory[0][i])+'</b>', styleBH)
            inter.append(description)
        final.append(inter)
        
        for i in range(1,len(self.inventory)):
            inter=[]
            for j in range(len(self.inventory[i])):
                description = Paragraph(str(self.inventory[i][j]), styleBH)            #Remplissage des cases
                inter.append(description)
            final.append(inter)
        
        #Instanciation du tableau#
        table = Table(final, colWidths)
        Taille_tab=cm*(0.7*(len(self.inventory)))
        table.setStyle(TableStyle([
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ]))

        table.wrapOn(self.c, self.page_width, self.page_height)
        table.drawOn(self.c, *self.coord((self.page_width-sum(colWidths))/2, (self.page_height-20-Taille_tab)))
        #Bandeau de bas de page#
        self.c.drawString(x=20, y=25, text="Mooring Simulator")
        self.c.drawRightString(x=self.page_width-20, y=25, text=str(self.Qline_2.text())+"        "+time.strftime('%d/%m/%y %H:%M',time.localtime())+"        "+str(self.c.getPageNumber()))
        self.c.setFont('Times-Bold',14)
        self.c.drawCentredString(x=((self.page_width)/2), y=45,text=str(self.Qline_1.text()))
        self.c.setFont('Times-Roman',12)
        self.c.showPage()

        self.c.save()                                                                  #Sauvegarde du fichier pdf
        newpath=self.mypath+'\Report'+'\\'
        rm=0
        try:                                                                           #On deplace le rapport en changeant son chemin dans le dossier Report
            rename(self.mypath+'\\'+self.Title+'.pdf',newpath+self.Title+'.pdf')
        except WindowsError:                                                            #En cas d erreur si un fichier possedant ce chemin existe deja on le supprime puis on le remplace
            remove(newpath+self.Title+'.pdf')
            rm=1
        if rm==1:
            rename(self.mypath+'\\'+self.Title+'.pdf',newpath+self.Title+'.pdf')
            

   
    
