# ArabicNamesParser

## Overview

This Python module, `NamesProcessing`, provides functions and classes for processing and normalizing Arabic names. It includes methods for handling prefixes, patterns, and extracting information from complex name structures.

## Exported Functions and Classes

* **Name Class**

  * Represents an Arabic name with methods for normalization and parsing.
  * The available properties are:
    1. `FullName`: The original full name.
    2. `OtherInfo`: Additional information extracted from brackets or parentheses in the full name.
    3. `FullNameNormalized`: The normalized version of the full name using the `normalize_arabic_name` function.
    4. `ComposingNamesNormalized`: A list of normalized composing names extracted from the full name, considering prefixes and patterns.
* **Pattern Class**

  * Defines a pattern used for identifying and extracting parts of the full name as a single entry.
* **normalize_arabic_name Function**

  * Normalizes Arabic names by replacing specific characters and removing diacritics.
* **get_arabic_names_df Function**

  * The fubction relies on the [Sultan Qaboos Encyclopedia of Arabic Names](http://arabiclexicon.hawramani.com/sultan-qaboos-encyclopedia-of-arab-names/) dataset, available in the file `Sultan_Qaboos_Encyclopedia_Names.csv`.

## Usage

### Classes

#### Name

There are optional parameters that can be provided when creating an instance:

1. `prePatterns`: A list of pre-defined patterns used before trying to extract any composing name.
2. `postPatterns`: A list of post-patterns used after extracting names and before splitting names by space as a last resort.
3. `prefixes`: A list of prefixes that may appear in names such as `ابو، ابن، ام، بن`.
4. `normalizer`: A function used for normalizing names; by default, it uses the `normalize_arabic_name` function.

```python
fullName = "ابن علي [Ibn Ali]"
allNamesNormalized = ["على", "عبد الله", "محمد"]
name_instance = Name(fullName, allNamesNormalized)
```

* `FullName`: "ابن علي [Ibn Ali]"
* `OtherInfo`: ["Ibn Ali"]
* `FullNameNormalized`: "ابن على"
* `ComposingNamesNormalized`: ["ابن", "على"]

#### Pattern

```python
pattern_instance = Pattern(pattern=r'[\d\s]*([^\d]+$)', group=1)
```

### Functions

#### normalize_arabic_name

```python
normalized_name = normalize_arabic_name("أحمد")
```

#### get_arabic_names_df

There is an optional parameter to customize the normalization:

* `normalizer`: A function used for normalizing names; by default, it uses the `normalize_arabic_name` function.

```python
df_names = get_arabic_names_df()
```

## Dependencies

* `pandas`: Used for handling data frames.
* `re`: Python regular expression module.

## Contributing

Feel free to contribute by opening issues or creating pull requests. We welcome any improvements or suggestions to enhance the functionality of this module
