# -*- coding: utf-8 -*-
'''
Created on 2 sept. 2021

@author: martin.schoreisz
'''
import unittest
from os.path import exists
from Connexion_Transfert import ouvrirFichierParametre, ConnexionBdd


class TestConnexionBdd(unittest.TestCase):

    def testFichierParams(self):
        """
        tester que le chemain dans le code est bon
        """
        self.assertTrue(exists(r'C:\Users\martin.schoreisz\git\Outils\Outils\Martin_Perso\Id_connexions'))
        
    def testIdConnexionDansFichiersParams(self):
        """
        tester qu'un nom de connexion non pr�sent dans le fichier renvoie bien une erreur de cl�
        """
        self.assertRaises(KeyError,ouvrirFichierParametre, 'toto', 'boulot')
        
    def testConnexionsSqlAlchemyOuvertes(self):
        """
        verfier que la connexions sqlAlchemy est bien ouverte  
        """
        with ConnexionBdd('local_otv_boulot') as c:
            conn=c.sqlAlchemyConn
            self.assertFalse(conn.closed)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()