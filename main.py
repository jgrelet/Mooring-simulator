#########################################################################
#Mooring Simulator, 2014                                               ##
#Edited by Arnaud Le Fur, IFREMER                                      ##
#                                                                      ##
#########################################################################



import sys
from PyQt5 import QtCore,QtGui, QtWidgets

from library_window import Library_wind
#from preference_window import Preference_wind
from report_window import Report_wind
from environnement_window import Environnement_wind
from new_mooring_window import MooringWindow
from simulate_window import Simulate_wind
import myQDockWidget
from os import getcwd
from tkinter import Tk
import copy

from reportlab.pdfbase import _fontdata_enc_winansi
from reportlab.pdfbase import _fontdata_enc_macroman
from reportlab.pdfbase import _fontdata_enc_standard
from reportlab.pdfbase import _fontdata_enc_symbol
from reportlab.pdfbase import _fontdata_enc_zapfdingbats
from reportlab.pdfbase import _fontdata_enc_pdfdoc
from reportlab.pdfbase import _fontdata_enc_macexpert
from reportlab.pdfbase import _fontdata_widths_courier
from reportlab.pdfbase import _fontdata_widths_courierbold
from reportlab.pdfbase import _fontdata_widths_courieroblique
from reportlab.pdfbase import _fontdata_widths_courierboldoblique
from reportlab.pdfbase import _fontdata_widths_helvetica
from reportlab.pdfbase import _fontdata_widths_helveticabold
from reportlab.pdfbase import _fontdata_widths_helveticaoblique
from reportlab.pdfbase import _fontdata_widths_helveticaboldoblique
from reportlab.pdfbase import _fontdata_widths_timesroman
from reportlab.pdfbase import _fontdata_widths_timesbold
from reportlab.pdfbase import _fontdata_widths_timesitalic
from reportlab.pdfbase import _fontdata_widths_timesbolditalic
from reportlab.pdfbase import _fontdata_widths_symbol
from reportlab.pdfbase import _fontdata_widths_zapfdingbats

class Mooring_Simulator(QtWidgets.QMainWindow):
    """Classe definissant la fenetre principale"""
    
    def __init__(self,parent=None):
        """Initialisation des differentes fenetre """
        super(Mooring_Simulator, self).__init__(parent)
        #Recupere resolution de lecran#
        root = Tk()
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        #Recupere le chemin du fichier#
        self.mypath=getcwd()
        self.Defaut_folder=self.mypath+'\Library\Library.xls'
        self.zoneCentrale = QtWidgets.QTabWidget()
        self.zoneCentrale.setTabsClosable(True)
        self.setCentralWidget(self.zoneCentrale)
        #Creation des fenetres preferences, environnement, bibliotheque
        self.resize(200,200)
        #self.create_preference()
        #self.preference_dockwidget.hide()
        self.create_report()
        self.create_environnement()
        self.create_library_wind(self.Defaut_folder)
        self.showMaximized()
        self.report_dockwidget.hide()
        self.environnement_dockwidget.hide()
        self.library_dockwidget.hide()
        
        
        self.zoneCentrale.tabCloseRequested.connect(self.closerequested)
        #Creation des menus et des actions associees#
        #Action#
        self.new_mooring_Action = QtGui.QAction(QtGui.QIcon('exit24.png'), 'New Mooring', self)
        self.new_mooring_Action.triggered.connect(self.new_mooring_pushButton_clicked)
        
        self.load_mooring_Action = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Load Mooring', self)
        self.load_mooring_Action.triggered.connect(self.load_mooring_pushButton_clicked)

        self.save_mooring_Action = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Save Mooring', self)
        self.save_mooring_Action.triggered.connect(self.save_mooring_pushButton_clicked)
        
        self.exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)
        
        self.open_library_Action = QtGui.QAction(QtGui.QIcon('exit24.png'),'Show Library', self)
        self.open_library_Action.triggered.connect(self.library_pushButton_clicked)
        
        self.load_library_Action = QtGui.QAction(QtGui.QIcon('exit24.png'),'Load new Library', self)
        self.load_library_Action.triggered.connect(self.load_library_pushButton_clicked)


