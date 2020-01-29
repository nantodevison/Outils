# -*- coding: utf-8 -*-
'''
Created on 26 oct. 2017

@author: martin.schoreisz
'''

import matplotlib #pour eviter pb rcParams
import os
import shutil
import glob
import numpy as np
import pandas as pd
import geopandas as gp
import Connexion_Transfert as ct
from collections import Counter
from shapely.geometry import LineString
from geoalchemy2 import Geometry, WKTElement

def CopierFichierDepuisArborescence(dossierEntree,dossierSortie):
    """ fonction de copie en masse des fichiers au sein d'une raborescence
    en entrée : un path avec le préfixe r ou les \ doublés en \\
    """
    for root, dir, files in os.walk(dossierEntree):  #
        for file in files:
            path_file = os.path.join(root,file)
            try :
                shutil.copy2(path_file,dossierSortie)
            except :
                pass

def ListerFichierDossier(dossier,extension):
    """lister les fichier d'un dossier selon une extenssion
    en entrée : chemin du dossier avec le préfixe r ou les \ doublés en \\ 
    en entree : l'extension avec le '.'
    en sortie : listefinale : la liste des fichiers
    """
    listeCompleteFichier=glob.glob(dossier+"//*"+extension)
    listeFinale=[]
    for nomFichier in listeCompleteFichier : 
        suffixeNomFichier=os.path.split(nomFichier)[1]
        listeFinale.append(suffixeNomFichier)
    return listeFinale

def remplacementMultiple(text, dico):
    """fonction de remplacement de plusieurs caractères par d'autres
    en entrée : text : string : le texte dans lequel les remplacements s'effctuent
                dico : dictionnaire de string : dico de type {txt_a_remplacer : txt_de_remplacement, autre_txt_a_remplacer : autre_ou_mm_txt_de_remplacement,...}
    en sortie : text : le texte remplacé
    """
    for i, j in dico.iteritems():
        text = text.replace(i, j)
    return text     

def epurationNomRoute(nomRoute):
    '''
    fonction qui vire les 0 non significatif des routes
    en entree: le nom de la voie : texte
    en sortie : le nom de la voie : texte
    '''
    i,j=0,0 #initialisation compteur
    while nomRoute[i].isalpha(): #determiner le prefixe
        i+=1
    prefixe=nomRoute[:i]
    suffixe=nomRoute[i:]
    while suffixe[j]=='0': #determine le nombre de 0 non significatif
        j+=1
    suffixeTraite=suffixe[j:]
    return prefixe+suffixeTraite

def angle_entre_2_ligne(point_commun, point_ligne1, point_ligne2):
    '''
    Calcul d'angle entre 3 points
    en entree : -> list ou tuple de coordonnees des 3 points
    en sortie : -> angle float
    '''
    #creer les vecteurs
    v0=np.array(point_ligne1) - np.array(point_commun)
    v1=np.array(point_ligne2) - np.array(point_commun)
    angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
    angle_degres=np.degrees(angle) if np.degrees(angle) > 0 else abs(np.degrees(angle))
    return angle_degres

def  random_dates(start, end, n=10): 
    """
    creer des dates aleatoires
    en entree : start : string decrivant une date avec Y M D H M S
                end : string decrivant une date avec Y M D H M S
    en sortie : une date au format pandas
    """
    
    start=pd.to_datetime(start)
    end=pd.to_datetime(end)
    start_u = start.value//10**9
    end_u = end.value//10**9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')
   
