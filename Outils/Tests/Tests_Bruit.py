'''
Created on 24 oct. 2022

@author: martin.schoreisz
'''
import unittest
from Bruit.Meteo import (calculCategorieVentQualitatif, calculForceVentQualitatif, DonneesMeteoQualitatif,
                         calculForceRayonnementQualitatif, calculCouvNuageuseQualitatif)


class TestMeteo(unittest.TestCase):


    def testCalculCategorieVentQualitatifValOK(self):
        dicoTest = {0: {270: 'travers',
                        90: 'travers',
                        70: 'travers',
                        0: 'portant',
                        330: 'portant',
                        360: 'portant',
                        30: 'peu portant',
                        315: 'peu portant',
                        120: 'peu contraire',
                        210: 'peu contraire',
                        150: 'contraire',
                        180: 'contraire'},
                    90: {270: 'contraire',
                        90: 'portant',
                        70: 'portant',
                        0: 'travers',
                        330: 'peu contraire',
                        360: 'travers',
                        30: 'peu portant',
                        315: 'peu contraire',
                        120: 'peu portant',
                        210: 'peu contraire',
                        150: 'peu portant',
                        180: 'travers'}}
        for k, v in dicoTest.items():
                for o, val in v.items():
                    with self.subTest(i=o):
                        self.assertEqual(calculCategorieVentQualitatif(k, o), val)
                        
    
    def testCalculCategorieVentQualitatifValKO(self):
        listeValeurOff = [(-1, 0), (361, 0), (0, -1), (0, 361)]
        for i in listeValeurOff:
            with self.subTest(i=i):
                self.assertRaises(ValueError, calculCategorieVentQualitatif, i[0], i[1])
                
                
    def testCalculForceVentQualitatifValOK(self):
        dicoValsOk = {0: 'faible',
                      0.5: 'faible',
                      1: 'moyen',
                      2.9: 'moyen',
                      3: 'fort',
                      998: 'fort'} 
        for k, v in dicoValsOk.items():
            with self.subTest(i=k):
                self.assertEqual(calculForceVentQualitatif(k), v)
                
                
    def testCalculForceVentQualitatifValKO(self):
        listeValeurOff = [-1, 1000]
        for i, l in enumerate(listeValeurOff):
            with self.subTest(i=i):
                self.assertRaises(ValueError, calculForceVentQualitatif, l)
                
                
    def testCalculForceRayonnementQualitatifValOK(self):
        dicoValsOk = {0: 'faible',
                      39: 'faible',
                      40: 'moyen',
                      399.999: 'moyen',
                      400: 'fort',
                      999999: 'fort'} 
        for k, v in dicoValsOk.items():
            with self.subTest(i=k):
                self.assertEqual(calculForceRayonnementQualitatif(k), v)
                
                
    def testCalculForceRayonnementQualitatifValKO(self):
        listeValeurOff = [-1, 1000000]
        for i, l in enumerate(listeValeurOff):
            with self.subTest(i=i):
                self.assertRaises(ValueError, calculForceRayonnementQualitatif, l)
                
                
    def testCalculCouvNuageuseQualitatifValOK(self):
        dicoValsOk = {0: 'degage',
                      2: 'degage',
                      3: 'nuageux',
                      9: 'nuageux'} 
        for k, v in dicoValsOk.items():
            with self.subTest(i=k):
                self.assertEqual(calculCouvNuageuseQualitatif(k), v)
                
                
    def testCalculCouvNuageuseQualitatifValKO(self):
        listeValeurOff = [-1, 10]
        for i, l in enumerate(listeValeurOff):
            with self.subTest(i=i):
                self.assertRaises(ValueError, calculCouvNuageuseQualitatif, l)  
                          
                
    def testClassDonneesMeteoQualitatifValOK(self):
        """
        a completer avec les tests complets
        """
        dicoConditions = {('fort', 'contraire', 'sec', 'fort', 'degage', 'jour'): 'defavorable',
                          ('moyen', 'travers', 'sec', 'fort', 'degage', 'jour'): 'defavorable',
                          ('fort', 'travers', 'humide', 'moyen', 'degage', 'jour'): 'homogene',
                          ('moyen', 'peu portant', 'humide', 'moyen', 'degage', 'aube'): 'favorable',
                          ('moyen', 'peu portant', 'humide', 'moyen', 'degage', 'crepuscule'): 'favorable',
                          ('fort', 'portant', 'sec', 'moyen', 'nuageux', 'jour'): 'favorable',
                          ('faible', 'portant', 'sec', 'moyen', 'degage', 'nuit'): 'favorable',
                          ('fort', 'portant', 'sec', 'moyen', 'nuageux', 'nuit'): 'favorable'}
        for i, d in enumerate(dicoConditions.items()):
            with self.subTest(i=i):
                self.assertEqual(DonneesMeteoQualitatif(*d[0]).UiTi, d[1]) 

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()