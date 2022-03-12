from fastapi import FastAPI , File, UploadFile, Form
from pydantic import BaseModel
import pandas as pd
from scipy import stats
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


app = FastAPI()

class QueryString(BaseModel):
    """
    This class only contains one element, a string called "query".
    This setup will set Pydantic to expect a dictionary of format:
    {"query": "Some sort of string"}
    """
    query: str



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


    if(type(data[x][0]) == str and type(data[y][0]) == str ):
        cats=[]
        cats1 = x1
        if cats1:
           cats2 = x2
           cats.append(cats1)
           cats.append(cats2)
           data = data[data[x].apply(lambda x: x in cats)]
        data=cat_cat(data,x,y)
    elif(type(data[x][0]) == str and type(data[y][0]) != str ):
        cats=[]
        cats1 =x1
        if cats1:
           cats2 = x2
           cats.append(cats1)
           cats.append(cats2)
           data = data[data[x].apply(lambda x: x in cats)]
        data = cat_num(data, x)

    # print(data.head())
    # print(find_conf(data,x,y))
    conf = find_conf(data,x,y)


    return {'filename': data_file.filename,
            'confounding_variable': conf

            }
