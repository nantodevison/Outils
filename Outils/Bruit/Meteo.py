# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2022

@author: martin.schoreisz
Module de calcul lie aux donnees meteo
'''


from Outils import checkAttributsinDf, checkParamValues
from math import  log, cos, sqrt, radians
from datetime import timedelta, datetime, time
from statistics import mean
import pandas as pd
import numpy as np
import altair as alt

#
listAttributObligatoireDfDonneesCapteur = ['vts_vent_haut', 'vit_vent_bas', 'temp_haut', 'temp_bas', 'date_heure']
dfAngle = pd.DataFrame({'angle_min':[e for e in range(0, 361, 30)][:-1], 'angle_max':[e for e in range(0, 361, 30)][1:]})
nomAttrPenteTemp = 'a_t'
nomAttrPenteVtsVent = 'a_w'
nomAttrGradVts = 'gradient_vits'
nomAttrGradTemp = 'gradient_temp'
coeffConversionCelsiusKelvin = 274.15
dicoColonneMeteoFrance = {'numer_sta': 'station',
                          'date': 'date_3heures',
                          'dd': 'dir_vent_moy_10min',
                          'ff': 'vit_vent_moy_10min',
                          't': 'temperature_k',
                          'u': 'hygrometrie',
                          'n': 'nebulosite',
                          'nbas': 'nebulosite_nuage_inferieur',
                          'rr1': 'pluie_derniere_heure',
                          'rr3': 'pluie_3_dernieres_heures',
                          'rr6': 'pluie_6_dernieres_heures',
                          'rr12': 'pluie_12_dernieres_heures',
                          'rr24': 'pluie_24_dernieres_heures',}
numStationMerignac = 7510
listeColonnesMeteoFrance = [0, 1, 5, 6, 7, 9, 14, 15, 38, 39, 40, 41, 42]
conditionQualitativeVentFort = [3, 999]
conditionQualitativeVentMoyen = [1, 3]
conditionQualitativeVentFaible = [0, 1]
conditionQualitativeRayonnementFort = [400, 1000000]
conditionQualitativeRayonnementMoyen = [40, 400]
conditionQualitativeRayonnementFaible = [0, 40]
conditionQualitativeCouvNuageuseNuageux = [3, 9.01]
conditionQualitativeCouvNuageuseDegage = [0, 2.99]
dicoSecteurAngulaire = {'portant': ((330, 360.01), (0, 30)),
                        'peu portant': ((30, 70), (290, 330)),
                        'travers': ((70, 110), (250, 290)),
                        'peu contraire': ((110, 150), (210, 250)),
                        'contraire': ((150, 210), )}


def calculCategorieVentQualitatif(angleSourceRecepteur, angleVent):
    """
    calculer les conditions aérodynamiques selon la méthode qualitative
    angle source réceptuer : integer, angle entre le  source et le recepeteur, en degré dans un repère avec 0 au Nord
    angle source réceptuer : integer, orientation du vent, en dégré, dans un repère avec 0 au Nord
    vitesseVent : integer : en m/s
    """
    if not (0 <= angleSourceRecepteur <=360) or not (0 <= angleVent <=360):
        raise ValueError(f"la valeur de d'angle de source recepteur {angleSourceRecepteur} et / ou de vent {angleVent} doit ête telle que 0 <= angle <= 360")
    angleAbsolu = abs(angleSourceRecepteur - angleVent)
    for k, v in dicoSecteurAngulaire.items():
        if any(c[0] <= angleAbsolu < c[1] for c in v): 
            return k
    return


def calculForceVentQualitatif(vitesseVent):
    """
    renvoyer le type de vitesse du vent en fonction d'uen valeur
    vitesseVent : float en m/s
    """
    if conditionQualitativeVentFaible[0] <= vitesseVent < conditionQualitativeVentFaible[1]:
        return 'faible'
    elif conditionQualitativeVentMoyen[0] <= vitesseVent < conditionQualitativeVentMoyen[1]:
        return 'moyen'
    elif conditionQualitativeVentFort[0] <= vitesseVent < conditionQualitativeVentFort[1]:
        return 'fort'
    else:
        raise ValueError("la valeur de vitesse de vent doit etre compise entre 0 et 999 m/s")


def calculForceRayonnementQualitatif(Rayonnement):
    """
    vitesseVent : float en m/s
    """
    if conditionQualitativeRayonnementFaible[0] <= Rayonnement < conditionQualitativeRayonnementFaible[1]:
        return 'faible'
    elif conditionQualitativeRayonnementMoyen[0] <= Rayonnement < conditionQualitativeRayonnementMoyen[1]:
        return 'moyen'
    elif conditionQualitativeRayonnementFort[0] <= Rayonnement < conditionQualitativeRayonnementFort[1]:
        return 'fort'
    else:
        raise ValueError("la valeur de vitesse de rayoonement doit etre compise entre 0 et 999999")
    
def calculCouvNuageuseQualitatif(CouvNuageuse):
    """
    CouvNuageuse : float ou int en octa
    """
    if conditionQualitativeCouvNuageuseDegage[0] <= CouvNuageuse < conditionQualitativeCouvNuageuseDegage[1]:
        return 'degage'
    elif conditionQualitativeCouvNuageuseNuageux[0] <= CouvNuageuse < conditionQualitativeCouvNuageuseNuageux[1]:
        return 'nuageux'
    else:
        raise ValueError("la valeur de couverture nuageuse doit etre compise entre 0 et 9 octa")
    
    
def calculPeriodeQualitatif(heureLeverSoleil, heureCoucherSoleil, heure):
    """
    fournir le type de période selon l'heure de considérée
    in:
        heureLeverSoleil : datetime.datetime sur 24h
        heureCoucherSoleil : datetime.datetime sur 24h
        heure : datetime.datetime sur 24h
    """
    if heure <= heureLeverSoleil - timedelta(hours=1) or (heure >= heureCoucherSoleil + timedelta(hours=1)):
        return 'nuit'
    elif heure >= heureLeverSoleil + timedelta(hours=1) and (heure <= heureCoucherSoleil - timedelta(hours=1)):
        return 'jour'
    elif heureLeverSoleil - timedelta(hours=1) < heure < heureLeverSoleil - timedelta(hours=1):
        return 'aube'
    else:
        return 'crepuscule'
    
    
def calculConditionPropagationMeteoFranceQualitatif(dfMeteoFrance, angleSourceRecepteur, tupleLeverSoleil, tupleCoucherSoleil):
    """
    creer les attributsde propagatiçon qualitatif sur une df issue de 
    https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=90&id_rubrique=32
    renvoi une nouvelle df
    in : 
        dfMeteoFrance : datafranme qui doit contenir les attributs de dicoColonneMeteoFrance
        angleSourceRecepteur : integer : angle entre la source et le receptuer, dans un repere avec 0 au Nord
        tupleLeverSoleil : tuple de 2 integer représentant les heures et minutes de lever de soleil
        tupleCoucherSoleil : tuple de 2 integer représentant les heures et minutes de coucher de soleil
    """
    checkAttributsinDf(dfMeteoFrance, [c for c in dicoColonneMeteoFrance.values()] + ['vitesseHauteurPerso'])
    dfMeteoFranceAttr = dfMeteoFrance.assign(
    forceVent=dfMeteoFrance.vitesseHauteurPerso.apply(lambda x: calculForceVentQualitatif(x)),
    categorieVent=dfMeteoFrance.dir_vent_moy_10min.apply(lambda x: calculCategorieVentQualitatif(angleSourceRecepteur, x)),
    typeSol=dfMeteoFrance.pluie_24_dernieres_heures.apply(lambda x: 'humide' if x > 4 else 'sec'),
    typeRayonnement=dfMeteoFrance.nebulosite_nuage_inferieur.apply(lambda x: 'moyen' if x >= 3 else 'fort'),
    typeNuage=dfMeteoFrance.nebulosite_nuage_inferieur.apply(lambda x: calculCouvNuageuseQualitatif(x) if not
                                                             pd.isnull(x) else 'degage'),
    periode=dfMeteoFrance.date_3heures.apply(lambda x: calculPeriodeQualitatif(datetime.combine(x.date(), time(*tupleLeverSoleil)),
                                                                               datetime.combine(x.date(), time(*tupleCoucherSoleil)),
                                                                               x)))
    dfMeteoFranceAttr = dfMeteoFranceAttr.assign(
        Ui=dfMeteoFranceAttr.apply(
            lambda x: DonneesMeteoQualitatif(x.forceVent, x.categorieVent, x.typeSol, x.typeRayonnement, x.typeNuage, x.periode).Ui, axis=1),
        Ti=dfMeteoFranceAttr.apply(
            lambda x: DonneesMeteoQualitatif(x.forceVent, x.categorieVent, x.typeSol, x.typeRayonnement, x.typeNuage, x.periode).Ti, axis=1),
        ConditionPropagation=dfMeteoFranceAttr.apply(
            lambda x: DonneesMeteoQualitatif(x.forceVent, x.categorieVent, x.typeSol, x.typeRayonnement, x.typeNuage, x.periode).UiTi, axis=1))
    return dfMeteoFranceAttr


def correctionVitesseVentMeteoFrance(vitesse10m, hauteurCible, z0=0.01):
    """
    correction de la vitesse du vent issu d'un mat météoFrance
    in : 
        vitesse10m : float, issu des données MF
        hauteurCible : integer > 0 
        z0 : float
    """
    if hauteurCible < 0:
        raise ValueError('la hauteur cible doit être supérieure ou égale à 0')
    return vitesse10m * ((log(hauteurCible/z0))/(log(10/z0)))


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
            return "defavorable"
        elif gradientCeleriteSon > 0.015:
            return "favorable"
        else:
            return "homogene"
    elif hauteur > 8:
        if gradientCeleriteSon < -0.007:
            return "defavorable"
        elif gradientCeleriteSon > 0.007:
            return "favorable"
        else:
            return "homogene"
    else:
        if gradientCeleriteSon < -0.01:
            return "defavorable"
        elif gradientCeleriteSon > 0.01:
            return "favorable"
        else:
            return "homogene"
        
        
def forcePropagation(gradientCeleriteSon, seuilFaible=0.2, seuilMoyen=0.4):
    """
    remplacer la valeur numérique 'un gradeint par une valeur textuelle
    in : 
        gradientCeleriteSon : float : le gradeint calculé,
        seuilFaible : float : le seuil maxi en dessous duquel la force de propagation est jugée faible. default = 0.2
        seuilMoyen : float : le seuil maxi en dessous duquel la force de propagation est jugée moyenne (avec un seuil bas la valeur de seuilFaible
                             .default = 0.4
    out :
        valTest : float : valeur absolue du gradient de célérité
        : string parmi 'faible', 'moyenne', 'forte'
    """ 
    valTest = abs(gradientCeleriteSon)  
    if valTest <= 0.2: 
        return valTest, 'faible'
    elif 0.2 < valTest <= 0.4:
        return valTest, 'moyenne'
    else:
        return valTest, 'forte'


class DonneesMeteoQualitatif:
    """
    qualification des conditions de propagations du son selon des critères qualitatif
    """


    def __init__(self, typeVent, categorieVent, typeSol, typeRayonnement, typeNuage, periode):
        """
        attributs: 
            typeVent : string parmi 'fort', 'moyen', 'faible'
            categorieVent : string parmi 'contraire', 'peu contraire', 'travers', 'peu portant', 'portant'
            typeSol : tsring parmi 'humide' ou 'sec'
            typeRayonnement : string parmi 'fort', 'moyen', 'faible'
            typeNuage : string parmi nuageux, dégagé
            periode : string parmi 'jour', 'nuit'
        """
        checkParamValues(typeVent, ['fort', 'moyen', 'faible'])
        checkParamValues(categorieVent, ['contraire', 'peu contraire', 'travers', 'peu portant', 'portant'])
        checkParamValues(typeSol, ['humide', 'sec'])
        checkParamValues(typeRayonnement, ['fort', 'moyen', 'faible'])
        checkParamValues(typeNuage, ['nuageux', 'degage'])
        checkParamValues(periode, ['jour', 'nuit', 'aube', 'crepuscule'])
        self.Ui = self.calculUi(typeVent, categorieVent)
        self.Ti = self.calculTi( periode, typeRayonnement, typeNuage, typeSol, typeVent)
        self.UiTi = self.calculUiTi(self.Ui, self.Ti)
    
    def calculUi(self, typeVent, categorieVent):
        """
        déterination des condiction aérodynamiques
        """
        if typeVent == 'fort' and categorieVent == 'contraire':
            return 'U1'
        elif (typeVent in ('fort', 'moyen') and categorieVent == 'peu contraire' or 
              typeVent == 'moyen' and categorieVent == 'peu contraire'):
            return 'U2'
        elif categorieVent == 'travers' or typeVent == 'faible':
            return 'U3'
        elif (typeVent in ('fort', 'moyen') and categorieVent == 'peu portant' or 
              typeVent == 'moyen' and categorieVent == 'portant'):
            return 'U4'
        else:
            return 'U5' 
        
        
    def calculTi(self, periode, typeRayonnement, typeNuage, typeSol, typeVent):
        """
        détermination des coditions thermiques
        """
        if periode == 'jour' : 
            if typeRayonnement == 'fort':
                if typeSol == 'sec' and typeVent in ('faible', 'moyen'):
                    return 'T1'
                elif (typeSol == 'sec' and typeVent == 'fort') or typeSol == 'humide':
                    return 'T2'
                else:
                    raise NotImplementedError(" le cas de conditions n'est pas implémenté dans la norme et le code")
            else:
                if typeSol == 'sec':
                    return 'T2'
                else:
                    if typeVent in ('faible', 'moyen'):
                        return 'T2'
                    else:
                        return 'T3'
        elif periode in ('aube', 'crepuscule'):
            return 'T3'
        else:
            if typeNuage == 'nuageux':
                return 'T4'
            else:
                if typeVent in ('moyen', 'fort'):
                    return 'T4'
                else:
                    return 'T5'
                
                
    def calculUiTi(self, Ui, Ti):
        """
        detremination des conditions de propagation
        """
        checkParamValues(Ui, ['U1', 'U2', 'U3', 'U4', 'U5'])
        checkParamValues(Ti, ['T1', 'T2', 'T3', 'T4', 'T5'])
        if (Ui == 'U2' and Ti == 'T1') or (Ui == 'U1' and Ti == 'T2'):
            return 'defavorable'
        elif (Ti == 'T1') or (Ui == 'U1') or (Ui == 'U2' and Ti in ('T2, T3')) or (Ui == 'U3' and Ti in ('T1, T2')):
            return 'defavorable'
        elif (Ui == 'U4' and Ti == 'T2') or (Ui == 'U3' and Ti == 'T3') or (Ui == 'U2' and Ti == 'T4'):
            return 'homogene'
        elif (Ti == 'T3') or (Ui == 'U3') or (Ui == 'U5' and Ti in ('T2, T3')) or (Ui == 'U3' and Ti in ('T4, T5')):
            return 'favorable'
        else:
            return 'favorable'
        
 
def graphCompTempMesureeHautBas(dfMeteo, largeur=500, hauteur=300): 
    """
    produire un graph avec slider de choix de adte permettant de visualiser les tempértaure haute et basse d'un mât
    in : 
        dfMeteo
    """      
    checkAttributsinDf(dfMeteo, ['temp_bas', 'temp_haut', 'date_heure'])
    dfMeteoCompTemp = dfMeteo.assign(jour=dfMeteo.date_heure.dt.dayofyear,
                                     heure_minute=dfMeteo.date_heure.apply(lambda x: f"{x.strftime('%H:%M')}"))
    titre = alt.TitleParams(["Température selon le point de mesure", "et l'heure de la journée"],
                            align='center', anchor='middle', fontSize=20)
    slider = alt.binding_range(min=80, max=109, step=1)
    select_day = alt.selection_single(name="jour", fields=['jour'],
                                      bind=slider, init={'jour': 80})
    return (alt.Chart(dfMeteoCompTemp, width=largeur, height=hauteur, title=titre).transform_fold(
                ['temp_bas', 'temp_haut']).mark_line().encode(
                x=alt.X('heure_minute', title='Heure', axis=alt.Axis(labelOverlap=True)),
                y=alt.Y('value:Q', scale=alt.Scale(zero=False), title='Température (°C)', ),
                color=alt.Color('key:N', legend=alt.Legend(title=None, orient="top-left")))
                 .add_selection(select_day)
                 .transform_filter(select_day)
                 .configure_legend(titleFontSize=13, labelFontSize=12)
                 .configure_axis(labelFontSize=13, titleFontSize=12)) 
    

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
        hauteurEval : hauteur d'évaluation du gradient de célérité du son
    """
    
    def __init__(self, dfCapteurs, hauteurBas, hauteurHaut, pasAgregTemporel, dateHeureDeb, hauteurEval):
        """
        vérfication initiale des données
        """
        checkAttributsinDf(dfCapteurs, listAttributObligatoireDfDonneesCapteur)
        self.dfCapteurs = dfCapteurs
        self.hauteurBas = hauteurBas
        self.hauteurHaut = hauteurHaut
        self.pasAgregTemporel = pasAgregTemporel
        self.dateHeureDeb = dateHeureDeb
        self.hauteurEval = hauteurEval
        self.ajoutTempKelvin(self.dfCapteurs)
        self.dfPente = self.calculPente(self.moyennerTemporelDfCapteur())
        self.dfGradient = self.calculGradient(self.dfPente, self.hauteurEval)
        self.dfAngleGradient = self.analyseAngulaire(self.dfGradient)
        self.dfAngleGradient['ConditionPropagation'] = self.dfAngleGradient.grad_moy.apply(lambda x: conditionPropagation(x, hauteur=self.hauteurEval))
        
        
        
    def ajoutTempKelvin(self, df):
        df['temp_haut_k'] = df['temp_haut'] + coeffConversionCelsiusKelvin
        df['temp_bas_k'] = df['temp_bas'] + coeffConversionCelsiusKelvin
        return
        
        
    def moyennerTemporelDfCapteur(self):
        """
        agregation temporalle des donnees sources
        """ 
        return self.dfCapteurs.set_index('date_heure').resample(
            f'{self.pasAgregTemporel}T', origin=self.dateHeureDeb).agg(
                {'vts_vent_haut': 'mean', 'vit_vent_bas': 'mean', 'temp_haut': 'mean', 'temp_bas': 'mean', 'temp_haut_k': 'mean', 
                 'temp_bas_k': 'mean', 'dir_vent_haut': 'mean', 'dir_vent_bas': 'mean', 'hygro_haut': 'mean', 'hygro_bas': 'mean', 'rayonnement': 'mean', 
                 'pluie': 'sum'}).reset_index()
        
    
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
    
    
    def propagationSourceRecepteurRiverain(self, dfAngleGradient, *anglesSourcesRecepteurs):
        """
        fonction permettantg de limiter le résultats de dfAngleGradient seloj les angles sources recepteurs spécifiés.
        ATTENTION : le sens du mot "favaorable et défavorbale est inversé : on est du pount de vue Riverains : favorable à la 
        propagation = défavorable au riverain
        in : 
            dfAngleGradient : df issue de analyseAngulaire()
            AnglesSourcesRecepteurs : integers : les angles sources recepteurs à considérer
        out : 
            dfMeteo : df issue de dfAngleGradient ne conservant que les lignes avec un angle de propagation compris danns anglesSourcesRecepteurs
                      et ne fournissant que le gradient de célérité du son le plus élevé entre les possibles plusieusr valeurs
        """
        if len(anglesSourcesRecepteurs) == 1 :
            dfAnglesOrienteRecepteurs = dfAngleGradient.loc[
                (dfAngleGradient.apply(lambda x: x.angle_min <= abs(x.dir_vent_haut - anglesSourcesRecepteurs[0]) <= x.angle_max, axis=1))
                                                            ].copy().replace({'ConditionPropagation': 
                                                                              {'favorable': 'defavorable', 'defavorable': 'favorable'}})
        elif len(anglesSourcesRecepteurs) == 2 : 
            dfAnglesOrienteRecepteurs = dfAngleGradient.loc[
                (dfAngleGradient.apply(lambda x: x.angle_min <= abs(x.dir_vent_haut - anglesSourcesRecepteurs[0]) <= x.angle_max, axis=1)) |
                (dfAngleGradient.apply(lambda x: x.angle_min <= abs(x.dir_vent_haut - anglesSourcesRecepteurs[1]) <= x.angle_max, axis=1))
                                                            ].copy().replace({'ConditionPropagation': 
                                                                              {'favorable': 'defavorable', 'defavorable': 'favorable'}})
        else : 
            raise NotImplementedError("le nombre d'angle maxi pris en charge par le code est 2")
        dfMeteo = dfAnglesOrienteRecepteurs.loc[dfAnglesOrienteRecepteurs.grad_moy == dfAnglesOrienteRecepteurs.groupby('date_heure')['grad_moy'].
                                        transform('max')].drop_duplicates(['date_heure', 'grad_moy'])
        dfMeteo[['forcePropagation_num', 'forcePropagation_txt']] = dfMeteo.grad_moy.apply(lambda x: pd.Series(forcePropagation(x)))
        return dfMeteo
        
        