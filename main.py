import sqlite3
import os
from itertools import chain,combinations

global cur,DbName,con
DbName=""


def printChoices(choices):
    for i in range(len(choices)):
        print(f"{i}) {choices[i][0]}")
        
    choice = input()
    
    while not choice.isdigit() or int(choice) >= len(choices):
        choice = input("Entrée invalide veuillez réessayer:")
        
        
    os.system( "clear" if os.name == "posix"  else "cls")
    choices[int(choice)][1]()


'''SECTION VERIFIER DFS'''
def getLhs_RowAndRhs_Row(row):
    return (row[:-1], row[-1])

def MakeTableGood(table_name):
    tables = list(map(lambda x: x[0], cur.execute("SELECT name FROM sqlite_master WHERE type='table'")))
    
    if table_name not in tables:
        print(f"La table {table_name} n'existe pas suppression automatique de son apparence dans FuncDep")
        cur.execute(f"delete from FuncDep where table_name = '{table_name}'")
        con.commit()
        return
    dfList = []
    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))
    for df in ltr:
        attList = list(map(lambda x: x[0], cur.execute(f'select * from {table_name}').description))

        if len([x for x in df[0].split(" ") if x not in attList]) >0 or len([x for x in df[1].split(" ") if x not in attList]) > 0:
            print(f"un des attributs de la DF ({df[0].replace(" ",",")} -> {df[1].replace(" ",",")}) n'appartient pas à la liste d'attributs de la table {table_name}")
            print(f"suppression de la dépence fonctionnelle {df[0].replace(" ",",")} -> {df[1].replace(" ",",")}")
            cur.execute(f"delete from FuncDep where table_name = '{table_name}' and lhs = '{df[0]}' and rhs ='{df[1]}'")
            con.commit()
            continue
                
        if  len(df[1].split(" ")) > 1:
            print(f"La DF {df[0].replace(" ",",")} -> {df[1].replace(" ",",")} n'est pas singulière, suppression automatique.")
            cur.execute(f"delete from FuncDep where table_name = '{table_name}' and lhs = '{df[0]}' and rhs ='{df[1]}'")

            if  input("Voulez vous l'ajouter de manière singulière ? (y/n):") == "y":
                for uniqueRhs in df[1].split():
                    cur.execute(f"insert into FuncDep(table_name,lhs,rhs) values ('{table_name}','{df[0]}','{uniqueRhs}')")      
            con.commit()
            continue
        

def verifyTablesDNF(table_name):
    tables = list(map(lambda x: x[0], cur.execute("SELECT name FROM sqlite_master WHERE type='table'")))
    
    if table_name not in tables:
        print(f"La table {table_name} n'existe pas suppression automatique de son apparence dans FuncDep")
        cur.execute(f"delete from FuncDep where table_name = '{table_name}'")
        con.commit()
        return
    dfList = []
    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))
    for df in ltr:
        attList = list(map(lambda x: x[0], cur.execute(f'select * from {table_name}').description))

        if len([x for x in df[0].split(" ") if x not in attList]) >0 or len([x for x in df[1].split(" ") if x not in attList]) > 0:
            print(f"un des attributs de la DF ({df[0].replace(" ",",")} -> {df[1].replace(" ",",")}) n'appartient pas à la liste d'attributs de la table {table_name}")
            print(f"suppression de la dépence fonctionnelle {df[0].replace(" ",",")} -> {df[1].replace(" ",",")}")
            cur.execute(f"delete from FuncDep where table_name = '{table_name}' and lhs = '{df[0]}' and rhs ='{df[1]}'")
            con.commit()
            continue
                
        if  len(df[1].split(" ")) > 1:
            print(f"La DF {df[0].replace(" ",",")} -> {df[1].replace(" ",",")} n'est pas singulière, suppression automatique.")
            cur.execute(f"delete from FuncDep where table_name = '{table_name}' and lhs = '{df[0]}' and rhs ='{df[1]}'")

            if  input("Voulez vous l'ajouter de manière singulière ? (y/n):") == "y":
                for uniqueRhs in df[1].split():
                    cur.execute(f"insert into FuncDep(table_name,lhs,rhs) values ('{table_name}','{df[0]}','{uniqueRhs}')")      
            con.commit()
            continue
        (lhs,rhs) = (df[0].replace(" ",","),df[1])
        
        d = cur.execute(f"SELECT {lhs},{rhs} FROM {table_name}")
        dicoLtr = {}
        for row in d:
            
            row_lhs,row_rhs = getLhs_RowAndRhs_Row(row)
            
            if(row_lhs in list(dicoLtr.keys())):
                if row_rhs != dicoLtr[row_lhs]:
                    if df not in dfList:
                        dfList.append(df)
                    
            else:
                dicoLtr[row_lhs] = row_rhs
                
    return dfList
            

