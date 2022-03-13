import pandas as pd
import random


def flatten(t):
    return [item for sublist in t for item in sublist]

def aggregate (df, x, y, conf):
    new= df.groupby(x)[y].mean().reset_index()
    #print(new)
    new2= df.groupby([x,conf])[y].mean().reset_index()
    #print(new2)
    return new,new2



def aggregate_adj (df, x, y, conf):
    res = df.groupby([x, conf])[y].mean().reset_index()
    new1= df.groupby(x)[y].count().reset_index()
    new2= df.groupby([x,conf])[y].count().reset_index()
    # print(new2.reset_index())
    # print(new1.reset_index())
    res["adj"]=1.5
    for index, row in res.iterrows():
        adj= new1[new1[x] == row[x]][y] /new2.loc[index][y]
        val= res.loc[index][y]/new2.loc[index][y]*new1[new1[x] == row[x]][y]
        res.at[index, y]=val
        res.at[index, 'adj'] = adj

    nom = res.groupby(x)[y].sum().reset_index()
    denom = res.groupby(x)['adj'].sum().reset_index()
    for index, row in nom.iterrows():
        val= nom.loc[index][y]/denom.loc[index]['adj']
        nom.at[index,y]=val
    #print(nom)
    return nom




def adjust(  df , x ,y, conf ):
    cs = df[conf].unique()
    sam = []
    for i in cs:
        indexM = df[(df[x] == 1) & (df[conf] == i)].index.to_list()
        indexF = df[(df[x] == 0) & (df[conf] == i)].index.to_list()
        print(indexM)
        print(indexF)
        if (len(indexM) > len(indexF)):
            sam.append(random.sample(indexM, len(indexM) - len(indexF)))
        elif (len(indexM) < len(indexF)):
            sam.append(random.sample(indexF, len(indexF) - len(indexM)))



    print(sam)
    #df = df.drop(df.index[flatten(sam)])
    df = df[~df.index.isin(flatten(sam))]
    return df



def adjustN(  df , x , conf ):
    cs = df[conf].unique()
    sam = []
    lens = [ len(df[df[conf] == i]) for i in cs]
    minimum = min(lens)
    for i in cs:
        ins = df[ (df[conf] == i)].index.to_list()
        sam.append(random.sample(ins, len(ins) - minimum))
    print(flatten(sam))
    df = df[~df.index.isin(flatten(sam))]

    #df = df.drop(df.index[flatten(sam).sort()] ,  inplace=True)
    return df