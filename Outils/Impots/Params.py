# -*- coding: utf-8 -*-
'''
Created on 29 nov. 2022

@author: Martin
parametres de calcul des impots
'''
dicoBaremeProgressif = {'2021': {'tranche1': {'trancheMin': 0, 'trancheMax': 10225, 'tauxDImposition': 0},
                                 'tranche2': {'trancheMin': 10226, 'trancheMax': 26070, 'tauxDImposition': 0.11},
                                 'tranche3': {'trancheMin': 26071, 'trancheMax': 74545, 'tauxDImposition': 0.30},
                                 'tranche4': {'trancheMin': 74546, 'trancheMax': 160336, 'tauxDImposition': 0.41},
                                 'tranche5': {'trancheMin': 160336, 'trancheMax': 99999999999999, 'tauxDImposition': 0.41}}}
