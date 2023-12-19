import sqlite3
import os
from itertools import chain,combinations

global cur,DbName,con
DbName = "test.db" #TODO supprimer avant de rendre
#DbName="" remettre ça


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

def computeAtts(attributes,dfScheme):
    total = attributes.copy()
    dfSchemeFunc = dfScheme.copy() 
    asChanged = True    
    while asChanged:
        asChanged= False
        for df in dfSchemeFunc:
            if len([x for x in df[0].split(" ") if x not in total]) ==0:
                asChanged = True
                total.append(df[1])
                dfSchemeFunc.remove(df)
    return total

def fermeture(dfWanted,dfs):
    NotUsed = dfs.copy()
    print(NotUsed)
    NUComparator = []
    fermeture = [dfWanted[0].split(" ")]
    print(fermeture)
    while NotUsed != NUComparator:
        NUComparator= NotUsed.copy()
        for i in NotUsed:
            if stringContain(i[0], fermeture):
                NUComparator = [x for x in NUComparator if x not in fermeture]
                fermeture.append(i[1].split(" "))
    return fermeture

def verifyConsequences(table_name):

    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))
    listConsequences = []
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
            listConsequences.append(dfWanted)
    return listConsequences

def verifyAllConsequences():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    csq = []
    for name in names:
        print(name[0])
        csq = verifyConsequences(name[0])
        for element in csq:
            print(str(element) + "| Conséquence logique!")


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
        asChanged = True
        while asChanged:
            asChanged = False
            for dfComp in array:
                if (df!=dfComp) and (stringContain(dfComp[0],str(Tdfs[-1]))):
                    toAdd = (Tdfs[-1][0], addNotIn(dfComp[1],Tdfs[-1][0],Tdfs[-1][1]))
                    if toAdd != Tdfs[-1]:
                        Tdfs[-1] = toAdd
                        asChanged= True
    return Tdfs

def isBCNF(array,table_name):
    column = list(set(cur.execute(f"SELECT * FROM {table_name}").description))
    BCNF = True
    problematics = []
    for tuple in array:
        for element in column:
            if element[0] not in str(tuple):
                problematics.append(tuple)
                BCNF = False
                break
    return [BCNF,problematics]



def testAllBCNF():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    for name in names:
        ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{name[0]}'"))
        dfs = mergeDFS(ltr)
        tds = trueDependences(dfs)
        print(name[0])
        x = isBCNF(tds,name[0])
        if x[0]:
            print("BCNF RESPECTED")
        else:
            for element in x[1]:
                print(str(element) + "| Tuple Problematic")
#Section 3NF

def rightNotInLeft(array):
    newArray = []
    for element in array:
        lhs = element[0].split(" ")
        rhs = element[1].split(" ")
        trueRhs = [x for x in rhs if x not in lhs]
        newArray.append(" ".join(trueRhs))
    return newArray

def is3NF(table_name): 
    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))
    dfs = mergeDFS(ltr)
    
    tdfs = trueDependences(dfs)
    b = isBCNF(tdfs,table_name)
    r = rightNotInLeft(dfs)
    keys = str(getKeys(table_name)).replace(","," ")
    if(b[0]): 
        return [True,b,r]
    notIn = []
    for element in r:
        if not stringContain(element, keys):
            notIn.append(element)
    if notIn != []:
        bn = [False,[]]
        for element in b[1]:
            if not stringContain(element[1],keys):
                bn[1].append(element)
        return [False,bn,notIn]
    return [True,b,r]

def testAll3NF(): 
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    for name in names:
        ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{name[0]}'"))
        print(name[0])
        x = is3NF(name[0])
        if x[0]:
            print("3NF RESPECTED")
        else:             
           print(str(x[1][1]) + "| Tuples Problematic")
           print(str(x[2])+ "| Not in Keys")
             
def listDF():
    listDf = list(cur.execute("SELECT lhs,rhs,table_name FROM FuncDep"))
    for df in listDf:
        print(f"{df[0].replace(" ",",")} -> {df[1].replace(" ",",")} | dans la table : {df[2]}")
    input()
    
def notGoodInput(hand,table):
    if len(hand.split(" ")) == 0:
        return True
    for h in hand.split(" "):
        if h not in  list(map(lambda x: x[0], cur.execute(f'select * from {table}').description)):
            print(f"{h} not in {list(map(lambda x: x[0], cur.execute(f'select * from {table}').description))}")
            return True
    
    return False
    
def addDF():
    print("Voici les différentes tables :")
    tables = list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    print("0) retourner au menu principal")
    for i in range(len(tables)):
        if tables[i][0] != "FuncDep":
            print(f"{i+1}) {tables[i]}")
    
    table = input()
    
    if table == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while not table.isdigit() or int(table) >= len(tables) +1:
        table = input("invalid entry please retry:")
        if table == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return
        
    table = tables[int(table) -1]
    
    print(f"Voici les attributs de la table {table[0]}:")
    for att in list(map(lambda x: x[0], cur.execute(f'select * from {table[0]}').description)):print(att)
    
    print("Veuillez désormais choisir la main gauche de la dépendance fonctionnelle.")
    print("Pour cela merci de séparer chaque attribut par un espace :\" \".")
    print("Entrez \"0\" pour retourner au menu principal")
    
    lhs = input()
    if lhs == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while notGoodInput(lhs,table[0]):
        lhs = input("Entrée invalide veuillez réessayer:")
        if lhs =="0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return
        
    print("Veuillez désormais répéter ùle processus pour la main droite de la dépendance fonctionnelle.")
    print("Cependant veuillez entrer un attribut unique.")
    
    print("Entrez \"0\" pour retourner au menu principal")
    
    rhs = input()
    if rhs == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while notGoodInput(rhs,table[0]) or len(rhs.split(" ")) > 1:
        rhs = input("Entrée invalide veuillez réessayer:")
        if rhs == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return    
    
        
    if rhs in fermeture((rhs,lhs),list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table[0]}'"))) and input("c'est une conséquence logique, voulez vous tout de même l'ajouter ? (y/n): ") != "y":
        return
    
    cur.execute(f"insert into FuncDep(table_name,lhs,rhs) values ('{table[0]}','{lhs}','{rhs}')")    
    con.commit()

    if input("continuer (y/n): ") == "y":
        addDF()
        