def verifyAllDFs():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    print("0) retourner au menu principal")
    i = 1
    allPrbls =[]
    for name in names:
        print(f"pour la table {name[0]} : ")
        prbls = verifyTablesDNF(name[0])
        for element in prbls:
            print(f"{i}) {element[0].replace(" ",",")} -> {element[1].replace(" ",",")} | DF problématique !")
            allPrbls.append((name[0],element[0],element[1]))
            i+=1

        if len(prbls) == 0:
            print("Pas de DF problématique.")
        print()
    
    if len(allPrbls) ==0 or input("Voulez vous supprimer une DF problématique ? (y/n) : ") != 'y':
        return
                
    suppr = input("Entrez la DF à supprimer : ")
    if suppr == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while not suppr.isdigit() or int(suppr) >= len(allPrbls) +1:
        suppr = input("invalid entry please retry:")
        if suppr == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return
    suppr = int(suppr)
    cur.execute(f"delete from FuncDep where table_name = '{allPrbls[suppr-1][0]}' and lhs ='{allPrbls[suppr-1][1]}' and rhs ='{allPrbls[suppr-1][2]}'")
    con.commit()

    if input("continuer (y/n): ") == "y":
        verifyAllDFs()
    print()

            
            


''' Section Logic Consequences'''

def fermeture(dfWanted,dfs):
    NotUsed = dfs.copy()
    NUComparator = []
    fermeture = dfWanted[0]
    while NotUsed != NUComparator:
        NUComparator = NotUsed.copy()
        for i in NotUsed:
            if len([x for x in i[0].split(" ") if x not in fermeture]) == 0:
                NotUsed.remove(i)
                fermeture = fermeture + " " + i[1]
    return fermeture


def verifyConsequences(table_name):
    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE table_name = '{table_name}'"))
    listConsequences = []
    for i in range(len(ltr)):
        
        dfWanted = ltr[i]
        dfs = [x for x in ltr if x != ltr[i]]
        ferm = fermeture(dfWanted,dfs)

        if len([x for x in dfWanted[1].split(" ") if x not in ferm]) == 0:
            listConsequences.append(dfWanted)
    return listConsequences

def verifyAllConsequences():
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    allCsq = []
    i = 1
    print("0) retourner au menu principal")

    for name in names:
        print(f"pour la table {name[0]} : ")
        csq = verifyConsequences(name[0])
        for element in csq:
            print(f"{i}) {element[0].replace(" ",",")} -> {element[1].replace(" ",",")} | Conséquence logique!")
            allCsq.append((name[0],element[0],element[1]))
            i+=1

        if len(csq) == 0:
            print("Pas de conséquences logiques")
    
    if len(allCsq)==0 or  input("Voulez vous supprimer une conséquence logique ? (y/n) : ") != 'y':
        return
                
    suppr = input("Entrez la DF à supprimer : ")
    if suppr == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while not suppr.isdigit() or int(suppr) >= len(allCsq) +1:
        suppr = input("invalid entry please retry:")
        if suppr == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return
    suppr = int(suppr)
    cur.execute(f"delete from FuncDep where table_name = '{allCsq[suppr-1][0]}' and lhs ='{allCsq[suppr-1][1]}' and rhs ='{allCsq[suppr-1][2]}'")
    con.commit()

    if input("continuer (y/n): ") == "y":
        verifyAllConsequences()


