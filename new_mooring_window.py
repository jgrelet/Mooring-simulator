#############################################################################
##Moorinator, 2013                                                       ####
##Edited by Arnaud Le Fur, IFREMER                                       ####
##new_mooring_window.py creates the mooring window and its toolbox       ####
#############################################################################

from PyQt4 import QtCore, QtGui
import functools
import library_window
import xlrd
from os import getcwd

class MooringWidget(QtGui.QWidget):
    """Cette classe definit la partie gauche de l ecran de creation du mouillage : l espace de travail """
    def __init__(self, parent=None):
        super(MooringWidget, self).__init__(parent)
 
        self.mypath=getcwd()
        self.mypath=self.mypath+'\Library'
        #Fonction de zoom#
        zoom_in_Action = QtGui.QAction(QtGui.QIcon(self.mypath+'\Pictures\Icons\zoom_in.png'), 'Zoom_in', self)
        zoom_out_Action = QtGui.QAction(QtGui.QIcon(self.mypath+'\Pictures\Icons\zoom_out.png'), 'Zoom_out', self)
        zoom_in_Action.triggered.connect(functools.partial(self.zoom_mooring,1))
        zoom_out_Action.triggered.connect(functools.partial(self.zoom_mooring,0))
        self.current_zoom=0
        #Listes qui vont decrir le mouillage#
        self.liste_element=[]
        self.ropes_length=[]
        self.instru_depth=[]
        self.clamp_ratio=[]
        
        self.insert=0
        self.clamp=0
        self.anchor_weight_value='0'                                #Poids non defini
        self.toolbar = QtGui.QToolBar()                             #Toolbar en haut de la fenetre
        self.toolbar.addAction(zoom_in_Action)
        self.toolbar.addAction(zoom_out_Action)
        self.toolbar2 = QtGui.QToolBar()                            #Toolbar en bas de la fenetre
        label_toolbar=QtGui.QLabel("<b>Add new element<\b>")
        label_toolbar2=QtGui.QLabel("<b>Insert new element<\b>")
        self.label_toolbar=self.toolbar2.addWidget(label_toolbar)
        self.label_toolbar2=self.toolbar2.addWidget(label_toolbar2)
        self.label_toolbar2.setVisible(0)                           #Add par defaut
        
        self.moor_bigLayout=QtGui.QVBoxLayout()
        self.moor_bigLayout.addWidget(self.toolbar)
        self.moor_groupLayout=QtGui.QVBoxLayout()
        #Taille des boutons#
        self.size_pol=10
        self.f=QtGui.QFont("Times New Roman",self.size_pol)
        self.k_mult=1
        self.a=1.5
        #Zone de defilement vertical#
        self.moor_scrollArea = QtGui.QScrollArea()
        self.moor_groupLayout.addWidget(self.moor_scrollArea)
        
        self.scrolledWidget = QtGui.QWidget()
        self.mylayout=QtGui.QGridLayout(self.scrolledWidget)
        #Bouton insertion premier element#
        self.button_insert_first=QtGui.QPushButton("Insert First Element",self)
        self.button_insert_first.clicked.connect(self.insert_first_element)
        self.button_insert_first.setFixedSize(110*self.a*self.k_mult,22*(self.size_pol/10))
        self.button_insert_first.setFont(self.f)
        self.mylayout.addWidget(self.button_insert_first,0,0)
        #Ajout du widget dans la zone de defilement#
        self.moor_scrollArea.setWidget(self.scrolledWidget)
        self.moor_bigLayout.addLayout(self.moor_groupLayout)
        self.moor_bigLayout.addWidget(self.toolbar2)
        self.setLayout(self.moor_bigLayout)

        self.vbar = self.moor_scrollArea.verticalScrollBar()
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        """Cette fonction est appele lorsque l utilisateur entre dans la fenetre en faisant glisser un objet"""
 
        if event.mimeData().hasFormat('image/piece'):                       #Bon format
            pieceData = event.mimeData().data('image/piece')
            dataStream = QtCore.QDataStream(pieceData, QtCore.QIODevice.ReadOnly)
            pixmap = QtGui.QPixmap()
            location = QtCore.QPoint()
            dataStream >> pixmap >> location                        #on recupere le numero de la feuille excel et numero de la ligne de l element que veut clamper l utilisateur ##
            self.piece_sheet=location.x()
            self.piece_ind=location.y()
            event.accept()
        else:
            event.ignore()
     
    def dropEvent(self, event):
        """Cette fonction est appele lorsque l utilisateur lache l objet qu il faisait glisser"""
        tab=[]
        instru_depth=0
        self.piece_position=self.get_piece_position() #On recupere la position en y de chaque image du mouillage
        if  event.mimeData().hasFormat('image/piece'):
            for i in range(len(self.piece_position)):
                tab.append(abs(self.piece_position[i]-(event.pos().y()+self.vbar.value())))         #On fait la difference entre la position du curseur et la position de chaque image
            ind=tab.index(min(tab))                                                                 #On prend limage la plus proche comme support de clampage
            if self.ropes_length[ind]!=0:                                                           #Si le cable nest pas defini en auto
                reply = QtGui.QMessageBox.question(self, 'Message',
                "Do you want to clamp"+" " +str(self.tab_object[self.piece_sheet][self.piece_ind].name)+" "+"on"+" "+
                                                   str(self.tab_object[self.liste_element[ind][0]][self.liste_element[ind][1]].name),
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

                if reply == QtGui.QMessageBox.Yes:
                    self.liste_element[ind]=[self.liste_element[ind],[self.piece_sheet,self.piece_ind]] #On ajoute l element clampe dans liste_element
                    event.accept()
                    if self.tab_name_class[self.piece_sheet]=="Instruments":
                        self.clamp=1
                        self.ask_instru_depth(ind)                                                 #On demande la profondeur de l instrument
                        instru_depth=self.instru_depth_value                                        
                        self.clamp=0
                        if instru_depth.toFloat()[1]==True:
                            instru_depth=instru_depth.toFloat()[0]

                    self.instru_depth[ind]=[self.instru_depth[ind],instru_depth]                    #On ajoute la profondeur choisie dans instru_depth
                    self.vbar_value=self.vbar.value()
                    self.update_grid(1)                                                             #On met a jour le layout
                else:
                    event.ignore()
            else:
                QtGui.QMessageBox.warning(self,'Message',"You can't clamp on an auto rope")
                event.ignore()
    
            
    def dragMoveEvent(self, event):
        """Cette fonction est appele lorsque l utilisateur se deplace dans la fenetre en faisant glisser un objet """

        if event.mimeData().hasFormat('image/piece'):

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
            
    def get_piece_position(self):
        """Retourne la position verticale de chaque image du mouillage"""
        table=[77]                                      #offset qui est du a la toolbar situee au dessus de la fenetre 
        for i in range(len(self.liste_element)):
            pixmap=self.mylayout.itemAtPosition(i+1,1).widget().pixmap()
            table.append(table[i]+pixmap.height())
        table.remove(77)
        for i in range(len(self.liste_element)):                        #On recupere la position des centres des images
            pixmap=self.mylayout.itemAtPosition(i+1,1).widget().pixmap()
            table[i]=table[i]-(pixmap.height()/2)
        return table
    def zoom_mooring(self,k):
        """Fonction qui va permettre de mettre a jour les coefficients qui definissent la taille des images et des boutons
        Input : k : booleen qui correspondant au zoom (k=1) ou dezoom(k=0)"""
        
        k_zoom=2.

        if k==1:
            self.current_zoom=self.current_zoom+1
        if k==0:
            self.current_zoom=self.current_zoom-1 
            
        #On met a jour self.k, self.size_pol et self.a en fonction du zoom courant
        self.k_mult=k_zoom**self.current_zoom
        if self.current_zoom>=0:
            self.size_pol=10*1./(0.7**self.current_zoom)
        if self.current_zoom<0:
            self.size_pol=10*(0.65**(self.current_zoom*-1))
           
        self.f=QtGui.QFont("Times New Roman",self.size_pol)
        if self.current_zoom<0:
            self.a=1./self.k_mult
        if self.current_zoom>0:
            self.a=3./4
        if self.current_zoom==0:
            self.a=1.5

        self.update_grid(0) #On update 
        
    def ask_instru_depth(self,ind):
    
        """Cette fonction est appele lorsqu un instrument est ajoute ou clampe, elle cree la boite de dialogue
        Input : ind : indice de l instrument ou du support"""
        
        self.le = QtGui.QLineEdit(self)
        self.dialog=QtGui.QDialog(self)
        label=QtGui.QLabel('Enter the depth of the instrument (Auto for automatic):')
        auto=QtGui.QPushButton("Auto")
        ok=QtGui.QPushButton("Ok")
        auto.clicked.connect(functools.partial(self.instru_auto_clicked_on,ind))
        ok.clicked.connect(functools.partial(self.instru_ok_clicked_on,ind))
        layout=QtGui.QVBoxLayout()
        layout2=QtGui.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.le)
        layout2.addWidget(ok)
        layout2.addWidget(auto)
        layout.addLayout(layout2)
        self.dialog.setLayout(layout)
        self.dialog.exec_()
        
    def instru_auto_clicked_on(self,ind):
        """Cette fonction est appele lorsque l utilisateur defini la profondeur de l instrument en automatique 
        Input : ind : indice de l instrument ou du support """
        self.instru_depth_value=QtCore.QString('0')
        self.dialog.close()
        if self.clamp==1:                           #Si on est dans le cas d un clampage on apelle ask_ratio
            self.ask_ratio(ind)
            
    def instru_ok_clicked_on(self,ind):
        """Cette fonction est appele lorsque l utilisateur defini la profondeur de l instrument en automatique 
        Input : ind : indice de l instrument ou du support """
        self.instru_depth_value=self.le.text()
        self.dialog.close()
        if self.clamp==1:
            self.ask_ratio(ind)                     #Si on est dans le cas d un clampage on apelle ask_ratio
            
    def ask_ropes_length(self):
        """Cette fonction est appele lorsqu un cable est ajoute, elle cree la boite de dialogue
        """
        
        self.le = QtGui.QLineEdit(self)
        self.dialog= QtGui.QDialog(self)
        label=QtGui.QLabel('Enter the length  (Auto for automatic):')
        auto=QtGui.QPushButton("Auto")
        ok=QtGui.QPushButton("Ok")
        auto.clicked.connect(self.rope_auto_clicked_on)
        ok.clicked.connect(self.rope_ok_clicked_on)
        layout=QtGui.QVBoxLayout()
        layout2=QtGui.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.le)
        layout2.addWidget(ok)
        layout2.addWidget(auto)
        layout.addLayout(layout2)
        self.dialog.setLayout(layout)
        self.dialog.exec_()       
            
    def rope_auto_clicked_on(self):
        """Cette fonction est appele lorsque l utilisateur defini la longueur d un cable en automatique 
        """
        self.current_length=QtCore.QString('0')
        self.dialog.close()
        
    def rope_ok_clicked_on(self):
        """Cette fonction est appele lorsque l utilisateur defini la longueur d un cable manuellement """
        self.current_length=self.le.text()
        self.dialog.close()
    
    def ask_ratio(self,ind):
        """Cette fonction est appelle lors d un clampage, elle cree la boite de dialogue 
        Input : ind : indice de l instrument ou du support """
        self.le = QtGui.QLineEdit(self)
        self.dialog=QtGui.QDialog(self)
        label=QtGui.QLabel('Enter the clamp ratio (value from 0 to 1)')
        auto=QtGui.QPushButton("Auto")
        ok=QtGui.QPushButton("Ok")
        auto.clicked.connect(functools.partial(self.auto_ratio_clicked_on,ind))
        ok.clicked.connect(functools.partial(self.ok_ratio_clicked_on,ind))
        layout=QtGui.QVBoxLayout()
        layout2=QtGui.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.le)
        layout2.addWidget(ok)
        layout2.addWidget(auto)
        layout.addLayout(layout2)
        self.dialog.setLayout(layout)
        self.dialog.exec_()
        
    def auto_ratio_clicked_on(self,ind):
        """Cette fonction est appele lorsque l utilisateur choisi un clampage auto 
        Input : ind : indice de l instrument ou du support"""
        self.clamp_ratio[ind]=0 
        self.dialog.close()
        
    def ok_ratio_clicked_on(self,ind):
        """Cette fonction est appele lorsque l utilisateur choisi un clampage manuel 
        Input : ind : indice de l instrument ou du support"""
        if float(self.le.text())>0 and float(self.le.text())<1:
            self.clamp_ratio[ind]=float(self.le.text())
            self.dialog.close()
        else:
            QtGui.QMessageBox.warning(self,'Message',"Ratio value is between 0 and 1")
            
    def ask_anchor_weight(self):
        """Cette fonction est appelee lorsque lutilisateur ajoute un objet de type Anchor, elle cree la boite de dialogue"""
        self.le = QtGui.QLineEdit(self)
        self.dialog=QtGui.QDialog(self)
        label=QtGui.QLabel('Enter the wet weight of the anchor (kg):')
        ok=QtGui.QPushButton("Ok")
        ok.clicked.connect(self.anchor_ok_clicked_on)
        layout=QtGui.QVBoxLayout()
        layout2=QtGui.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.le)
        layout2.addWidget(ok)
        layout.addLayout(layout2)
        self.dialog.setLayout(layout)
        self.dialog.exec_()
        
    def anchor_ok_clicked_on(self):
        """Cette fonction est appele lorsque l'utilisateur valide le poids du lest"""
        self.anchor_weight_value=self.le.text()    
        self.dialog.close()
  
    def update_grid(self,vbar_statut):
        """Cette fonction permet d'afficher la ligne de mouillage en fonction de l etat des listes decrivant le mouillage 
        elle est appele a chaque fois qu'un element est ajoute, insere, supprime, clampe, declampe, en cas de zoom 
        Input : vbar_statut : Vaut 1 En cas d insertion, ou de suppression, de clampage, declampage 
                              Vaut 0 En cas d ajout"""
 
        scrolledWidget = QtGui.QWidget()
        self.mylayout=QtGui.QGridLayout(scrolledWidget)
        #Bouton insert first element#
        self.button_insert_first.setFixedSize(110*self.a*self.k_mult,22*(self.size_pol/10))
        self.button_insert_first.setFont(self.f)
        self.mylayout.addWidget(self.button_insert_first,0,0)
        
        self.create_mooring_image()                                             #Creation des images
        for i in range(len(self.liste_element)):                                #On parcourt la liste des elements
            if self.ropes_length[i]!=0:                                         #En cas de cable dont la longueur est connu on la rend visible 
                off=1
                line_edit_length=QtGui.QLineEdit(str(self.ropes_length[i]))
            else:
                off=0
            if i==(len(self.liste_element)-1) and self.anchor_weight_value!='0':
                off2=1
                
                line_edit_weight=QtGui.QLineEdit(str(self.anchor_weight_value)) #En cas de dernier element si le poids du lest est defini on rend visible celui ci
            else:
                off2=0
            if type(self.liste_element[i][0])!=int:                             #En cas de clampage on ajoute le bouton unclamp
                
                button_unclamp=QtGui.QPushButton("Unclamp Element",self)
                button_unclamp.setFixedSize(100*self.a*self.k_mult,22*(self.size_pol/10))
                button_unclamp.setFont(self.f)
                button_unclamp.clicked.connect(functools.partial(self.unclamp_element,i))
                self.mylayout.addWidget(button_unclamp,i+1,3+off)

            pixmap=self.image2[i]                                   
            #On ajoute les boutons de suppression et dinsertion a la bonne taille selon le zoom#
            button_exit=QtGui.QPushButton("Delete Element",self)                
            button_insert=QtGui.QPushButton("Insert Element",self)
            button_exit.setFixedSize(100*self.a*self.k_mult,22*(self.size_pol/10))
            button_insert.setFixedSize(100*self.a*self.k_mult,22*(self.size_pol/10))
            button_exit.setFont(self.f)
            button_insert.setFont(self.f)
            button_exit.clicked.connect(functools.partial(self.delete_element,i))
            button_insert.clicked.connect(functools.partial(self.insert_element,i))
            #On redimensionne l image selon le zoom#
            new_Pixmap=pixmap.scaledToWidth(pixmap.width()*self.k_mult,QtCore.Qt.SmoothTransformation)
            label=QtGui.QLabel()
            label.setPixmap(new_Pixmap)
            #Ajout dans le layout#
            self.mylayout.addWidget(button_insert,i+1,0)
            self.mylayout.addWidget(label,i+1,1)
            if off==1:
                 self.mylayout.addWidget(line_edit_length,i+1,2)
            if off2==1:
                self.mylayout.addWidget(line_edit_weight,i+1,2)
            self.mylayout.addWidget( button_exit,i+1,2+off+off2)
                  
        self.mylayout.setSpacing(0)
        self.moor_scrollArea.setWidget(scrolledWidget)
        self.vbar = self.moor_scrollArea.verticalScrollBar()
        if vbar_statut==0:                              #En cas d ajout d element la barre vertical prend sa valeur max
            self.vbar.setValue(self.vbar.maximum())
        else:
            self.vbar.setValue(self.vbar_value)         #En cas dinsertion suppression clampage elle garde sa valeur

        
    def unclamp_element(self,i):
        """Cette fonction est appele lorsque l utilisateur clique sur le bouton unclamp 
        input : i : indice de l element"""
        self.liste_element[i]=self.liste_element[i][0]
        self.instru_depth[i]=self.instru_depth[i][0]
        self.clamp_ratio[i]=2
        self.vbar_value=self.vbar.value()
        self.update_grid(1)
        
    def create_mooring_image(self):
        """Cette fonction permet de creer toute les images pour chaque element de liste_element """
        self.image2=[]
        self.max_len=[]
        self.max_width=[]
        #On definit la police et l offset#
        k=25
        offset=k*8
        font = QtGui.QFont("Arial")
        font.setPixelSize(k)  
        #On cherche d abord l image la plus large car tout le mouillage sera centre par rapport a celle-ci#
        for i in range(len(self.liste_element)):
            # add debug
            # print(i,self.liste_element[i])
            if type(self.liste_element[i][0])!=int:
                path=self.mypath+self.tab_object[self.liste_element[i][0][0]][self.liste_element[i][0][1]].image_file
                a=0.75*k*len(self.tab_object[self.liste_element[i][0][0]][self.liste_element[i][0][1]].name)
            else :
                path=self.mypath+self.tab_object[self.liste_element[i][0]][self.liste_element[i][1]].image_file
                a=0.75*k*len(self.tab_object[self.liste_element[i][0]][self.liste_element[i][1]].name)
            newImage=QtGui.QPixmap()
            if not newImage.load(path):
                    QtGui.QMessageBox.warning(self, "Open Image", "The image file could not be loaded.",QtGui.QMessageBox.Cancel)
                    return
            self.max_len.append(a)
            self.max_width.append(newImage.width())
        #Creation des images#
        for i in range(len(self.liste_element)):
            if type(self.liste_element[i][0])==int:                                                         #element non clampe
                path=self.mypath+self.tab_object[self.liste_element[i][0]][self.liste_element[i][1]].image_file
                newImage=QtGui.QPixmap()
                newImage.load(path)
                name=self.tab_object[self.liste_element[i][0]][self.liste_element[i][1]].name
                ImageResult2=QtGui.QPixmap(max(self.max_len)+max(self.max_width)+1*offset,newImage.height()) #On cree l image resultante avec une constante en largeur et la hauteur de l image dorigine
                ImageResult2.fill(QtCore.Qt.white)                                                           #On la remplit de blanc
                painter=QtGui.QPainter(ImageResult2)
                painter.setFont(font)
                painter.drawText(QtCore.QPoint(max(self.max_width)+offset,newImage.height()-5-abs(newImage.height()-23)/2), name ) #On ecrit le nom de l element a droite et centre en hauteur
                painter.drawPixmap(((max(self.max_width)-newImage.width())/2)+offset-offset/4, 0, newImage)                        #On dessine l image
                if self.instru_depth[i]!=0:
                    depth=str(self.instru_depth[i])
                    painter.drawText(QtCore.QPoint(35,newImage.height()-5-abs(newImage.height()-23)/2), depth)                     #Si la profondeur est connu celle ci est dessine a gauche 
                    
            else:
                #En cas de clampage#
                ImageResult2=self.create_clamp_image(self.liste_element[i]) #Creation de l image
                if type(self.instru_depth[i])==list:
                    for p in range(2):
                        if self.instru_depth[i][p]!=0:
                            painter=QtGui.QPainter(ImageResult2)
                            painter.setFont(font)
                            depth=str(self.instru_depth[i][p])
                            painter.drawText(QtCore.QPoint(35,ImageResult2.height()-5-abs(ImageResult2.height()-23)/2), depth)  # Si la profondeur est connu celle ci est dessine a gauche 
                      
            self.image2.append(ImageResult2)

    def create_clamp_image(self,element):
        """Cette fonction permet creer l image d un element clampe sur l autre 
        Input : element : tableau contenant le support et l element clampe"""
        #Definition de la police#
        k=25
        offset=k*8
        font = QtGui.QFont("Arial")
        font.setPixelSize(k)  
        newImage1 = QtGui.QPixmap()
        newImage2 = QtGui.QPixmap()
        #Chargement image1#
        if not newImage1.load(self.mypath+self.tab_object[element[0][0]][element[0][1]].image_file):
            QtGui.QMessageBox.warning(self, "Open Image",
                    "The image file could not be loaded.",
                    QtGui.QMessageBox.Cancel)
            return
        #Chargement image2#
        if not newImage2.load(self.mypath+self.tab_object[element[1][0]][element[1][1]].image_file):
            QtGui.QMessageBox.warning(self, "Open Image",
                    "The image file could not be loaded.",
                    QtGui.QMessageBox.Cancel)
            return
        
        name1=self.tab_object[element[0][0]][element[0][1]].name
        name2=self.tab_object[element[1][0]][element[1][1]].name
        text="clamped on "
        
        if newImage1.height()<newImage2.height():                                                           #Si le support est plus petit que l element clampe
            newImage2=newImage2.scaledToHeight(newImage1.height(),QtCore.Qt.SmoothTransformation)           #On redimensionne l element clampe
        ImageResult2=QtGui.QPixmap(max(self.max_len)+max(self.max_width)+1*offset,newImage1.height())
        ImageResult2.fill(QtCore.Qt.white)
        painter=QtGui.QPainter(ImageResult2);
        painter.setFont(font)
        #Dessine les deux images#
        painter.drawPixmap(((max(self.max_width)-newImage1.width())/2)+offset-offset/4, 0, newImage1);
        painter.drawPixmap(((max(self.max_width)-newImage1.width())/2)+offset-offset/4-newImage2.width(), (newImage1.height()-newImage2.height())/2, newImage2);
        #Ajout du texte#
        painter.drawText(QtCore.QPoint(max(self.max_width)+offset,ImageResult2.height()-5-abs(ImageResult2.height()-3*23)/2), name1)
        painter.drawText(QtCore.QPoint(max(self.max_width)+offset,ImageResult2.height()-5-(abs(ImageResult2.height()-3*23)/2+23)), text)
        painter.drawText(QtCore.QPoint(max(self.max_width)+offset,ImageResult2.height()-5-(abs(ImageResult2.height()-3*23)/2+46)), name2)
        
        return ImageResult2
        
    def delete_element(self,k):
        """Cette fonction est appelle lorsque l utilisateur clique sur le k ieme bouton delete 
        Input : k : indice de l element supprime """
        if self.insert!=1:
            #On le supprime de toutes les listes#
            del self.liste_element[k]
            del self.ropes_length[k]
            del self.instru_depth[k]
            del self.clamp_ratio[k]
            self.vbar_value=self.vbar.value()
            self.update_grid(1)
        else:
            QtGui.QMessageBox.information(self,'Message',"Choose an element to insert")
            
    def insert_element(self,k):
        """Cette fonction est appelle lorsque l utilisateur clique sur le k ieme bouton insertion
        Input : k : indice de l element qui precede le nouvel element insere"""
        if self.insert!=1:
            self.insert=1
            self.insert_pos=k
            self.change_toolbar_label_state(1)
            self.vbar_value=self.vbar.value()
            
        else:
            QtGui.QMessageBox.information(self,'Message',"Choose an element to insert")
 
    def insert_first_element(self):
        """Cette fonction est appelle lorsque l utilisateur clique sur le bouton insert first element
        """
        #Insert first element pushbutton clicked on, Permit to insert a new first element#
        if self.insert!=1:
            self.insert=1
        
            self.insert_pos=-1
            self.change_toolbar_label_state(1)
            self.vbar_value=self.vbar.value()
        else:
            QtGui.QMessageBox.information(self,'Message',"Choose an element to insert")
            
        
    def change_toolbar_label_state(self,state):
        """Change l etat de la toolbar en fonction de state 
            Input : state : 0 : ajout d un element
                          : 1 : insertion d un element 
                          """
        if state==1:

            self.label_toolbar.setVisible(0)
            self.label_toolbar2.setVisible(1)

        else:
            self.label_toolbar.setVisible(1)
            self.label_toolbar2.setVisible(0)        
                
                  
                  
