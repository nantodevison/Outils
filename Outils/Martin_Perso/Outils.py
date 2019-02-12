# -*- coding: utf-8 -*-
'''
Created on 26 oct. 2017

@author: martin.schoreisz
'''

import os
import shutil
import glob

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
    print (nomRoute,i, prefixe, suffixe,j,suffixeTraite )
    return prefixe+suffixeTraite
    
    