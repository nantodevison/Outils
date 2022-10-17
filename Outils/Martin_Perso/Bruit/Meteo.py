# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2022

@author: martin.schoreisz
Module de calcul lie aux donnees meteo
'''


from Outils import checkAttributsinDf, checkParamValues
from math import  log, cos, sqrt, radians
from statistics import mean
import pandas as pd
import numpy as np

listAttributObligatoireDfDonneesCapteur = ['vts_vent_haut', 'vit_vent_bas', 'temp_haut', 'temp_bas', 'date_heure']
dfAngle = pd.DataFrame({'angle_min':[e for e in range(0, 361, 30)][:-1], 'angle_max':[e for e in range(0, 361, 30)][1:]})
nomAttrPenteTemp = 'a_t'
nomAttrPenteVtsVent = 'a_w'
nomAttrGradVts = 'gradient_vits'
nomAttrGradTemp = 'gradient_temp'
coeffConversionCelsiusKelvin = 274.15


def calculGradientVitesseSon(temp, gradientTemp, gradientVitesse, angle):
    """
    calcul du gradeint de vitesse du son, à une hauteur donnée.
    in : 
        temp : float : temperature
        gradientTemp : float : gradeint de température
        gradientVitesse : float : gradient de vitesse
        angle : float : angle en degre
    """
    try:
        return (10.0407 / sqrt(temp) * gradientTemp) + (gradientVitesse * cos(radians(angle)))
    except ValueError:
        return np.nan
    
    
def conditionPropagation(gradientCeleriteSon, hauteur=3):
    checkParamValues(hauteur, [3, 6, 10])
    if hauteur <= 4.5:
        if gradientCeleriteSon < -0.015:
            return "défavorable"
        elif gradientCeleriteSon > 0.015:
            return "favorable"
        else:
            return "homogene"
    elif hauteur > 8:
        if gradientCeleriteSon < -0.007:
            return "défavorable"
        elif gradientCeleriteSon > 0.007:
            return "favorable"
        else:
            return "homogene"
    else:
        if gradientCeleriteSon < -0.01:
            return "défavorable"
        elif gradientCeleriteSon > 0.01:
            return "favorable"
        else:
            return "homogene"
    

class DonneesMeteo(object):
    """
    classe permettant le traitement des données météo. est basée sur une 
    dataframe contenant les infos fournies par les capteurs : 
    vts_vent_haut, vts_vent_bas, temp_haut, temp_bas, date_heure
    attribut : 
        dfCapteurs : dataframe de base
        dfPente : df des capteurs avec les pentes a_t et a_w
        hauteurBas : integer : hauteur des capteurs bas
        hauteurHaut : hauteur des capteurs haut
        pasAgregTemporel : integer : pas d'agregation des données mesurées en minutes
        dateHeureDeb : string : date et heure de début à prendre en comte, format YYYY-mm-dd HH:MM:SS
        a_w : pente de la variation de vitesse du vent selon la hauteur
        a_t : pente de la variation de température selon la hauteur
    """
    
    def __init__(self, dfCapteurs, hauteurBas, hauteurHaut, pasAgregTemporel, dateHeureDeb):
        """
        vérfication initiale des données
        """
        checkAttributsinDf(dfCapteurs, listAttributObligatoireDfDonneesCapteur)
        self.dfCapteurs = dfCapteurs
        self.hauteurBas = hauteurBas
        self.hauteurHaut = hauteurHaut
        self.pasAgregTemporel = pasAgregTemporel
        self.dateHeureDeb = dateHeureDeb
        self.ajoutTempKelvin(self.dfCapteurs)
        self.dfPente = self.calculPente(self.moyennerTemporelDfCapteur())
        
        
    def ajoutTempKelvin(self, df):
        df['temp_haut_k'] = df['temp_haut'] + coeffConversionCelsiusKelvin
        df['temp_bas_k'] = df['temp_bas'] + coeffConversionCelsiusKelvin
        return
        
        
    def moyennerTemporelDfCapteur(self):
        """
        agregation temporalle des donnees sources
        """ 
        return self.dfCapteurs.set_index('date_heure').resample(f'{self.pasAgregTemporel}T',
                                                                origin=self.dateHeureDeb).mean().reset_index()
        
    
    def calculPente(self, df):
        """
        calculer a_w et a_t, les pentes de la regression log linéaire de la vitesse et de la température par raport au sol 
        pour chaque occurence de la df de base.
        in : 
            df : donnees en entree, en general issu demoyennerTemporelDfCapteur
        out : 
            a_t : float : pente de la température
            a_w : float : pente de la vitesse du vent
        """
        df[nomAttrPenteVtsVent] = ((df.vts_vent_haut - df.vit_vent_bas) / (
            log(self.hauteurHaut) - log (self.hauteurBas)))
        df[nomAttrPenteTemp] = ((df.temp_haut_k - df.temp_bas_k) / (
            log(self.hauteurHaut) - log (self.hauteurBas)))
        return df
        
        
    def calculGradient(self, df, hauteurCalcul):
        """
        à partir du calcul des pentes, calculer les gradients à une hauteur données.Modification 'sur place' de la Df en entrée
        in : 
            df : donnees en entree, en general issu demoyennerTemporelDfCapteur. Doit contenir les attributs a_t et a_w
            hauteurCalcul : hauteur à laquelle sont déterminé les conditions de propagation
        """
        df = df.copy()
        checkAttributsinDf(df, [nomAttrPenteVtsVent, nomAttrPenteTemp])
        df[nomAttrGradVts] = df[nomAttrPenteVtsVent] / hauteurCalcul
        df[nomAttrGradTemp] = df[nomAttrPenteTemp] / hauteurCalcul
        return df
    
    
    def analyseAngulaire(self, dfGradient):
        """
        pour chaque secteur angulaire, fournir le gradient de célérité du son.
        modif sur place
        in : 
           dfGradient : dataframe issue de  calculGradient
        """
        checkAttributsinDf(dfGradient, listAttributObligatoireDfDonneesCapteur + 
                           [nomAttrGradVts, nomAttrGradTemp])
        dfAngleGradient = dfGradient.merge(dfAngle, how='cross')
        dfAngleGradient['grad_min'] = dfAngleGradient.apply(lambda x: calculGradientVitesseSon(x.temp_bas_k, x[nomAttrGradTemp], 
                                                                                 x[nomAttrGradVts], x.angle_min), axis=1)
        dfAngleGradient['grad_max'] = dfAngleGradient.apply(lambda x: calculGradientVitesseSon(x.temp_haut_k, x[nomAttrGradTemp], 
                                                                                     x[nomAttrGradVts], x.angle_max), axis=1)
        dfAngleGradient['grad_moy'] = dfAngleGradient.apply(lambda x: calculGradientVitesseSon(mean([x.temp_haut_k, x.temp_bas_k]),
                                                                                               x[nomAttrGradTemp],
                                                                                               x[nomAttrGradVts],
                                                                                               mean([x.angle_max, x.angle_min]))
        , axis=1)   
        return dfAngleGradient
        
        
    
        
        