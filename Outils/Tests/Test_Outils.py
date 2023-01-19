'''
Created on 5 oct. 2021

@author: martin.schoreisz
'''
import unittest
import pandas as pd
from Outils.Outils import checkAttributsinDf, checkAttributValues, checkValuesInAttribut


class TestOutils(unittest.TestCase):


    def test_checkAttributsinDf_str(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertTrue(checkAttributsinDf(df, 'tata'))
        
        
    def test_checkAttributsinDf_strList(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertTrue(checkAttributsinDf(df, ['toto', 'tata']))
        
        
    def test_checkAttributsinDf_ListAttrNotIn(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertRaises(AttributeError, checkAttributsinDf, df, ['titi', 'tutu'])   
        
        
    def test_checkAttributsinDf_AttrNotIn(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertRaises(AttributeError, checkAttributsinDf, df, 'titi') 
        
        
    def test_checkAttributsinDf_TypeAttrFail(self):
        df=pd.DataFrame({'toto':[1,2,3], 'tata':[1,2,3]})
        self.assertRaises(TypeError, checkAttributsinDf, df, 123)
        
        
    def test_checkAttributValues_ok(self):
        df=pd.DataFrame({'attr':['toto', 'tata']})
        self.assertTrue(checkAttributValues(df, 'attr', 'toto', 'tata'))
        
        
    def test_checkAttributValues_ko(self):
        df=pd.DataFrame({'attr':['toto', 'tata']})
        self.assertRaises(ValueError,checkAttributValues,df, 'attr', 'titi', 'tata')


    def test_checkValuesInAttribut_ok(self):
        df=pd.DataFrame({'attr':['toto', 'tata']})
        self.assertTrue(checkAttributValues(df, 'attr', 'toto', 'tata'))
        
        
    def test_checkValuesInAttribut_ko(self):
        df=pd.DataFrame({'attr':['toto', 'tata']})
        self.assertRaises(ValueError,checkAttributValues,df, 'attr', 'titi', 'tata')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()