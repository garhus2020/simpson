import pandas as pd
from scipy import stats
import numpy as np
from fix import adjust, adjustN, aggregate, aggregate_adj

def bool_to_str(pandasDF):
    booleandf = pandasDF.select_dtypes(include=[bool])
    booleanDictionary = {True: 'TRUE', False: 'FALSE'}

    for column in booleandf:
        pandasDF[column] = pandasDF[column].map(booleanDictionary)
    return pandasDF



def cat_cat(data , x, y):
    valsx=data[x].unique()
    valsy=data[y].unique()
    data[x] = data[x].replace({valsx[0]: 0, valsx[1]: 1})
    data[y] = data[y].replace({valsy[0]: 0, valsy[1]: 1})
    return data

def cat_num(data , x):
    valsx=data[x].unique()
    data[x] = data[x].replace({valsx[0]: 0, valsx[1]: 1})
    return data

def find_conf(df,x,y):
    results=[]
    rM = stats.pearsonr(df[x], df[y])[0]
    print(rM)
    cols=df.loc[:, ~df.columns.isin([x, y])].columns
    num_cols=df._get_numeric_data().columns
    pots=list(set(cols) - set(num_cols))
    for col in pots:
      vals=df[col].unique()
      print(vals)
      num_vals=len(df[col].unique())
      if(num_vals >10):
        continue
      coefs = []
      for val in vals:
        f=df[ df[col] == val]
        #print(f)
        if (f.shape[0] <3):
          coefs.append(-1)
          continue
        r = stats.pearsonr(f[x], f[y])[0]
        coefs.append(r)
        #print(r)
      if ((all(i > 0 for i in coefs) and rM <= 0) or (all(i < 0 for i in coefs) and rM >= 0)):
              print(col)
              print("Simpson Paradox holds for this dataset \n")
              print(coefs)
              results.append((col, 100000))
      else:
              if (rM> 0):
                print("\n Number of reversed subgroups ")
                print(col)
                print(sum(1 for i in coefs if i < 0))
                print(coefs)
                results.append((col,sum(1 for i in coefs if i < 0)))
              elif (rM < 0):
                print("\n Number of reversed subgroups ")
                print(col)
                print(sum(1 for i in coefs if i > 0))
                print(coefs)
                results.append((col, sum(1 for i in coefs if i > 0)))
              else:
                print("\n Number of reversed subgroups ")
                print(sum(1 for i in coefs if i != 0))
                print(coefs)
                results.append((col, sum(1 for i in coefs if i != 0)))
    return max(results , key = lambda x: x[1])[0]





def main():
    # C:\Users\huseyn98\Downloads\kidney_stone_data.csv
    # C:\Users\huseyn98\Downloads\admission_data.csv
    # C:\Users\huseyn98\Downloads\penguins_size.csv
    # C:\Users\huseyn98\Downloads\californiaDDSDataV2.csv
    # C:\Users\huseyn98\Downloads\iris.csv
    # C:\Users\huseyn98\Downloads\auto-mpg.csv

    #  sepal_length  sepal_width  petal_length petal_width

    # displacement  horsepower   acceleration weight
    # treatment success
    # culmen_length_mm  culmen_depth_mm
    path = input("enter path to  csv file : ")
    data = pd.read_csv(path)
    data = data.dropna()
    x = input("enter x var name : ")
    y = input("enter y var name : ")
    data = bool_to_str(data)


    if(type(data[x][0]) == str and type(data[y][0]) == str ):
        cats=[]
        cats1 = input("Enter first pivot cat for x, press enter if none : ")
        if cats1:
           cats2 = input("Enter first pivot cat for x, press enter if none : ")
           cats.append(cats1)
           cats.append(cats2)
           data = data[data[x].apply(lambda x: x in cats)]
        data=cat_cat(data,x,y)
    elif(type(data[x][0]) == str and type(data[y][0]) != str ):
        cats=[]
        cats1 = input("Enter first pivot cat for x, press enter if none : ")
        if cats1:
           cats2 = input("Enter first pivot cat for x, press enter if none : ")
           cats.append(cats1)
           cats.append(cats2)
           data = data[data[x].apply(lambda x: x in cats)]
        data = cat_num(data, x)

    # print(data.head())
    conf = find_conf(data,x,y)

    # print(data.tail())
    aggregate(data,x,y,conf)
    aggregate_adj(data,x,y,conf)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

