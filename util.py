import difflib
from rapidfuzz import process, fuzz
from collections.abc import Iterable
from math import sin, cos, pi

def clean_or_count(x, freq_map):
    s = str(x).lower()
    if similar(s, "None") > 0.7 or similar(s, "nan") > 0.7 or len(s) == 0:
        return 0
    
    items = s.split(",")
    for i in items:
        if i in freq_map:
            freq_map[i] += 1
        else:
            freq_map[i] = 0
    return items

def get_freq_corrected_map(freq_map):
    corrected = {}
    freq_list = list(freq_map.keys())

    for item in freq_list:
        if item in corrected:
            continue
        matches = process.extract(item, freq_list, scorer=fuzz.ratio, limit=200)
        corrected[item] = max(matches, key=lambda x: freq_map.get(x[0], 0))[0]

    return corrected

def apply_most_freq(items, most_frequent):
    if items == 0:
        return items
    return [most_frequent.get(el, el).strip() for el in items]

def sum_map_entries(key, val_map):
    return sum(val_map.get(el, 0) for el in key) if key != 0 else 0

def get_unique_set(items):
    return set(element for sublist in items if sublist != 0 for element in sublist)

def value_counts(items, freq_map = None):
    if freq_map is None:
        freq_map = {}
    for el in items:
        clean_or_count(el, freq_map)
    if freq_map is None:
        return freq_map

def depth_value_counts(items):
    freq_map = {}
    for sub in items:
        if type(sub) is not int:
            value_counts(sub, freq_map)
    return freq_map

def freq_correct_col(df, col_name):
    freq_map = {}
    df[col_name] = df[col_name].map(lambda x: clean_or_count(x, freq_map))
    corrected = get_freq_corrected_map(freq_map)
    df[col_name] = df[col_name].map(lambda x: apply_most_freq(x, corrected))

def depth_summed_freq_encode(df, col_name):
    freq_map = depth_value_counts(df[col_name].array)
    total = sum(freq_map.values())
    df[col_name] = df[col_name].apply(lambda x: sum_map_entries(x, freq_map) / total)

def roman2int(x: str) -> int:
    if x == "iv":
        return 4;
    else: 
        return x.count('i')

def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def parse_gene(df, gene):
    df[gene] = df[gene].apply(lambda x: 1 if x == "Mutated" else 0)
    
def parse_condition(df, gene):
        df[gene] = df[gene].apply(lambda x: 1 if x == "Positive" else 0)
        
def parse_elevated(df, gene):
        df[gene] = df[gene].apply(lambda x: 1 if x == "Elevated" else 0)

def lowhigh(x):
    s = str(x)
    if s == "Low":
        return 1
    elif s == "High":
        return 2
    return 0
    
def parse_lowhigh(df, gene):
    df[gene] = df[gene].apply(lowhigh)

def get_month_cycle(date):
    theta = pi * (date.month - 1) / 6
    return (sin(theta), cos(theta))
