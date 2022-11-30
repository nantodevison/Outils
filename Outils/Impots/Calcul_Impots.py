# -*- coding: utf-8 -*-
'''
Created on 29 nov. 2022

@author: Martin
'''


from Impots.Params import dicoBaremeProgressif


def calculNombreDePart(adulte=2, enfant=1, parentIsole=False):
    """
    nombre de part selon le nombre de personnes composant le foyer
    in : 
        adulte : integer : nombre d'adulte
        enfant : integer : nombre d'enfant
    """
    if adulte == 0:
        raise ValueError("il faut au moins un adulte pour payer des impots")
    return adulte + (enfant / 2) if not parentIsole else adulte + (enfant / 2) + 0.5

class Revenu(object):
    '''
    calcul du bareme de l'impots sur le revenu.
    in:
        annee : string
        revenuNetImposable : integer
        adultes : integer : nb d'adultes du foyer
        enfants : integer : nombre d'enfant du foyer
    '''


    def __init__(self, annee, revenuNetImposable, adultes, enfants, parentIsole=False):
        '''
        initialisation du nombre de part et du quotient famillial
        '''
        self.annee = annee
        self.revenuNetImposable = revenuNetImposable
        self.adultes = adultes
        self.enfants = enfants
        self.parentIsole = parentIsole
        self.nombreDePart = calculNombreDePart(adultes, enfants, parentIsole)
        self.quotientFamilial = self.calculQuotientFamilial()
        self.getTauxMarginalImposition()
        self.calculImpotsRevenuParTranche()
        self.calculImpotRevenu()
     
        
    def calculQuotientFamilial(self):
        return self.revenuNetImposable / self.nombreDePart
    
    
    def getDicoTrancheImposition(self):
        """
        recuperer les tranches d'imposition, erreur si annee pas fourni
        """
        if self.annee not in dicoBaremeProgressif.keys():
            raise ValueError(f"l'annee {self.annee} n'est pas présente dans les paramètres de bareme progressif")
        return dicoBaremeProgressif[self.annee]
    
    
    def getdicoTrancheConcernee(self):
        """
        isoler les tranches d'imposition concernee selon le quotient familial
        """
        return {k: v for k, v in self.getDicoTrancheImposition().items() if v['trancheMin'] <= self.quotientFamilial}
    
    
    def getTauxMarginalImposition(self):
        """
        le taux marginal d'imposition est le taux de la tranche dasn laquelle se situe le quotient famillial
        """
        dicoTrancheConcernee = self.getdicoTrancheConcernee()
        self.tauxMarginalImposition = f"{int(max([d['tauxDImposition'] for d in dicoTrancheConcernee.values()]) * 100)} %"
    
        
    def calculImpotsRevenuParTranche(self):
        """
        en fonction de l'annee (et donc du dico de params), on va calculer l'impots par tranche d'imposition.
        out:
            dicoSommeImpot : dico en {tranche: montant}
        """    
        dicoTrancheConcernee = self.getdicoTrancheConcernee()
        dicoSommeImpot = {}
        for i in range(len(dicoTrancheConcernee)):
            i += 1
            if i == 1:
                dicoSommeImpot[f'tranche{i}'] = 0
            else :
                if dicoTrancheConcernee[f'tranche{i}']['trancheMax'] <= self.quotientFamilial:
                    dicoSommeImpot[f'tranche{i}'] = (dicoTrancheConcernee[f'tranche{i}']['trancheMax'] - dicoTrancheConcernee[f'tranche{i-1}']['trancheMax']
                                                     ) * dicoTrancheConcernee[f'tranche{i}']['tauxDImposition']
                else:
                    dicoSommeImpot[f'tranche{i}'] = (
                        self.quotientFamilial - dicoTrancheConcernee[f'tranche{i-1}']['trancheMax']) * dicoTrancheConcernee[f'tranche{i}']['tauxDImposition']
        self.dicoImpotsRevenuParTranche = dicoSommeImpot
    
    
    def calculImpotRevenu(self):
        self.montantImpotRevenu = round(sum(self.dicoImpotsRevenuParTranche.values()) * self.nombreDePart,2)
        
        
        
        
        