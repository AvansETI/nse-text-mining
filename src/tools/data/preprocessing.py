import copy
import os
import re
from enchant.checker import SpellChecker
import enchant
import numpy as np
from tools.utils.value_checks import is_number
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


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

    def remove_white_space_group(string):
        regex = r"(?:([a-zA-Z0-9_.]+[@]{1}[a-z0-9]+[\.][a-z]+))|([^a-zA-Z0-9 ])"
        result = re.sub(regex, r'\g<1>', string)

        return result

    # Remove all punctuation using regex
    data[column_name] = \
        data[column_name].map(remove_white_space_group)


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
    # custom_checkers = [SpellChecker(enchant.PyPWL(dict)) for dict in custom_dicts]
    # checkers = checkers + custom_checkers

    total_errors = {}
    for checker in checkers:
        lang_errors = []

        for line_index, line in enumerate(data):
            checker.set_text(line)

            line_errors = []
            for err in checker:
                if (err.word) == 'empty':
                    break

                line_errors.append({'word': err.word, 'pos': err.wordpos})

            lang_errors.append({'line': line_index, 'errors': line_errors})

        total_errors[checker.lang] = lang_errors

    return total_errors


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
        to_lower(data_copy, column)
        remove_punctuation(data_copy, column)

    return data_copy


def spell_check_data(data, columns=[], exclude=True, language=['nl-NL', 'en-EN'], custom_dicts=[]):
    """
    Performs spell checking on the whole dataset
    """
    columns_to_use = filter(lambda x: x if (x not in columns and exclude) or (x in columns and not exclude) else None, data.columns)

    all_errors = {}
    for column in columns_to_use:
        results = check_spelling(data[column], language, custom_dicts)

        for lang in results:
            lang_errors = all_errors.get(lang, [])
            lang_errors.append({'col': column, 'errors': results[lang]})

            all_errors[lang] = lang_errors

    return all_errors


def redact_phone_numbers(data, columns=[], exclude=True):
    """
    Replaces phone numbers (re: .*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?) with reference ([phone-number(index)])
    """
    phone_number_regex = re.compile(r".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?")

    # make sure all values are viewed as a string and include or exclude given columns based on exclude flag
    data = data.astype(str)
    data_with_columns = data.drop(columns, axis=1) if exclude else data[columns]

    redacted = {}

    index = 0
    for label, series in data_with_columns.items():
        for item in series:
            value = item

            found_numbers = re.findall(phone_number_regex, item)
            for found in found_numbers:
                if found not in redacted.keys():
                    value = value.replace(found, f'[phone-number({index})]')
                    redacted[found] = f'[phone-number({index})]'
                    index = index + 1
                else:
                    value = value.replace(found, redacted[found])

            series = series.replace(item, value)
        data_with_columns[label] = series

    # update data with redacted phonenumebrs
    data.update(data_with_columns)

    return (data, redacted)


def redact_email_addresses(data, columns=[], exclude=True):
    """
    Replaces email addresses (re: ([a-zA-Z0-9_.]+[@]{1}[a-z0-9]+[\.][a-z]+)) with reference ([email(index)])
    """
    email_regex = re.compile(r"([a-zA-Z0-9_.]+[@]{1}[a-z0-9]+[\.][a-z]+)")

    # make sure all values are viewed as a string and include or exclude given columns based on exclude flag
    data = data.astype(str)
    data_with_columns = data.drop(columns, axis=1) if exclude else data[columns]

    redacted = {}

    index = 0
    for label, series in data_with_columns.items():
        for item in series:
            value = item

            found_addresses = re.findall(email_regex, item)
            for found in found_addresses:
                if found not in redacted.keys():
                    value = value.replace(found, f'[email({index})]')
                    redacted[found] = f'[email({index})]'
                    index = index + 1
                else:
                    value = value.replace(found, redacted[found])

            series = series.replace(item, value)
        data_with_columns[label] = series

    # update data with redacted email addresses
    data.update(data_with_columns)

    return (data, redacted)


def remove_stop_words(data, columns=[], exclude=True):
    data_with_columns = data.drop(columns, axis=1) if exclude else data[columns]

    # make sure files are downloaded
    nltk.download('stopwords')
    nltk.download('punkt')

    stop = stopwords.words('dutch')
    pat = r'\b(?:{})\b'.format('|'.join(stop))

    for col_label in data_with_columns:
        data_with_columns[col_label] = data_with_columns[col_label].str.replace(pat, '')

    data.update(data_with_columns)

    return data
