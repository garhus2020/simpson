from fastapi import FastAPI , File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from scipy import stats
from fix import adjust, adjustN, aggregate, aggregate_adj
import json
import time

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

def reverse_cat_num(data_copy,data , x):
    valsx=data_copy[x].unique()
    data[x] = data[x].replace({0: valsx[0], 1: valsx[1]})
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
              results.append((col, 1))
      else:
              if (rM> 0):
                print("\n Number of reversed subgroups ")
                print(sum(1 for i in coefs if i <= 0)/num_vals)
                results.append((col,sum(1 for i in coefs if i <= 0)/num_vals))
              elif (rM < 0):
                print("\n Number of reversed subgroups ")
                print(sum(1 for i in coefs if i >= 0)/num_vals)
                results.append((col, sum(1 for i in coefs if i >= 0)/num_vals))
              else:
                print("\n Number of reversed subgroups ")
                print(sum(1 for i in coefs if i != 0)/num_vals)
                results.append((col, sum(1 for i in coefs if i != 0)/num_vals))

    con = max(results , key = lambda x: x[1])
    return (con[0],con[1])







app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Add a simple GET response at the base url "/"
@app.get("/")
def read_root():
    return {"test_response": "Hello World!"}


@app.post('/uploadfile/')
async def create_data_file(
        experiment: str = Form(...),
        data_file: UploadFile = File(...),
):
    # decoded = base64.b64decode(data_file.file)
    # decoded = io.StringIO(decoded.decode('utf-8'))

    print(pd.read_csv(data_file.file))

    return {'filename': data_file.filename,
            'experiment': experiment}


@app.post('/confounder/')
async def find_confounder(
        x: str = Form(...),
        y: str = Form(...),
        x1: str = Form(...),
        x2: str = Form(...),
        data_file: UploadFile = File(...),):

    data = pd.read_csv(data_file.file)
    data = data.dropna()
    # x = input("enter x var name : ")
    # y = input("enter y var name : ")
    data = bool_to_str(data)
    data_copy = data.copy()
    flag=0

    if(type(data[x][0]) == str and type(data[y][0]) == str ):
        flag=1
        cats=[]
        cats1 = x1
        if cats1:
           cats2 = x2
           cats.append(cats1)
           cats.append(cats2)
           data = data[data[x].apply(lambda x: x in cats)]
        data=cat_cat(data,x,y)
    elif(type(data[x][0]) == str and type(data[y][0]) != str ):
        flag=1
        cats=[]
        cats1 =x1
        if cats1:
           cats2 = x2
           cats.append(cats1)
           cats.append(cats2)
           data = data[data[x].apply(lambda x: x in cats)]
        data = cat_num(data, x)

    conf,prop = find_conf(data,x,y)
    #js = data.to_json(orient='index')

    if (flag ==0):
        time.sleep(3)
        return {
                'confounding_variable': conf,
                'reversed_params': prop
                }

    agg_data, disagg_data = aggregate(data,x,y,conf)
    agg_data, disagg_data = json.loads(json.dumps(reverse_cat_num(data_copy,agg_data,x).to_json(orient='records'))), json.loads(json.dumps(reverse_cat_num(data_copy,disagg_data,x).to_json(orient='records')))
    fixed_agg_data = aggregate_adj(data,x,y,conf)
    fixed_agg_data = json.loads(json.dumps(reverse_cat_num(data_copy,fixed_agg_data,x).to_json(orient='records')))
    time.sleep(3)
    return {
            'confounding_variable': conf,
            'reversed_params': prop
            }
    # return {'filename': data_file.filename,
    #         'confounding_variable': conf,
    #         'reversed_params' : prop,
    #         'agg_data': agg_data,
    #         'disagg_date': disagg_data,
    #         'fixed_agg_data': fixed_agg_data
    #         }
