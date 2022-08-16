# -*- coding: utf-8 -*-
'''
Created on 26 avr. 2017

@author: Martin
'''

from datetime import datetime
from sqlalchemy import create_engine
import subprocess, os
import psycopg2
import pyodbc
from osgeo import ogr
import pandas as pd
import geopandas as gp
from shapely.geometry import Point




#fonction d'ouverture du fichier de parametres
def ouvrirFichierParametre(typeParametres):
    chemin=r'C:\Users\martin.schoreisz\git\Outils\Outils\Martin_Perso\Id_connexions'
    with open(chemin,'r') as f_id :
        dicoParametres={}
        for texte in f_id :
            ligne=texte.strip().split(' ')
            dicoParametres[ligne[0]]=ligne[1:]
        if typeParametres not in dicoParametres.keys() : 
            raise KeyError(f'la valeur {typeParametres} n\'est pas présente dans le fichier d\'identifiants des connexions')
        else : 
            return (dicoParametres[typeParametres])
 
def Ogr2ogr_pg2shp(connstringOgr,fichierShape, requeteSql,reprojection=''):
        """
        fonction d'export de postgres vers du shape
        en entree : 
        connstringOgr : issu de la classe ConnexionBdd, attribut connstringOgr
        fichierShape : nom complet du fichier shape
        reprojection: entier decrivant l'epsg, exemple : 2154
        requeteSql : un string decrivant la requete sql de selection des donnees a exporter
        """
        connexion=connstringOgr.replace(' ','\"',1)
        reprojection='-t_srs EPSG:'+str(reprojection) if reprojection!='' else ''
        redirection_gdaldata=r"cd C:\Users\martin.schoreisz\AppData\Local\Programs\Python\Python38\Lib\site-packages\osgeo\data\gdal"
        cmd='ogr2ogr -f "ESRI shapefile" %s %s" %s -sql "%s" '%(fichierShape, connexion, reprojection, requeteSql)
        commande=redirection_gdaldata+" && "+cmd
        print(f"debut export fichier {fichierShape} \n a {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 

def ogr2ogr_shp2pg(connstringOgr,fichier,schema='public', table='tmp_import_shp',SRID='2154',geotype='MULTILINESTRINGZ', dims=3, creationMode='',encodageClient='UTF-8', requeteSql='', version_simple=False): 
        """"
        fonction d'import d'un shape dans postgres avec parametres
        en entree  
        connexionOgr issue de ConnexionBdd.connstringOgr
        fichier : raw string 
        creationMode : rien pour créée une nouvelle table, -append -update pour ajouter a une existante (faut mettre les deux
        version_simple : faire un import sans données de SRID, geotype, ndim
        """
        connexion=connstringOgr.replace(' ','\"',1)
        if version_simple : 
            cmd='ogr2ogr %s -f "postgreSQL" -lco "SCHEMA=%s" -lco GEOMETRY_NAME=geom %s\" %s -nln %s.%s' %(creationMode,schema,connexion, fichier,schema,table)
        elif SRID : 
            cmd='ogr2ogr %s -f "postgreSQL" -a_srs "EPSG:%s"  -nlt %s -dim %s -lco "SCHEMA=%s" -lco GEOMETRY_NAME=geom %s\" %s -nln %s.%s %s' %(creationMode,SRID,geotype,dims,schema,connexion, fichier,schema,table,requeteSql)
        else : 
            cmd='ogr2ogr %s -f "postgreSQL" -lco "SCHEMA=%s" -lco GEOMETRY_NAME=geom %s\" %s -nln %s.%s %s' %(creationMode,schema,connexion, fichier,schema,table,requeteSql)
        
        encodage='SET PGCLIENTENCODING='+encodageClient
        redirection_gdaldata=r'cd C:\Users\martin.schoreisz\AppData\Local\Programs\Python\Python38\Lib\site-packages\osgeo\data\gdal' 
        commande=redirection_gdaldata+" && "+encodage+" && "+cmd
        print(f"debut import fichier {fichier} avec shape2pg à {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 

def ogr2ogr_csv2pg(connstringOgr, fichier,schema='public', table='tmp_import_shp',encodageClient='UTF-8', headers='YES'):
        connexion=connstringOgr.replace(' ','\"',1)
        cmd=f'ogr2ogr -f "postgreSQL" --config PG_USE_COPY YES -lco "SCHEMA={schema}" {connexion}\" {fichier} -nln {schema}.{table} -oo HEADERS={headers}'
        encodage='SET PGCLIENTENCODING='+encodageClient
        redirection_gdaldata=r'cd C:\Users\martin.schoreisz\AppData\Local\Programs\Python\Python38\Lib\site-packages\osgeo\data\gdal' 
        commande=redirection_gdaldata+" && "+encodage+" && "+cmd
        print(f"debut import fichier {fichier} avec shape2pg à {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 
    
def ogr2ogr_pg2dbf(connstringOgr,fichierdbf, requeteSql):        
        connexion=connstringOgr.replace(' ','\"',1)
        redirection_gdaldata=r"cd C:\Users\martin.schoreisz\AppData\Local\Programs\Python\Python38\Lib\site-packages\osgeo\data\gdal"
        cmd='ogr2ogr -f "ESRI shapefile" %s %s" -sql "%s" '%(fichierdbf, connexion, requeteSql)
        commande=redirection_gdaldata+" && "+cmd
        print(f"debut export fichier {fichierdbf} \n a {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 
        
def ogr2ogrAsc2xyz(fichierAsc,epsg=2154):
        """Fonction de conversion d'un fichier .asc en .xyz"""
        fichierXyz=fichierAsc[:-3]+'xyz'
        redirection_gdaldata=r"cd C:\Users\martin.schoreisz\AppData\Local\Programs\Python\Python38\Lib\site-packages\osgeo\data\gdal"
        commandeGdal='gdal_translate -of XYZ -a_srs EPSG:%s %s %s'%(epsg,fichierAsc,fichierXyz)
        cmd= redirection_gdaldata+'&&'+ commandeGdal
        subprocess.call(cmd,shell=True)
        return fichierXyz
    
def ogr2ogrAsc2shp(fichierAsc,dossierSortie,opZonage,fichierZonage=None,epsg=2154):
    """
    Conversion d'un fichier asc en shp, par le biais de l'xyz,
    in : 
        fichierAsc : rawstring du chemin defichier complet
        dossierSortie rawstrig du dossier de sortie
        fichierZonage : rawstring d'un fichier shape de limitation des donnees
        opZonage : string, operation defiltre,; cf doc geopandas
    """
    ogr2ogrAsc2xyz(fichierAsc,epsg=2154)
    fichierXyz=pd.read_csv(fichierAsc[:-3]+'xyz', sep=' ',header=None, names=['x','y','z'])
    os.remove(fichierAsc[:-3]+'xyz')
    fichierXyz['geom']=fichierXyz.apply(lambda x : Point(x.x, x.y,x.z), axis=1)
    gdf=gp.GeoDataFrame(fichierXyz, geometry='geom', crs=f"EPSG:{epsg}")
    gdf=gdf.loc[gdf.geom.apply(lambda x : x.z!=-99999)]
    if fichierZonage :
        dfZonage=gp.read_file(fichierZonage)
        gp.sjoin(gdf,dfZonage,how='inner',op=opZonage ).to_file(os.path.join(dossierSortie,os.path.split(fichierAsc)[1][:-3]+'shp'))
    else : 
        gdf.to_file(os.path.join(dossierSortie,os.path.split(fichierAsc)[1][:-3]+'shp'))
    

class Ogr2Ogr(object):
    '''
    transcrition des principales fonctions d'ogr2ogr.exe
    '''
    
    def Raster2pg(self,urlFichierEntree,urlFichierSortie,bdd,user,schema,table,options='-s 2154 -F'):
        """transferer 1 ou plsuieurs raster dans postgres"""
        self.redirection='cd C:\\Program Files\\PostgreSQL\\9.5\\bin'
        self.commandeRaster='raster2pgsql %s %s %s.%s > %s.sql'%(options,urlFichierEntree,schema, table, urlFichierSortie)
        self.commandePsql='psql -d %s -U %s -f %s.sql'%(bdd,user,urlFichierSortie)
        self.commande=self.redirection+' && '+self.commandeRaster+' && '+self.commandePsql
        print (self.commande)
        subprocess.call(self.commande,shell=True)
    

class ConnexionBdd(object):

    def __init__(self,typeBdd='local_otv_boulot', schema='public', table='tmp',parent=None, fichierMdb=None):
        '''
        Constructeur
        les identiiants de connexions sont generes automatiquement lors de la creation de l'objet
        mais on peut les changer et les modif si besoin en entrant un nouveau typeBdd
        '''
        
        #attributs   partir des parametres
        self.typeBdd=typeBdd
        self.fichierMdb=fichierMdb
        if self.typeBdd=='mdb' : # dans le cas d'un fichier mdb il faut s'assurer que le driver est là
            if not [x for x in pyodbc.drivers() if x.startswith('Microsoft Access Driver')] : 
                raise self.DriverMdbError() 
            if not fichierMdb : 
                raise self.FichierMdbError()
        else : 
            self.serveur, self.port, self.user, self.mdp, self.bdd = ouvrirFichierParametre(self.typeBdd)
        self.creerConnexionString()

    def creerConnexionString(self):
        """
        determination des chaines permettant les connexions pour Psycopg2 et Ogr
        creation de l'engine de sqlalchemy
        """
        if self.typeBdd=='mdb' : 
            self.connstringMdb = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' + f'DBQ={self.fichierMdb};'
        else : 
            self.connstringPsy="host=%s user=%s password=%s dbname=%s port=%s" %(self.serveur, self.user, self.mdp, self.bdd, self.port)
            self.connstringOgr="PG: host=%s dbname=%s user=%s password=%s port=%s" %(self.serveur,self.bdd,self.user,self.mdp,self.port)
            self.engine=create_engine(f'postgresql://{self.user}:{self.mdp}@{self.serveur}:{self.port}/{self.bdd}') 

    def __enter__(self):
        if self.typeBdd=='mdb' :
            self.connexionMdb = pyodbc.connect(self.connstringMdb)
            self.mdbCurs = self.connexionMdb.cursor()
        else :
            self.connexionPsy=psycopg2.connect(self.connstringPsy)#toto
            self.curs=self.connexionPsy.cursor()
            self.connexionOgr=ogr.Open(self.connstringOgr)
            self.sqlAlchemyConn=self.engine.connect()
        return self
    
    def __exit__(self,*args):
        if self.typeBdd=='mdb' :
            self.connexionMdb.close()#fermer la connexion au mdb
        else : 
            self.connexionOgr.Destroy() #fin de la connexion Ogr
            self.connexionPsy.close() #fin d ela connexion Psy
            self.sqlAlchemyConn.close()#fin conn sqlAlchemy
            self.engine.dispose()#fermer l'engine sql alchemy
        return False
    
    class DriverMdbError(Exception):
        """
        Exception levee il manque le driver mdb, i.e il n'y a pas de Microsoft office sur le PC
        """     
        def __init__(self):
            Exception.__init__(self,'il manque le drivers mdb, cf https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access ')
    
    class FichierMdbError(Exception):
        """
        Exception levee il manque le fichier mdb, ou si il y a un pb avec son chemi ou ses donnees
        """     
        def __init__(self):
            Exception.__init__(self,'pb avec le fichier mdb, son nom (accent, underscire, caracteres speciaux...), son chemin (doit etre complet en raw string) ou ses donnees')
      

