#############################################################################
##Mooring simulator, 2014                                                ####
##Edited by Arnaud Le Fur, IFREMER                                       ####
#############################################################################

from PyQt4 import QtGui
import copy
import numpy as np
from math import cos, sin, atan, sqrt
from mySimulateCanvas import MySimulateCanvas


class Simulate_wind(QtGui.QWidget):
    """Classe contenant la fenetre de simulation """

    def __init__(self, data, parent=None):
        """initialisation, calcul et affichage des resultats de la simulation
        Input : data : Tableau reunissant toutes les donnees necessaires a la simulation
                data[0] : Liste des objets constituants le mouillage
                data[1] : Les profondeurs et valeurs de courants
                data[2] : Liste des profondeur fixe des instruments
                data[3] : Trainee induite par les elements lors de la chute du lest
                data[4] : Largeur de l ecran
                data[5] : Chemin du programme
                data[6] : Liste des ratio de clampage des instruments
                """
        super(Simulate_wind, self).__init__(parent)

        l_max = 10.  # Longueur max d un element
        count = 0
        self.release_ind = 0
        self.data = data
        self.table_match = np.zeros(len(self.data[0]))

        # Corrige la saisie de lutilisateur en cas de saisie positive du poids du lest
        if float(eval(self.data[0][-1].mass)) > 0:
            self.data[0][-1].mass = str(-1*float(eval(self.data[0][-1].mass)))

        # Calcul l inventaire des elements utilise sur la ligne
        self.inventory = self.calculate_inventory()
        # Calcul des profondeurs en statique, sans courant, ni allongement
        self.static_depth = self.calculate_static()
        # Calcul du temps, de la vitesse de chute et des tensions max lors de cette chute
        self.T, self.V_chute_t, self.T_max = self.resolve_max_Tension()
        self.percent_max_T = []
        self.weight_kg = []
        self.old_depth = []
        # Calcul du poids minimal,ideal,maximal pour le lest
        self.max_value_anchor = self.Anchor_max_value()

        #Calcul_des_tensions_max/Breaking_strenght#
        for i in range(len(self.T_max)):
            if type(self.data[0][i]) != list:
                if hasattr(self.data[0][i], "breaking_strength"):
                    self.percent_max_T.append(
                        100*self.T_max[i]/(9.81*eval(self.data[0][i].breaking_strength)))
                else:
                    self.percent_max_T.append(0.0)
                # On recupere egalement le poids de chaque element en kg
                self.weight_kg.append(eval(self.data[0][i].mass))
            else:
                if hasattr(self.data[0][i][0], "breaking_strength"):
                    self.percent_max_T.append(
                        100*self.T_max[i]/(9.81*eval(self.data[0][i][0].breaking_strength)))
                else:
                    self.percent_max_T.append(0.0)
                self.weight_kg.append(
                    eval(self.data[0][i][0].mass)+eval(self.data[0][i][1].mass))

        # On calcul la flottabilite en cas de rupture de la partie superieure en kg
        self.get_buoyancy_kg()

        # On met en place une table de correspondance entre la ligne dorigine et la ligne decoupee en troncon
        for i in range(len(self.data[0])):
            self.table_match[i] = i+count
            if type(self.data[0][i]) != list:
                if eval(self.data[0][i].length) > l_max:
                    coeff = round(eval(self.data[0][i].length)/l_max)
                    count = count+coeff-1
            else:
                if eval(self.data[0][i][0].length) > l_max:
                    coeff = round(eval(self.data[0][i][0].length)/l_max)
                    count = count+coeff-1

        i = 0
        # On decoupe les cables en troncon de longueur minimale : cable de 100m = 10 x cable de 10 m
        while i < len(self.data[0]):
            if type(self.data[0][i]) != list:
                if eval(self.data[0][i].length) > l_max:
                    #on met a jour le poids, la longueur, et la surface#
                    coeff = round(eval(self.data[0][i].length)/l_max)
                    new_length = str(eval(self.data[0][i].length)/coeff)
                    new_mass = str(eval(self.data[0][i].mass)/coeff)
                    new_projected_area = str(
                        eval(self.data[0][i].projected_area)/coeff)
                    self.data[0][i].length = new_length
                    self.data[0][i].mass = new_mass
                    self.data[0][i].projected_area = new_projected_area

                    # on ajoute le nouveau troncon en position i+1
                    for j in range(int(coeff)-1):
                        self.data[0].insert(
                            i+1, copy.deepcopy(self.data[0][i]))
                        self.data[2].insert(i+1, 0)

            else:  # Element clampes
                if eval(self.data[0][i][0].length) > l_max:
                    coeff = round(eval(self.data[0][i][0].length)/l_max)
                    new_length = str(eval(self.data[0][i][0].length)/coeff)
                    new_mass = str(eval(self.data[0][i][0].mass)/coeff)
                    new_projected_area = str(
                        eval(self.data[0][i][0].projected_area)/coeff)
                    self.data[0][i][0].length = new_length
                    self.data[0][i][0].mass = new_mass
                    self.data[0][i][0].projected_area = new_projected_area
                    count = 0
                    for j in range(int(coeff)-1):
                        self.data[0].insert(
                            i+1, copy.deepcopy(self.data[0][i][0]))
                        self.data[2].insert(i+1, 0)
                        count = count+1
            i = i+1

        self.depth = self.make_vector()  # Initialisation du vecteur profondeur
        self.current_vector(self.depth)  # Initialisation du vecteur de courant
        alpha, F, P = self.resolve()  # Resolution du systeme
        self.calculate_stretch(F)  # Calcul des allongements
        self.calculate_ratio(alpha)  # Calcul des ratios de clampage
        self.plot_figure(alpha, P, F)  # Plot des 4 graphiques de la simulation
        # Genere le tableau recapitulatif de la simulation
        self.make_table(alpha, F)

    def calculate_inventory(self):
        """Cette fonction permet de retourner un tableau contenant la liste des elements,longueurs et le nombre dutilisation
        Output : Result : Tableau contenant l inventaire"""
        inventory_name = []
        inventory_length = []
        Result = [["Name", "Length (m) / Number"]]
        #On recupere d abord tout les noms des elements#
        for i in range(len(self.data[0])):
            if type(self.data[0][i]) != list:
                if not(self.data[0][i].name) in inventory_name:
                    inventory_name.append(self.data[0][i].name)
                    inventory_length.append(0)
            else:
                if not(self.data[0][i][0].name) in inventory_name:
                    inventory_name.append(self.data[0][i][0].name)
                    inventory_length.append(0)
                if not(self.data[0][i][1].name) in inventory_name:
                    inventory_name.append(self.data[0][i][1].name)
                    inventory_length.append(0)
        #On incremente ensuite soit son nombre dutilisation soit la longueur si c est un cable#
        for i in range(len(self.data[0])):
            if type(self.data[0][i]) != list:
                ind = inventory_name.index(self.data[0][i].name)
                if self.data[0][i].__class__.__name__ == "Ropes":
                    inventory_length[ind] = inventory_length[ind] + \
                        eval(self.data[0][i].length)
                else:
                    inventory_length[ind] = inventory_length[ind]+1
            else:  # Elements clampes
                ind = inventory_name.index(self.data[0][i][0].name)
                if self.data[0][i][0].__class__.__name__ == "Ropes":
                    inventory_length[ind] = inventory_length[ind] + \
                        eval(self.data[0][i][0].length)
                else:
                    inventory_length[ind] = inventory_length[ind]+1
                ind = inventory_name.index(self.data[0][i][1].name)
                if self.data[0][i][1].__class__.__name__ == "Ropes":
                    inventory_length[ind] = inventory_length[ind] + \
                        eval(self.data[0][i][1].length)
                else:
                    inventory_length[ind] = inventory_length[ind]+1
        for i in range(len(inventory_name)):
            Result.append([inventory_name[i], inventory_length[i]])
        return Result

    def calculate_static(self):
        """Cette fonction permet de sauvegarder les longueurs d origines et retourne un vecteur avec les profondeurs(en haut de l element) 
        en statique : sans allongement ni courant
        Output : subduct : vecteur de profondeur statique"""
        subduct = [self.data[1][1][-1]+eval(self.data[0][-1].length)]
        self.original_length = []
        for b in self.data[0]:
            if type(b) != list:
                self.original_length.append(round(eval(b.length), 1))
            else:
                self.original_length.append(
                    [round(eval(b[0].length), 1), round(eval(b[1].length), 1)])

        for i in range(2, len(self.data[0])+1):

            if type(self.data[0][-i]) != list:
                subduct.insert(0, subduct[0]+eval(self.data[0][-i].length))
            else:
                subduct.insert(0, subduct[0]+eval(self.data[0][-i][0].length))
        return subduct

    def resolve_max_Tension(self):
        """Cette fonction permet de calculer la vitesse, le temps de chute et les tensions maximales lors de cette chute 
        Output : T : Vecteur temps
                V_chute_t : Vecteur vitesse de chute en fonction du temps
                T_max : Tension max pour chaque element """

        Tension = []
        T_max = []
        g = 9.81
        h = 0
        T = [0]
        t = 0.
        mass_lest = eval(self.data[0][-1].mass)
        floor_depth = abs(self.data[1][1][len(self.data[1][0])-1])
        #Calcul de la flottabilite#
        for i in range(len(self.data[0])):
            Tension.append(0)
            for j in range(i+1):
                if j == len(self.data[0]):
                    break
                else:
                    if type(self.data[0][j]) != list:
                        Tension[i] = Tension[i]+g*eval(self.data[0][j].mass)
                    else:
                        Tension[i] = Tension[i]+g * \
                            (eval(self.data[0][j][0].mass) +
                            eval(self.data[0][j][1].mass))

        # Trainee induite par les elements superieures au lest
        a = (self.data[3][-1])/(-mass_lest)
        b = g-(Tension[-2]/(-mass_lest))  # Tension au niveau du lest
        if b > 0:
            i = 0
            cond = 0
            t = 0.1
            Time = 0.
            V_chute_t = [0]
            while cond == 0:
                # Evaluation de la variation de la vitesse de chute en fonction du temps cf L.MARIE
                Time = Time+t
                T.append(Time)
                V_chute_t.append((b-a*V_chute_t[-1]**2)*t+V_chute_t[-1])
                h = h+V_chute_t[i]*t
                if h >= floor_depth:  # On touche le fond
                    cond = 1
                i = i+1

            v_chute = V_chute_t[-1]  # Vitesse en regime permanent
            for i in range(len(Tension)):
                T_max.append(0)
                # Calcul des Tensions max
                T_max[i] = (self.data[3][i]*(v_chute**2)+Tension[i])
            T_max[-1] = 0.0
            return T, V_chute_t, T_max
        else:
            QtGui.QMessageBox.warning(
                self, 'Message', "Your Anchor is too light")

    def Anchor_max_value(self):
        """Cette fonction permet de calculer quel est le poids maximal du lest qui entraine une Tension max 
        egale a la charge de rupture 
        Output : masse maximale"""
        vec_v_chute = []
        Tension = []
        g = 9.81
        #Calcul de la flottabilite#
        for i in range(len(self.data[0])):
            Tension.append(0)
            for j in range(i+1):
                if j == len(self.data[0]):
                    break
                else:
                    if type(self.data[0][j]) != list:
                        Tension[i] = Tension[i]+g*eval(self.data[0][j].mass)
                    else:
                        Tension[i] = Tension[i]+g * \
                            (eval(self.data[0][j][0].mass) +
                            eval(self.data[0][j][1].mass))
        #On evalue la vitesse de chute maximale que supporte les elements du mouillage, depend de leur charge de rupture#
        for i in range(len(self.data[0])):
            if type(self.data[0][i]) != list:
                if hasattr(self.data[0][i], "breaking_strength"):
                    v_chute = sqrt(
                        (eval(self.data[0][i].breaking_strength)*g-Tension[i])/(self.data[3][i]))
                    vec_v_chute.append(v_chute)
            else:
                if hasattr(self.data[0][i][0], "breaking_strength"):
                    v_chute = sqrt(
                        (eval(self.data[0][i][0].breaking_strength)*g-Tension[i])/(self.data[3][i]))
                    vec_v_chute.append(v_chute)

        # On prend l element qui supporte la vitesse de chute la plus petite, cas le plus defavorable
        mass_max = (Tension[-2]+self.data[3][-1]*(min(vec_v_chute))**2)/g
        return mass_max

    def get_buoyancy_kg(self):
        """Cette fonction permet de calculer la flottabilite restante en cas de sectionnement de la partie superieure en kg """
        release_ind = 0
        for i in range(len(self.data[0])):
            # On recupere l indice du largueur car ce calcule nest pas pertinent en dessous de celui-ci
            if(self.data[0][i].__class__.__name__) == "Releases":
                release_ind = i
        self.Buoyancy_kg = [self.weight_kg[release_ind]]
        for i in reversed(range(release_ind)):
            self.Buoyancy_kg.insert(0, self.Buoyancy_kg[0]+self.weight_kg[i])
        while len(self.Buoyancy_kg) != len(self.weight_kg):
            self.Buoyancy_kg.append(0.0)

    def make_vector(self):
        """Cette fonction permet de calculer la profondeur de chaque element(en son centre) 
        Output : depth : vecteur profondeur"""
        depth = [self.data[1][1][len(self.data[1][0])-1]]

        #Calcul de la profondeur en haut de l element#
        for i in range(2, len(self.data[0])+2):
            depth.insert(0, 0)
            if type(self.data[0][-i+1]) != list:
                depth[-i] = depth[-i+1]+eval(self.data[0][-i+1].length)
            else:
                depth[-i] = depth[-i+1]+eval(self.data[0][-i+1][0].length)
        depth.remove(self.data[1][1][len(self.data[1][0])-1])
        #On enleve la moitie pour obtenir la profondeur du milieu de lelement#
        for i in range(len(self.data[0])):
            if type(self.data[0][i]) != list:
                depth[i] = depth[i]-eval(self.data[0][i].length)/2
            else:
                depth[i] = depth[i]-eval(self.data[0][i][0].length)/2
        return depth

    def current_vector(self, depth):
        """Cette fonction permet dobtenir une valeur de courant par interpolation pour chaque profondeur du vecteur depth 
        Input : Vecteur profondeur
        Output : Vecteur courant """
        current_vector = []
        # On interpole lineairement, on calcul donc les coefficients k et b de la droite y=k*x+b
        for i in range(len(depth)):
            a = 0

            while(depth[i] < self.data[1][1][a]):
                a = a+1
            k = (self.data[1][0][a-1]-self.data[1][0][a]) / \
                (self.data[1][1][a-1]-self.data[1][1][a])
            b = self.data[1][0][a-1]-k*self.data[1][1][a-1]
            current_vector.append(k*depth[i]+b)

        return current_vector

    def update_depth(self, depth, alpha):
        """Cette fonction permet de mettre a jour le vecteur profondeur en fonction de l inclinaison de la ligne 
        Input : depth : vecteur profondeur d origine
                alpha : vecteur angle 
        Output : depth : vecteur profondeur mis a jour"""
        depth = [self.data[1][1][len(self.data[1][0])-1]]

        #Calcul de la profondeur en haut de l element#
        for i in range(2, len(self.data[0])+2):
            depth.insert(0, 0)
            if type(self.data[0][-i+1]) != list:
                depth[-i] = depth[-i+1] + \
                    cos(alpha[-i+1])*eval(self.data[0][-i+1].length)
            else:
                depth[-i] = depth[-i+1] + \
                    cos(alpha[-i+1])*eval(self.data[0][-i+1][0].length)
        depth.remove(self.data[1][1][len(self.data[1][0])-1])

        #Calcul de la profondeur au milieu de l element#
        for i in range(len(self.data[0])):
            if type(self.data[0][i]) != list:
                depth[i] = depth[i]-cos(alpha[i]) * \
                    eval(self.data[0][i].length)/2
            else:
                depth[i] = depth[i]-cos(alpha[i]) * \
                    eval(self.data[0][i][0].length)/2

        return depth

    def resolve(self):
        """Resolution du comportement de la ligne de mouillage 
        Output : F : Effort sur chaque element
                alpha : Inclinaison
                P : Poids en newton
        """
        alpha = []
        alpha_new = []
        Fx = []
        Fy = []
        F = []
        Tn = []
        Tt = []
        P = []
        new_depth = []
        rho = 1028
        cond = 1
        fact_convergence = 1
        it = 0
        g = 9.81
        for i in range(len(self.depth)):
            alpha.append(0)
            alpha_new.append(0)
            Fx.append(0)
            Fy.append(0)
            Tn.append(0)
            Tt.append(0)
            F.append(0)
            new_depth.append(self.depth[i])  # Vecteur initialise precedemment
            #Calculate Weight#
            if type(self.data[0][i]) != list:
                P.append(eval(self.data[0][i].mass)*g)
            else:
                inter = [eval(self.data[0][i][0].mass)*g,
                        eval(self.data[0][i][1].mass)*g]
                P.append(inter)

        while (cond == 1):  # Tant que le systeme nest pas stable
            it = it+1
            for i in range(len(alpha)):  # On met a jour la valeur de alpha
                alpha[i] = alpha_new[i]
            # On met a jour le vecteur profondeur
            new_depth = self.update_depth(new_depth, alpha)
            # On met a jour le vecteur de courant
            V = self.current_vector(new_depth)
            #On commence par la tete de mouillage#
            Tn[0] = 0.5*rho*eval(self.data[0][0].nl_drag_cf)*eval(self.data[0]
                                                                [0].projected_area)*(V[0]*cos(alpha[0]))**2  # Calcul trainee normal
            Tt[0] = 0.5*rho*eval(self.data[0][0].tl_drag_cf)*eval(self.data[0]
                                                                [0].projected_area)*(V[0]*sin(alpha[0]))**2  # Calcul trainee tangentielle
            Fx[0] = Tn[0]*cos(alpha[0])+Tt[0] * \
                sin(alpha[0])  # Resultante selon x
            Fy[0] = Tt[0]*cos(alpha[0])-Tn[0]*sin(alpha[0]) + \
                P[0]  # Resultante selon y
            alpha_new[0] = atan(Fx[0]/Fy[0])  # Angle
            F[0] = sqrt(Fx[0]**2+Fy[0]**2)  # Norme
            #On calcule element par element en partant du haut#
            for i in range(1, len(self.depth)-1):
                if type(self.data[0][i]) != list:
                    Tn[i] = 0.5*rho*eval(self.data[0][i].nl_drag_cf)*eval(
                        self.data[0][i].projected_area)*(V[i]*cos(alpha[i]))**2  # Calcul trainee normal
                    Tt[i] = 0.5*rho*eval(self.data[0][i].tl_drag_cf)*eval(self.data[0][i].projected_area)*(
                        V[i]*sin(alpha[i]))**2  # Calcul trainee tangentielle
                    Fx[i] = Tn[i]*cos(alpha[i])+Tt[i] * \
                        sin(alpha[i])+Fx[i-1]  # Resultante selon x
                    Fy[i] = Tt[i]*cos(alpha[i])-Tn[i]*sin(alpha[i]) + \
                        P[i]+Fy[i-1]  # Resultante selon y
                    alpha_new[i] = fact_convergence*atan(Fx[i]/Fy[i])  # Angle
                    F[i] = sqrt(Fx[i]**2+Fy[i]**2)  # Norme
                #ELement clampe#
                else:

                    Tn[i] = 0.5*rho*(V[i]*cos(alpha[i])**2)*(eval(self.data[0][i][0].nl_drag_cf)*eval(self.data[0][i][0].projected_area) +  # Calcul trainee normal
                                                            eval(self.data[0][i][1].nl_drag_cf)*eval(self.data[0][i][1].projected_area))

                    Tt[i] = 0.5*rho*(V[i]*sin(alpha[i])**2)*(eval(self.data[0][i][0].tl_drag_cf)*eval(self.data[0][i][0].projected_area) +  # Calcul trainee tangentielle
                                                            eval(self.data[0][i][1].tl_drag_cf)*eval(self.data[0][i][1].projected_area))

                    Fx[i] = Tn[i]*cos(alpha[i])+Tt[i] * \
                        sin(alpha[i])+Fx[i-1]  # Resultante selon x
                    Fy[i] = Tt[i]*cos(alpha[i])-Tn[i]*sin(alpha[i]) + \
                        P[i][0]+P[i][1]+Fy[i-1]  # Resultante selon y
                    alpha_new[i] = fact_convergence*atan(Fx[i]/Fy[i])  # Angle
                    F[i] = sqrt(Fx[i]**2+Fy[i]**2)  # Norme

            cond = 0

            for i in range(len(self.depth)):  # Condition d arret
                if abs(alpha[i]-alpha_new[i]) > 0.0001:
                    cond = 1
                    break

        return alpha, F, P

    def calculate_stretch(self, F):
        """Cette fonction permet de calculer l allongement dun cable en fonction de leffort qui lui est applique
        Input : F : Effort subit par le cable """
        new_stretch = 0
        self.percent_stretch = []
        for i in range(len(self.data[0])):
            new_stretch = 0
            if type(self.data[0][i]) != list:
                if self.data[0][i].__class__.__name__ == "Ropes":
                    # On calcule  le pourcentage de la charge de rupture qui est applique au cable
                    ratio = 100/9.81 * \
                        (F[i]/eval(self.data[0][i].breaking_strength))
                    new_stretch = (round(eval(self.data[0][i].poly_1), 2)*ratio**2+round(eval(
                        self.data[0][i].poly_2), 2)*ratio+round(eval(self.data[0][i].poly_3), 2))/100
                    # En fonction des 3 coefficients polynomiales entre pour le materiau on calcul lallongement : allongement (%) = coeff1*(%Charge de rupture)^2+coeff2*(%Charge de rupture)+coeff3
                    # On met a jour la nouvelle longueur
                    self.data[0][i].length = str(
                        eval(self.data[0][i].length)*(1+new_stretch))
            #Element clampe#
            else:
                if self.data[0][i][0].__class__.__name__ == "Ropes":
                    ratio = 100/9.81 * \
                        (F[i]/eval(self.data[0][i][0].breaking_strength))
                    new_stretch = (round(eval(self.data[0][i][0].poly_1), 2)*ratio**2+round(eval(
                        self.data[0][i][0].poly_2), 2)*ratio+round(eval(self.data[0][i][0].poly_3), 2))/100
                    self.data[0][i][0].length = str(
                        eval(self.data[0][i][0].length)*(1+new_stretch))
            self.percent_stretch.append(100*new_stretch)

    def calculate_ratio(self, alpha):
        """Cette fonction permet de calculer le ratio de clampage definie par lutilisateur comme automatique 
        Input : alpha : vecteur angle d inclinaison"""

        #Calcul des coordonnees x et y en fonction de l inclinaison#
        y_float = [self.data[1][1][len(self.data[1][0])-1]]
        for i in range(len(self.data[2])):
            if type(self.data[2][i]) != list:
                if self.data[2][i] > 0:
                    self.data[2][i] = self.data[2][i]+y_float[-1]
            else:
                if self.data[2][i][1] > 0:
                    self.data[2][i][1] = self.data[2][i][1]+y_float[-1]

        x_float = [0]
        for i in range(2, len(self.data[0])+2):
            y_float.insert(0, 0)
            x_float.insert(0, 0)
            if type(self.data[0][-i+1]) != list:
                y_float[-i] = y_float[-i+1] + \
                    cos(alpha[-i+1])*eval(self.data[0][-i+1].length)
                x_float[-i] = x_float[-i+1] + \
                    sin(alpha[-i+1])*eval(self.data[0][-i+1].length)
            else:
                y_float[-i] = y_float[-i+1] + \
                    cos(alpha[-i+1])*eval(self.data[0][-i+1][0].length)
                x_float[-i] = x_float[-i+1] + \
                    sin(alpha[-i+1])*eval(self.data[0][-i+1][0].length)
        y_float.remove(self.data[1][1][len(self.data[1][0])-1])
        x_float.remove(x_float[-1])
        self.myxfloat = x_float
        self.myyfloat = y_float
        # Coordonnee x de la bouee de tete
        self.x_instru = [x_float[0] -
                        sin(alpha[0])*eval(self.data[0][0].length)/2]
        # Coordonnee y de la bouee de tete
        self.y_instru = [y_float[0] -
                        cos(alpha[0])*eval(self.data[0][0].length)/2]
        self.x_instru_top = []
        self.y_instru_top = []
        self.name_instru = [self.data[0][0].name]  # Nom de la bouee de tete
        for i in range(len(self.data[6])):
            if self.data[6][i] == 0.0:  # Ratio defini comme auto
                calc = 0
                # Si la profondeur choisi par lutilisateur est plus haut que le support de clampage
                if self.data[2][self.find_match(i)][1] > self.myyfloat[self.find_match(i)]:
                    # le ratio est fixe au minimum c est a dire 0
                    self.data[6][i] = 0
                    calc = 1
                # Si la profondeur choisi par lutilisateur est plus basse que le support de clampage
                if self.data[2][self.find_match(i)][1] < self.myyfloat[self.find_match(i+1)]:
                    # le ratio est fixe au minimum c est a dire 1
                    self.data[6][i] = 1
                    calc = 1
                if calc == 0:
                    malongueur = eval(
                        self.data[0][self.find_match(i)][0].length)
                    lon = 0
                    p = 1
                    for j in range(int(self.table_match[i])+1, int(self.table_match[i+1])):
                        malongueur = malongueur+eval(self.data[0][j].length)
                    while(self.myyfloat[self.find_match(i)+p] > self.data[2][self.find_match(i)][1]):
                        if type(self.data[0][self.find_match(i)+p-1]) != list:
                            lon = lon + \
                                eval(self.data[0]
                                    [self.find_match(i)+p-1].length)
                        else:
                            lon = lon + \
                                eval(
                                    self.data[0][self.find_match(i)+p-1][0].length)
                        p = p+1
                    ratio = ((self.myyfloat[self.find_match(i)+p-1]-self.data[2][self.find_match(i)][1])/(cos(alpha[self.find_match(i)+p-1]))
                            + 0.5*eval(self.data[0][self.find_match(i)][1].length)+lon)/malongueur
                    self.data[6][i] = ratio

                if self.data[6][i] >= 1 or self.data[6][i] <= 0:
                    QtGui.QMessageBox.warning(
                        self, 'Message', "An instrument is clamped beyond it support")

        #Calcul de la profondeur des instruments#
        for i in range(len(self.data[6])):
            if type(self.data[0][self.find_match(i)]) != list:
                if (self.data[0][self.find_match(i)]).__class__.__name__ == "Instruments":
                    self.name_instru.append(
                        self.data[0][self.find_match(i)].name)
                    self.x_instru.append(self.myxfloat[self.find_match(
                        i)]-0.5*eval(self.data[0][self.find_match(i)].length)*sin(alpha[self.find_match(i)]))
                    self.y_instru.append(self.myyfloat[self.find_match(
                        i)]-0.5*eval(self.data[0][self.find_match(i)].length)*cos(alpha[self.find_match(i)]))
                    # coordonnee x en haut de l instrument
                    self.x_instru_top.append(self.myxfloat[self.find_match(i)])
                    # coordonnee y en haut de l instrument
                    self.y_instru_top.append(self.myyfloat[self.find_match(i)])
        #Element clampe#
            else:
                if (self.data[0][self.find_match(i)][1]).__class__.__name__ == "Instruments":
                    self.name_instru.append(
                        self.data[0][self.find_match(i)][1].name)
                    malongueur = eval(
                        self.data[0][self.find_match(i)][0].length)
                    lon = eval(self.data[0][self.find_match(i)][0].length)
                    lon2 = lon
                    p = 0
                    ratio = self.data[6][i]
                    for j in range(int(self.table_match[i])+1, int(self.table_match[i+1])):
                        malongueur = malongueur+eval(self.data[0][j].length)
                    while(lon < malongueur*self.data[6][i]):
                        ratio = ratio-lon2/malongueur
                        p = p+1
                        lon = lon + \
                            eval(self.data[0]
                                [int(self.table_match[i])+p].length)
                        lon2 = eval(
                            self.data[0][int(self.table_match[i])+p].length)

                    self.x_instru.append(self.myxfloat[self.find_match(
                        i)+p]-ratio*malongueur*sin(alpha[self.find_match(i)+p]))
                    self.y_instru.append(self.myyfloat[self.find_match(
                        i)+p]-ratio*malongueur*cos(alpha[self.find_match(i)+p]))
                    self.x_instru_top.append(self.myxfloat[self.find_match(i)+p]-(ratio*malongueur-0.5*eval(
                        self.data[0][self.find_match(i)][1].length))*sin(alpha[self.find_match(i)+p]))  # coordonnee x en haut de l instrument
                    self.y_instru_top.append(self.myyfloat[self.find_match(i)+p]-(ratio*malongueur-0.5*eval(
                        self.data[0][self.find_match(i)][1].length))*cos(alpha[self.find_match(i)+p]))  # coordonnee y en haut de l instrument

    def calculate_subduction(self):
        """Cette fonction permet de calculer la subduction entrainee par le courant et les allongements 
        Output : vecteur subduct """
        subduct = []
        for i in range(len(self.static_depth)):
            subduct.append(self.static_depth[i]-self.myyfloat[i])
        return subduct

    def find_match(self, ind):
        """Cette fonction utilise la table de correspondance 
        Input : Indice sans troncon de cable
        Output : Indice avec troncon"""
        return int(self.table_match[ind])

    def resolve_backup(self, P):
        """Cette fonction permet de resoudre le backup jusqu au largueurs 
        Input : poids en newton 
        Output : backup,zero de flottabilite"""
        result2 = []
        zero = []
        for i in range(len(self.data[0])):
            if(self.data[0][i].__class__.__name__) == "Releases":
                self.release_ind = i+1

        for i in range(self.release_ind):
            result = 0
            for j in range(i, self.release_ind):
                if type(P[j]) != list:
                    result = result+P[j]
                else:
                    result = result+P[j][0]+P[j][1]
            result2.append(result)
        for i in range(len(result2)):
            zero.append(0)
        return result2, zero

    def plot_figure(self, alpha, P, F):
        """Cette fonction permet de tracer les quatres graphes 
        Input : alpha : angle d inclinaison
                : P : Poids
                F : Effort
                """

        if hasattr(self, "plot_mooring"):
            self.plot_mooring.hide()

        backup, zero = self.resolve_backup(P)

        for i in range(len(self.T_max)):
            self.old_depth.append(self.myyfloat[self.find_match(i)])

        self.groupLayout = QtGui.QVBoxLayout()
        self.scrollArea = QtGui.QScrollArea()
        self.groupLayout.addWidget(self.scrollArea)
        self.scrolledWidget = QtGui.QWidget()  # Zone de defilement verticale
        self.scrolledWidget.setMinimumWidth(self.data[4])
        self.layout = QtGui.QVBoxLayout(self.scrolledWidget)

        self.widget_graph = QtGui.QWidget(self)

        sc1 = MySimulateCanvas(self.myxfloat, self.myyfloat, backup, self.T_max, self.T,
                            self.old_depth, self.V_chute_t, self.release_ind, self.name_instru,
                            self.x_instru, self.y_instru, self.data[5], self.widget_graph)
        self.layout.addWidget(sc1)
        min_value_anchor = F[-2]/9.81  # Valeur minimale lest
        # Valeur safe lest formule visbeck runmoor
        safe_value_anchor = (1.5/9.81) * \
            (F[-2]*(cos(alpha[-2])+0.6*sin(alpha[-2])))
        self.anchor_value = [round(safe_value_anchor, 1), -1*round(
            float(self.data[0][-1].mass), 1), round(max(self.percent_max_T), 1)]
        #Affichage valeurs lest#
        self.widget_anchors = QtGui.QWidget(self)
        self.anchors_layout = QtGui.QGridLayout()
        label1 = QtGui.QLabel("Anchors's WET weight (kg)")
        label1.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 2px solid black }")
        label2 = QtGui.QLabel("Min")
        label2.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 2px solid black }")
        label3 = QtGui.QLabel("Max")
        label3.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 2px solid black }")
        label4 = QtGui.QLabel(str(round(min_value_anchor, 1)))
        label4.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 1px solid black }")
        label5 = QtGui.QLabel(str(round(self.max_value_anchor, 1)))
        label5.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 1px solid black }")
        label6 = QtGui.QLabel("Safe Anchor's weight")
        label6.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 2px solid black }")
        label7 = QtGui.QLabel("Selected Anchor's weight")
        label7.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 2px solid black }")
        label8 = QtGui.QLabel(str(self.anchor_value[0]))
        label8.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 1px solid black }")
        label9 = QtGui.QLabel(str(self.anchor_value[1]))
        # Valeur choisie < valeur recommande
        if self.anchor_value[1] < self.anchor_value[0]:
            label9.setStyleSheet(
                "QLabel { background-color : red; color : white ;border: 2px solid black }")
        else:
            label9.setStyleSheet(
                "QLabel { background-color : green; color : white;border: 1px solid black }")

        label10 = QtGui.QLabel("Max Launch Tension / Breaking Strength (%)")
        label10.setStyleSheet(
            "QLabel { background-color : white; color : black;border: 2px solid black }")
        label11 = QtGui.QLabel(str(self.anchor_value[2]))
        if round(max(self.percent_max_T), 1) > 40:  # T_max/Ultimate_load >40%
            label11.setStyleSheet(
                "QLabel { background-color : red; color : white ;border: 2px solid black }")
        else:
            label11.setStyleSheet(
                "QLabel { background-color : green; color : white;border: 1px solid black }")

        self.anchors_layout.addWidget(label2, 0, 1)
        self.anchors_layout.addWidget(label3, 0, 3)
        self.anchors_layout.addWidget(label1, 1, 0)
        self.anchors_layout.addWidget(label4, 1, 1)
        self.anchors_layout.addWidget(label5, 1, 3)
        self.anchors_layout.addWidget(label6, 0, 2)
        self.anchors_layout.addWidget(label7, 0, 4)
        self.anchors_layout.addWidget(label8, 1, 2)
        self.anchors_layout.addWidget(label9, 1, 4)
        self.anchors_layout.addWidget(label10, 2, 0)
        self.anchors_layout.addWidget(label11, 2, 1)

        self.widget_anchors.setLayout(self.anchors_layout)
        self.layout.addWidget(self.widget_anchors)

    def make_table(self, alpha, F):
        """Cette fonction permet de creer le tableau qui contient toutes les informations de la simulation
        Input : alpha : Vecteur angle d inclinaison
                F : Vecteur effort """
        name = []
        length = []
        length_stretch = []
        Tab_final = []
        self.Tab_report = []
        ind_instrum = []
        my_prof = []
        F_Kp = []
        warn = []
        count = 0
        release_ind = 0
        #Reconstitue les troncons en un seul cable#
        for i in range(len(self.table_match)):
            for j in range(i, int(self.table_match[i])-count):
                if type(self.data[0][i-1]) != list:
                    self.data[0][i-1].length = str(
                        eval(self.data[0][i-1].length)+eval(self.data[0][i].length))
                    self.data[0][i-1].mass = str(eval(self.data[0]
                                                    [i-1].mass)+eval(self.data[0][i].mass))
                    self.data[0][i-1].projected_area = str(
                        eval(self.data[0][i-1].projected_area)+eval(self.data[0][i].projected_area))
                else:
                    self.data[0][i-1][0].length = str(
                        eval(self.data[0][i-1][0].length)+eval(self.data[0][i].length))
                    self.data[0][i-1][0].mass = str(
                        eval(self.data[0][i-1][0].mass)+eval(self.data[0][i].mass))
                    self.data[0][i-1][0].projected_area = str(
                        eval(self.data[0][i-1][0].projected_area)+eval(self.data[0][i].projected_area))
                del(self.data[0][i])
                del(alpha[i])
                del(F[i])
                del(self.myxfloat[i])
                del(self.myyfloat[i])
                del(self.percent_stretch[i])
                count = count+1

        size = len(self.data[0])-1
        for i in range(len(alpha)):
            alpha[i] = alpha[i]*(180/(3.14))  # Converti radian en degre

        subduct = self.calculate_subduction()  # Calcule de la subduction

        for p in self.data[0]:
            if type(p) != list:
                name.append(p.name)
            else:
                # Recuperation des noms
                name.append(p[0].name+' '+'+'+' '+p[1].name)

        count = 0
        for i in range(len(self.data[0])):

            F_Kp.append(F[i]/9.81)  # Convertion des efforts en Kp
            if type(self.data[0][i]) != list:
                length.append(self.original_length[i])
                my_prof.append(str(round(self.myyfloat[i], 1)))
                # Detection des instruments
                if self.data[0][i].__class__.__name__ == "Instruments":
                    ind_instrum.append(i)
                    count = count+1
                if self.data[0][i].__class__.__name__ == "Releases":  # Detection du release
                    release_ind = i

                if self.data[0][i].__class__.__name__ == "Ropes":
                    length_stretch.append(str(round(eval(self.data[0][i].length), 1))+' '+'('+str(
                        round(self.percent_stretch[i], 1))+'%'+')')  # Recuperation des longueurs allongees
                else:
                    length_stretch.append('')

            #Element clampe#
            else:
                length.append(self.original_length[i][0])
                if self.data[0][i][1].__class__.__name__ == "Instruments":
                    ind_instrum.append(i)
                    my_prof.append(str(round(self.myyfloat[i], 1))+' '+'+'+' '+str(round(self.y_instru_top[count], 1))+' '+'ratio = '+str(
                        round(self.data[6][i], 2)))  # Affichage profondeur support+profondeur element clampe+clamp_ratio
                    if self.data[6][i] >= 1 or self.data[6][i] <= 0:
                        warn.append(i)
                    count = count+1
                else:
                    my_prof.append(str(round(self.myyfloat[i], 1)))
                if self.data[0][i].__class__.__name__ == "Ropes":
                    length_stretch.append(
                        self.data[0][i][0].length+' '+'('+self.percent_stretch[i]+')')
                else:
                    length_stretch.append('')

        Tab = np.zeros((size+1, 8))
        Tab[:, 0] = length
        Tab[:, 1] = F_Kp
        Tab[:, 2] = alpha
        Tab[:, 3] = self.myxfloat
        Tab[:, 4] = subduct
        Tab[:, 5] = self.Buoyancy_kg
        Tab[:, 6] = self.weight_kg
        Tab[:, 7] = self.percent_max_T

        for i in range(Tab.shape[0]):
            inter = [name[i]]  # On commence par les noms
            for j in range(1):
                inter.append(Tab[i][j])  # Longueur
            inter.append(my_prof[i])  # Profondeur
            for j in range(1, Tab.shape[1]):  # Reste du tableau
                inter.append(Tab[i][j])
            inter.append(length_stretch[i])
            Tab_final.append(inter)
        Tab_final.insert(0, ["Name", "Static Length (m)", "Depth (m)", "Tension (Kp)", "Angle (deg)",
                            "Dx (m)", "Dz (m)", "Buoy (kg)", "Weight (kg)", "Launch Tension (%)", "Length Stretched (m)"])
        tab_grid = QtGui.QGridLayout()
        inter = []
        for j in range(len(Tab_final[0])):  # Affichage du nom des categories
            label = QtGui.QLabel(Tab_final[0][j])
            label.setStyleSheet(
                "QLabel { background-color : white; color : black;border: 2px solid black }")
            tab_grid.addWidget(label, 0, j)
            inter.append(Tab_final[0][j])

        self.Tab_report.append(inter)
        for k in range(1, len(Tab_final)):
            # Affichage de chaque element sauf terminaison
            if self.data[0][k-1].__class__.__name__ != "Terminals":
                inter = []
                for l in range(len(Tab_final[k])):
                    if type(Tab_final[k][l]) != str:
                        Tab_final[k][l] = str(round(Tab_final[k][l], 1))
                    inter.append(Tab_final[k][l])
                    label = QtGui.QLabel(Tab_final[k][l])
                    # On repere en bleu ciel : la bouee de tete, les instruments, les largueurs, et le lest
                    if k-1 in ind_instrum or k == 1 or k-1 == release_ind or k == len(Tab_final)-1:
                        label.setStyleSheet(
                            "QLabel { background-color : rgb(168, 211, 255); color : black;border: 1px solid black }")
                        if k-1 in warn:  # Un instrument clampe au dela de son support
                            label.setStyleSheet(
                                "QLabel { background-color : red; color : black;border: 1px solid black }")

                    else:
                        label.setStyleSheet(
                            "QLabel { background-color : white; color : black;border: 1px solid black }")
                    tab_grid.addWidget(label, k, l)
                self.Tab_report.append(inter)
        tab_grid.setSpacing(0)

        self.layout.addLayout(tab_grid)

        self.scrollArea.setWidget(self.scrolledWidget)
        self.setLayout(self.groupLayout)
