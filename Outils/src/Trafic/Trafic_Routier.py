# -*- coding: utf-8 -*-
'''
Created on 30 nov. 2022

@author: martin.schoreisz
module de representation / travail des donnees de trafic
'''


import altair as alt
from Outils.Outils import checkAttributsinDf
from datetime import datetime


def graphDebitVitesse1jour(dfDebitVitesseVoiesBddWide, jour, NomVoies, sens, largeur=390, hauteur=200): 
    """
    cr��er un graph fondamental sur les voies lente, m�diane, rapide pour un jour donn�e
    pour un compteur donn�e
    in:
        dfDebitVitesseVoiesBddWide : dataframe des trafic et d�bit, avec attributs date_heure, voie, sens, TV, Vmoy_TV
        jour : integer: dayofyear
        NomVoies liste de string  des noms de voies � consid�rer
        sens : string: nom du sens consid�r�
        largeur : larguer des charts en pixel
        hauteur : hauteur des charts en pixel
    """
    checkAttributsinDf(dfDebitVitesseVoiesBddWide, ['date_heure', 'voie', 'sens', 'TV', 'Vmoy_TV'])
    return alt.hconcat(*[(alt.Chart(dfDebitVitesseVoiesBddWide
                                     .assign(heure=dfDebitVitesseVoiesBddWide.date_heure.dt.hour)
                                     .loc[(dfDebitVitesseVoiesBddWide.date_heure.dt.dayofyear == jour) & (dfDebitVitesseVoiesBddWide['voie'] == voie) &
                                                                   (dfDebitVitesseVoiesBddWide['sens'] == sens)],
                                    title = [f"{datetime.strptime('2022' + '-' + str(jour).rjust(3, '0'), '%Y-%j').strftime('%Y-%m-%d')} - jour n�{jour}",
                                             f"Code Canal = {voie} : {sens}"],
                                   width=largeur, height=250).mark_circle(size=100).encode(
                x=alt.X('TV', title='D�bit'),
                y=alt.Y('Vmoy_TV', title='Vitesse'),
                color=alt.Color('heure:N', scale=alt.Scale(scheme='turbo'))) + 
                           alt.Chart(dfDebitVitesseVoiesBddWide.loc[(dfDebitVitesseVoiesBddWide.date_heure.dt.dayofyear == jour) 
                                                                     & (dfDebitVitesseVoiesBddWide['voie'] == voie) &
                                                                   (dfDebitVitesseVoiesBddWide['sens'] == sens)],
                                    title = [f"{datetime.strptime('2022' + '-' + str(jour).rjust(3, '0'), '%Y-%j').strftime('%Y-%m-%d')} - jour n�{jour}",
                                             f"Code Canal = {voie} : sens : inter"],
                                   width=largeur, height=250).mark_line(strokeWidth=0.5, color='gray').encode(
                x=alt.X('TV', title='D�bit'),
                y=alt.Y('Vmoy_TV', title='Vitesse'),
                order='date_heure:T')) for voie in NomVoies])
    
    
def graphDebitVitesseplusieursjour(dfDebitVitesseVoiesBddWide, listJour, NomVoies, sens, largeur=390, hauteur=200):     
    """
    cr��er un graph fondamental sur les voies lente, m�diane, rapide pour plsueiurs jour donn�e
    pour un compteur donn�e
    in:
        dfDebitVitesseVoiesBddWide : dataframe des trafic et d�bit, avec attributs date_heure, voie, sens, TV, Vmoy_TV
        listJour :  list integer: dayofyear
        NomVoies liste de string  des noms de voies � consid�rer
        sens : string: nom du sens consid�r�
        largeur : larguer des charts en pixel
        hauteur : hauteur des charts en pixel
    """
    return alt.vconcat(*[graphDebitVitesse1jour(dfDebitVitesseVoiesBddWide, j, NomVoies, sens, largeur=390, hauteur=200)
                         for j in listJour])
