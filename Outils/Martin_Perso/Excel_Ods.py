# -*- coding: utf-8 -*-
'''
Created on 5 sept. 2018

@author: martin.schoreisz
'''
from PyQt5.QtWidgets import QApplication #uniquemnt pour run le module
import pyexcel, sys

class Excel(object):
    '''
    classe de traitement des fichiers excel :
    ouverture / lecture
    copy
    enregistrement 
    '''


    def __init__(self, fichier):
        '''
        les parametres de init : 
        --chemin du fichier (en raw string si possible)
        --un book de pyexcel (http://docs.pyexcel.org/en/latest/tutorial.html)
        '''
        self.fichier=fichier
        self.book=pyexcel.get_book(file_name=self.fichier)
    
    def lireFeuilleParNumero(self,numeroFeuille):
        '''
        récupérer les valeur d'une feuille selon la position de celle-ci (1,2,3..). 1ere feuille = position 1
        en entree : un book de pyexcel
        en sortie : une sheet de pyexcel
        '''
        donnees=self.book.sheet_by_index(numeroFeuille-1)
        return donnees

    def lireFeuilleParNom(self,nomFeuille):
        '''
        récupérer les valeur d'une feuille selon le nom de celle-ci (
        en entree : un book de pyexcel
        en sortie :une sheet de pyexcel
        '''
        donnees=self.book.sheet_by_name(nomFeuille)
        return donnees
        
    def lireDonneesParLigneColonne(self,feuille,numLigne,numColonne):
        '''
        recupérer une valeur d'une feuille selon la ligne et la colonne (début à 1)
        en entree : une sheet de pyexcel
        en sortie : une valeur (string ou numeric ou autre)
        '''
        valeur=feuille[numLigne-1,numColonne-1]
        return valeur
     
    def lireParPositionExcel(self,feuille,position): 
        '''
        recupérer une valeur d'une feuille selon la ligne et la colonne
        en entree : une sheet de pyexcel
        en sortie : une valeur (string ou numeric ou autre)
        '''
        valeur=feuille[position]
        return valeur
    
    def enregistrerFeuille(self,feuille,fichierSortie):
        '''
        enregistrer une feuille sous
        en entree : le chemin + nom du fichier+extension a enrgistrer en raw string si possible
        '''  
        feuille.save_as(fichierSortie)
    
    def filtrerLigneVide(self,feuille):
        '''
        filtrer les lignes vides
        http://docs.pyexcel.org/en/latest/sheet.html#filter-out-some-data
        '''
        liste=[]
        i=0
        for row in feuille :
            if all(''==element for element in row) :
                liste.append(i)
            i+=1
        feuille.filter(row_indices=liste)
        return feuille
    
    def filtrerColonneVide(self,feuille):
        '''
        filtrer les lignes vides
        http://docs.pyexcel.org/en/latest/sheet.html#filter-out-some-data
        '''
        liste=[]
        i=0
        for column in feuille.columns() :
            if all(''==element for element in column) :
                liste.append(i)
            i+=1
        feuille.filter(column_indices=liste)
        return feuille
    
    def dico2Sheet(self,dico):
        '''
        transforme un dico en feuille de type pyexcel
        en entree : dico : dictionnaire
        en sortie : une feuille
        '''
        feuille=pyexcel.get_sheet(adict=dico)
        return feuille

if __name__=='__main__': #dans le cas oÃ¹ on execute le module
    app=QApplication(sys.argv)
    
    instanceExcel=Excel(r'C:\Temp_Martin\2016_global_TV_2.xls')
    feuille=instanceExcel.lireFeuilleParNumero(1)
    feuille=instanceExcel.filtrerColonneVide(feuille)
    instanceExcel.enregistrerFeuille(feuille,r'C:\Temp_Martin\2016_global_TV_XX.xls')