def creer_graph(gdf, bdd,id_name='id', schema='public', table='graph_temp', table_vertex='graph_temp_vertices_pgr'):
    """
    creer un graph a partir d'une geodataframe en utilisant les ofnctions de postgis.
    attention, pas de return, la table reste dans postgis
    en entree : 
        gdf : geodataframe de geopandas 
        bdd : string, bdd postgis utilisee pour faire le graph
        id_name : string : nom de la colonne contenant l'id_uniq
        schema : string, nom du schema ou stocke le graph teporaire dans postgis
        table : string, nom dde la table ou stocke le graph teporaire dans postgis
        table_vertex : string, nom de l table des vertex ou stocke le graph teporaire dans postgis
    """
    gdf_w=gdf.copy()
    #verifier que l'identifiant est un entier
    if gdf[id_name].dtype!=np.int64 : 
        raise TypeError('l''id doit etre converti en entier')
    #trouver le nom de la geom
    geom_name=gdf_w.geometry.name
    #passer les donnees en 2D
    gdf_w[geom_name]=gdf_w.geometry.apply(lambda x : LineString([xy[0:2] for xy in list(x.coords)]))
    #type de geom ets rid
    geo_type=gdf_w.geometry.geom_type.unique()[0].upper()
    geo_srid=int([a for a in gdf_w.geometry.crs.values()][0].split(':')[1])
    #passer la geom en texte pour export dans postgis
    gdf_w[geom_name] = gdf_w[geom_name].apply(lambda x: WKTElement(x.wkt, srid=geo_srid))
    with ct.ConnexionBdd(bdd) as c:
        #supprimer table si elle existe
        rqt=f"drop table if exists {schema}.{table} ; drop table if exists {schema}.{table_vertex} "
        c.sqlAlchemyConn.execute(rqt)
        #passer les donnees
        gdf_w.to_sql(table,c.sqlAlchemyConn,schema=schema,if_exists='append', index=False,
                   dtype={geom_name:Geometry(geo_type, srid=geo_srid)})
        c.sqlAlchemyConn.execute(f"""alter table {schema}.{table} rename column {geom_name}  to geom ;
                                    alter table {schema}.{table} alter column geom type geometry(MULTILINESTRING,{geo_srid})
                                    using st_Multi(geom)""")
        #creer le graph : soit source et target existent deja et on les remets a null, soit on les crees
        if all([a in gdf_w.columns for a in ['source', 'target']]) :
            rqt_creation_graph=f"""update {schema}.{table} set source=null, target=null ; 
                             select pgr_createTopology('{schema}.{table}', 0.001,'geom','{id_name}')"""
        elif all([a not in gdf_w.columns for a in ['source', 'target']]): 
            rqt_creation_graph=f"""alter table {schema}.{table} add column source int, add column target int ; 
                             select pgr_createTopology('{schema}.{table}', 0.001,'geom','{id_name}')"""
        c.sqlAlchemyConn.execute(rqt_creation_graph)
        rqt_anlyse_graph=f"SELECT pgr_analyzeGraph('{schema}.{table}', 0.001,'geom','{id_name}')"
        c.curs.execute(rqt_anlyse_graph)#je le fait avec psycopg2 car avec sql acchemy ça ne passe pas
        c.connexionPsy.commit()

