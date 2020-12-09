# -*- coding: utf-8 -*-
'''
Created on 26 oct. 2017

@author: martin.schoreisz
'''

import matplotlib #pour eviter pb rcParams
import os
import shutil
import glob
import pyproj
import numpy as np
import pandas as pd
import geopandas as gp
import Connexion_Transfert as ct
from collections import Counter
from datetime import datetime
from shapely.geometry import LineString
from shapely.ops import transform
from geoalchemy2.types import Geometry, WKTElement
from sqlalchemy.schema import MetaData
from sqlalchemy import inspect
from sklearn.cluster import DBSCAN
from builtins import isinstance

def CopierFichierDepuisArborescence(dossierEntree,dossierSortie, extension=None):
    """ fonction de copie en masse des fichiers au sein d'une raborescence
    in : 
        dossierEntree : raw string du dossier à parcourir
        dossierSortie : raw string du dossier destination
        extension : string : extension avec le . pour ne copier que les fichier es types souhaites
    """
    for root, dir, files in os.walk(dossierEntree):  #
        for file in files:
            path_file = os.path.join(root,file)
            if extension : 
                if file.lower().endswith(extension.lower()) : 
                    try :
                        shutil.copy2(path_file,dossierSortie)
                    except :
                        pass
            else :
                try :
                    shutil.copy2(path_file,dossierSortie)
                except :
                    pass

def ListerFichierDossier(dossier,extension=''):
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
    attention, pas de return, la table reste dans postgis.
    attention aussi si les lignes en entree sont des multilignes : seule la 1ere composante estconservee
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
    #verifier qu'on a bien une geoDataFrame
    if not isinstance(gdf_w,gp.GeoDataFrame) : 
        raise TypeError('if faut convertir les donnees en GeoDataFrame')
    
    #trouver le nom de la geom
    geom_name=gdf_w.geometry.name
    #passer les donnees en 2D et en linestring si Multi
    gdf_w[geom_name]=gdf_w.geometry.apply(lambda x : LineString([xy[0:2] for xy in list(x[0].coords)]) if x.geom_type=='MultiLineString' else 
                                                      LineString([xy[0:2] for xy in list(x.coords)]))
    #type de geom ets rid
    geo_type=gdf_w.geometry.geom_type.unique()[0].upper()
    geo_srid=int(gdf_w.crs.to_string().split(':')[1])
    #passer la geom en texte pour export dans postgis
    gdf_w[geom_name] = gdf_w[geom_name].apply(lambda x: WKTElement(x.wkt, srid=geo_srid))
    with ct.ConnexionBdd(bdd) as c:
        #supprimer table si elle existe
        rqt=f"drop table if exists {schema}.{table} ; drop table if exists {schema}.{table_vertex} "
        c.sqlAlchemyConn.execute(rqt)
        print(f'creer_graph : donnees mise en forme, connexion ouverte ; {datetime.now()}')
        #passer les donnees
        gdf_w.to_sql(table,c.sqlAlchemyConn,schema=schema, index=False,
                   dtype={geom_name:Geometry(geo_type, srid=geo_srid)})
        print(f'creer_graph : donnees transferees dans la base postgis ; {datetime.now()}')
        rqt_modif_geom=f"""alter table {schema}.{table} rename column {geom_name}  to geom ;
                                    alter table {schema}.{table} alter column geom type geometry(MULTILINESTRING,{geo_srid})
                                    using st_Multi(geom)""" if geom_name!='geom' else f"""
                                    alter table {schema}.{table} alter column geom type geometry(MULTILINESTRING,{geo_srid})
                                    using st_Multi(geom) ; """
        rqt_modif_attr=f"""alter table {schema}.{table} alter column "source" TYPE int8 ; 
                           alter table {schema}.{table} alter column "target" TYPE int8"""
        c.sqlAlchemyConn.execute(rqt_modif_geom)
        c.sqlAlchemyConn.execute(rqt_modif_attr)
        print(f'creer_graph : geometrie modifiee ; {datetime.now()}')
        #creer le graph : soit source et target existent deja et on les remets a null, soit on les crees
        if all([a in gdf_w.columns for a in ['source', 'target']]) :
            rqt_creation_graph=f"""update {schema}.{table} set source=null::integer, target=null::integer ; 
                             select pgr_createTopology('{schema}.{table}', 0.001,'geom','{id_name}')"""
        elif all([a not in gdf_w.columns for a in ['source', 'target']]): 
            rqt_creation_graph=f"""alter table {schema}.{table} add column source int, add column target int ; 
                             select pgr_createTopology('{schema}.{table}', 0.001,'geom','{id_name}')"""
        c.sqlAlchemyConn.execute(rqt_creation_graph)
        c.connexionPsy.commit()
        print(f'creer_graph : topologie cree ; {datetime.now()}')
        rqt_anlyse_graph=f"SELECT pgr_analyzeGraph('{schema}.{table}', 0.001,'geom','{id_name}')"
        c.curs.execute(rqt_anlyse_graph)#je le fait avec psycopg2 car avec sql acchemy ça ne passe pas
        print(f'creer_graph : graph cree ; {datetime.now()}')
        c.connexionPsy.commit()