class ObjectList(QtGui.QListWidget):
    """Cette classe definit une liste de Widget, une instance de cette classe est creee pour chaque type d objet, 
    les objets apparaissent sous formes d icones """
    def __init__(self, parent=None):
        """Initialisation de la classe """
        super(ObjectList, self).__init__(parent)
        
        self.setViewMode(QtGui.QListView.IconMode)
        self.setIconSize(QtCore.QSize(110, 110))
        self.setSpacing(0)
        self.mypath=getcwd()
        self.mypath=self.mypath+'\Library'
    def addObject(self,pixmap,sheet,nb):
        """Ajout d un objet dans l ObjectList 
        Input : pixmap : icone
                sheet :  numero de feuille excel
                nb :     numero de ligne
                """
        pieceItem = QtGui.QListWidgetItem(self)
        pieceItem.setIcon(QtGui.QIcon(pixmap))
        pieceItem.setData(QtCore.Qt.UserRole, [pixmap,sheet,nb])                                                #On ajoute les informations dont on a besoin dans l item
        pieceItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        
    def dragMoveEvent(self, event):
        """Cette fonction est appele quand lutilisateur fait glisser l objet qu'il a selectionne"""
        if event.mimeData().hasFormat('piece'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, supportedActions):
        """Cette fonction est appele lorsque l utilisateur reste cliquer sur un objet pour le faire glisser
        """
        item = self.currentItem()
        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        ok=item.data(QtCore.Qt.UserRole).toList()
        #On recupere les infos contenus dans l item#
        pixmap = QtGui.QPixmap(ok[0])
        sheet = ok[1].toInt()
        nb = ok[2].toInt()
        loc=QtCore.QPoint(sheet[0],nb[0])
        
        dataStream << pixmap << loc                 #On les ajoute dans le dataStream et ces informations pourront etre recuperees par la classe mooringWidget

        mimeData = QtCore.QMimeData()
        mimeData.setData('image/piece', itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)

        if drag.exec_(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            a=2
        
            
class MooringWindow(QtGui.QWidget):
    """Cette fonction defini la fenetre globale """
    def __init__(self, default_folder,screen_width, parent=None):
        """Initialisation de la fenetre 
        Input : default_folder : chemin de Library.xls 
                screen_width : largeur de l ecran """
        super(MooringWindow, self).__init__(parent)

        self.mooringImage = QtGui.QPixmap()
        self.default_folder=default_folder
        self.screen_width=screen_width
        self.mypath=getcwd()
        self.mypath=self.mypath+'\Library'
        #Creation toolbar#
        refresh_library=QtGui.QAction(QtGui.QIcon(self.mypath+'\Pictures\Icons\Refresh.png'), 'Refresh_library', self)
        refresh_library.triggered.connect(self.refresh_library)
        self.toolbar3 = QtGui.QToolBar()
        self.toolbar3.addAction(refresh_library)
        
        self.frameLayout2 = QtGui.QVBoxLayout()         #Contient la toolbar et les objectlist
        self.frameLayout = QtGui.QHBoxLayout()          #Contient le mooringWidget et le framelayout2
        self.mooringWidget = MooringWidget()
        self.mooringWidget.show()
        self.frameLayout.addWidget(self.mooringWidget)
        self.frameLayout2.addWidget(self.toolbar3)
        self.piece=self.create_widget()                 #Creation des Objectlist dans le widget piece
        self.frameLayout2.addWidget(self.piece)
        self.frameLayout.addLayout(self.frameLayout2)
        self.setWindowTitle("Mooring")
        self.setLayout(self.frameLayout)
        self.openImage()

    def create_widget(self):
        """Creation des ObjectList 
        Output : piece : QMdiArea contenant tout les ObjectList"""
        self.get_library(self.default_folder)                   #Chargement des donnees de Library.xls#
        
        self.mooringWidget.tab_object=self.tab_object
        self.mooringWidget.tab_name_class=self.tab_name_class
        self.openImage()                                        #Creation des icones
        piece=QtGui.QMdiArea()
        piece.setMaximumWidth(0.38*self.screen_width)
        for i in range(len(self.tab_object)):
            objectList=ObjectList()                             #Creation d un objectlist pour chaque type d element
            for j in range(len(self.tab_object[i])):
                objectList.addObject(self.image[i][j],i,j)      #On ajoute chaque objet
            
            objectList.itemDoubleClicked.connect(functools.partial(self.add_new_element,i)) #On connecte le double clique avec la fonction add_new_element
            ObjectList_subwind=QtGui.QMdiSubWindow()
            ObjectList_subwind.setWidget(objectList)
            ObjectList_subwind.setWindowTitle(self.tab_name_class[i])
            ObjectList_subwind.setWindowIcon(QtGui.QIcon('exit24.png'))
            piece.addSubWindow(ObjectList_subwind)
            

        piece.setViewMode(1)                                    #Vue sous forme d onglet               
        
        return piece
                
    def openImage(self, path=None):
        """Cree les icones pour chaque objet de chaque ObjectList """
        self.image=[]
        
        for i in range(len(self.tab_object)):
            self.inter=[]
            for j in range(len(self.tab_object[i])):
                newImage = QtGui.QPixmap()
                if not newImage.load(self.mypath+self.tab_object[i][j].image_file):
                    QtGui.QMessageBox.warning(self, "Open Image",
                            "The image file could not be loaded."+str(i)+str(j),
                            QtGui.QMessageBox.Cancel)
                    return
                text=self.tab_object[i][j].name
                cap=0
                #Definition la police#
                font = QtGui.QFont("Arial")
                font.setPixelSize(18)
                
                w,h=newImage.width(),newImage.height()
                ImageResult=QtGui.QPixmap(150,150)              #Taille de l icone
                ImageResult.fill(QtCore.Qt.white)
                painter=QtGui.QPainter(ImageResult)
                for a in text:
                    if a.isupper():
                        cap=cap+1
                true_len=len(text)+cap*0.5   #Cap designe le nombre de majuscule 
                if true_len>16:              #Si la chaine est trop longue on la divise en deux 

                    mytext=text.split('-',1)
                    if len(mytext)==1:
                        mytext=text.split(' ',1)
                        if len(mytext)==1:
                            mytext=text.split('_',1)
                            if len(mytext)==1:
                                mytext=[text[0:int(len(text)/2)],text[int(len(text)/2)+1:len(text)-1]]
                    if h>114:                                           #On a besoin de 36 pixel pour ecrire les deux chaines de charactere l un sous l autre
                        if(w/h)*114<=150:                               
                            newImage=newImage.scaledToHeight(114,QtCore.Qt.SmoothTransformation)
                            w,h=newImage.width(),newImage.height()
                        else:
                            newImage=newImage.scaledToWidth(150,QtCore.Qt.SmoothTransformation)
                            w,h=newImage.width(),newImage.height()      
                    painter.setFont(font)
                    painter.drawPixmap((150-w)/2,(114-h)/2, newImage);
                    painter.drawText(QtCore.QPoint((150-true_len*4.5)/2,128), mytext[0] );
                    painter.drawText(QtCore.QPoint((150-true_len*4.5)/2,146), mytext[1] );
                        
                else: 
                    if h>132:                                           #On a besoin de 18 pixel pour ecrire une chaine de charactere
                        if(w/h)*114<=150:
                            newImage=newImage.scaledToHeight(132,QtCore.Qt.SmoothTransformation)
                            w,h=newImage.width(),newImage.height()
                        else:
                            newImage=newImage.scaledToWidth(150,QtCore.Qt.SmoothTransformation)
                            w,h=newImage.width(),newImage.height()
                            
                    painter.setFont(font)
                    painter.drawPixmap((150-w)/2,(132-h)/2, newImage);
                    painter.drawText(QtCore.QPoint((150-true_len*9)/2,146), text );
                    

               
                self.inter.append(ImageResult)                      #On a une liste pour chaque type d objet #
            self.image.append(self.inter)

    def add_new_element(self,k,item):
        """Cette fonction est appele lorsque l utilisateur double clique sur un item pour l ajouter 
        Input : k : indice de la feuille Excel du type d element
              : item : Item de l ObjectList"""
     
        liste=self.piece.subWindowList(0)
        col=liste[k].widget().row(item)   #On recupere le numero de la ligne dans la feuille excel
        length=0
        instru_depth=0
        anchor_weight=0
        if self.tab_name_class[k]=="Ropes": #Si c est un cable on demande sa longueur 
            self.mooringWidget.ask_ropes_length()
            length=self.mooringWidget.current_length
            if length.toFloat()[1]==True:
                length=length.toFloat()[0]
        if self.tab_name_class[k]=="Instruments": #Si c est un instrument on demande sa profondeur
            self.mooringWidget.ask_instru_depth(k)
            if hasattr(self.mooringWidget,"instru_depth_value"):
                instru_depth=self.mooringWidget.instru_depth_value
                if instru_depth.toFloat()[1]==True:
                    instru_depth=instru_depth.toFloat()[0]
            else:
                instru_depth=0.0                    #Profondeur non precise
        if self.tab_name_class[k]=="Anchors":
            self.mooringWidget.ask_anchor_weight()  #Si c'est un lest on demande le poids
            
            
        if self.mooringWidget.insert==0:                        #Pas d insertion
            if len(self.mooringWidget.liste_element)==0:        #On demande la profondeur de la bouee de tetes
                self.mooringWidget.ask_instru_depth(0)
                instru_depth=self.mooringWidget.instru_depth_value
                if instru_depth.toFloat()[1]==True:
                    instru_depth=instru_depth.toFloat()[0]
            self.mooringWidget.liste_element.append([k,col])    #On ajoute dans les listes les informations entrees par lutilisateur
            self.mooringWidget.ropes_length.append(length)
            self.mooringWidget.clamp_ratio.append(2)            # 2 : Pas de clampage
            self.mooringWidget.instru_depth.append(instru_depth)
            self.mooringWidget.update_grid(0)                   #Mis a jour du mouillage
            
        else:                                                   #Insertion 
            if self.mooringWidget.insert_pos+1==0:              #En cas d insertion en premiere position on demande la profondeur de la bouee de tete
                self.mooringWidget.ask_instru_depth(0)
                instru_depth=self.mooringWidget.instru_depth_value
                if instru_depth.toFloat()[1]==True:
                    instru_depth=instru_depth.toFloat()[0]
            self.mooringWidget.liste_element.insert(self.mooringWidget.insert_pos+1,[k,col])
            self.mooringWidget.ropes_length.insert(self.mooringWidget.insert_pos+1,length)
            self.mooringWidget.instru_depth.insert(self.mooringWidget.insert_pos+1,instru_depth)
            self.mooringWidget.clamp_ratio.insert(self.mooringWidget.insert_pos+1,2)
            self.mooringWidget.insert=0
            self.mooringWidget.change_toolbar_label_state(0)
            self.mooringWidget.update_grid(1)
    def creer_objet(self):
        """Fonction similaire a celle de Library wind"""
        a=2
   
    def refresh_library(self):
        """Fonction similaire a celle de Library wind"""
        a=[]

        for i in range(len(self.mooringWidget.liste_element)):
            if type(self.mooringWidget.liste_element[i][0])==int:
                a.append(self.tab_object[self.mooringWidget.liste_element[i][0]][self.mooringWidget.liste_element[i][1]].name)
            else:
                a.append([self.tab_object[self.mooringWidget.liste_element[i][0][0]][self.mooringWidget.liste_element[i][0][1]].name,
                          self.tab_object[self.mooringWidget.liste_element[i][1][0]][self.mooringWidget.liste_element[i][1][1]].name])
        
        self.frameLayout2.removeWidget(self.piece)
        self.piece.close()
        self.piece=self.create_widget()
        self.frameLayout2.addWidget(self.piece)
        self.mooringWidget.liste_element=[]
        for i in range(len(a)):
            if type(a[i])==str:
                for j in range(len(self.tab_object)):
                    for k in range(len(self.tab_object[j])):
                        if self.tab_object[j][k].name==a[i]:
                            self.mooringWidget.liste_element.append([j,k])     
            else:
                temp=[]
                for l in range(len(a[i])):
                    for j in range(len(self.tab_object)):
                        for k in range(len(self.tab_object[j])):
                            if self.tab_object[j][k].name==a[i][l]:
                                temp.append([j,k])

                self.mooringWidget.liste_element.append(temp)
        
    def get_library(self,name):
        """Fonction similaire a celle de Library wind"""

        methodes = {
            "__init__": self.creer_objet
            }
        wb = xlrd.open_workbook(name)
        self.tab_name_class=wb.sheet_names()
        self.tab_class=[]
        self.tab_object=[]
        self.tab_attr=[]
        for i in range(len(self.tab_name_class)):
            class1=type(str(self.tab_name_class[i]),(),methodes)
            class1.__name__= str(self.tab_name_class[i])
            self.tab_class.append(class1)

        for i in range(len(self.tab_name_class)):
            tab_inter=[]
            a=wb.sheet_by_name(self.tab_name_class[i])
     
            for j in range(0,a.ncols):
                for k in range(1,a.nrows):
                    if str(a.col_values(j)[k])=="attribute":
                        colnum=j
                        rownum=k
            for p in range(rownum+1,a.nrows):
                tab_inter2=[]
                obj=self.tab_class[i]()
                for m in range(colnum+1,a.ncols):
                    tab_inter2.append(a.col_values(m)[rownum])
                    setattr(obj,a.col_values(m)[rownum],str(a.col_values(m)[p]))
                    
                tab_inter.append(obj)
            
            self.tab_object.append(tab_inter)
            self.tab_attr.append(tab_inter2)