def deleteDF():
    print("Voici les différentes tables :")
    tables = list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    print("0) retourner au menu principal")
    for i in range(len(tables)):
        if tables[i][0] != "FuncDep":
            print(f"{i+1}) {tables[i]}")
    
    table = input()
    if table == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    while not table.isdigit() or int(table) >= len(tables) +1:
        table = input("invalid entry please retry:")
        if table == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return
        
    table = tables[int(table) -1][0]

    print(table)

    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table}'"))
    print("Voici les différentes dépendances fonctionnelles :")
    print("0) retourner au menu principal")
    for i in range(len(ltr)):
        print(f"{i+1}) {ltr[i][0].replace(" ",",")} --> {ltr[i][1]}")
    
    df = input()
    if df == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    while not df.isdigit() or int(df) >= len(ltr) +1:
        df = input("invalid entry please retry:")
        if df == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return

    df = ltr[int(df) -1]
    cur.execute(f"delete from FuncDep where table_name = '{table}' and  lhs = '{df[0]}' and rhs = '{df[1]}'")
    con.commit()
    
    if input("continuer (y/n): ") == "y":
        deleteDF()
    
    

def getAllKeys():
    names = list(set(cur.execute("select table_name from FuncDep")))
    for name in names:
        print(f"For {name}: ")
        print(getKeys(name[0]))

def getKeys(tableName):
    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{tableName}'"))
    logicCsq = verifyConsequences(tableName)
    ltr = [x for x in ltr if x not in logicCsq]

    attributes = list(map(lambda x: x[0], cur.execute(f'select * from {tableName}').description))
    useless = []
    necessary = []
    middleGround = []
    for att in attributes:
        rightCount,leftCount = 0,0
        for df in ltr:
            if att in df[0]:
                rightCount+=1
            elif att in df[1]:
                leftCount+=1
        if rightCount >= 0 and leftCount==0:
            necessary.append(att)
        elif rightCount > 0 and leftCount > 0:
            middleGround.append(att)
        else:
            useless.append(att)     

    necessaryComputed = computeAtts(necessary,ltr)
    if len(necessary) != 0 and len([x for x in attributes if x not in necessaryComputed]) == 0:
        return [",".join(necessary)]
    
    subArr = []
    for i in chain.from_iterable(combinations(middleGround, r) for r in range(len(middleGround)+1)):
        subArr.append(necessary + list(i))
        
    final = []
    i = 0
    while(len(subArr) != 0):
        i+=1
        actual = subArr[0]
        subArr.remove(subArr[0])
        actualComputed = computeAtts(actual,ltr)
    
        if len([x for x in attributes if x not in actualComputed]) == 0:
            final.append(actual)
            for y in subArr:
                if len([x for x in actual if x not in y]) == 0:
                    subArr.remove(y)
    
    for j in range(len(final)):
        final[j] = ",".join(final[j])
    return final

def verifyAllDFs():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    for name in names:
        print(name[0])
        verifyTablesDNF(name[0])


def printStartInterface():
    global cur,con  # retirer avant de rendre
    if DbName !="":
        con = sqlite3.connect(f"DB/{DbName}")
        cur = con.cursor()
        return
    
    print("\n") 
    print("Bienvenue dans notre Système de gestion des DFs de bases de données.")
    print("Veuillez fournir le nom de la table sur laquelle vous voulez travailler.")
    connectDb()
    
def connectDb():
    global cur, DbName,con
    DbName = input("nom de la Db (dans le répertoire DB):")

    while not os.path.isfile(f"DB/{DbName}"):
        print(f"Le fichier \"DB/{DbName}\" n'existe pas veuillez réessayer.")
        
    con= sqlite3.connect(f"DB/{DbName}")
    cur = con.cursor()
    
    if ("FuncDep",) not in list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'")):
        print("Il fut remarqué que FuncDep n'existe pas pour cette Database nous l'ajoutons.")
        cur.execute("create table FuncDep ('table_name','lhs','rhs')")
        
        
printStartInterface()

while -1:
    printChoices([[f"Se connecter à une autre base de donnée que \"{DbName}\"", connectDb],
              ["Lister les dépendances fonctionnelles", listDF], 
              ["Ajouter une dépendance fonctionnelle", addDF],
              ["supprimer une dépendance fonctionnelle", deleteDF],
              # TODO : ["modifier une dépendance fonctionnelle", modifyDF],
              ["Vérifier les dépendances fonctionnelles de chaque table", verifyAllDFs],
              ["Vérifier les conséquences logiques de chaque table",verifyAllConsequences],
              ["Verifier si chaque table est en BCNF",testAllBCNF],
              ["Afficher les clés de chaque table (ayant des DFs)",getAllKeys],
              ["Verifier si chaque table est en 3NF",testAll3NF],
              ["Quitter",quit]
              ],)
