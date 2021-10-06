'''
Created on 5 oct. 2021

@author: martin.schoreisz
'''
import unittest
import pandas as pd
import Outils as O


class TestOutils(unittest.TestCase):


    def test_checkAttributsinDf_str(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertTrue(O.checkAttributsinDf(df, 'tata'))
        
    def test_checkAttributsinDf_strList(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertTrue(O.checkAttributsinDf(df, ['toto', 'tata']))
        
    def test_checkAttributsinDf_ListAttrNotIn(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertRaises(AttributeError, O.checkAttributsinDf, df, ['titi', 'tutu'])   
        
    def test_checkAttributsinDf_AttrNotIn(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertRaises(AttributeError, O.checkAttributsinDf, df, 'titi') 
        
    def test_checkAttributsinDf_TypeAttrFail(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertRaises(TypeError, O.checkAttributsinDf, df, 123)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()