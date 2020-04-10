# -*- coding: utf-8 -*-
'''
Created on 26 avr. 2017

@author: Martin
'''
import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from sqlalchemy import create_engine
import subprocess
import psycopg2
import pyodbc
from osgeo import ogr
import paramiko
from stat import S_ISDIR

#fonction d'ouverture du fichier de parametres
def ouvrirFichierParametre(typeParametres):
    with open(r'C:\Users\martin.schoreisz\git\Outils\Outils\Martin_Perso\Id_connexions','r') as f_id :
        dicoParametres={}
        for texte in f_id :
            ligne=texte.strip().split(' ')
            dicoParametres[ligne[0]]=ligne[1:]
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
        redirection_gdaldata="cd C:\Program Files\GDAL\gdal-data"
        cmd='ogr2ogr -f "ESRI shapefile" %s %s" %s -sql "%s" '%(fichierShape, connexion, reprojection, requeteSql)
        commande=redirection_gdaldata+" && "+cmd
        print(f"debut export fichier {fichierShape} \n a {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 

def ogr2ogr_shp2pg(connstringOgr,fichier,schema='public', table='tmp_import_shp',SRID='2154',geotype='MULTILINESTRING', dims=3, creationMode='',encodageClient='UTF-8', requeteSql=''): 
        """"
        fonction d'import d'un shape dans postgres avec parametres
        en entree  
        connexionOgr issue de ConnexionBdd.connstringOgr
        fichier : raw string 
        """
        connexion=connstringOgr.replace(' ','\"',1)
        cmd='ogr2ogr %s -f "postgreSQL" --config PG_USE_COPY YES -a_srs "EPSG:%s"  -nlt %s -dim %s -lco "SCHEMA=%s" -lco GEOMETRY_NAME=geom %s\" %s -nln %s.%s %s' %(creationMode,SRID,geotype,dims,schema,connexion, fichier,schema,table,requeteSql)
        encodage='SET PGCLIENTENCODING='+encodageClient
        redirection_gdaldata=r'cd C:\Program Files\GDAL\gdal-data' 
        commande=redirection_gdaldata+" && "+encodage+" && "+cmd
        print(f"debut import fichier {fichier} avec shape2pg à {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 

def ogr2ogr_csv2pg(connstringOgr, fichier,schema='public', table='tmp_import_shp',encodageClient='UTF-8', headers='YES'):
        connexion=connstringOgr.replace(' ','\"',1)
        cmd=f'ogr2ogr -f "postgreSQL" --config PG_USE_COPY YES -lco "SCHEMA={schema}" {connexion}\" {fichier} -nln {schema}.{table} -oo HEADERS={headers}'
        encodage='SET PGCLIENTENCODING='+encodageClient
        redirection_gdaldata=r'cd C:\Program Files\GDAL\gdal-data' 
        commande=redirection_gdaldata+" && "+encodage+" && "+cmd
        print(f"debut import fichier {fichier} avec shape2pg à {datetime.now().time().isoformat(timespec='seconds')} \n avec commande {cmd}")
        subprocess.call(commande,shell=True)
        print('Fait') 
        
        
        

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
    
    def Asc2xyz(self,fichierAsc,epsg=2154):
        """Fonction de conversion d'un fichier .asc en .xyz"""
        fichierXyz=fichierAsc[:-3]+'xyz'
        redirection_gdaldata="cd C:\Program Files\GDAL\gdal-data"
        commandeGdal='gdal_translate -of XYZ -a_srs EPSG:%s %s %s'%(epsg,fichierAsc,fichierXyz)
        cmd= redirection_gdaldata+'&&'+ commandeGdal
        subprocess.call(cmd,shell=True)
        return fichierXyz
    

class ConnexionBdd(object):

    def __init__(self,typeBdd, schema='public', table='tmp',parent=None, fichierMdb=None):
        '''
        Constructeur
        les identiiants de connexions sont generes automatiquement lors de la creation de l'objet
        mais on peut les changer et les modif si besoin en entrant un nouveau typeBdd
        '''
        
        #attributs �  partir des parametres
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
      

class ConnexionSsh(paramiko.SSHClient):
    """
    Classe de connexion  un sftp ssh
    utilise le module paramiko
    en entree : 
    host (hote sans sftp:// ex :acoustique.cerema.fr )
    port (entier ex: 22)
    username (string ex : gittadmin)
    mdp (string ex : bruitAcou00!)
    """
    
    def __init__(self, host='acoustique.cerema.fr', port=22, username='gittadmin', mdp='bruitAcou00!') :
        """
        constrcuteur
        """
        #self.ssh = paramiko.SSHClient()
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host=host
        self.port=port
        self.mdp=mdp
        self.username=username
        self.connect(self.host, self.port,  self.username, self.mdp)
        self.sftp = self.open_sftp()
        print(self.host, self.sftp)
    
        """
        #definir les chemins
        remote_path=r'/Projet_Reussir_2017_CBS/024/lineaire/'
        remote_file='lineaire_fer.shp'
        file_remote=remote_path+remote_file
        file_local=r'E:\Boulot\python3\test\toto.shp'
        self.sftp.get(file_remote, file_local)"""

    
    def sftp_walk(self,remotepath):
        path=remotepath
        files=[]
        folders=[]
        for f in self.sftp.listdir_attr(path):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        if files:
            yield path, files
        for folder in folders:
            new_path=remotepath+'/'+folder
            new_path=new_path.replace('//','/')
            for x in self.sftp_walk(new_path):
                yield x

if __name__=='__main__':
    app=QApplication(sys.argv)
    toto=ConnexionBdd('Bdd_95_local')
    print(toto.connstringPsy)