import pandas as pd
import re

def normalize_arabic_name(name):
    name = name.strip()
    name = name.replace('أ', 'ا')
    name = name.replace('إ', 'ا')
    name = name.replace('آ', 'ا')
    name = name.replace('ئ', 'ى')
    name = name.replace('ي', 'ى')
    name = name.replace('ؤ', 'و')
    name = name.replace('ة', 'ه')

    name = name.replace('ً', '')   # Remove tanween fatha
    name = name.replace('ٌ', '')   # Remove tanween damma
    name = name.replace('ٍ', '')   # Remove tanween kasra
    name = name.replace('َ', '')   # Remove fatha
    name = name.replace('ُ', '')   # Remove damma
    name = name.replace('ِ', '')   # Remove kasra
    name = name.replace('ّ', '')   # Remove shadda
    name = name.replace('ْ', '')   # Remove sokon
    
    name = re.sub(r'[^\w\s\[\]{}()<>]', '', name)  # Remove punctuation excluding brackets
    name = re.sub('\s+', ' ', name)
    
    return name

prePatterns = [
]

postPatterns = [
    NamesProcessing.Pattern(pattern=r'[\d\s]*([^\d]+$)', group=1)
]

prefixes = [
    "ابن",
    "ابو",
    "ام",
    "بن"
]

class Pattern:
    def __init__(self, pattern, group):
        self.pattern = pattern
        self.group = group
        
class Name:
    def __init__(self, fullName, allNames, prePatterns = prePatterns, postPatterns = [],
                 prefixes = [], normalizer = normalize_arabic_name):
        self.FullName, self.OtherInfo = _find_other_info(fullName)
        self.FullNameNormalized = normalizer(self.FullName)
        self.ComposingNamesNormalized = _parse_names_from_list(
                                            self.FullNameNormalized,
                                            allNames, prePatterns,
                                            postPatterns, prefixes)
    
def _find_other_info(fullName):
    extracted_text = re.findall(r'[\[{(<]([^\[\]{}()<>]*)[\]})>]', fullName)
    fullName = re.sub(r'[\[{(<][^\[\]{}()<>]*[\]})>]', '', fullName)
    # Flatten the list of extracted text
    extracted_text = [text for text in extracted_text if text]

    return fullName, extracted_text

def _process_names_with_regex(patterns, fullNameNormalized, composingNames, index):
    for pattern in patterns:        
        match = re.search(pattern.pattern, fullNameNormalized)
        while match:
            group = match.group(pattern.group)
            fullNameNormalized = fullNameNormalized.replace(group, str(index))
            composingNames[str(index)] = group
            index += 1
            match = re.search(pattern.pattern, fullNameNormalized)
    return index, fullNameNormalized

def _replace_name(fullNameNormalized, nameNormalized, replacement):
    posStart = fullNameNormalized.find(nameNormalized)
    posEnd = posStart + len(nameNormalized)

    if posStart != 0:
        nameNormalized = ' ' + nameNormalized
        replacement = ' ' + replacement

    if posEnd != len(fullNameNormalized):
        nameNormalized += ' '
        replacement += ' '

    return fullNameNormalized.replace(nameNormalized, replacement)

def _find_prefix(prefixes, string, position):
    for prefix in prefixes:
        if string.startswith(prefix, position - len(prefix) - 1):
            return prefix
    return None

def _add_prefix_to_name(fullNameNormalized, nameNormalized, posStart, prefixes):
    prefix = _find_prefix(prefixes, fullNameNormalized, posStart)
    if prefix:
        nameNormalized = f"{prefix} {nameNormalized}"
        posStart -= len(prefix) + 1
    return nameNormalized, posStart

def _replace_all_prefixes(fullNameNormalized, composingNames, index, prefixes):
    patterns = []
    for prefix in prefixes:
        pattern = f'({re.escape(prefix)}\s[^\d\s]+)'
        group = 1
        patterns.append(Pattern(pattern=pattern, group=group))
        
    return _process_names_with_regex(patterns, fullNameNormalized, composingNames, index)

def _parse_names_from_list(fullNameNormalized, allNamesNormalized, prePatterns, postPatterns, prefixes):
    composingNames = dict()  
    i, fullNameNormalized = _process_names_with_regex(prePatterns, fullNameNormalized, composingNames, 0)

    allNamesNormalized.sort(key=len, reverse=True)

    for nameNormalized in allNamesNormalized:
        posStart = fullNameNormalized.find(nameNormalized)
        if posStart != -1:
            replacement = str(i)
            nameNormalized, posStart = _add_prefix_to_name(fullNameNormalized, nameNormalized, posStart, prefixes)
            composingNames[replacement] = nameNormalized
            fullNameNormalized = _replace_name(fullNameNormalized, nameNormalized, replacement)
            i += 1
    
    i, fullNameNormalized = _replace_all_prefixes(fullNameNormalized, composingNames, i, prefixes)
    i, fullNameNormalized = _process_names_with_regex(postPatterns, fullNameNormalized, composingNames, i)
    composingNamesNormalized = [composingNames.get(x, x) for x in fullNameNormalized.split(' ')]
    return composingNamesNormalized


def get_arabic_names_df(normalizer = normalize_arabic_name):
    dfAllNames = pd.read_csv('NamesProcessing/Sultan_Qaboos_Encyclopedia_Names.csv')

    dfAllNames['Normalized_Name'] = dfAllNames.apply(lambda row: normalizer(row['Name']), axis=1)
    dfAllNames.sort_values(by='Normalized_Name', key=lambda col: col.str.len(), inplace=True, ascending=False)
    
    return dfAllNames