import pandas as pd
import itertools
import re
import os

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

class Pattern:
    def __init__(self, pattern, group):
        self.pattern = pattern
        self.group = group

prePatterns = [
]

postPatterns = [
    # Pattern(pattern=r'[\d\s]*([^\d]+$)', group=1)
]

prefixes = [
    "ابن",
    "ابو",
    "ام",
    "بن"
]

postfixes = [
    "الله",
    "الدىن",
    "النبى",
    "الرسول",
]

class Name:
    def __init__(self, fullName, allNames, prePatterns = prePatterns, postPatterns = postPatterns,
                 prefixes = prefixes, normalizer = normalize_arabic_name, postfixes = postfixes):
        cp_prefixes = []
        for prefix in prefixes:
            cp_prefixes.append(normalizer(prefix))
        cp_postfixes = []
        for postfix in postfixes:
            cp_postfixes.append(normalizer(postfix))
        self.FullName, self.OtherInfo = _find_other_info(fullName)
        self.FullNameNormalized = normalizer(self.FullName)
        self.ComposingNamesNormalized = _parse_names_from_list(
                                            self.FullNameNormalized,
                                            allNames, prePatterns,
                                            postPatterns, cp_prefixes, cp_postfixes)
    
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

def _replace_name(fullNameNormalized, nameNormalized, replacement, posStart, max_replacements):
             
    posEnd = posStart + len(nameNormalized)

    if posStart != 0:
        nameNormalized = ' ' + nameNormalized
        replacement = ' ' + replacement

    if posEnd != len(fullNameNormalized):
        nameNormalized += ' '
        replacement += ' '
        
    return fullNameNormalized.replace(nameNormalized, replacement, max_replacements)

def _find_prefix(prefixes, string, position):
    for prefix in prefixes:
        if position > 0:
            #check if a prefix exists before starting position and make sure prefix is a separate word
            if string.startswith(' '+prefix if position > len(prefix)+1 else prefix, max(0, position - len(prefix) - 2)):
                return prefix
    return None

def _find_postfix(postfixes, string, word, position):
    for postfix in postfixes:
        if position > 0:
            #check if a postfix exists after starting string and make sure postfix is a separate word
            if string.startswith(word + ' ' + postfix + ' ', position) or string.endswith(word + ' ' + postfix):
                return postfix
    return None

def _add_prefix_to_name(fullNameNormalized, nameNormalized, posStart, prefixes):
    prefix = _find_prefix(prefixes, fullNameNormalized, posStart)
    if prefix:
        nameNormalized = f"{prefix} {nameNormalized}"
        posStart -= len(prefix) + 1
    return nameNormalized, posStart

def _add_postfix_to_name(fullNameNormalized, nameNormalized, posStart, postfixes):
    postfix = _find_postfix(postfixes, fullNameNormalized, nameNormalized, posStart)
    if postfix:
        nameNormalized = f"{nameNormalized} {postfix}"
    return nameNormalized, posStart

def _replace_all_fixes(fullNameNormalized, composingNames, index, prefixes, postfixes):
    patterns = []
    for prefix, postfix in itertools.product(postfixes, prefixes):
        pattern = f'({re.escape(prefix)}\s[^\d\s]+\s{re.escape(postfix)})'
        group = 1
        patterns.append(Pattern(pattern=pattern, group=group))
    
    for prefix in prefixes:
        pattern = f'({re.escape(prefix)}\s[^\d\s]+)'
        group = 1
        patterns.append(Pattern(pattern=pattern, group=group))
    
    for posfix in postfixes:
        pattern = f'([^\d\s]+\s{re.escape(posfix)})'
        group = 1
        patterns.append(Pattern(pattern=pattern, group=group))
        
    return _process_names_with_regex(patterns, fullNameNormalized, composingNames, index)

def _parse_names_from_list(fullNameNormalized, allNamesNormalized, prePatterns, postPatterns, prefixes, postfixes=[]):
    composingNames = dict()  
    i, fullNameNormalized = _process_names_with_regex(prePatterns, fullNameNormalized, composingNames, 0)

    allNamesNormalized.sort(key=len, reverse=True)

    for nameNormalized in allNamesNormalized:
        og_nameNormalized = nameNormalized
        og_fullNameNormalized = ''
        posStart = 0
        while posStart != -1 and og_fullNameNormalized != fullNameNormalized:
            nameNormalized = og_nameNormalized
            og_fullNameNormalized = fullNameNormalized
            posStart = fullNameNormalized.find(nameNormalized)
            if posStart != -1:
                replacement = str(i)
                nameNormalized, posStart = _add_prefix_to_name(fullNameNormalized, nameNormalized, posStart, prefixes)
                nameNormalized, posStart = _add_postfix_to_name(fullNameNormalized, nameNormalized, posStart, postfixes)
                composingNames[replacement] = nameNormalized
                fullNameNormalized = _replace_name(fullNameNormalized, nameNormalized, replacement, posStart, 1)
                i += 1            
    
    i, fullNameNormalized = _replace_all_fixes(fullNameNormalized, composingNames, i, prefixes, postfixes)
    i, fullNameNormalized = _process_names_with_regex(postPatterns, fullNameNormalized, composingNames, i)
    composingNamesNormalized = [composingNames.get(x, x) for x in fullNameNormalized.split(' ')]
    return composingNamesNormalized

def _get_arabic_names_df_pickled(pickle_name):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    filePartialPath = os.path.join(script_directory, pickle_name)
    return pd.read_pickle(filePartialPath+".pickle")

def _get_arabic_names_df():
    df1 = _get_arabic_names_df_pickled('Sultan_Qaboos_Encyclopedia_Names')
    df2 = _get_arabic_names_df_pickled('muslimbabynames_hawramani')
    df3 = _get_arabic_names_df_pickled('additional_names')

    dfAllNames = pd.concat([df1, df2, df3])
    dfAllNames.sort_values(by='Normalized_Name', key=lambda col: col.str.len(), inplace=True, ascending=False)
    return dfAllNames
    
def get_arabic_names_df(normalizer = None):
    dfAllNames = _get_arabic_names_df()
    
    if normalizer != None:
        dfAllNames['Normalized_Name'] = dfAllNames.apply(lambda row: normalizer(row['Name']), axis=1)
        dfAllNames.sort_values(by='Normalized_Name', key=lambda col: col.str.len(), inplace=True, ascending=False)
        
    return dfAllNames