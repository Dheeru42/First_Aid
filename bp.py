import pandas as pd
from sklearn.model_selection import train_test_split
ram = pd.read_csv('blood_pressure.csv')
# 
o_df = {'Yes':1,'No':0}
o_d = {'Low':0,'High':2,'Normal':1}
g_od = {'Male':0,'Female':1}
ram['Headache'] = ram['Headache'].map(o_df)
ram['Dizziness'] = ram['Dizziness'].map(o_df)
ram['Fatigue'] = ram['Fatigue'].map(o_df)
ram['Shortness_of_Breath'] = ram['Shortness_of_Breath'].map(o_df)
ram['Blurred_Vision'] = ram['Blurred_Vision'].map(o_df)
ram['Chest_Pain'] = ram['Chest_Pain'].map(o_df)
ram['Sweating'] = ram['Sweating'].map(o_df)
ram['Sleep_Problems'] = ram['Sleep_Problems'].map(o_df)
ram['Swelling_in_legs'] = ram['Swelling_in_legs'].map(o_df)
ram['Tinnitus'] = ram['Tinnitus'].map(o_df)
ram['Irregular_Heartbeat'] = ram['Irregular_Heartbeat'].map(o_df)
ram['Hypertension_Level'] = ram['Hypertension_Level'].map(o_d)
ram['Gender'] = ram['Gender'].map(g_od)
# 
x = ram.iloc[:,:-1]
y = ram['Hypertension_Level']
# 
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2)
# 
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier()
rfc.fit(x_train,y_train)
# rfc.score(x_test,y_test)*100,rfc.score(x_train,y_train)*100
# 
def encode_symptom(value):
    """Helper function to encode 'yes' as 1 and 'no' as 0."""
    return 1 if value.lower() == 'yes' else 0

def encode_gender(value):
    """Helper function to encode 'male' as 0 and 'female' as 1."""
    return 1 if value.lower() == 'female' else 0
# 
def bpmodel(age,gender,headache,dizziness,bv,cp,fatigue,sb,ih,sw,sp,sil,ti):
  # print('<---- Welcome To RAM Hospital Check Yourself From Disease ---->')
  encoded_gender = encode_gender(gender)
  encoded_headache = encode_symptom(headache)
  encoded_dizziness = encode_symptom(dizziness)
  encoded_bv = encode_symptom(bv)
  encoded_cp = encode_symptom(cp)
  encoded_fatigue = encode_symptom(fatigue)
  encoded_sb = encode_symptom(sb)
  encoded_ih = encode_symptom(ih)
  encoded_sw = encode_symptom(sw)
  encoded_sp = encode_symptom(sp)
  encoded_sil = encode_symptom(sil)
  encoded_ti = encode_symptom(ti)
  patient = [[age, encoded_gender, encoded_headache, encoded_dizziness, encoded_bv, encoded_cp,
              encoded_fatigue, encoded_sb, encoded_ih, encoded_sw, encoded_sp, encoded_sil, encoded_ti]]
  new_data = pd.DataFrame(patient,columns=x_train.columns)
  result = rfc.predict(new_data)
  return result
  
# print(bpmodel(24,'No','No','No','No','No','No','No','No','No','No','No','No'))
