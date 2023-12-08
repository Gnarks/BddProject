import sqlite3
import os

global cur,DbName
DbName = "test.db"

def printChoices(choices):
    for i in range(len(choices)):
        print(f"{i}) {choices[i][0]}")
        
    choice = input()
    
    while not choice.isdigit() or int(choice) >= len(choices):
        choice = input("Entrée invalide veuillez réessayer:")
        
        
    os.system( "clear" if os.name == "posix"  else "cls")
    choices[int(choice)][1]()

def getLhs_RowAndRhs_Row(row):
    return (row[:-1], row[-1])

def verifyTablesDNF(table_name):

    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FunctDep WHERE table_name = '{table_name}'"))

    for df in ltr:
        
        (lhs,rhs) = (df[0].replace(" ",","),df[1])
        
        d = cur.execute(f"SELECT {lhs},{rhs} FROM {table_name}")
        dicoLtr = {}
        for row in d:
    
            row_lhs,row_rhs = getLhs_RowAndRhs_Row(row)
            
            if(row_lhs in list(dicoLtr.keys())):
                if row_rhs != dicoLtr[row_lhs]:
                    print("biiip:" + str(row))
            else:
                dicoLtr[row_lhs] = row_rhs
                
def listDF():
    listDf = list(cur.execute(f"SELECT lhs,rhs,table_name FROM FunctDep"))
    for df in listDf:
        print(f"{df[0].replace(" ",",")} -> {df[1].replace(" ",",")} | dans la table : {df[2]}")
    input()
    
def notGoodInput(hand,table):
    print(hand.split(","))
    if len(hand.split(",")) == 0: return True
    print( list(map(lambda x: x[0], cur.execute(f'select * from {table}').description)))
    for h in hand.split(","):
        if h not in  list(map(lambda x: x[0], cur.execute(f'select * from {table}').description)):
            print(f"{h} not in")
            return True
    
    return False
    
def addDF():
    
    print("Voici les différentes tables :")
    tables = list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    for i in range(len(tables)):
        print(f"{i}) {tables[i]}")
    
    table = input()
    
    while not table.isdigit() or int(table) >= len(tables):
        table = input("invalid entry please retry:")
        
    table = tables[int(table)]
        
    print(f"Voici les attributs de la table {table[0]}:")
    for att in list(map(lambda x: x[0], cur.execute(f'select * from {table[0]}').description)): print(att)
    
    print(f"Veuillez désormais choisir la main gauche de la dépendance fonctionnelle.")
    print(f"Pour cela merci de séparer chaque attribut par \",\"")
    
    lhs = input()
    while notGoodInput(lhs,table[0]):
        lhs = input("Entrée invalide veuillez réessayer:")
        
    print(f"Veuillez désormais répéter le processus pour la main droite de la dépendance fonctionnelle.")
    print(f"De nouveau merci de séparer chaque attribut par \",\"")
    
    rhs = input()
    while notGoodInput(rhs,table[0]):
        rhs = input("Entrée invalide veuillez réessayer:")
        
    print(list(cur.execute(f"insert into FunctDep(table_name,lhs,rhs) values ('{table[0]}','{lhs}','{rhs}')"))) #TODO changer fucntdep -> FuncDep
    
    
    if input("continuer : y/n") == "y":
        addDF()
    #TODO push les changes 


def verifyAllDFs():
    names = list(cur.execute(f"SELECT table_name FROM FunctDep"))
    for name in names:
        print(name[0])
        verifyTablesDNF(name[0])


def printStartInterface():
    global cur #TODO retirer
    print("\n") 
    print("Bienvenue dans notre Système de gestion des DFs de bases de données.")

    print("Veuillez fournir le nom de la table sur laquelle vous voulez travailler.")
    #connectDb()
    con = sqlite3.connect("DB/test.db")
    cur = con.cursor()

    
def connectDb():
    global cur, DbName
    DbName = input("nom de la Db (dans le répertoire DB):")

    while not os.path.isfile(f"DB/{DbName}"):
        print(f"Le fichier \"DB/{DbName}\" n'existe pas veuillez réessayer.")
        DbName = input("nom de la Db (dans le répertoire DB):")
        
    con= sqlite3.connect(f"DB/{DbName}")
    cur = con.cursor()
        
printStartInterface()

while -1:
    printChoices([[f"Se connecter à une autre base de donnée que \"{DbName}\"", connectDb],
              ["Lister les dépendances fonctionnelles", listDF], 
              ["ajouter une dépendance fonctionnelle", addDF],
              # TODO :["supprimer une dépendance fonctionnelle," deleteDF],
              ["Vérifier toutes les dépendances fonctionnelles", verifyAllDFs],
              ["Quitter",quit]
    
              ],)
# TODO changer le nom de functttttDep -> FuncDep