def epurer_graph_trouver_lignes_vertex(vertex, lignes):
    """
    trouver les lignes et vertex des voies de categories 5 qui intersectent que des voies de categoriie 3 ou plus. prealable a la
    fonction epurer_graph().
    in : 
        vertex : df des vertex issu de analyze graph. doit contenir les attributs cnt
        lignes : gdf des lignes issue de createtopoology. doit contenir les attribut id_ign, source, target, importance
    out : 
        lignes_filtrees : gdf issue de lignes filtrees des lignes a suppr
        liste_ligne_filtre : liste des id_ign a enlever
        liste_vertex_filtre : liste des vertex a enlever
    """
    
    def filtrer_noeud(tuple_importance,tuple_ign):
        dico_counter=Counter(tuple_importance)
        if (len(tuple_importance) >= 3 and '5' in dico_counter.keys() and (len(tuple_importance)-dico_counter['5']) >=2
            and all([a not in tuple_importance for a in ['NC','4']])): #il y a au moins 2 lignes il y a une ligne 5, et au moins 2 autres lignes et que ces autres lignes ne sont pas NC ou 4  
                    return tuple([tuple_ign[l]for l in[i for i, j in enumerate(tuple_importance) if j=='5']])
        else : return False
    
    #isoler les noeud qui supportent plus de 2 lignes
    vertx_sup3=vertex.loc[vertex['cnt']>2].copy()
    #joindre avec les données de ligne
    vertx_importance=pd.concat([vertx_sup3.merge(lignes[['id_ign','source','importance']].rename(columns={'source':'id'}),on='id'),
     vertx_sup3.merge(lignes[['id_ign','target','importance']].rename(columns={'target':'id'}),on='id')],axis=0, sort=False).drop('the_geom',axis=1)
    #regrouper par id et avoir un tuple des importances
    vertx_importance_grp=vertx_importance.groupby('id').agg({'id_ign' : lambda x : tuple(x),'importance' : lambda x : tuple(x)})
    vertx_importance_grp['supprimable']=vertx_importance_grp.apply(lambda x : filtrer_noeud(x['importance'],x['id_ign']),axis=1)
    #filtrer la source
    liste_ligne_filtre=[b for a in vertx_importance_grp.loc[vertx_importance_grp['supprimable']!=False].supprimable.tolist() for b in a]
    liste_vertex_filtre=[a for a in vertx_importance_grp.loc[vertx_importance_grp['supprimable']!=False].index.tolist()]
    lignes_filtrees=lignes.loc[~lignes['id_ign'].isin(liste_ligne_filtre)].copy()
    return lignes_filtrees, liste_ligne_filtre, liste_vertex_filtre
    
