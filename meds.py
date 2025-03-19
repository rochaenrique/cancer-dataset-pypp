import util
import asyncio
import aiohttp

cache = {}
URL = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
async def getrxcui(session, term) -> int:
    async with session.get(f'{URL}?term={term}') as res:
        try: 
            data = await res.json()
            if 'approximateGroup' in data:
                num = int(data['approximateGroup']['candidate'][0]['rxcui'])
                cache[term] = num
                return num
        except (KeyError, IndexError):
            pass
    cache[term] = 0        
    return 0

async def fetch_ids(medications):
    async with aiohttp.ClientSession() as session:
        tasks = [getrxcui(session, med) for med in medications]
        results = await asyncio.gather(*tasks)
        return dict(zip(medications, results))

async def parse_medications(df):
    util.freq_correct_col(df, 'medications')
    
    unique_meds = util.get_unique_set(df['medications'])
    id_map = await fetch_ids(unique_meds)
    
    df['medications'] = df['medications'].map(lambda x: util.sum_map_entries(x, id_map))
