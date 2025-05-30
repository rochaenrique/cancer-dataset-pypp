import pandas as pd
import util
from profiler import Profile
import asyncio
import datetime, dateutil
from sklearn import set_config
import re
import sys

if len(sys.argv) < 4:
    print('Error: Expected input and output file names')
    print(f'Usage: {sys.argv[0]} <data_type> <in.csv> <out.csv>')
    exit(1)
elif sys.argv[1] != 'train' and sys.argv[1] != 'test':
    print(f'Data type must be \'train\' or \'test\'')
    exit(1)

is_train    = sys.argv[1] == 'train'
input_file  = sys.argv[2]
output_file = sys.argv[3]

set_config(transform_output="pandas")

with Profile(f'Loading {input_file}'):
    df = pd.read_csv(input_file)

# drop columns
with Profile('Dropping columns'):
    df.drop(columns=[
        'favorite_color',
        'hospital',
        'education',
        'edad_paciente',
        'marital_status',
        'insurance_provider',
    ], inplace=True)
   
if False:
    # cancer subtype
    with Profile('cancer_subtype'):
        cancer_subtype_count = df['cancer_subtype'].value_counts()
        df['cancer_subtype'] = df['cancer_subtype'].map(cancer_subtype_count/ sum(cancer_subtype_count))
    
    # # diagnosis
    # # TODO: If the diagnosis type matters change to one-hot encoding
    # df = pd.get_dummies(df, columns=['diagnosis'], dtype=int)
    with Profile('diagnosis'):
        df['has_cancer'] = df['diagnosis'].apply(lambda x: 0 if x == "No Cancer" else 1)
        df.drop(columns=['diagnosis'], inplace=True)
    
# gender
with Profile('sexo_paciente'):
    df['sexo_paciente'].value_counts()
    df['sexo_paciente'] = df['sexo_paciente'].apply(lambda x: 0 if str(x)[0] == 'F' else 1)
    
# hospital code
with Profile('hospital_code'):
    df['hospital_code'] = df['hospital_code'].apply(lambda x: int(str(x)[4:]))

# employment
with Profile('employment'):
    df['employment'] = df['employment'].apply(lambda x: 1 if x == "Employed" or x == "Student" else 0)

# date
# cycling encoding to the month
# just the value to the year
# disregarding day and time
with Profile('diagnosis_date_paciente'):
    df['diagnosis_date_paciente_month_cycle_x'] = 0.0
    df['diagnosis_date_paciente_month_cycle_y'] = 0.0
    df['diagnosis_date_paciente_year'] = 0
  
    for index, row in df.iterrows():
        date = dateutil.parser.parse(row['diagnosis_date_paciente'])
        month_cycle = util.get_month_cycle(date)
      
        df.at[index, 'diagnosis_date_paciente_year'] = date.year
        df.at[index, 'diagnosis_date_paciente_month_cycle_x'] = month_cycle[0]
        df.at[index, 'diagnosis_date_paciente_month_cycle_y'] = month_cycle[1]

    df.drop(columns=['diagnosis_date_paciente'], inplace=True)

# blood type
# parse with A B and R+ R- matrix
# one-hot encoding
with Profile('blood_type'):
  df['blood_group_a'] = 0
  df['blood_group_b'] = 0
  df['blood_r_factor'] = 0
  
  for index, row in df.iterrows():
      blood_type = str(row['blood_type'])
      if "A" in blood_type:
          df.at[index, 'blood_group_a'] = 1
      if "B" in blood_type:
          df.at[index, 'blood_group_b'] = 1
      if "+" in blood_type:
          df.at[index, 'blood_r_factor'] = 1
          
  df.drop(columns=['blood_type'], inplace=True)

# doctor
# text parsing
# frequency encoding
with Profile('doctor'):
    def remove_first_prefix(name) -> str:
        if name == 0:
            return
        terms = name.split(' ')
        if len(terms) < 2:
            return terms[0]
        return ''.join(terms[1:])

    df['doctor'] = df['doctor'].apply(remove_first_prefix)
    util.freq_correct_col(df, 'doctor')
  
    df['doctor'] = df['doctor'].apply(lambda x: x[0] if x != 0 else 0)
    doctor_count = df['doctor'].value_counts()
    total_doctor_count = sum(doctor_count)
    df['doctor'] = df['doctor'].map(doctor_count / total_doctor_count)

# symptoms
# text parsing
# freq encoding
with Profile('symptoms'):
    util.multi_label_encode(df, 'symptoms', cleanup_col_names=True)
    df.drop(columns = ['symptoms'], inplace=True)
  
# comorbidities
# text parsing
# one-hot encoding if not too many
with Profile('comorbidities'):
    def clean_str_list(x, regex):
        if x == 0: 
            return x
        return regex.sub(r'', str(x)).replace('|', ',')
    regex = re.compile(r'[\[\'"\]\\]')
  
    df['comorbidities'] = df['comorbidities'].apply(lambda x: clean_str_list(x, regex))
    util.multi_label_encode(df, 'comorbidities', cleanup_col_names=True)
    df.drop(columns = ['comorbidities'], inplace=True)
  
# medications
# text parse
with Profile('medications'):
    util.multi_label_encode(df, 'medications', cleanup_col_names=True)
    df.drop(columns = ['medications'], inplace=True)

with Profile(f'Writing {output_file}'):
    df.to_csv(output_file)
