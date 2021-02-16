#############################################################################
##Mooring Simulator                                                      ####                    
##Edited by Arnaud Le Fur, IFREMER, 2014                                 ####
##library_window.py                                                      ####
#############################################################################

#!/usr/bin/python
#-*- coding: utf-8 -*-

import xlrd
from PyQt5 import QtGui, QtWidgets
import functools
from os import getcwd,startfile

class Library_wind(QtWidgets.QWidget):
    '''Classe creant la fenetre de bibliotheque a partir du chemin en input '''
    
    def __init__(self,name):
        '''Initialisation de la fenetre contenant la bibliotheque
        Input : name : chemin du fichier Library.xls'''
        
        super(Library_wind, self).__init__()
        self.Initialize_Library(name)
        self.myLayout_library=QtGui.QVBoxLayout()
        mypath=getcwd()     #Recuperation du repertoire courant
        #Bouton refresh
        refresh_library=QtGui.QAction(QtGui.QIcon(mypath+'\Library\Pictures\Icons\Refresh.png'), 'Refresh_library', self)
        refresh_library.triggered.connect(functools.partial(self.refresh_library,name))
        #Bouton launch
        launch_library=QtGui.QAction(QtGui.QIcon(mypath+'\Library\Pictures\Icons\Spreadsheet.png'), 'Launch_library', self)
        launch_library.triggered.connect(functools.partial(self.launch_library,name))
        #Toolbar
        self.toolbar = QtGui.QToolBar()
        self.toolbar.addAction(refresh_library)
        self.toolbar.addAction(launch_library)
        #Ajout dans le layout
        self.myLayout_library.addWidget(self.toolbar)
        self.myarea=self.create_label()
        self.myLayout_library.addWidget(self.myarea)
        self.setLayout(self.myLayout_library)
        self.resize(400,201)

    def Initialize_Library(self,name):
        '''Creation dynamique des classes et des objets a partir du fichier excel
        Input : name : chemin du fichier Library.xls'''
        methodes = {
            "__init__": self.creer_objet
            }
        #Ouverture du fichier
        wb = xlrd.open_workbook(name)
        #On recupere le nom des classes correspondant aux feuilles
        self.tab_name_class=wb.sheet_names()
        self.tab_class=[]
        self.tab_object=[]
        self.tab_attr=[]
        #On cree chaque type de classe
        for i in range(len(self.tab_name_class)):
            class1=type(str(self.tab_name_class[i]),(),methodes)
            class1.__name__= str(self.tab_name_class[i])
            self.tab_class.append(class1)
        #Creation des objets
        for i in range(len(self.tab_name_class)):
            self.tab_inter=[]
            a=wb.sheet_by_name(self.tab_name_class[i])
            for j in range(0,a.ncols):
                for k in range(1,a.nrows):
                    if str(a.col_values(j)[k])=="attribute":
                        colnum=j
                        rownum=k
            for p in range(rownum+1,a.nrows):
                self.tab_inter2=[]
                #Creation dun objet
                obj=self.tab_class[i]()
                for m in range(colnum+1,a.ncols):
                    self.tab_inter2.append(a.col_values(m)[rownum])
                    #On lui assigne le nom et la valeur de ses attribut
                    setattr(obj,a.col_values(m)[rownum],str(a.col_values(m)[p]))
                self.tab_inter.append(obj)
            self.tab_object.append(self.tab_inter)
            self.tab_attr.append(self.tab_inter2)
            
    def refresh_library(self,name):
        '''Cette fonction est appelee lorsque lutilisateur veut actualiser la bibliotheque
            cela consiste a recharger tout les objets du fichier excel et a recreer le tableau
            Input : name : chemin du fichier Library.xls'''
        self.Initialize_Library(name)
        self.myLayout_library.removeWidget(self.myarea)
        #Suppression de lancienne fenetre
        self.myarea.close()
        self.myarea=self.create_label()
        #Ajout de la nouvelle
        self.myLayout_library.addWidget(self.myarea)
        
    def launch_library(self,name):
        '''Lance directement le tableur a partir du logiciel
        Input : name : chemin du fichier Library.xls'''
        startfile(name)
    
    def create_label(self):
        '''Creation des label a partir des listes dobjet initialisees precedement
        Output : myarea : Fenetre globale contenant chaque onglet pour chaque type delement'''
        #myarea : fenetre globale
        myarea=QtGui.QMdiArea(self)
        #On parcourt chaque classe
        for i in range(len(self.tab_name_class)):
            #Creation dune sous fenetre pour chaque classe
            wind=QtGui.QWidget()
            cate=myarea.addSubWindow(wind)
            cate.setWindowTitle(self.tab_name_class[i])
            cate.setWindowIcon(QtGui.QIcon('exit24.png'))
            #Les sous fenetre de myarea sont vues sous la forme donglets
            myarea.setViewMode(1)
            groupLayout=QtGui.QVBoxLayout()
            #Creation de la barre de defilement 
            scrollArea = QtGui.QScrollArea ();
            groupLayout.addWidget(scrollArea)
            scrolledWidget = QtGui.QWidget()
            #Creation du layout grid contenant toutes les cases du tableau
            grid=QtGui.QGridLayout(scrolledWidget)
            #Creation du label pour le titre de chaque attribut
            for j in range(len(self.tab_attr[i])): 
                label=QtGui.QLabel(self.tab_attr[i][j])
                label.setStyleSheet("QLabel { background-color : white; color : black;border: 2px solid black }")
                grid.addWidget(label,0,j)
            #Creation des labels pour chaque valeur de chaque attribut#
            for k in range(len(self.tab_object[i])):
                for l in range(len(self.tab_attr[i])):
                    label=QtGui.QLabel(getattr(self.tab_object[i][k],self.tab_attr[i][l]))
                    label.setStyleSheet("QLabel { background-color : white; color : black;border: 1px solid black }")
                    grid.addWidget(label,1+k,l)
            grid.setSpacing(0)
            scrollArea.setWidget(scrolledWidget);
            wind.setLayout(groupLayout)
        return myarea
    def creer_objet(self):
        '''Fonction dinitialisation dynamique des classes '''
        Initialize=1
        
    
