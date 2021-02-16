#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################################
##Mooring Simulator, 2014
##Edited by Arnaud Le Fur, IFREMER
#############################################################################

from PyQt5 import QtGui, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyEnvironnementCanvas(FigureCanvas):
    """Cette classe permet de recuperer dans un QWidget un graph de type Matplotlib correspondant au profil de courant"""
    def __init__(self, x, y, title, xlabel, ylabel,parent=None, width=5, height=5, dpi=100):
        """Initialisation du graphique a partir des parametres dentree
        Input : x : Vecteur correspondant aux valeurs du courant
                y : Vecteur correspondant aux profondeurs
                title : Titre du graphique
                xlabel : Titre de laxe des abscisses
                ylabel : Titre de laxe des ordonnees
                parent : QWidget parent
        Output : QWidget
        """
        fig = Figure(figsize=(width, height), dpi=dpi)
        #marge a gauche, a droite, largeur, hauteur
        self.axes = fig.add_axes([0.15, 0.25, 0.8, 0.5])
        
        self.axes.hold(False)
       
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.axes.plot(x, y)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.set_title(title)
        self.axes.tick_params(axis='both', which='major', labelsize=10)
        self.axes.tick_params(axis='both', which='minor', labelsize=8)
        self.axes.grid(True)

        