def plus_proche_voisin(df_src, df_comp, dist_recherche, id_df_src, id_df_comp, same=False):
    """
    trouver l'objet le plus proche dans un rayon donné
    en entree : 
        df_src : geodataframe : les objets dont on veut trouver le plus proche voisin
        df_comp : geodataframe : les objets qui vont servir à chercher le plus proche
        dist_recherche : int : le rayon de recherche en mètre
        id_df_src : string : nom du champs identifiant à transférer
        id_df_comp : string : nom du champs identifiant à transférer
        same : boleen : si la mm df est entree 2 fois en entree
    """
    
    df_src_temp, df_comp_temp=df_src.copy(), df_comp.copy() #copie pour ne pas modifier la df source
    geom_src_nom,geom_comp_nom=df_src_temp.geometry.name, df_comp_temp.geometry.name
    df_src_temp['geom_src']=df_src_temp.geometry #stocker la geometrie source
    df_src_temp.geometry=df_src_temp.buffer(dist_recherche)#passer la geom en buffer
    intersct_buff=gp.sjoin(df_src_temp,df_comp_temp,how='left',op='intersects') #chcrecher les objets qui intersectent
    intersct_buff.geometry=df_src_temp.geom_src#repasser la geom en point
    
    id_comp=id_df_comp+'_right'
    if id_df_src==id_df_comp : #si les 2 ids ont le mm nom la jointure spatiale a produit un nom avec _right apres
        id_src=id_df_src+'_left'  
        intersct_buff=intersct_buff.merge(df_comp_temp[[id_df_comp,geom_comp_nom]], left_on=id_comp, right_on=id_df_comp)#recupérer la gémoétrie des objets qui intersectent
        if geom_src_nom==geom_comp_nom : #si les noms de geometries sont les memes des suffixes sont ajoutes
            geom_src_nom,geom_comp_nom=geom_src_nom+'_x',geom_comp_nom+'_y'
        intersct_buff['dist_pt_ligne']=intersct_buff.apply(lambda x : x[geom_src_nom].distance(x[geom_comp_nom]), axis=1) #définir la disance entre les df
        if same : 
            intersct_buff=intersct_buff.loc[intersct_buff[id_src]!=intersct_buff[id_comp]]
        joint_dist_min=intersct_buff.loc[intersct_buff.groupby(id_src)['dist_pt_ligne'].transform(min)==intersct_buff
                                         ['dist_pt_ligne']][[id_src,id_comp]].copy()
    else : 
        intersct_buff=intersct_buff.merge(df_comp_temp[[id_df_comp,'geometry']], left_on=id_df_comp, right_on=id_df_comp)
        if geom_src_nom==geom_comp_nom : #si les noms de geometries sont les memes des suffixes sont ajoutes
            geom_src_nom,geom_comp_nom=geom_src_nom+'_x',geom_comp_nom+'_y'
        intersct_buff['dist_pt_ligne']=intersct_buff.apply(lambda x : x[geom_src_nom].distance(x[geom_comp_nom]), axis=1)
        joint_dist_min=intersct_buff.loc[intersct_buff.groupby(id_df_src)['dist_pt_ligne'].transform(min)==intersct_buff
                                         ['dist_pt_ligne']][[id_df_src,id_df_comp]].copy()
        
    return joint_dist_min
    
def nb_noeud_unique_troncon_continu(df, idtroncon,nom_idtroncon):
    """
    compter le nombre de noeud unique (i.e en bout de troncon) d'un troncon qui ne s'interrompt pas
    in : 
        df : dataframe de ligne, doit contenir les attributs 'source', 'target' et un attribut d'identifiant de troncon
        idtroncon : identifiant du troncon
        nom_idtroncon : string : nom de l'attribut d'identifaint de tranocn
    out : 
        list_noeud_uniq : list des noeuds vu une seule fois dans le troncon
        list_noeud : list des noeuds du troncon
    """
    noeud_troncon=df.loc[df[nom_idtroncon]==idtroncon] # toute les lignes du troncon
    #utilisation de Counter pour avoir le nb d'occurence'
    list_noeud=[k for k in Counter(noeud_troncon.source.tolist()+noeud_troncon.target.tolist()).keys()]
    list_noeud_uniq=tuple([k for k,v in Counter(noeud_troncon.source.tolist()+noeud_troncon.target.tolist()).items() if v==1]) 
    return list_noeud_uniq,list_noeud

def verif_index(df, nom_a_check, reset=True, nouveau_nom=None):
    """
    verifier le nom de l'index d'une datatframe et soit reseter l'index, soit changer le nom
    in : 
        df: la df a verifier
        nom_a_check : string : le nom suposséede l'index
        reset : boolen : reseter l'index ou non
        nouveau_nom : le nouveau nom si renommage
    """
    if df.index.name==nom_a_check and reset : 
        return df.reset_index()
    else : 
        return df

        
        
        
        
        
        
        
        
        
        
        
        
    