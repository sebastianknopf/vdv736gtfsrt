import re

from datetime import datetime
from io import StringIO
from html.parser import HTMLParser
from typing import List

class _HtmlTagStripper(HTMLParser):
     
    def __init__(self) -> None:
         super().__init__()
         
         self.reset()
         self.strict = False
         self.convert_charrefs = True
         self.text = StringIO()

    def handle_data(self, d: str) -> None:
         self.text.write(d)

    def get_stripped_text(self) -> str:
         return self.text.getvalue()
    
def _strip_tags(input: str) -> str:
     s = _HtmlTagStripper()
     s.feed(input)

     return s.get_stripped_text()

def create_translated_string(languages: List[str], texts: List[str]) -> dict:
    translated_string = dict()
    translated_string['translation'] = list()

    if len(languages) != len(texts):
        raise ValueError('the number of languages must be the same like the number of texts')
    
    for n in range(0, len(languages)):
        
        translated_text = _strip_tags(texts[n])
        translated_text = translated_text.replace('\t', '')
        translated_text = re.sub(' +', ' ', translated_text)
        
        translated_string['translation'].append({
            'language': languages[n].lower(),
            'text': translated_text
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