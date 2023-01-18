# -*- coding: utf-8 -*-
'''
Created on 25 mai 2022

@author: martin.schoreisz
module de manipulation des niveaux de bruit
'''
from math import log10, sqrt
from Outils.Outils import checkParamValues, checkAttributsinDf
import pandas as pd

pRef = 20*pow(10,-6) 
sourceTypeAgregTemporalleList = ['pression', 'leq_a']


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
        return 10*log10(pow(10,l1/10)+pow(10,l2/10))


def calculLden(laeq618, laeq1822, laeq226):
    """
    calculé le Lden a partirdes niveaux moyen sur les periodes reglementaires
    """
    return 10*log10((12/24*10**(laeq618/10)) + (4/24*10**((laeq1822+5)/10)) + (4/24*10**((laeq226+10)/10)))


def calculTNI(l10, l90):
    """
    le trafic noise index
    in : 
        l10 : bruit dépassé 10 % du temps.
        l90 : bruit dépassé 90% du temp
    """
    return 4 * (l10-l90) + l90 - 30


def niveau2Pression(NiveauBruit):
    """
    transformer un niveau de pression en dB en pression en Pascal
    in : 
        NiveauBruit : reel positif
    out : 
        pression : reel positif
    """
    return pRef*pow(10,NiveauBruit/20)

def pression2Niveau(pression):
    """
    transformer une pression efficace en pascal en niveau en db
    in : 
        pression : reel positif
    out : 
        NiveauBruit : reel positif
    """
    return 20*log10(pression/pRef)


def moyenneQuadratiquePression(iterablePression):
    """
    calculer la moyenne quadratique de pression. c'est la pression efficace moyenne
    in : 
        iterablePression : numeric : iterable de pression
    out :
        moyennequadratqPression : numeric : moyenne quadratique de pression
    """ 
    return sqrt((1/len(iterablePression))*sum([pow(i, 2) for i in iterablePression]))


def agregationTemporelle(horoDateDebut, horodateFin, pasTemporelMinute, dfDonneesBrutes, sourceType, reglementaire=False):
    """
    agreger les données issue de recupDonneesAcoustiqueSiteInstru().
    in : 
        pasTemporelMinute : integer. Le pas d'agrégation temporelle des données.
        dfDonneesBrutes : dataframe.doit contenir un attribut 'pression' de type numeric décrivant la pression sonore
        sourceType : string. Parmi 'pression' ou 'leq_a' selon l'attribut deja presentdans la df source
        horoDateDebut : date ou horodate au format YYYY-mm-dd ou YYYY-mm-dd HH:MM:SS
        horodateFin : date ou horodate au format YYYY-mm-dd ou YYYY-mm-dd HH:MM:SS
        reglementaire : boolean. si true alors pasTemporelMinute est ignores pour agreges selon les periodes 6-18, 18-22, 22-6
    out : 
        dfMin : dataframe agregee avec les atributs pression et leq_a correspondants
    """
    # creation d'un index de date
    if not reglementaire:
        if pd.to_datetime(horodateFin) < pd.to_datetime(horoDateDebut):
            raise ValueError('la date de fin et antérieure à la date de début ou ce sont les mêmes')
        indexDate = pd.date_range(horoDateDebut, horodateFin, freq=f'{pasTemporelMinute}T')
    else:
        indexDate = indexPeriodesReglementaires(horoDateDebut, horodateFin)
    dfDonneesBrutesCopy = dfDonneesBrutes.copy()
    checkParamValues(sourceType, sourceTypeAgregTemporalleList)
    if sourceType == 'pression':
        checkAttributsinDf(dfDonneesBrutesCopy, 'pression')
        dfDonneesBrutesCopy['leq_a'] = dfDonneesBrutesCopy.pression.apply(lambda x: pression2Niveau(x))
    elif sourceType == 'leq_a':
        checkAttributsinDf(dfDonneesBrutesCopy, 'leq_a')
        dfDonneesBrutesCopy['pression'] = dfDonneesBrutesCopy.leq_a.apply(lambda x: niveau2Pression(x))
    # sur des périodes de X minutes
    dfMin = dfDonneesBrutesCopy.groupby(indexDate[indexDate.searchsorted(dfDonneesBrutesCopy.set_index('date_heure').index)]).agg(
        pression=pd.NamedAgg(column="pression", aggfunc=lambda x: moyenneQuadratiquePression(x)),
        leq_a=pd.NamedAgg(column="pression", aggfunc=lambda x: pression2Niveau(moyenneQuadratiquePression(x))))
    # mise en forme des donnees 6 minutes
    dfMin.index.rename('date_heure', inplace=True)
    dfMin.reset_index(inplace=True)
    return dfMin


def indexPeriodesReglementaires(horoDateDebut, horodateFin):
    """
    sortir un index des periodes reglementaires sur une période
    in :
        horoDateDebut : date ou horodate au format YYYY-mm-dd ou YYYY-mm-dd HH:MM:SS
        horodateFin : date ou horodate au format YYYY-mm-dd ou YYYY-mm-dd HH:MM:SS
    out : 
        pandas datetimeIndex par période reglementaire
    """
    if pd.to_datetime(horodateFin) <= pd.to_datetime(horoDateDebut):
        raise ValueError('la date de fin et antérieure à la date de début ou ce sont les mêmes')
    return pd.DatetimeIndex(pd.concat([pd.Series(pd.date_range(horoDateDebut, horodateFin)) +
                                                       pd.Timedelta(hours=h) for h in (6, 18, 22)]
                                                      ).sort_values().reset_index(drop=True))
    