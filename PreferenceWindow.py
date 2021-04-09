#############################################################################
##Moorinator, 2013                                                       ####
##Edited by Arnaud Le Fur, IFREMER                                       ####
##PreferenceWindowow.py creates the preference window and its buttons     ####
#############################################################################

from PyQt5 import QtGui, QtWidgets

class PreferenceWindow(QtWidgets.QMdiArea):
    
    def __init__(self):
        super(PreferenceWindow, self).__init__()



        
        self.wind_unit=QtWidgets.QWidget()
        
        self.grid_unit = QtWidgets.QGridLayout()
        self.grid_unit.setSpacing(1)
       
        self.wind_unit.setLayout(self.grid_unit)
       
        self.edit_unit=self.addSubWindow(self.wind_unit)
        self.edit_unit.setWindowTitle('Units')
        self.edit_unit.setWindowIcon(QtGui.QIcon('exit24.png'))
        
        
        btn2 = QtWidgets.QPushButton('Save', self)
        self.combo_unit1=QtWidgets.QComboBox()
        self.label_unit1=QtWidgets.QLabel("Length")
        self.combo_unit1.addItem("m")
        self.combo_unit1.addItem("ft")
        self.combo_unit2=QtWidgets.QComboBox()
        self.label_unit2=QtWidgets.QLabel("Mass")                      
        self.combo_unit2.addItem("kg")
        self.combo_unit2.addItem("lb")
        self.combo_unit3=QtWidgets.QComboBox()
        self.label_unit3=QtWidgets.QLabel("Strength")
        self.combo_unit3.addItem("N")
        self.combo_unit3.addItem("kp")
        self.grid_unit.addWidget(self.label_unit1,0,0)
        self.grid_unit.addWidget(self.label_unit2,1,0)
        self.grid_unit.addWidget(self.label_unit3,2,0)
        self.grid_unit.addWidget(self.combo_unit1,0,1)
        self.grid_unit.addWidget(self.combo_unit2,1,1)
        self.grid_unit.addWidget(self.combo_unit3,2,1)
        self.grid_unit.addWidget(btn2,3,1)
        btn2.clicked.connect(self.save_unit_btn)                         
        self.resize(400,201)
        self.setViewMode(1)
                
   

    def save_unit_btn(self):
        # Save all parameters chosen #
        self.unit_length_chosen=self.combo_unit1.currentIndex()
        self.unit_mass_chosen=self.combo_unit2.currentIndex()
        self.unit_strength_chosen=self.combo_unit3.currentIndex()
        QtWidgets.QMessageBox.information(self,'Message',"Parameters saved")