def epurer_graph(bdd,id_name, schema, table, table_vertex):
    """
    enlever d'un graph en bdd les voies de catégorie 5 qui intersectent des voies de catégorie 4 ou plus
    attention, cela modifie les tables directement dans postgis.
    attention mm pb pour multilignes que dans creer_graph()
    en entree : 
        bdd : string, bdd postgis utilisee pour faire le graph
        id_name : string : nom de la colonne contenant l'id_uniq
        schema : string, nom du schema ou stocke le graph teporaire dans postgis
        table : string, nom dde la table ou stocke le graph teporaire dans postgis
        table_vertex : string, nom de l table des vertex ou stocke le graph teporaire dans postgis
    """
    with ct.ConnexionBdd(bdd) as c:
        vertex=pd.read_sql(f'select * from {schema}.{table_vertex}',c.sqlAlchemyConn)
        lignes=gp.GeoDataFrame.from_postgis(f'select * from {schema}.{table}',c.sqlAlchemyConn,geom_col='geom',crs={'init': 'epsg:2154'})
    lignes_filtrees=epurer_graph_trouver_lignes_vertex(vertex, lignes)[0]
    #la repasser dans la table postgis
    creer_graph(lignes_filtrees,bdd,id_name,schema, table, table_vertex)

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
        intersct_buff=intersct_buff.merge(df_comp_temp[[id_df_comp,geom_comp_nom]], left_on=id_df_comp, right_on=id_df_comp)
        if geom_src_nom==geom_comp_nom : #si les noms de geometries sont les memes des suffixes sont ajoutes
            geom_src_nom,geom_comp_nom=geom_src_nom+'_x',geom_comp_nom+'_y'
        intersct_buff['dist_pt_ligne']=intersct_buff.apply(lambda x : x[geom_src_nom].distance(x[geom_comp_nom]), axis=1)
        joint_dist_min=intersct_buff.loc[intersct_buff.groupby(id_df_src)['dist_pt_ligne'].transform(min)==intersct_buff
                                         ['dist_pt_ligne']][[id_df_src,id_df_comp]].copy()
        
    return joint_dist_min

def cluster_spatial(gdf, distance):
    """
    ajouter un attribut 'n_cluster' de regourpement des objets d'une df selon une distance inter objet
    necessite une gdf avec une géométrir selon un CRS en mètres
    se base sur l'algorythme DBSCAN
    in : 
        gdf : geodataframe avec une geometrie en mètre
        distance : integer : ecart max entre 2 objets regroupables
    """
    gdf['x_l93']=gdf.geometry.apply(lambda x : x.x)
    gdf['y_l93']=gdf.geometry.apply(lambda x : x.y)
    limMet_clust=[[x, y] for x, y in zip(gdf.x_l93.tolist(), gdf.y_l93.tolist())]
    db = DBSCAN(eps=distance, min_samples=2).fit(limMet_clust)
    labels = db.labels_
    gdf['n_cluster']=labels

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

def check_colonne_in_table_bdd(bdd, schema_r, table_r,*colonnes) : 
    """
    verifier qu'une table d'une bdd contient les colonnes ciblees
    in : 
       bdd : string : descriptions de la bdd, cf modules id_connexion
       schema_r : string : le nom du schema supportant la table
       table_r : le nom de la table
       colonnes : le nom des colonnes devant etre dans la table, separe par une virgule
    out : 
        flag : booleen : true si toute les colonnes sont das la table, False sinon
        list_colonne_manquante : lisrte des colonnes qui manque
    """
    with ct.ConnexionBdd(bdd) as c : 
        m=MetaData(bind=c.engine,schema=schema_r)
        m.reflect()
        inspector=inspect(c.engine)
    for t in m.tables.keys() : 
        if t==f'{schema_r}.{table_r}' : 
            columns=[c['name'] for c in inspector.get_columns(table_r, schema=schema_r)]
    if all([e in columns for e in colonnes]) : 
        return True,[]
    else : 
        return False,[e for e in colonnes if e not in columns]        
        
def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos   

def gp_changer_nom_geom(gdf, new_name, srid=2154):
    """
    changer le nom de la colonne geometrie dans une geodataframe
    """
    gdf_modif=gdf.rename(columns={gdf.geometry.name : new_name}).set_geometry(new_name)
    return gdf_modif 

def find_sublist(sub, bigger):
    first, rest = sub[0], sub[1:]
    pos = 0
    try:
        while True:
            pos = bigger.index(first, pos) + 1
            if not rest or bigger[pos:pos+len(rest)] == rest:
                return pos
    except ValueError:
        return -1
    
def reprojeter_shapely(geom, epsg_src, epsg_dest):
    """
    reprojeter une géométrie shapely, ou simplement préparer une transformation applicable à plusieurs geom si geom = None
    in :     
        geom: geom shapely
        epsg_src : string : ex : '2154'
        epsg_dest : string : ex : '4326'
    """
    src = pyproj.CRS(f'EPSG:{epsg_src}')
    dest = pyproj.CRS(f'EPSG:{epsg_dest}')
    project = pyproj.Transformer.from_crs(src, dest, always_xy=True).transform
    if not geom : 
        return project, None
    return project, transform(project, geom)
        
        
        
        
        
        
        
        
    