# -*- coding: utf-8 -*-
'''
Created on 25 mai 2022

@author: martin.schoreisz
module de manipulation des niveaux de bruit
'''
from math import log10

pRef = 20*pow(10,-6) 


def Niveau2Pression(NiveauBruit):
    """
    transformer un niveau de pression en dB en pression en Pascal
    in : 
        NiveauBruit : reel positif
    out : 
        pression : reel positif
    """
    return pRef*pow(10,NiveauBruit/20)

def Pression2Niveau(pression):
    """
    transformer une pression efficace en pascal en niveau en db
    in : 
        pression : reel positif
    out : 
        NiveauBruit : reel positif
    """
    return 20*log10(pression/pRef)