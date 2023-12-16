import sqlite3
import os
#comment
global cur,DbName,con
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

    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))

    
    for df in ltr:

        print(f"For {str(df)}: ")
        okValue = True 
        (lhs,rhs) = (df[0].replace(" ",","),df[1])
        
        d = cur.execute(f"SELECT {lhs},{rhs} FROM {table_name}")
        dicoLtr = {}
        for row in d:
    
            row_lhs,row_rhs = getLhs_RowAndRhs_Row(row)
            
            if(row_lhs in list(dicoLtr.keys())):
                if row_rhs != dicoLtr[row_lhs]:
                    print(str(row) + " | Tuple problématique! ")
                    okValue = False
            else:
                dicoLtr[row_lhs] = row_rhs
        if okValue:
            print("DF respectée")

# Section Logic Consequences

def getAllLhs(dfArray):
    lhs=[]
    for i in dfArray:
        lhs.append(i[0])
    return lhs


def fermeture(dfWanted,dfs):
    NotUsed = dfs
    NUComparator = []
    fermeture = [dfWanted[0]]
    while NotUsed != NUComparator:
        NUComparator = NotUsed
        for i in NotUsed:
            if i[0] in fermeture:
                NUComparator = NUComparator.remove(i)
                fermeture.append(i[1])
    return fermeture

def verifyConsequences(table_name):

    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))
    
    for i in range(len(ltr)):
        dfWanted = ltr[i]
        if i in range(1,len(ltr)):
            dfs = ltr[:i] + ltr[i+1:]
        elif(i == 0):
            dfs = ltr[i+1:]
        else:
            dfs = ltr[:i]
        ferm = fermeture(dfWanted,dfs)
        if(dfWanted[1] in ferm):
            print(str(dfWanted) + "| Conséquence logique!")


def verifyAllConsequences():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))

    for name in names:
        print(name[0])
        verifyConsequences(name[0])

#Section BCNF
def stringContain(isIn, contain):
    listIsIn = isIn.split(" ")
    for element in listIsIn:
        if element not in contain:
            return False
    return True

def addNotIn(toAdd, addedlhs, addedrhs):
    listToAdd = toAdd.split(" ")
    toReturn = addedrhs
    for element in listToAdd:
        if element not in addedlhs and element not in addedrhs:
            toReturn = toReturn + " " + element
    return toReturn
    
def mergeDFS(array):
    dico ={}
    for df in array:
        if df[0] in list(dico.keys()):
            dico[df[0]] = dico[df[0]]+ " " + df[1]
        else:
            dico[df[0]] = df[1]
    newDfs = []
    for key in list(dico.keys()):
        newDfs.append((key , dico[key]))
    return newDfs

def trueDependences(array):
    Tdfs = []
    for df in array:
        Tdfs.append(df)
        for dfComp in array:
            if df!=dfComp and stringContain(dfComp[0],str(df)):
                toAdd = (df[0], addNotIn(dfComp[1],df[0],df[1]))
                Tdfs[-1] = toAdd
    return Tdfs



def isBCNF(array,table_name):
    column = list(set(cur.execute(f"SELECT * FROM {table_name}").description))
    BCNF = True
    for tuple in array:
        for element in column:
            if element[0] not in str(tuple):
                print(f"{tuple} problématique")
                BCNF = False
    if BCNF:
        print("BCNF IS RESPECTED")

def testAllBCNF():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    for name in names:
        ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{name[0]}'"))
        dfs = mergeDFS(ltr)
        dfs = trueDependences(dfs)
        print(name[0])
        isBCNF(dfs,name[0])

def listDF():
    listDf = list(cur.execute("SELECT lhs,rhs,table_name FROM FuncDep"))
    for df in listDf:
        print(f"{df[0].replace(" ",",")} -> {df[1].replace(" ",",")} | dans la table : {df[2]}")
    input()
    
def notGoodInput(hand,table):
    if len(hand.split(",")) == 0:
        return True
    for h in hand.split(","):
        if h not in  list(map(lambda x: x[0], cur.execute(f'select * from {table}').description)):
            print(f"{h} not in {list(map(lambda x: x[0], cur.execute(f'select * from {table}').description))}")
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
    for att in list(map(lambda x: x[0], cur.execute(f'select * from {table[0]}').description)):
        print(att)
    
    print("Veuillez désormais choisir la main gauche de la dépendance fonctionnelle.")
    print("Pour cela merci de séparer chaque attribut par \",\"")
    
    lhs = input()
    while notGoodInput(lhs,table[0]):
        lhs = input("Entrée invalide veuillez réessayer:")
        
    print("Veuillez désormais répéter le processus pour la main droite de la dépendance fonctionnelle.")
    print("De nouveau merci de séparer chaque attribut par \",\"")
    
    rhs = input()
    while notGoodInput(rhs,table[0]):
        rhs = input("Entrée invalide veuillez réessayer:")
        
    print(list(cur.execute(f"insert into FuncDep(table_name,lhs,rhs) values ('{table[0]}','{lhs}','{rhs}')"))) 
    
    if input("continuer( y/n): ") == "y":
        addDF()
    con.commit()

def verifyAllDFs():
    
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    for name in names:
        print(name[0])
        verifyTablesDNF(name[0])


def printStartInterface():
    global cur,con 
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
              ["Ajouter une dépendance fonctionnelle", addDF],
              # TODO :["supprimer une dépendance fonctionnelle," deleteDF],
              ["Vérifier toutes les dépendances fonctionnelles", verifyAllDFs],
              ["Vérifier conséquences logique",verifyAllConsequences],
              ["Verifier BCNF",testAllBCNF],
              ["Quitter",quit]
              ],)
