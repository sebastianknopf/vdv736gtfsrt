from datetime import datetime
from typing import List

def create_translated_string(languages: List[str], texts: List[str]) -> dict:
    translated_string = dict()
    translated_string['translation'] = list()

    if len(languages) != len(texts):
        raise ValueError('the number of languages must be the same like the number of texts')
    
    for n in range(0, len(languages)):
        translated_string['translation'].append({
            'language': languages[n].lower(),
            'text': texts[n]
        })

    return translated_string

def create_url(urldict: dict, **variables) -> dict:
        
    languages = list()
    texts = list()
    for lang, template in urldict.items():
        url = template
        for key, value in variables.items():
            tkey = f"[{key}]"
            url = url.replace(tkey, value)

        languages.append(lang)
        texts.append(url)
    
    return create_translated_string(languages, texts)

def iso2unix(iso_timestamp: str) -> int:
        dt = datetime.strptime(iso_timestamp, '%Y-%m-%dT%H:%M:%SZ')
        return int((dt - datetime(1970, 1, 1)).total_seconds())