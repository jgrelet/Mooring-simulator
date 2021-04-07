#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################################
##Mooring Simulator, 2014
##Edited by Arnaud Le Fur, IFREMER
#############################################################################


from PyQt5 import QtWidgets

class myQDockWidget(QtWidgets.QDockWidget):
    '''Cette classe permet de surdefinir la fonction close '''
    
    def __init__(self,parent=None):
        '''Initialisation '''
        super(myQDockWidget, self).__init__(parent)
        
    def closeEvent(self, event):
        '''Permet de cacher la fenetre au lieu de la fermer '''
        event.ignore()
        self.hide()