#       self.edit_preference_Action = QtGui.QAction(QtGui.QIcon('exit24.png'),'Preferences', self)
#       self.edit_preference_Action.triggered.connect(self.edit_preference_clicked)
#

        self.edit_environnement_Action = QtGui.QAction(QtGui.QIcon('exit24.png'),'Set Environnemental Conditions', self)
        self.edit_environnement_Action.triggered.connect(self.edit_environnement_pushButton_clicked)

        self.start_simulation_Action = QtGui.QAction(QtGui.QIcon(self.mypath+'\Library\Pictures\Icons\play.png'),'Start simulation', self)
        self.start_simulation_Action.triggered.connect(self.start_simulation_pushButton_clicked)

        self.generate_report_Action = QtGui.QAction(QtGui.QIcon('exit24.png'),'Generate report', self)
        self.generate_report_Action.triggered.connect(self.generate_report_pushButton_clicked)
        
        self.statusBar()
        #Menu#
        self.menubar = self.menuBar()
        
        self.fileMenu = self.menubar.addMenu('&File')
        self.libraryMenu = self.menubar.addMenu('&Library')
        self.configurationMenu = self.menubar.addMenu('&Configuration')
        self.simulateMenu = self.menubar.addMenu('&Simulate')
        
        #Ajout des actions au Menu#
        self.fileMenu.addAction(self.new_mooring_Action)
        self.fileMenu.addAction(self.load_mooring_Action)
        self.fileMenu.addAction(self.save_mooring_Action)
        self.fileMenu.addAction(self.exitAction)
        
        self.libraryMenu.addAction(self.open_library_Action)
        self.libraryMenu.addAction(self.load_library_Action)

        #self.configurationMenu.addAction(self.edit_preference_Action)
        self.configurationMenu.addAction(self.edit_environnement_Action)

        self.simulateMenu.addAction(self.start_simulation_Action)
        self.simulateMenu.addAction(self.generate_report_Action)
        
        self.setWindowTitle('Mooring Simulator')    
        self.show()
    
    def create_library_wind(self,path):
        """Charge le fichier Library.xls a partir de path et cree la fenetre 
        Input : path : chemin du fichier.xls"""
        self.library_wind=Library_wind(path)
        self.library_wind.setMinimumWidth(self.screen_width/2)
        self.library_wind.setMinimumHeight(200)
        self.library_dockwidget=myQDockWidget.myQDockWidget()
        self.library_dockwidget.setWidget(self.library_wind)
        #Ajoute la bibliotheque dans le DockWidget en position haute#
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.library_dockwidget)
        self.library_dockwidget.setWindowTitle('Library')
        
    def create_mooring_wind(self,file_name):
        """Creer la fenetre d edition du mouillage dans un nouvel onglet avec le nom file_name
        Input : File_name : nom du fichier"""
        
        self.mooring_wind = MooringWindow(self.Defaut_folder,self.screen_width)
        self.zoneCentrale.addTab(self.mooring_wind,file_name)
        self.zoneCentrale.setCurrentWidget(self.mooring_wind)
        #Update la bibliothèque
        self.create_library_wind(self.Defaut_folder)
        self.library_dockwidget.hide()
    
    
    def load_mooring_pushButton_clicked(self):
        """Permet de charger un mouillage prealablement sauvegarde """
        
        fileName=QtGui.QFileDialog.getOpenFileName(self, ("Open File"),"/home",("Mooring (*.py)")) #l utilisateur va chercher a l aide de l explorer le fichier de sauvegarde
        fichier = open(fileName, "r")
        
        filename=self.get_file_name(fileName)
        
        i=0
        list_item=[]
        list_length=[]
        clamp_ratio=[]
        current_point=[]
        data=fichier.readlines()
        #Recupere dabord la liste et la longueur des elements + clampage
        while data[i]!="depth_instru\n":
            leng=""
            j=0
            clamp=0
            #Detection des clampage#
            for p in range(len(data[i])-4):
                           if data[i][p]=="c":
                               if data[i][p+1]=="l":
                                   if data[i][p+2]=="a":
                                       if data[i][p+3] =="m":
                                         if  data[i][p+4] == "p":
                                               clamp=1
                                               ind=p+6
            #pas de clampage#
            if clamp==0:
                clamp_ratio.append(2)
                while data[i][j]!=" ":
                    
                    leng=leng+data[i][j]
                    j=j+1
                item=""
                for k in range(eval(leng)):
                    item=item+data[i][j+1+k]
                list_item.append(item)                  #On recupere le nom des items
            
                length_item=""
                l=j+2+eval(leng)
                while l<len(data[i]):
                    length_item=length_item+data[i][l]
                    l=l+1
                list_length.append(eval(length_item))   #On recupere la longueur des item
            #clampage#
            if clamp==1:
                while data[i][j]!=" ":
                    
                    leng=leng+data[i][j]
                    j=j+1
                item=""
                length_item=""
                for k in range(eval(leng)):
                    item=item+data[i][j+1+k]
                inter=[item]                            #On recupere le nom du support
                for n in range(j+2+eval(leng),ind-7):
                    length_item=length_item+data[i][n]
                list_length.append(eval(length_item))   #On recupere la longueur du support
                leng=""
                while data[i][ind]!=" ":
                    
                    leng=leng+data[i][ind]
                    ind=ind+1
                item=""
                for k in range(ind+1,ind+1+eval(leng)):
                    item=item+data[i][k]
                inter.append(item)                      #On recupere le nom de l element clampe
                list_item.append(inter)
                z=0
                clamp_rat=''
                while(data[i][ind+1+eval(leng)+z])!=';':
                    clamp_rat=clamp_rat+data[i][ind+1+eval(leng)+z]
                    z=z+1
                clamp_ratio.append(float(clamp_rat))    #On recupere le ratio de clampage
            i=i+1
        i=i+1
        list_depth_instru=[]
       
        while data[i]!="fin\n":
            inter=[]
            depth=""
            clamp=0
            for u in range(len(data[i])-1):
                    depth=depth+data[i][u]
                    if data[i][u]=='_':
                           clamp=1
            if clamp!=1:
                    list_depth_instru.append(eval(depth))  #Recupere la profondeur des elements non clampe
                           
            else:
                
                j=0
                depth=""
                while data[i][j]!='_':
                    depth=depth+data[i][j]
                    j=j+1
                inter.append(eval(depth))
                depth=""
                for k in range(j+1,len(data[i])-1):
                    depth=depth+data[i][k]
                inter.append(eval(depth))
                list_depth_instru.append(inter)     #Recupere la profondeur des elements clampes
            i=i+1
        
        i=i+2
        if data[i]!='0':                            #Recupere les valeurs de courants et leur profondeur
            for j in range(1+i,1+i+int(data[i])):
                point=data[j].split(':')[0]
                current_point.append(point)
        #On cree une fenetre avec la liste,longueurs des elements et profondeur des instruments detectes#
        self.create_mooring_wind(filename)
        self.mooring_wind.get_library(self.Defaut_folder)
        self.mooring_wind.mooringWidget.liste_element=[]
        #On modifie liste_element avec les noms detectes dans list_item
        for i in range(len(list_item)):
            if type(list_item[i])==str:
                for j in range(len(self.mooring_wind.tab_object)):
                    for k in range(len(self.mooring_wind.tab_object[j])):
                        if self.mooring_wind.tab_object[j][k].name==list_item[i]:
                            self.mooring_wind.mooringWidget.liste_element.append([j,k])     
            else:
                temp=[]
                for l in range(len(list_item[i])):
                    for j in range(len(self.mooring_wind.tab_object)):
                        for k in range(len(self.mooring_wind.tab_object[j])):
                            if self.mooring_wind.tab_object[j][k].name==list_item[i][l]:
                                temp.append([j,k])
                self.mooring_wind.mooringWidget.liste_element.append(temp)
        #On affecte toutes listes#
        self.mooring_wind.mooringWidget.ropes_length=list_length
        self.mooring_wind.mooringWidget.instru_depth=list_depth_instru
        self.mooring_wind.mooringWidget.clamp_ratio=clamp_ratio
        self.mooring_wind.show()
        self.mooring_wind.mooringWidget.zoom_mooring(0)
        #On supprime les points de courant existant#
        for i in range(len(self.environnement_wind.liste_point)):
            self.environnement_wind.remove_current_point(self.environnement_wind.liste_point[0])
        #On recupere dans t la profondeur du fond, la maniere de definir les profondeur, le poids du lest#
        t=[]
        for i in range(3):
            val=''
            for a in data[-i-1]:
                if a !=';':
                    val=val+a
                else:
                    t.append(val)
                    break
        #On affecte les 3 valeurs de t#
        self.mooring_wind.mooringWidget.anchor_weight_value=t[2]
        self.environnement_wind.choice_depht_height.setText(t[0])
        self.environnement_wind.combo_1.setCurrentIndex(int(t[1]))
        self.environnement_wind.combo_onActivated()       #On appelle la fonction du combobox
        if (data[-1])!="None":
            self.environnement_wind.save_surf_bott_btn(1) #On sauvegarde les parametre
        if len(current_point)!=0:
            #On met a jour les valeurs et profondeur de courant du fond et de la surface#
            self.environnement_wind.label_current7.setText(current_point[0].split(';')[0]) 
            self.environnement_wind.line1.setText(current_point[0].split(';')[1])
            self.environnement_wind.label_current5.setText(current_point[-1].split(';')[0])
            self.environnement_wind.line2.setText(current_point[-1].split(';')[1])
            #On met a jour les valeurs et profondeur de courant des points intermediaires
            for i in reversed(range(1,len(current_point)-1)):
                self.environnement_wind.create_new_current_point()
                self.environnement_wind.mylayout.itemAtPosition(3,1).widget().setText(current_point[i].split(';')[0])
                self.environnement_wind.mylayout.itemAtPosition(3,2).widget().setText(current_point[i].split(';')[1])
            #self.environnement_wind.update()
        self.mooring_wind.mooringWidget.update_grid(0)#On met a jour le layout de la ligne de mouillage
        
    def save_mooring_pushButton_clicked(self):
        """Fonction appele lorsque lutilisateur clique sur save mooring """
        fileName=QtGui.QFileDialog.getSaveFileName (self, ("Save File"),"/home",("Mooring (*.py)"))  #On recupere dans Filename le chemin du fichier de sauvegarde
        self.create_save(fileName)                                                                   #Creation du fichier de sauvegarde
        filename=self.get_file_name(fileName)
        self.zoneCentrale.setTabText(self.zoneCentrale.currentIndex(),filename)                      #Le titre de l onglet venant d etre sauvegarde prend le nom entre par l utilisateur
        
        
    def create_save(self, fileName):
        """Cette fonction permet de remplir avec le bon formalisme le fichier de sauvegarde """
        fichier = open(fileName, "w")
        #Sauvegarde le nom et la longueur des elements#
        for i in range(len(self.mooring_wind.mooringWidget.liste_element)):
            if type(self.mooring_wind.mooringWidget.liste_element[i][0])!=list:
                #Element non clampe#
                fichier.write(str(len(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0]][self.mooring_wind.mooringWidget.liste_element[i][1]].name))
                              +" "+self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0]][self.mooring_wind.mooringWidget.liste_element[i][1]].name
                              +" "+str(self.mooring_wind.mooringWidget.ropes_length[i])+"\n")

            else:
                #Element clampe#
                #On ajoute le nom de l element et le clamp_ratio
                fichier.write(str(len(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0][0]][self.mooring_wind.mooringWidget.liste_element[i][0][1]].name))+" "+
                              self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0][0]][self.mooring_wind.mooringWidget.liste_element[i][0][1]].name+" "+
                              str(self.mooring_wind.mooringWidget.ropes_length[i])+ " "+"clamp" + " " +
                              str(len(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][1][0]][self.mooring_wind.mooringWidget.liste_element[i][1][1]].name))+" "
                              +self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][1][0]][self.mooring_wind.mooringWidget.liste_element[i][1][1]].name+
                              str(self.mooring_wind.mooringWidget.clamp_ratio[i])+";"+"\n")
             
        fichier.write("depth_instru\n")
        #Sauvegarde la profondeur des instruments#
        for i in range(len(self.mooring_wind.mooringWidget.liste_element)):
             if type(self.mooring_wind.mooringWidget.instru_depth[i])!=list:
                 fichier.write(str(self.mooring_wind.mooringWidget.instru_depth[i])+"\n")
             else:
                  fichier.write(str(self.mooring_wind.mooringWidget.instru_depth[i][0])+"_"+str(self.mooring_wind.mooringWidget.instru_depth[i][1])+"\n")        
        fichier.write("fin\n")
        fichier.write("\n")
        y,x=self.environnement_wind.get_all_current_value()                                 #Recupere les valeurs et profondeur de courant
        fichier.write(str(len(x))+'\n')
        for i in range(len(x)):
            fichier.write(str(x[i])+';'+str(y[i])+':'+'\n')                               #Ecriture profondeur;valeur:
        fichier.write(str(self.mooring_wind.mooringWidget.anchor_weight_value)+';'+'\n')  #Poids du lest
        fichier.write(str(self.environnement_wind.combo_1.currentIndex())+';'+'\n')       #Index du combo definissant la maniere de definir les profondeurs
        fichier.write(self.environnement_wind.choice_depht_height.text()+';')             #Profondeur du fond/surface
        
    def new_mooring_pushButton_clicked(self):
        """Cette fonction est appele lorsque l utilisateur clique sur le bouton new_mooring  """
        fileName="New_Mooring"                                                                 #Nom par defaut
        self.create_mooring_wind(fileName)                                                     #Creation du nouvel onglet
        for i in range(len(self.environnement_wind.liste_point)):
            self.environnement_wind.remove_current_point(self.environnement_wind.liste_point[0]) #On supprime les anciens points de courant
        self.environnement_wind.choice_depht_height.setText("None")                              #On reinitialise la profondeur du fond
        self.environnement_wind.param_saved=0                                                    #Parametre non sauvegardes
        self.mooring_wind.show()
        
              
    def library_pushButton_clicked(self):
        """Fonction appele lorsque l utilisateur clique sur show library """
        self.library_dockwidget.hide()
        self.library_dockwidget.show()
        
            
    def load_library_pushButton_clicked(self):
        """Fonction appele lorsque l utilisateur charge un autre fichier Library.xls"""
        self.library_dockwidget.hide()
        fileName = QtGui.QFileDialog.getOpenFileName(self, ("Open File"),"/home",("Spreadsheet  (*.xls)"));   
        self.create_library_wind(fileName)          
        self.Defaut_folder=fileName
        if hasattr(self,"mooring_wind"):                                                            #On actualise la bibliothèque du mouillage en cours
            self.mooring_wind.default_folder=self.Defaut_folder
            self.mooring_wind.refresh_library()
                
        self.library_dockwidget.show()

