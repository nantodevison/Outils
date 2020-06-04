# -*- coding: utf-8 -*-
'''
Created on 4 mai 2020

@author: martin.schoreisz
Module comprenant les fonctions pouvant etre utilisees en décorateurs
'''

import pandas as pd

def concat_df(creer_df) :
    """
    fonction decorateur d'agregation de df creees a la vollee ayant la mme structure
    """
    def wrapper(liste) :
        for i in range(len(liste)) :
            if isinstance(liste[i],list) or isinstance(liste[i],tuple): #si 'c'est un des deux types alors on decompose la liste qui est une liste de liste (i.e liste de paramètres)
                if i==0 :
                    tot=creer_df(*liste[i])
                else :
                    tot=pd.concat([tot,creer_df(*liste[i])], axis=0,sort=False)
            else :
                if i==0 :
                    tot=creer_df(liste[i])
                else :
                    tot=pd.concat([tot,creer_df(liste[i])], axis=0,sort=False)
        return tot
    return wrapper
"""
@concat_df
def test_df(p1,p2,p3):
    liste=[[p*2,p*4, p*6] for p in [p1,p2,p3]]
    print(liste)
    return pd.DataFrame(liste, columns=['id','toto','tata'])

l=[(1,2,3),(10,20,30),(100,200,300)]
test_df(l)"""