'''Section BCNF'''

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
                if (df!=dfComp) and (len([x for x in dfComp[0].split(" ") if x not in str(Tdfs[-1])])==0):
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
            print("BCNF RESPECTÉ")
        else:
            for element in x[1]:
                problems = list(set(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE lhs = '{element[0]}'")))
                for pb in problems:
                    print(str(pb[0]) + " -> " + str(pb[1]) + "| DF Problematique")
                    
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
        if len([x for x in element.split(" ") if x not in keys]) != 0:
            notIn.extend([x for x in element.split(" ")])
    if notIn != []:
        bn = [False,[]]
        for element in b[1]:
            if len([x for x in element[1].split(" ") if x not in keys]) != 0:
                bn[1].append(element)
        return [False,bn,list(set(notIn))]
    return [True,b,r]

def testAll3NF(): 
    names = list(set(cur.execute("SELECT table_name FROM FuncDep")))
    for name in names:
        print(name[0])
        x = is3NF(name[0])
        if x[0]:
            print("3NF RESPECTÉ")
        else:
            for element in x[1][1]:
                problems = list(set(cur.execute(f"SELECT lhs,rhs FROM FuncDep WHERE lhs = '{element[0]}'")))
                for pb in problems:
                    if pb[1] in x[2]:
                        print(str(pb[0]) + " -> " + str(pb[1]) + "  | DF Problematique.")
                        print([y for y in x[2] if y in pb[1]][0] + "  | n'est dans aucune clef.")



'''Section Affichage'''
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
    tables = [x for x in tables if x[0] != "FuncDep"]
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
    
    print(f"Voici les attributs de la table {table}:")
    for att in list(map(lambda x: x[0], cur.execute(f'select * from {table}').description)):print(att)
    
    print("Veuillez désormais choisir la main gauche de la dépendance fonctionnelle.")
    print("Pour cela merci de séparer chaque attribut par un espace :\" \".")
    print("Entrez \"0\" pour retourner au menu principal")
    
    lhs = input()
    if lhs == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while notGoodInput(lhs,table):
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
    
    while notGoodInput(rhs,table) or len(rhs.split(" ")) > 1:
        rhs = input("Entrée invalide veuillez réessayer:")
        if rhs == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return    
    
    cur.execute(f"insert into FuncDep(table_name,lhs,rhs) values ('{table}','{lhs}','{rhs}')")    
    con.commit()

    if input("continuer (y/n): ") == "y":
        addDF()
        
def deleteDF():
    print("Voici les différentes tables :")
    tables = list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    print("0) retourner au menu principal")
    tables = [x for x in tables if x[0] != "FuncDep"]
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
    
    
    
def modifyDF():
    
    print("Voici les différentes tables :")
    tables = list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    print("0) retourner au menu principal")
    tables = [x for x in tables if x[0] != "FuncDep"]
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
    print(f"Voici les attributs de la table {table}")
    for att in list(map(lambda x: x[0], cur.execute(f'select * from {table}').description)):print(att)

    
    print("Veuillez désormais choisir la main gauche de la dépendance fonctionnelle.")
    print("Pour cela merci de séparer chaque attribut par un espace :\" \".")
    print("Entrez \"0\" pour retourner au menu principal")
    
    lhs = input()
    if lhs == "0":
        os.system( "clear" if os.name == "posix"  else "cls")
        return
    
    while notGoodInput(lhs,table):
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
    
    while notGoodInput(rhs,table) or len(rhs.split(" ")) > 1:
        rhs = input("Entrée invalide veuillez réessayer:")
        if rhs == "0":
            os.system( "clear" if os.name == "posix"  else "cls")
            return    
    
    cur.execute(f"update FuncDep set lhs='{lhs}',rhs='{rhs}' where table_name ='{table}' and  lhs = '{df[0]}' and rhs = '{df[1]}'")
    con.commit()
    
    if input("continuer (y/n): ") == "y":
        deleteDF()


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
        toKeep =[]
        if len([x for x in attributes if x not in actualComputed]) == 0:
            final.append(actual)
            for y in subArr:
                if len([x for x in actual if x not in y]) != 0:
                    toKeep.append(y)
            subArr = toKeep.copy()
    
    for j in range(len(final)):
        final[j] = ",".join(final[j])
    return final



def printStartInterface():
    print("\n") 
    print("Bienvenue dans notre Système de gestion des DFs de bases de données.")
    print("Veuillez fournir le nom de la table sur laquelle vous voulez travailler.")
    connectDb()
    
def connectDb():
    global cur, DbName,con
    DbName = input("nom de la Db (dans le répertoire DB):")

    while not os.path.isfile(f"DB/{DbName}"):
        print(f"Le fichier \"DB/{DbName}\" n'existe pas veuillez réessayer : ")
        DbName = input()
        
    con= sqlite3.connect(f"DB/{DbName}")
    cur = con.cursor()
    
    if ("FuncDep",) not in list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'")):
        print("Il fut remarqué que FuncDep n'existe pas pour cette Database nous l'ajoutons.")
        cur.execute("create table FuncDep ('table_name','lhs','rhs')")

    for table in  list(cur.execute("SELECT name FROM sqlite_master WHERE type='table'")):
        MakeTableGood(table[0])

        
        
printStartInterface()

while -1:
    printChoices([[f"Se connecter à une autre base de donnée que \"{DbName}\"", connectDb],
              ["Lister les dépendances fonctionnelles", listDF], 
              ["Ajouter une dépendance fonctionnelle", addDF],
              ["supprimer une dépendance fonctionnelle", deleteDF],
              ["modifier une dépendance fonctionnelle", modifyDF],
              ["Vérifier les dépendances fonctionnelles de chaque table", verifyAllDFs],
              ["Vérifier les conséquences logiques de chaque table",verifyAllConsequences],
              ["Verifier si chaque table est en BCNF",testAllBCNF],
              ["Afficher les clés de chaque table (ayant des DFs)",getAllKeys],
              ["Verifier si chaque table est en 3NF",testAll3NF],
              ["Quitter",quit]
              ],)
