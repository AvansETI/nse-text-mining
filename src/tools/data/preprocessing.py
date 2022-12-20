import copy
import os
import re
from enchant.checker import SpellChecker
import enchant
import numpy as np
from tools.utils.value_checks import is_number


def replace_empty_with_placeholder_empty(data):
    """
    Replace all NA values with the string 'EMPTY_FIELD'
    """
    data.fillna('EMPTY_FIELD', inplace=True)
    data.head()


def remove_punctuation(data, column_name):
    """
    Remove all punctuation from a column in a dataset
    """

    # Remove all punctuation using regex
    data[column_name] = \
        data[column_name].map(lambda x: re.sub('\\W', ' ', x) if not is_number(x) else x)


def to_lower(data, column_name):
    """
    Convert column in dataset to lowercase letters
    """

    # convert all text to lower
    data[column_name] = \
        data[column_name].map(lambda x: x.lower() if not is_number(x) else x)


def check_spelling(data, language, custom_dicts=[]):
    """
    Check spelling of all answers using the languages defined in language (ex: ['nl-NL', 'en-EN'], default: ['nl-NL', 'en-EN'])
    """
    # TODO: fix checks
    # make sure the rights types are passed
    # if not isinstance(language, array.ArrayType):
    #     raise Exception('Language must be of array type')
    # if not isinstance(custom_dicts, array.ArrayType):
    #     raise Exception('Custom_dicts must be of array type')

    # Construct spell checkers for each language
    checkers = [SpellChecker(enchant.DictWithPWL(lang, './src/dicts/ignore.txt')) for lang in language]
    custom_checkers = [SpellChecker(enchant.PyPWL(dict)) for dict in custom_dicts]
    checkers = checkers + custom_checkers

    # Dictionary containing the errors for each language
    misspelled = {}

    # flatten the data and split into words,
    # then check spelling for each language and add results to dict
    # words = [word for word in (answer for answer in (col for col in data))]

    words = [word for word in (row.split() for row in data)]
    words = np.hstack(words)

    for checker in checkers:
        misspelled[checker.lang] = list([word for word in words if not checker.check(word)])
        # filter(lambda x: x if not x else None,

    return misspelled


def clean(data, columns=[], exclude=True):
    """
    Runs all preprocessing cleaning methods on the given data for the given columns
    exclude = True -> do not process given columns, process all others
    exclude = False -> do process all columns given, exclude the rest
    """
    # Copy array as to not change original data
    data_copy = copy.deepcopy(data)

    # TODO: fix checks
    # if not isinstance(columns, array.ArrayType):
    #     raise Exception('Columns must be of array type')

    # replace all empties
    for column in data.columns:
        replace_empty_with_placeholder_empty(data_copy)

    columns_to_use = filter(lambda x: x if (x not in columns and exclude) or (x in columns and not exclude) else None, data.columns)

    for column in columns_to_use:
        remove_punctuation(data_copy, column)
        to_lower(data_copy, column)

    return data_copy


def spell_check_data(data, columns=[], exclude=True, language=['nl-NL', 'en-EN'], custom_dicts=[]):
    """
    Performs spell checking on the whole dataset
    """
    columns_to_use = filter(lambda x: x if (x not in columns and exclude) or (x in columns and not exclude) else None, data.columns)

    all_errors = []

    for column in columns_to_use:
        results = check_spelling(data[column], language, custom_dicts)
        all_errors.append(results)

    final_dict = {}
    for result in all_errors:
        final_dict = final_dict | result

    return final_dict