import sqlite3
import os


def printChoices(choices):
    for i in range(len(choices)):
        print(f"{i}) {choices[i][0]}")
    choice = int(input())
    choices[choice][1]()
    #printChoices([["createDB", createDB], ["delete", deleteDB], ["hohoho",modifyTable]])


# Section VerifyDB
con= sqlite3.connect("DB/test.db") #Ã  changer selon le nom de la Db mais on se sait
cur = con.cursor()

def getLhsFromRow(row):
    lhs = row[:-1]
    return lhs

def getRhsFromRow(row):
    return row[-1]

def toString(col):
    string= ""
    for i in col:
        if i == " ":
            string += ","
        else:
            string += i
    return string

def verifyTablesDNF(table_name):

    ltr = list(cur.execute(f"SELECT lhs,rhs FROM FunctDep WHERE table_name = '{table_name}'"))

    for df in ltr:
        lhs = toString(df[0])
        rhs = df[1]
        
        d = cur.execute(f"SELECT {lhs},{rhs} FROM {table_name}")
        dicoLtr = {}
        for row in d:
            row_lhs = getLhsFromRow(row)
            row_rhs = getRhsFromRow(row)
            if(row_lhs in list(dicoLtr.keys())):
                if row_rhs != dicoLtr[row_lhs]:
                    print("biiip:" + str(row))
            else:
                dicoLtr[row_lhs] = row_rhs


def verifyAllDFs():
    names = list(cur.execute(f"SELECT table_name FROM FunctDep"))
    for name in names:
        print(name[0])
        verifyTablesDNF(name[0])


verifyAllDFs()