#        
#   def edit_preference_clicked(self):
#     #Show the preferences window#
#       self.preference_dockwidget.hide()
#       self.preference_dockwidget.show()
         
    def edit_environnement_pushButton_clicked(self):
        """Fonction appele lorsque l utilisateur clique sur set environnemental conditions """
        self.environnement_dockwidget.hide()
        self.environnement_dockwidget.show()


    def start_simulation_pushButton_clicked(self):
        """Fonction appele lorsque l utilisateur clique sur start simulation """
        if self.environnement_wind.param_saved==1:        #On verifie que les parametres environnementals ont ete sauvegarde
            self.estimate_length()                        #On estime les longueurs des cables definies comme automatique
            data=self.gathering_mooring_information()     #On recupere dans data toutes les infos necessaire a la simulation
            self.simulate_wind = Simulate_wind(data)        
            self.zoneCentrale.addTab(self.simulate_wind,"Simulation_"+self.zoneCentrale.tabText(self.zoneCentrale.currentIndex()))
            self.gathering_report_information()           #On recupere les infos necessaire pour la redaction du rapport
        else:
            QtGui.QMessageBox.information(self,'Message',"Choose environemental conditions before starting simulation")
            

    def estimate_length(self):
        """Cette fonction permet d estimer les longueurs des cables definies comme automatique grace aux profondeurs des instruments rentrees par l utilisateur"""
        inter=[]
        self.mooring_wind.mooringWidget.clamp_ratio2=[]
        for a in self.mooring_wind.mooringWidget.clamp_ratio:
            self.mooring_wind.mooringWidget.clamp_ratio2.append(a)            #On sauvegarde les valeurs d origines du clamp ratio 
        for i in range(len(self.mooring_wind.mooringWidget.instru_depth)):    #On verifie que l utilisateur a entre des valeurs coherentes pour les profondeurs des instruments
            if type(self.mooring_wind.mooringWidget.instru_depth[i])!=list:
                if self.environnement_wind.combo_1.currentIndex()==0:
                    if self.mooring_wind.mooringWidget.instru_depth[i]<0:
                        self.mooring_wind.mooringWidget.instru_depth[i]=self.mooring_wind.mooringWidget.instru_depth[i]*-1  #En cas d erreur de saisie on modifie la valeur
                if self.environnement_wind.combo_1.currentIndex()==1:
                    if self.mooring_wind.mooringWidget.instru_depth[i]>0:
                        self.mooring_wind.mooringWidget.instru_depth[i]=self.mooring_wind.mooringWidget.instru_depth[i]*-1  #En cas d erreur de saisie on modifie la valeur
                    
            else:
                #Element clampe#
                for j in range(len(self.mooring_wind.mooringWidget.instru_depth[i])):
                    if self.environnement_wind.combo_1.currentIndex()==0:
                        if self.mooring_wind.mooringWidget.instru_depth[i][j]<0:
                            self.mooring_wind.mooringWidget.instru_depth[i][j]=self.mooring_wind.mooringWidget.instru_depth[i][j]*-1
                    if self.environnement_wind.combo_1.currentIndex()==1:
                        if self.mooring_wind.mooringWidget.instru_depth[i][j]>0:
                            self.mooring_wind.mooringWidget.instru_depth[i][j]=self.mooring_wind.mooringWidget.instru_depth[i][j]*-1

        floor=self.environnement_wind.combo_1.currentIndex()*(-1*self.environnement_wind.choice_depht_height.text().toFloat()[0])   #Profondeur du fond 
        depth=[]
        depth.append(floor)
        my_depth=0
        mylength=[]
        clamp=0
        a=1
        for i in range(len(self.mooring_wind.mooringWidget.ropes_length)):      #On recupere les longueurs de chaque element
             if type(self.mooring_wind.mooringWidget.instru_depth[i])!=list:
                myobject=self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0]][self.mooring_wind.mooringWidget.liste_element[i][1]]
             else:
                myobject=self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0][0]][self.mooring_wind.mooringWidget.liste_element[i][1][0]]
             if hasattr(myobject,"length"):
                mylength.append(eval(myobject.length))
                
             else:
                 mylength.append(float(self.mooring_wind.mooringWidget.ropes_length[i]))
        if 0.0 in mylength:                                               #Cela veut dire que ce cable est defini en auto
            for i in reversed(range(len(mylength))):
                if mylength[i]!=0:
                    depth.insert(0,depth[0]-mylength[i])                  #On calcule la profondeur jusqu'a la longueur inconnue
                else:
                    inter=0
                    for j in reversed(range(i)):                            
                        inter=inter+mylength[j]                           #On calcule la longueur entre le cable defini en automatique et l instrument
                        if type(self.mooring_wind.mooringWidget.instru_depth[j])!=list:
                          #Pas de clampage
                            if self.mooring_wind.mooringWidget.instru_depth[j]!=0:
                                my_depth=self.mooring_wind.mooringWidget.instru_depth[j]    #On recupere la profondeur de l instrument
                                clamp=0
                                break
                            else:
                                    my_depth=0
                        else:
                          #Clampage
                            for k in range(len(self.mooring_wind.mooringWidget.instru_depth[j])):
                                if self.mooring_wind.mooringWidget.clamp_ratio[j] !=2 or self.mooring_wind.mooringWidget.clamp_ratio[j]!=0: #On verifie que le ratio de clampage est bien definie
                                    if self.mooring_wind.mooringWidget.instru_depth[j][k]!=0:
                                        my_depth=self.mooring_wind.mooringWidget.instru_depth[j][k] #On recupere la profondeur de l instrument
                                        longu=eval(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[j][k][0]][self.mooring_wind.mooringWidget.liste_element[j][k][1]].length)#longueur de l instrument
                                        clamp=1
                                        break
                                    else:
                                        my_depth=0
                            if my_depth!=0:
                                break
                    if clamp==1:
                        ma_longueur=depth[0]+(my_depth)+float(self.mooring_wind.mooringWidget.clamp_ratio[j])*mylength[j]-longu/2-inter #On calcule ma_longueur pour placer le haut de instrument a la profondeur a my_depth
                    else:
                        ma_longueur=depth[0]+(my_depth)-inter

                    if ma_longueur<0:
                        QtGui.QMessageBox.warning(self,'Message',"Error your mooring is incorrectly designed some length are negatives")

                        
                    mylength[i]=ma_longueur
                    self.mooring_wind.mooringWidget.ropes_length[i]=ma_longueur        #On affecte la longueur calcule
                    depth.insert(0,depth[0]-mylength[i])                               #On insere la nouvelle profondeur
            self.mooring_wind.mooringWidget.update_grid(0)
 
                
                
    def gathering_mooring_information(self):
        """Recuperation des donnees necessaires pour la simulation 
        Output : data : data[0] : Liste des objets constituants le mouillage
                        data[1] : Les profondeurs et valeurs de courants
                        data[2] : Liste des profondeur fixe des instruments
                        data[3] : Trainee induite par les elements lors de la chute du lest
                        data[4] : Largeur de l ecran
                        data[5] : Chemin du programme
                        data[6] : Liste des ratio de clampage des instruments
                        """
        self.mooring_wind.refresh_library()
        tab=[]
        data=[]
        drag_v=[]
        for i in range(len(self.mooring_wind.mooringWidget.liste_element)):
        #On copie liste_element#
            if type(self.mooring_wind.mooringWidget.liste_element[i][0])==int:
                tab.append(copy.deepcopy(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0]][self.mooring_wind.mooringWidget.liste_element[i][1]]))
            else:
                tab.append([copy.deepcopy(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][0][0]][self.mooring_wind.mooringWidget.liste_element[i][0][1]]),
                            copy.deepcopy(self.mooring_wind.tab_object[self.mooring_wind.mooringWidget.liste_element[i][1][0]][self.mooring_wind.mooringWidget.liste_element[i][1][1]])])
        #On calcule la trainee induite par la ligne de mouillage#
        for i in range(len(tab)):
            drag_v.append(0)
            for j in range(i+1):
                if j==len(tab):
                    break
                else:
                    if type(tab[j])!=list:
                        drag_v[i]=drag_v[i]+0.5*1025*eval(tab[j].projected_area)*eval(tab[j].tl_drag_cf)
                    else:
                        drag_v[i]=drag_v[i]+0.5*1025*(eval(tab[j][0].projected_area)*eval(tab[j][0].tl_drag_cf)+eval(tab[j][1].projected_area)*eval(tab[j][1].tl_drag_cf))
        
        tab[-1].mass=str(self.mooring_wind.mooringWidget.mylayout.itemAtPosition(len(tab),2).widget().text())   #On affecte le poids du lest
        self.mooring_wind.mooringWidget.anchor_weight_value=tab[-1].mass                                        #On sauvegarde la valeur
        for i in range(len(tab)):
            if type(tab[i])!=list:
              #Element non clampe#
                if not(hasattr(tab[i],"length")):
                    tab[i].length=str(self.mooring_wind.mooringWidget.mylayout.itemAtPosition(i+1,2).widget().text())   #On affecte la longueur du cable
                    tab[i].mass=str(eval(tab[i].length)*eval(tab[i].mass))                                              #On calcule la masse du cable
                    tab[i].projected_area=str(eval(tab[i].length)*eval(tab[i].projected_area))                          #On calcule la surface du cable
                    self.mooring_wind.mooringWidget.ropes_length[i]=tab[i].length
            else:
              #Element clampe#
                if not(hasattr(tab[i][0],"length")):
                    tab[i][0].length=str(self.mooring_wind.mooringWidget.mylayout.itemAtPosition(i+1,2).widget().text())
                    tab[i][0].mass=str(eval(tab[i][0].length)*eval(tab[i][0].mass))
                    tab[i][0].projected_area=str(eval(tab[i][0].length)*eval(tab[i][0].projected_area))
                    self.mooring_wind.mooringWidget.ropes_length[i]=tab[i][0].length

        data.append(tab) 
        x_float,y_float=self.environnement_wind.get_all_current_value()
        
        if self.environnement_wind.combo_1.currentIndex()==0:
            top=y_float[0]
            for i in range(len(y_float)):
                y_float[i]=y_float[i]-top
        data.append([x_float,y_float])                                            #On ajoute profondeur et valeur de courant
        data.append(copy.deepcopy(self.mooring_wind.mooringWidget.instru_depth))  #On ajoute les profondeurs des instruments
        data.append(drag_v)                                                       #Trainee du mouillage
        data.append(self.screen_width)                                            #Largeur de l ecran
        data.append(self.mypath)                                                  #Chemin du fichier
        data.append(self.mooring_wind.mooringWidget.clamp_ratio2)                 #On ajoute la copie de clamp_ratio
        
        return data
        
    def gathering_report_information(self):
        """Cette fonction recupere tout les informations necessaire pour la generation du rapport """
        self.report_wind.Tab_report=self.simulate_wind.Tab_report         #On copie le tableau de simulation dans la fenetre du rapport
        self.report_wind.inventory=self.simulate_wind.inventory           #On copie l inventaire dans la fenetre du rapport
        self.report_wind.anchor_value=self.simulate_wind.anchor_value     #On copie la valeur du lest dans la fenetre du rapport
        k=25
        offset=k*8
        font = QtGui.QFont("Arial")
        font.setPixelSize(k)  
        self.report_wind.mooring_image_width=[]
        self.report_wind.mooring_image_height=[]
        count=0
        for i in range(len(self.mooring_wind.mooringWidget.image2)):    #On parcourt l ensemble des images
            pixmap=self.mooring_wind.mooringWidget.image2[i]
            painter=QtGui.QPainter(pixmap)
            blank=QtGui.QPixmap(3*offset/4,pixmap.height())
            blank.fill(QtCore.Qt.white)
            painter.drawPixmap(0,0,blank)
            painter.setFont(font)
            if type(self.simulate_wind.data[0][i])!=list:
                #Pas de clampage#
                if self.simulate_wind.data[0][i].__class__.__name__=="Ropes":
                    text=str(self.simulate_wind.original_length[i])+' '+'m'                                   #Si c est un cable on ajoute la longueur sur l image 
                    painter.drawText(QtCore.QPoint(35,pixmap.height()-5-abs(pixmap.height()-23)/2), text)
                if self.simulate_wind.data[0][i].__class__.__name__=="Instruments" or i==0:
                    text=str(round(self.simulate_wind.myyfloat[i],1))+' '+'m'                                 #Si c est un instrument on ajoute la profondeur sur l image 
                    painter.drawText(QtCore.QPoint(3,pixmap.height()-5-abs(pixmap.height()-23)/2), text)
            else:
                #Clampage#
                if self.simulate_wind.data[0][i][0].__class__.__name__=="Ropes":
                    text=str(self.simulate_wind.original_length[i][0])+' '+'m'
                    painter.drawText(QtCore.QPoint(0.75*offset+0.5*max(self.mooring_wind.mooringWidget.max_width)+30,pixmap.height()-5-abs(pixmap.height()-23)/2),text)
                if self.simulate_wind.data[0][i][1].__class__.__name__=="Instruments":
                    text=str(round(self.simulate_wind.y_instru_top[count],1))+' '+'m'
                    painter.drawText(QtCore.QPoint(35,pixmap.height()-5-abs(pixmap.height()-23)/2), text)
                    count=count+1
                       
            if i==len(self.mooring_wind.mooringWidget.image2)-1:                                              #On ajoute la profondeur du fond
                text=str(self.environnement_wind.choice_depht_height.text())+''+'m'
                painter.drawText(QtCore.QPoint(35,pixmap.height()-5), text)
                
            pixmap.save(self.mypath+'\Report\Pictures\img'+str(i)+'.png')                                     #Sauvegarde de l image
            self.report_wind.mooring_image_width.append(pixmap.width())
            self.report_wind.mooring_image_height.append(pixmap.height())
        self.report_wind.mypath=self.mypath   
        
    def generate_report_pushButton_clicked(self):
        """Cette fonction est appele lorsque l utilisateur clique sur le bouton generate report """
        if hasattr(self,"simulate_wind"):                                                                    #On verifie que le mouillage a bien ete simule
            self.report_dockwidget.show()    
        else:
            QtGui.QMessageBox.information(self,'Message',"Simulate your mooring before creating the report")
        
        self.report_dockwidget.show()
        
