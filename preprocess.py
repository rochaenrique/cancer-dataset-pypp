import pandas as pd
import meds, util
from profile import Profile
import asyncio
import datetime, dateutil
import re

with Profile('Load file'):
    df = pd.read_csv('data/train.csv')

# drop columns
with Profile('Dropping columns'):
    df = df.drop(columns=[
        'favorite_color',
        'hospital',
        'education',
        'patient_id',
        'edad_paciente',
        'marital_status',
        'insurance_provider'
    ])

# gender
with Profile('sexo_paciente'):
    df['sexo_paciente'].value_counts()
    df['sexo_paciente'] = df['sexo_paciente'].apply(lambda x: 0 if str(x)[0] == 'F' else 1)

# cancer stage
with Profile('cancer_stage'):
    def parse_cancer_stage(x):
        s = str(x)
        return util.roman2int(s[6:]) if len(s) > 6 else 0
    
    df['cancer_stage'] = df['cancer_stage'].apply(parse_cancer_stage)

# genes
with Profile('Genes'):
    util.parse_gene(df, 'KRAS')
    util.parse_gene(df, 'BRAF')
    util.parse_gene(df, 'HER2')
    util.parse_gene(df, 'AR')
    util.parse_gene(df, 'C-KIT')
    
    # pos negative
    util.parse_condition(df, 'ER')
    util.parse_condition(df, 'PR')
    util.parse_condition(df, 'ALK')
    util.parse_condition(df, 'EGFR')
    util.parse_elevated(df, 'PSA')
    
    # low high
    util.parse_lowhigh(df, 'MSI')
    util.parse_lowhigh(df, 'PD-L1')

# hospital code
with Profile('hospital_code'):
    df['hospital_code'] = df['hospital_code'].apply(lambda x: int(str(x)[4:]))

# employment
with Profile('employment'):
    df['employment'] = df['employment'].apply(lambda x: 1 if x == "Employed" or x == "Student" else 0)

# date
with Profile('diagnosis_date_paciente'):
    df['diagnosis_date_paciente'] = df['diagnosis_date_paciente'].apply(lambda x: dateutil.parser.parse(x).timestamp())

# cancer subtype
with Profile('cancer_subtype'):
    cancer_subtype_count = df['cancer_subtype'].value_counts()
    df['cancer_subtype'] = df['cancer_subtype'].map(cancer_subtype_count/ sum(cancer_subtype_count))

# diagnosis
# TODO: If the diagnosis type matters change to one-hot encoding
# df = pd.get_dummies(df, columns=['diagnosis'], dtype=int)
with Profile('diagnosis'):
    df['has_cancer'] = df['diagnosis'].apply(lambda x: 0 if x == "No Cancer" else 1)
    df.drop(columns=['diagnosis'], inplace=True)

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
    util.freq_correct_col(df, 'symptoms')
    util.depth_summed_freq_encode(df, 'symptoms')

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
    util.freq_correct_col(df, 'comorbidities')
    util.depth_summed_freq_encode(df, 'comorbidities')
    
# medications
# text parse
# fetch rxcui
with Profile('medications'):
    asyncio.run(meds.parse_medications(df))

with Profile('Write out.csv'):
    df.to_csv('data/out.csv')
