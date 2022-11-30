# -*- coding: utf-8 -*-
'''
Created on 17 fevr. 2021

@author: martin.schoreisz
Module de calcul des emissions de bruit selon la norme NFS31-133
'''

import math
import pandas as pd

def sommeEnergetique(l1,l2):
    """
    faire la somme energetique de deux niveaux de puissance
    """
    if l1 == 0 and l2 == 0:
        return 0
    elif l1 == 0 and l2 != 0:
        return l2
    elif l1 != 0 and l2 == 0:
        return l1
    else:
        return 10*math.log10(pow(10,l1/10)+pow(10,l2/10))

def testValiditeVts(vtsVl, vtsPl):
    if vtsVl<20 or vtsVl>130: 
        raise ValueError("la vitesse vl doit etre entre 20 et 130 km/h")
    if vtsPl<20 or vtsPl>100: 
        raise ValueError("la vitesse pl doit etre entre 20 et 100 km/h")  
    
def testValiditeRevt(categorieRevt):
    if categorieRevt not in ('r1', 'r2', 'r3') : 
        raise ValueError("la categorie de revetement doit etre parmi 'r1', 'r2', 'r3'")
    
def testValiditeAllure(allure):
    if allure not in ('s','a' ,'d') : 
        raise ValueError("l'allure doit etre parmi 's','a' ,'d'")
    
def testDeclivite(declivite):
    if not -6<=declivite<=6 : 
        raise ValueError('la declivite doit etre comprise entre -6 et 6')

