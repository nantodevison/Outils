# -*- coding: utf-8 -*-
'''
Created on 26 oct. 2017

@author: martin.schoreisz
'''

import matplotlib #pour eviter pb rcParams
import os
import shutil
import glob
import numpy as np
import pandas as pd

def CopierFichierDepuisArborescence(dossierEntree,dossierSortie):
    """ fonction de copie en masse des fichiers au sein d'une raborescence
    en entrée : un path avec le préfixe r ou les \ doublés en \\
    """
    for root, dir, files in os.walk(dossierEntree):  #
        for file in files:
            path_file = os.path.join(root,file)
            try :
                shutil.copy2(path_file,dossierSortie)
            except :
                pass

def ListerFichierDossier(dossier,extension):
    """lister les fichier d'un dossier selon une extenssion
    en entrée : chemin du dossier avec le préfixe r ou les \ doublés en \\ 
    en entree : l'extension avec le '.'
    en sortie : listefinale : la liste des fichiers
    """
    listeCompleteFichier=glob.glob(dossier+"//*"+extension)
    listeFinale=[]
    for nomFichier in listeCompleteFichier : 
        suffixeNomFichier=os.path.split(nomFichier)[1]
        listeFinale.append(suffixeNomFichier)
    return listeFinale

def remplacementMultiple(text, dico):
    """fonction de remplacement de plusieurs caractères par d'autres
    en entrée : text : string : le texte dans lequel les remplacements s'effctuent
                dico : dictionnaire de string : dico de type {txt_a_remplacer : txt_de_remplacement, autre_txt_a_remplacer : autre_ou_mm_txt_de_remplacement,...}
    en sortie : text : le texte remplacé
    """
    for i, j in dico.iteritems():
        text = text.replace(i, j)
    return text     

def epurationNomRoute(nomRoute):
    '''
    fonction qui vire les 0 non significatif des routes
    en entree: le nom de la voie : texte
    en sortie : le nom de la voie : texte
    '''
    i,j=0,0 #initialisation compteur
    while nomRoute[i].isalpha(): #determiner le prefixe
        i+=1
    prefixe=nomRoute[:i]
    suffixe=nomRoute[i:]
    while suffixe[j]=='0': #determine le nombre de 0 non significatif
        j+=1
    suffixeTraite=suffixe[j:]
    return prefixe+suffixeTraite

def angle_entre_2_ligne(point_commun, point_ligne1, point_ligne2):
    '''
    Calcul d'angle entre 3 points
    en entree : -> list ou tuple de coordonnees des 3 points
    en sortie : -> angle float
    '''
    #creer les vecteurs
    v0=np.array(point_ligne1) - np.array(point_commun)
    v1=np.array(point_ligne2) - np.array(point_commun)
    angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
    angle_degres=np.degrees(angle) if np.degrees(angle) > 0 else abs(np.degrees(angle))
    return angle_degres

def  random_dates(start, end, n=10): 
    """
    creer des dates aleatoires
    en entree : start : string decrivant une date avec Y M D H M S
                end : string decrivant une date avec Y M D H M S
    en sortie : une date au format pandas
    """
    
    start=pd.to_datetime(start)
    end=pd.to_datetime(end)
    start_u = start.value//10**9
    end_u = end.value//10**9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')
    
    