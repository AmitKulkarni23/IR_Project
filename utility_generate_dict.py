"""
Python file that will be used to generate a json file of the form
{cacm_file_name_1 : parsed_taokenized_data_file_1,
cacm_file_name_2 : parse_tokenized_data_file_2....}
"""

# Import Statements
import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
import string
import re


def store_data(all_paths_dict):
    """
    Function that will parse and tokenize all HTML files in the CACM collection
    :param all_paths_dict: A dictionary containing all tghe relative paths to
    data in the test_collection
    Basically it is the json file "all_paths.json" in dictionary format
    :return: a dictionary of the form
    # Note: The url_text_dict will be of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    """

    # Get the absolute path of the folder containing the 3024 HTML documents
    # Note : The paths stored in the
    # all_paths.json file are relative to the folder
    # IR_Project

    # To get the absolute path we are using os.path.realpath(".")
    # which will give us the current path ( be it Mac, Windows, Linux)

    # To this we are appending the string obtained
    # from the the all_paths.json file
    # Note: The strings in these json files all use
    # Windows specific separators(\)
    # Therefore to get non_dependent_os_path we are using the pathlib library

    os_specific_path = os.path.realpath(".") + all_paths_dict["test_data"]["test_collection_path"]
    non_dependent_path = Path(os_specific_path)

    # Get the filename where you want to store the parsed and tokenized output
    parsed_tokenized_output_json_filename = Path(os.path.realpath(".") + all_paths_dict["parsed_tokenized_output_json_file"])

    # Note: The url_text_dict will be of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    url_text_dict = perform_parsing_tokenization(non_dependent_path)

    # Write this dictionary to a json file
    with open(parsed_tokenized_output_json_filename, "w+") as o_fd:
        json.dump(url_text_dict, o_fd, indent=4)

    return url_text_dict


def perform_parsing_tokenization(folder_path):
    """
    Function that will perform the core of the parsing and the tokenization
    :param folder_path: Path to the folder containing all the .html files
    :return: a dictionary of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2"}
    """

    # This will be the dictionary that will be returned
    final_dict = {}

    print("The folder path is ", folder_path)

    # Iterate through the folder
    for html_file in os.listdir(folder_path):
        if html_file.endswith(".html"):
            # Just a safety check, we need to parse only HTML files
            # Get the doc id for this particular HTMl file
            # for example html_file = "abcd.html"
            # doc_id = "abcd"
            doc_id = html_file[:-5]

            # Read the HTML contents of this file
            with open(folder_path / html_file) as html_fd:
                raw_html_data = html_fd.read()

            # Now contents contains all the data in the HTMl file
            # Create BeautifulSoup object
            temp_bs4_obj = BeautifulSoup(raw_html_data, features="html5lib")

            # First get the title of this page
            title = temp_bs4_obj.title
            if title:
                # If title is present
                title_text = title.text
            else:
                title_text = " "

            non_parsed_text = title_text + " " + temp_bs4_obj.text

            # Finally perform punctuation handling and write this
            # and store the text in a dictionary
            final_dict[doc_id] = perform_punctuation_handling(non_parsed_text).lower()

    return final_dict


def perform_punctuation_handling(text):
    """
    Function that performs punctuation handling of the text present
    :param text: The dump of text obtained from parsing the HTML
    (removing unwanted tags)
    :return: text wherein punctuation is removed except hyphens
    and punctuation withing digits are maintained

    Examples:
    Initially
    text = "abdc.efjhi, lmnoabcd-efgh-jkl122-2345,789123a-bcdABC$$$##, CDEF xyz mnop,,,,"
    Convert this to a list
    list_of_text = ["abdc.efjhi, lmno", "abcd-efgh-jkl", "122-2345,789", "123a-bcd", "ABC$$$##, CDEF xyz mnop,,,,"]
    perform_punctuation_handling(list_of_text)

    The list_of_text now will be as follows:
    ['abdc efjhi  lmno', 'abcd-efgh-jkl', '122-2345,789', '123a-bcd', 'ABC       CDEF xyz mnop    ']
    """

    # Convert the given text to list of strings by using the
    # in-built split method
    list_of_text = text.split()

    # Create a regular expression compiler
    # replace all punctuations except hyphens
    p = re.compile(r"(\b[-]\b)|[\W_]")

    # Create a set of punctuation
    puncs = set(string.punctuation)
    for idx, text in enumerate(list_of_text):
        if check_if_digits_punctuation(text, puncs):
            # Is a a number with punctuations
            # Dont do anything
            continue
        else:
            final_text = p.sub(lambda m: (m.group(1) if m.group(1) else " "), text)
            list_of_text[idx] = final_text

    return strip_additional_spaces(" ".join(list_of_text))


def check_if_digits_punctuation(given_str, puncs):
    """
    Helper function that checks if a given string only conatisn digits and punctuations
    :param puncs: set of all punctuation marks in string.punctuation
    :param given_str: a string
    :return: True, iff the string contains digits and punctuations
    """

    # if everything is a punctuation
    if all(i in string.punctuation for i in given_str):
        return False

    # Check if the string is composed of only digits and punctuation
    if all(i.isdigit() or i in puncs for i in given_str):
        return True

    return False


def strip_additional_spaces(text):
    """
    Helper function that will strip out additional spaces present in text
    :param text: The text from the HTML obtained
    """
    return re.sub(' +', ' ', text).rstrip().lstrip()

