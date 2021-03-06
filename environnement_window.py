#######################################################################################
##Mooring Simulator, 2014                                                           ####
##Edited by Arnaud Le Fur, IFREMER                                                  ####
########################################################################################


from myEnvironnementCanvas import MyEnvironnementCanvas
from PyQt4 import QtGui
import functools

class Environnement_wind(QtGui.QMdiArea):
    """Cette classe genere la fenetre de definitions des contraintes environnementales """
    def __init__(self):
        """Initialisation de la fenetre et des boutons """
        super(Environnement_wind, self).__init__()
        
        self.liste_point=[]
        self.param_saved=0
        #Premier onglet#
        self.window_1=QtGui.QWidget()
        self.subwindow_1=self.addSubWindow(self.window_1)
        self.subwindow_1.setWindowTitle('Define surface / bottom')
        self.subwindow_1.setWindowIcon(QtGui.QIcon('exit24.png'))
        self.combo_1=QtGui.QComboBox()
        self.combo_1.addItem("Position defined by height from bottom to surface")
        self.combo_1.addItem("Position defined by depth from surface to bottom")
        self.combo_1.activated.connect(self.combo_onActivated)
      
        self.btn1 = QtGui.QPushButton('Save', self)
        self.btn1.clicked.connect(functools.partial(self.save_surf_bott_btn,0))
        self.choice_depht_height = QtGui.QLineEdit("None")
        self.depht_height1=QtGui.QLabel("Surface height")
        self.window_1_layout1=QtGui.QVBoxLayout()
        self.window_1_layout2=QtGui.QHBoxLayout()
        self.window_1_layout1.addWidget(self.combo_1)
        self.window_1_layout2.addWidget(self.depht_height1)
        self.window_1_layout2.addWidget(self.choice_depht_height)
        self.window_1_layout2.addWidget(self.btn1)
        self.window_1_layout1.addLayout(self.window_1_layout2)
        self.window_1.setLayout(self.window_1_layout1)
        #Deuxieme onglet#
        self.window_2=QtGui.QWidget()
        self.subwindow_2=self.addSubWindow(self.window_2)
        self.subwindow_2.setWindowTitle('Define currents')
        self.subwindow_2.setWindowIcon(QtGui.QIcon('exit24.png'))
        self.windows_2_layout2=QtGui.QHBoxLayout() #Va contenir la grille des points definissant le courant et le plot du profil de courant
        self.window_2.setLayout(self.windows_2_layout2)
        #Definition des labels#
        self.label_current1=QtGui.QLabel(self.combo_1.currentText())
        self.label_current2=QtGui.QLabel("Height")
        self.label_current3=QtGui.QLabel("Current value")
        self.label_current4=QtGui.QLabel("Top")
        self.label_current5=QtGui.QLabel("0")
        self.line1=QtGui.QLineEdit("0.0")
        self.label_current6=QtGui.QLabel("Bottom")
        self.label_current7=QtGui.QLabel("None")
        self.line2=QtGui.QLineEdit("0.0")
        self.btn3 = QtGui.QPushButton('Create new point', self)
        self.btn3.clicked.connect(self.create_new_current_point)
        self.plot_profile_button=QtGui.QPushButton('Plot current profile', self)
        self.plot_profile_button.clicked.connect(self.Plot_profile)
        
        self.label_current2.setStyleSheet("QLabel { background-color : white; color : black;border: 2px solid black }")
        self.label_current3.setStyleSheet("QLabel { background-color : white; color : black;border: 2px solid black }")
        self.label_current4.setStyleSheet("QLabel { background-color : white; color : black;border: 2px solid black }")
        self.label_current5.setStyleSheet("QLabel { background-color : white; color : black;border: 1px solid black }")
        self.label_current6.setStyleSheet("QLabel { background-color : white; color : black;border: 2px solid black }")
        self.label_current7.setStyleSheet("QLabel { background-color : white; color : black;border: 1px solid black }")
        
        #Ajout des labels dans la grille#
        self.widget1=QtGui.QWidget()
        self.mylayout=QtGui.QGridLayout()
        self.mylayout.addWidget(self.label_current1,0,0,1,4)
        self.mylayout.addWidget(self.label_current2,1,1)
        self.mylayout.addWidget(self.label_current3,1,2)
        self.mylayout.addWidget(self.label_current4,2,0)
        self.mylayout.addWidget(self.label_current5,3,1)
        self.mylayout.addWidget(self.line1,2,2)
        self.mylayout.addWidget(self.label_current6,3,0)
        self.mylayout.addWidget(self.label_current7,2,1)
        self.mylayout.addWidget(self.line2,3,2)
        self.mylayout.addWidget(self.btn3,4,0)
        self.mylayout.addWidget(self.plot_profile_button,4,1)
        self.widget1.setLayout(self.mylayout)
        
        self.windows_2_layout2.addWidget(self.widget1)                      #Ajout de la grille dans le layout
       
        self.setViewMode(1)                                                 #Subwindows vue sous forme d onglet
        self.setActiveSubWindow(self.subwindow_1)
        self.resize(400,201)
    def combo_onActivated(self):
        """Cette fonction est appele lorsque lutilisateur change letat de la liste deroulante 
         Soit les profondeurs sont definies par hauteur a partir du fond ou par immersion a partir de la surface """
        
        if self.combo_1.currentIndex()==0:
            self.depht_height1.setText("Surface height")
        else:
            self.depht_height1.setText("Bottom depth")
            

    def save_surf_bott_btn(self,test):
        """ Cette fonction est appele lorsque lutilisateur clique sur le bouton de sauvegarde des parametres """

        self.label_current1.setText(self.combo_1.currentText())
        text=self.choice_depht_height.text()
        if self.combo_1.currentIndex()==0:                  #Profondeurs definies par hauteur a partir du fond
            self.label_current5.setText("0")
            self.label_current2.setText("Height")
            if text!='None':
                if float(text)<0:                           #Les profondeurs sont donc obligatoirement positives on vient donc corriger les erreurs de saisies de lutilisateur
                    text=str(-float(text))
                    self.choice_depht_height.setText(text)
            self.label_current7.setText(text)
        else:                                               #Profondeurs definies par immersion a partir de la surface
            self.label_current2.setText("Depth")
            if text!='None':
                if float(text)>0:                           #Les profondeurs sont donc obligatoirement negatives on vient donc corriger les erreurs de saisies de lutilisateur
                    text=str(-float(text))
                    self.choice_depht_height.setText(text)
            self.label_current5.setText(text)
            self.label_current7.setText("0")
            
        if test!=1:
            QtGui.QMessageBox.information(self,'Message',"Parameters saved")
        self.param_saved=1
    
    def Plot_profile(self):
        """Permet de tracer le profil de courant a partir des points definies par lutilisateur """
        x_float,y_float=self.get_all_current_value()        #Recuperation des valeurs
        if hasattr(self,"sc1"):                             #Sil existe un precedent graphique celui-ci est detruit
            self.sc1.hide()
        self.plot_widget = QtGui.QWidget(self)
        self.sc1 = MyEnvironnementCanvas(x_float, y_float, "Current Profile", "Speed (m.s-1)","Depth(m)", self.plot_widget) #Plot du graphique
        self.windows_2_layout2.addWidget(self.sc1)                                                                          #Ajout dans le layout

    def create_new_current_point(self):
        """Cette fonction est appele lorsque lutilisateur ajoute un nouveau point de courant """
        #Creation des 3 labels#
        new_depth=QtGui.QLineEdit()         #Profondeur du courant
        new_value=QtGui.QLineEdit()         #Valeur du courant 
        new_button_delete = QtGui.QPushButton('Remove point', self) #Bouton de suppression adapte

        k=len(self.liste_point)+3
        new_button_delete.clicked.connect(functools.partial(self.remove_current_point,k)) #Connecte le bouton delete a la fonction de suppression en passant en parametre son indice

        for i in reversed (range(3,len(self.liste_point)+5)):                             #On decale vers le bas tout les labels se situant apres le nouveau point en partant de la fin
            self.mylayout.addWidget(self.mylayout.itemAtPosition(i,0).widget(),i+1,0)
            self.mylayout.addWidget(self.mylayout.itemAtPosition(i,1).widget(),i+1,1)
            if i!=len(self.liste_point)+4:
                self.mylayout.addWidget(self.mylayout.itemAtPosition(i,2).widget(),i+1,2)
    
        self.mylayout.addWidget(new_depth,3,1)                                            #On ajoute les 3 labels a lemplacement que lon vient de liberer
        self.mylayout.addWidget(new_value,3,2)
        self.mylayout.addWidget(new_button_delete,3,0)
        self.liste_point.insert(0,k)                                                      #On ajoute le nouveau point dans la liste

    def remove_current_point(self,k1):
        """Cette fonction est appele lorsque lutilisateur clique sur le bouton de suppression
        Input : indice du point """

        k=self.liste_point.index(k1)+3                                                   #On vient chercher a partir de linput le positionnement reelle dans la grille
        for i in range(3):                                                               #On supprime les 3 labels concernes 
            self.mylayout.itemAtPosition(k,i).widget().hide()
            self.mylayout.removeWidget(self.mylayout.itemAtPosition(k,i).widget())
    
        for i in range(k+1,len(self.liste_point)+5):                                     #On decale vers le haut tout les labels se situant apres point supprime
            self.mylayout.addWidget(self.mylayout.itemAtPosition(i,0).widget(),i-1,0)
            self.mylayout.addWidget(self.mylayout.itemAtPosition(i,1).widget(),i-1,1)
            if i!=len(self.liste_point)+4:
                self.mylayout.addWidget(self.mylayout.itemAtPosition(i,2).widget(),i-1,2)
        self.liste_point.remove(k1)                                                      #On supprime le point de la liste

    def get_all_current_value(self):
        """Cette fonction retourne l ensemble des points de courant et leur profondeur
        output : y : profondeur des points
                 x : valeur du courant
                 """
        x=[]
        y=[]
        for i in range(2,len(self.liste_point)+4):
            if self.mylayout.itemAtPosition(i,1).widget().text()!='None':
                x.append(float(self.mylayout.itemAtPosition(i,1).widget().text()))
            else:
                x.append(0)
            y.append(float(self.mylayout.itemAtPosition(i,2).widget().text()))
        return y,x
   

