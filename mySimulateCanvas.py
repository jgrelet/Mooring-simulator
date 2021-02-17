#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################################
##Mooring Simulator, 2014
##Edited by Arnaud Le Fur, IFREMER
#############################################################################

from PyQt4 import QtGui
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pylab as plt

class MySimulateCanvas(FigureCanvas):
    """Cette classe permet dune part de recuperer dans un QWidget un graphe global de type Matplotlib contenant les quatres graphiques
        et dautre part denregistrer les 4 images correspondants a chaque graphique"""
    def __init__(self, x, y, backup, T_max, T, old_depth, V_chute, release_ind, instru_name, x_instru, y_instru, path, parent=None, width=2, height=6, dpi=100):
        """Initialisation
        Input : x : vecteur abscisse ( evitement )
                y : vecteur profondeur
                backup : vecteur backup
                T_max : vecteur Tension max
                T : vecteur temps
                old_depth : vecteur profondeur non discretise
                V_chute : vecteur vitesse de chute
                release_ind : indice du largueur discretise
                instru_name : nom  instruments
                x_instru : evitement instruments
                y_instru : profondeur instruments
                path : chemin de sauvegarde
                parent : widget parent
                """
        
        fig = Figure(figsize=(width, height), dpi=dpi)
        #On met le bon chemin
        path=path.replace('\\','\\\\')
        
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        #Definition des axes pour les 4 subplots
        self.axes1=fig.add_subplot(141)
        self.axes1.tick_params(axis='both', which='major', labelsize=10)
        self.axes1.tick_params(axis='both', which='minor', labelsize=8)
        
        self.axes2=fig.add_subplot(142)
        self.axes2.tick_params(axis='both', which='major', labelsize=10)
        self.axes2.tick_params(axis='both', which='minor', labelsize=8)
        
        self.axes3=fig.add_subplot(143)
        self.axes3.tick_params(axis='both', which='major', labelsize=10)
        self.axes3.tick_params(axis='both', which='minor', labelsize=8)
        
        self.axes4=fig.add_subplot(144)
        self.axes4.tick_params(axis='both', which='major', labelsize=10)
        self.axes4.tick_params(axis='both', which='minor', labelsize=8)
        
        #Definition du profil du mouillage#
        #version plt pour sauvegarde#
        plt.figure(figsize=(4, 8))
        plt.plot(x, y, x_instru, y_instru, 'ro')    #plot du profil + point pour intrument
        plt.xlabel("Dx (m)")
        plt.ylabel("Depth(m)")
        plt.title("Mooring Profile")
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tick_params(axis='both', which='minor', labelsize=7)
        plt.grid(True)
        #version axes pour subplot#
        self.axes1.plot(x, y, x_instru, y_instru, 'ro')
        self.axes1.set_xlabel("Dx (m)")
        self.axes1.set_ylabel("Depth(m)")
        self.axes1.set_title("Mooring Profile" )
        self.axes1.grid(True)
        y_prec=10e10
        for i in range(len(x_instru)):     #on rajoute le nom des instrument
            x1=x_instru[i]+0.1*max(x)
            y1=y_instru[i]-0.01*(y[0]-y[-1])
            if (x1>0.7*max(x)):            #si on a pas de place a droite de la ligne pour le nom, celui ci est place a gauche
                x1=x1-0.6*max(x)
            if (abs(y1-y_prec)/(y[0]-y[-1]))<4./200:
                y1=y_prec-(4./200)*(y[0]-y[-1])  #si les instruments sont trop serre, il y a un petit offset pour eviter un chevauchement des nom
            y_prec=y1
            self.axes1.text(x1,y1,instru_name[i],fontsize=8)
            plt.text(x1,y1,instru_name[i],fontsize=8)
   
        plt.savefig(path+'//Report//Pictures//Fig1.png',dpi=180,bbox_inches='tight',pad_inches=0.1)
        plt.close()
        #Definition du backup#
        #version plt pour enregistrement#
        zero=np.zeros(len(backup[1:]))
        plt.figure(figsize=(4, 8))
        plt.plot(backup[1:],y[1:release_ind],zero, y[1:release_ind]) #On sarrete aux largueurs le graphique nest pas pertinent pour le reste de la ligne
        plt.xlabel( "Buoyancy (N) ")
        plt.ylabel("Depth (m)")
        plt.title("Backup Profile")
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tick_params(axis='both', which='minor', labelsize=7)
        plt.grid(True)
        plt.savefig(path+'//Report//Pictures//Fig2.png',dpi=180,bbox_inches='tight',pad_inches=0.1)
        plt.close()
        #version axes pour subplot# 
        self.axes2.plot(backup[1:],y[1:release_ind],zero, y[1:release_ind])
        self.axes2.set_xlabel( "Buoyancy (N) ")
        self.axes2.set_ylabel("Depth (m)")
        self.axes2.set_title("Backup Profile")
        self.axes2.grid(True)
        #Definition launch tension#
        #version plt pour enregistrement#  
        plt.figure(figsize=(4, 8))
        plt.plot(T_max[:-1], old_depth[:-1])
        plt.xlabel( "Tension (N) ")
        plt.ylabel("Depth (m)")
        plt.title("Launch Tension")
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tick_params(axis='both', which='minor', labelsize=7)
        plt.grid(True)
        plt.savefig(path+'//Report//Pictures//Fig3.png',dpi=180,bbox_inches='tight',pad_inches=0.1)
        plt.close()
        #version axes pour subplot#
        self.axes3.plot(T_max[:-1], old_depth[:-1])
        self.axes3.set_xlabel( "Tension (N) ")
        self.axes3.set_ylabel("Depth (m)")
        self.axes3.set_title("Launch Tension")
        self.axes3.grid(True)
        #Definition vitesse de chute#
        #version plt pour enregistrement#
        plt.figure(figsize=(4, 8))
        plt.plot(T, V_chute)
        plt.xlabel("Time (s)")
        plt.ylabel("Speed (m.s- 1)")
        plt.title("Launch Speed Profile")
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tick_params(axis='both', which='minor', labelsize=7)
        plt.grid(True)
        plt.savefig(path+'//Report//Pictures//Fig4.png',dpi=180,bbox_inches='tight',pad_inches=0.1)
        plt.close()
        #version axes pour subplot#    
        self.axes4.plot(T, V_chute)
        self.axes4.set_xlabel("Time (s)")
        self.axes4.set_ylabel("Speed (m.s- 1)")
        self.axes4.set_title("Launch Speed Profile")
        self.axes4.grid(True)

        fig.subplots_adjust( left  = 0.1,  right = 0.95, bottom = 0.12,  top = 0.92,  wspace = 0.4,  hspace = 0.05  )
        