#   def create_preference(self):
#     #Create the preferences window#
#       self.preference_wind=Preference_wind()
#       self.preference_dockwidget=myQDockWidget.myQDockWidget()
#       self.preference_dockwidget.setWidget(self.preference_wind)
#       self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.preference_dockwidget)
#        self.preference_dockwidget.setWindowTitle('Preferences')

    def create_report(self):
        """Creation de la fenetre du rapport """
        self.report_wind=Report_wind()
        self.report_dockwidget=myQDockWidget.myQDockWidget()
        self.report_dockwidget.setWidget(self.report_wind)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.report_dockwidget)
        self.report_dockwidget.setWindowTitle('Report parameters')
    def create_environnement(self):
        """Create de la fenetre des contraintes environnementales"""
        self.environnement_wind=Environnement_wind()
        self.environnement_wind.setMinimumWidth(0.75*0.5*self.screen_width)
        self.environnement_wind.setMinimumHeight(200)
        self.environnement_dockwidget=myQDockWidget.myQDockWidget()
        self.environnement_dockwidget.setWidget(self.environnement_wind)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.environnement_dockwidget)
        self.environnement_dockwidget.setWindowTitle('Set Environnemental Conditions')
        self.environnement_dockwidget.show()
        
    def get_file_name(self, fileName):
        """Cette fonction permet de recuperer le nom du fichier a partir du chemin """
        filename=""
        i=0
        while(fileName[-i]!='/'):
              filename=filename+fileName[-i]
              i=i+1   
        filename2=""
        for i in reversed(range(1,len(filename))):
            filename2=filename2+filename[i]
        return filename2
        
    def closerequested(self,k):
        """Cette fonction est appele lorsque l utilisateur ferme une fenetre de simulation """
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to close this window?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.zoneCentrale.removeTab(k)
        
        
    def closeEvent(self, event):
        """Cette fonction est appele lorsque l utilisateur veut fermer le logiciel """
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('main_icon.png'))
    ex=Mooring_Simulator()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
