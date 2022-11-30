'''
Created on 29 nov. 2022

@author: Martin
'''
import unittest
from Impots.Calcul_Impots import calculNombreDePart, Revenu


class Test(unittest.TestCase):
    
    
    def setUp(self):
        """
        cas de tests issus de https://www.service-public.fr/particuliers/vosdroits/F1419
        """
        self.cas = {'cas1': ((Revenu('2021', 30000, 1, 0).dicoImpotsRevenuParTranche, 
                             Revenu('2021', 30000, 1, 0).montantImpotRevenu,
                             Revenu('2021', 30000, 1, 0).tauxMarginalImposition),
                             ({'tranche1': 0, 'tranche2': 1742.95, 'tranche3': 1179.0},
                              2921.95, '30 %')),
                    'cas2': ((Revenu('2021', 60000, 2, 0).dicoImpotsRevenuParTranche, 
                              Revenu('2021', 60000, 2, 0).montantImpotRevenu,
                              Revenu('2021', 60000, 2, 0).tauxMarginalImposition),
                              ({'tranche1': 0, 'tranche2': 1742.95, 'tranche3': 1179.0},
                              5843.9, '30 %')),
                    'cas3': ((Revenu('2021', 60000, 2, 2).dicoImpotsRevenuParTranche, 
                              Revenu('2021', 60000, 2, 2).montantImpotRevenu,
                              Revenu('2021', 60000, 2, 2).tauxMarginalImposition),
                              ({'tranche1': 0, 'tranche2': 1075.25},
                              3225.75, '11 %')),
                    'cas4': ((Revenu('2021', 30000, 1, 2, True).dicoImpotsRevenuParTranche, 
                              Revenu('2021', 30000, 1, 2, True).montantImpotRevenu,
                              Revenu('2021', 30000, 1, 2, True).tauxMarginalImposition),
                              ({'tranche1': 0, 'tranche2': 195.25}, 488.12, '11 %'))}


    def testcalculNombreDePart(self):
        cas = ((2, 1, False, 2.5), (1, 2, False, 2), (1, 2, True, 2.5), (1, 0, False, 1))
        for p in cas:
            with self.subTest(p=p):
                self.assertEqual(calculNombreDePart(p[0], p[1], p[2]), p[3])
                
    
    def testcalculNombreDePartError(self):
        self.assertRaises(ValueError,calculNombreDePart,0,2)
        
        
    def testClasseRevenu(self):
        for k, v in self.cas.items():
            if k != 'cas5':
                for i in range(3):
                    with self.subTest(i=i):
                        self.assertEqual(v[0][i], v[1][i])
                        
                        
    def testClasseRevenuError(self):
        self.assertRaises(ValueError,Revenu,'1900', 30000, 1, 2, True)
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()