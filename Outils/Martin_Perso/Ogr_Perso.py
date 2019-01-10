'''
Created on 23 juil. 2018

@author: martin.schoreisz
'''
from osgeo import ogr

class DonneesShapefile(object):
    """
    classe regroupant les fonctions peremttant d'obtenir les caracteristiques d'un fichier shape
    """
    def __init__(self,fichierShape):
        """Constructeur
        cree les attributs des caracteristiques des fichiers shape
        """
        self.fichierShape=fichierShape
        self.driver = ogr.GetDriverByName("ESRI Shapefile")
        self.datasource = self.driver.Open(self.fichierShape)
        self.layer = self.datasource.GetLayer()
        self.layerDef= self.layer.GetLayerDefn()
    
    def listeAttributs(self):
        """
        liste des attributs du fichers passe en parametres de la classe
        en sortie : une liste des noms d'attributs
        """
        listeAttributs=[]
        for i in range(self.layerDef.GetFieldCount()):
            listeAttributs.append(self.layerDef.GetFieldDefn(i).GetName())
        return listeAttributs
    
    def nbAttributs(self):
        """
        compter le nombre d'attributs du fichers passe en parametres de la classe
        en sortie le nb d'attribut
        """
        nbAttributs=self.layerDef.GetFieldCount()
        return nbAttributs
    
    def creerAttribut(self,nomAttribut,typeAttribut,longueurTexte='250'):
        """
        créer un nouvel attribut.
        en entrée : le nom de l'attribut
                    le type de l'attribut. doit prendre une valeur suivante reel, texte
        """
        if typeAttribut=='reel' :
            attribut=ogr.FieldDefn(nomAttribut,ogr.OFTReal)
        elif typeAttribut=='texte' :
            attribut=ogr.FieldDefn(nomAttribut,ogr.OFTString)
            attribut.SetWidth(longueurTexte)
        else :
            print ('erreur type d\'attribut)')
        
        self.layer.CreateField(attribut)
        return   