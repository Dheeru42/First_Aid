import pandas as pd
from sklearn.model_selection import train_test_split
ram = pd.read_csv('die.csv')
# 
o_df = {'Yes':1,'No':0}
o_d = {'Low':0,'High':2,'Normal':1}
g_od = {'Male':0,'Female':1}
ram['Fever'] = ram['Fever'].map(o_df)
ram['Cough'] = ram['Cough'].map(o_df)
ram['Fatigue'] = ram['Fatigue'].map(o_df)
ram['Difficulty Breathing'] = ram['Difficulty Breathing'].map(o_df)
ram['Blood Pressure'] = ram['Blood Pressure'].map(o_d)
ram['Gender'] = ram['Gender'].map(g_od)
# Encoding
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
ram['Disease'] = le.fit_transform(ram['Disease'])
ram.head()
# 
x = ram.iloc[:,:-1]
y = ram['Outcome Variable']
# 
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2)
# 
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier()
rfc.fit(x_train,y_train)
rfc.score(x_test,y_test)*100,rfc.score(x_train,y_train)*100
# 
def encode_symptom(value):
    """Helper function to encode 'yes' as 1 and 'no' as 0."""
    return 1 if value.lower() == 'yes' else 0

def encode_gender(value):
    """Helper function to encode 'male' as 0 and 'female' as 1."""
    return 1 if value.lower() == 'female' else 0

def encode_bp(value):
    """Helper function to encode 'low' as 0, 'normal' as 1, and 'high' as 2."""
    if value.lower() == 'normal':
        return 1
    elif value.lower() == 'high':
        return 2
    else:
        return 0
# 
def dies(die,fever,cough,fatigue,db,age,gender,bp):
  encoded_gender = encode_gender(gender)
  encoded_fatigue = encode_symptom(fatigue)
  encod_db = encode_symptom(db)
  encod_fever = encode_symptom(fever)
  encod_cough = encode_symptom(cough)
  encod_bp = encode_bp(cough)
  patient = [[die,encod_fever,encod_cough,encoded_fatigue,encod_db,age,encoded_gender,encod_bp]]
  # 
  new_data = pd.DataFrame(patient,columns=x_train.columns)
  new_data['Disease']=le.transform(new_data['Disease'])
  result = rfc.predict(new_data)
  return result
  
# print(dies('Common Cold','No','No','No','No',24,'Male','Low'))