class Route(object):
    """
    fournir les information de puissance acoustique d'u troncon acoustiquement homogene d'une route 
    """
    
    def __init__(self,debitVl, debitPl, vtsVl, vtsPl,categorieRevt='r2',ageRevt=10,allure='s',declivite=0, drainant=False):
        """
        attributs a fournir : 
            categorieRevt : string : r1 ou r2 ou r3,
            ageRevt : integer, 
            vtsVl : integer entre 20 et 130, 
            vtsPl : integer entre 20 et 100, 
            declivite : integer entre -6 et 6 ,
            debitVl : integer >0 , 
            debitPl : integer >0 ,
            allure : string  : 's' ou 'a' ou 'd' defaut='s', 
            drainant : booleen defaut=false
        attributs calcule : 
            lrwmVl : composante roulement vehicule unitaire VL
            lmwmVl : composante moteur vehicule unitaire VL
            lrwmPl : composante roulement vehicule unitaire PL
            lmwmPl : composante moteur vehicule unitaire PL
            lwmVl : emission vehicule unitaire VL
            lwmPl : emission vehicule unitaire PL
            lwVl : emission VL par metre de lignes source
            lwPl : emission PL par metre de lignes source
            lwm : emission par metre de ligne source
            dfCorrecTierOctave : df des corrections tiers d'octave pour calcul de spectre
            spectre : df de repartition spectrale (sur demande via repartitionSpectrale())
        """
        testValiditeVts(vtsVl, vtsPl)
        testValiditeRevt(categorieRevt)
        testValiditeAllure(allure)
        testDeclivite(declivite)
        self.categorieRevt,self.ageRevt, self.vtsVl, self.vtsPl = categorieRevt,ageRevt, vtsVl, vtsPl
        self.allure, self.declivite, self.drainant=allure, declivite, drainant
        self.debitVl, self.debitPl=debitVl, debitPl
        self.dfCorrecTierOctave=pd.DataFrame({'freq':sorted(2*[100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,
            3150,4000,500]),'typeRvt':['drainant','autre']*18,'correction':[-22,-27,-22,-26,-20,-24,-17,-21,-15,-19,-12,-16,-10,-14,-8,-11,-9,-11,-9,-8,-10,
            -7,-11,-8,-12,-10,-13,-13,-16,-16,-18,-18,-20,-21,-23,-23]}).set_index('freq')   
        self.calculGlobalEmission()

    def calculGlobalEmission(self):
        """
        enchainer les fonctions ci-dessous pour aboutir à la creation des attributs d'instance
        """
        self.calculLrwmVl()
        self.calculLmwmVl()
        self.calculLrwmPl()
        self.calculLmwmPl()
        self.calculLwmVl()
        self.calculLwmPl()
        self.calculLwVl()
        self.calculLwPl()
        self.calculLwm()

    def calculLrwmVl(self):
        """
        puissance d'emission par metre de ligne source pour la composante roulement des VL pour un vheicule unitaire
        """
        if self.categorieRevt=='r1' : 
            lrwmBase = 53.4+(21*math.log10(self.vtsVl/90))
            correcRevtJeune=-4 if self.ageRevt<=2 else 0.5*(self.ageRevt-10)
        elif self.categorieRevt=='r2' : 
            lrwmBase = 55.4+(20.1*math.log10(self.vtsVl/90))
            correcRevtJeune=-2 if self.ageRevt<=2 else 0.25*(self.ageRevt-10)
        else :
            lrwmBase = 57.5+(21.4*math.log10(self.vtsVl/90))
            correcRevtJeune=-1.6 if self.ageRevt<=2 else 0.2*(self.ageRevt-10)
        
        if self.ageRevt>=10 : 
            self.lrwmVl = lrwmBase
        else : 
            self.lrwmVl = lrwmBase + correcRevtJeune

    def calculLrwmPl(self):
        """
        puissance d'emission par metre de ligne source pour la composante roulement des PL pour un vheicule unitaire
        """
        if self.categorieRevt=='r1' : 
            lrwmBase = 61.5+(20*math.log10(self.vtsPl/80))
            correcRevtJeune=-2.4 if self.ageRevt<=2 else 0.3*(self.ageRevt-10)
        elif self.categorieRevt=='r2' : 
            lrwmBase = 63.4+(20*math.log10(self.vtsPl/80))
            correcRevtJeune=-1.2 if self.ageRevt<=2 else 0.15*(self.ageRevt-10)
        else :
            lrwmBase = 64.2+(20*math.log10(self.vtsPl/80))
            correcRevtJeune=-1 if self.ageRevt<=2 else 0.12*(self.ageRevt-10)
    
        if self.ageRevt>=10 : 
            self.lrwmPl = lrwmBase
        else : 
            self.lrwmPl = lrwmBase + correcRevtJeune

    def calculLmwmVl(self):
        """
        niveau de puissance de la composante moteur des VL pour un vheicule unitaire
        """
        if self.allure=='s' : 
            if 20<=self.vtsVl<=30 :
                self.lmwmVl=36.7-(10*math.log10(self.vtsVl/90))
            elif 31<=self.vtsVl<=110 : 
                self.lmwmVl=42.4+(2*math.log10(self.vtsVl/90))
            else : 
                self.lmwmVl=40.7+(21.3*math.log10(self.vtsVl/90))
        elif self.allure=='a' : 
            if 25<=self.vtsVl<=100 : 
                self.lmwmVl=46.1-(10*math.log10(self.vtsVl/90))
            else : 
                self.lmwmVl=44.3+(28.6*math.log10(self.vtsVl/90))
        else : 
            if 25<=self.vtsVl<=80 : 
                self.lmwmVl=42.1-(4.5*math.log10(self.vtsVl/90))
            elif 81<=self.vtsVl<=110 : 
                self.lmwmVl=42.4+(2*math.log10(self.vtsVl/90))
            else : 
                self.lmwmVl=40.7+(21.3*math.log10(self.vtsVl/90))

    def calculLmwmPl(self):
        """
        niveau de puissance de la composante moteur des PL pour un vheicule unitaire
        """
        if (0<=self.declivite<=2 and (self.allure== 's' or self.allure== 'd')) or (
            self.allure== 'd' and  2<self.declivite<=6) : 
            correctif=0
        elif self.allure== 'a' and ((0<=self.declivite<=2) or (-6<=self.declivite<-2)) : 
            correctif=5
        elif -6<=self.declivite<-2 and (self.allure== 's' or self.allure== 'd') : 
            correctif=1*(self.declivite-2)
        elif 2<self.declivite<=6 : 
            if self.allure== 'a' : 
                correctif=5+(max(2*(self.declivite-4.5),0))
            else : 
                correctif=2*(self.declivite-2)
        
        if 20<=self.vtsPl<=70 : 
            self.lmwmPl=49.6-(10*math.log10(self.vtsPl/80))+ correctif
        else : 
            self.lmwmPl=50.4+(3*math.log10(self.vtsPl/80))+ correctif
            
            
    def calculLwmVl(self):
        """
        calcul de la puissance d'emission VL pour un debit unitaire
        in : 
            LwMoteur : float : composante moteur
            lwRoulement : float :composante roulement
        """
        self.lwmVl = sommeEnergetique(self.lrwmVl,self.lmwmVl) 
    
    def calculLwmPl(self):
        """
        calcul de la puissance d'emission PL pour un debit unitaire
        in : 
            LwMoteur : float : composante moteur
            lwRoulement : float :composante roulement
        """
        self.lwmPl = sommeEnergetique(self.lrwmPl,self.lmwmPl) 
        
    def calculLwVl(self):
        if pd.isnull(self.debitVl) or self.debitVl == 0: 
            self.lwVl = 0
        else: 
            self.lwVl=self.lwmVl+10*math.log10(self.debitVl)
    
    def calculLwPl(self):
        if pd.isnull(self.debitPl) or self.debitPl == 0: 
            self.lwPl = 0
        else:
            self.lwPl=self.lwmPl+10*math.log10(self.debitPl)
    
    def calculLwm(self):
        """
        calcul du niveau de puissance par unite de longueur pour une route
        """
        
        self.lwm=round(sommeEnergetique(self.lwVl, self.lwPl),2)
            
    def repartitionSpectrale(self):
        if self.drainant : 
            self.spectre=self.lwm+self.dfCorrecTierOctave.loc[self.dfCorrecTierOctave.typeRvt=='drainant'].correction
        else : 
            self.spectre=self.lwm+self.dfCorrecTierOctave.loc[self.dfCorrecTierOctave.typeRvt!='drainant'].correction
        



    
    