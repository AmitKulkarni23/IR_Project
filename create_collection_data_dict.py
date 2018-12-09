"""
Python file that will be used to generate a json file of the form
{cacm_file_name_1 : parsed_taokenized_data_file_1,
cacm_file_name_2 : parse_tokenized_data_file_2....}

Credits -> https://tinyurl.com/yd4vz7c6
"""

# Import Statements
import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
import string
import re
import argparse
import errno


def read_json_document(json_file_name):
    """
    Helper function to read all the path variables form the json file
    Note: We are maintaining a json file to read all the input paths of our
    test collection and also the output_paths

    This will help us change the output/input paths of
    data easily(just change in the json file) instead of worrying about changing
    paths in the codebase
    :return: a dictionary after the reading the entire json file
    """

    with open(json_file_name) as fd:
        data = json.load(fd)

    return data


def store_data(json_fname):
    """
    Function that will parse and tokenize all HTML files in the CACM collection
    :param json_fname: The file name containing all the relative paths
    Basically it is the json file "all_paths.json"
    :return: Write to a .sjon file a dictionary of the format
    # Note: The url_text_dict will be of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    """

    # Get the absolute path of the folder containing the 3024 HTML documents
    # Note : The paths stored in the
    # all_paths.json file are relative to the folder
    # IR_Project
    all_paths_dict = read_json_document(json_fname)

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

    if not os.path.exists(os.path.dirname(parsed_tokenized_output_json_filename)):
        try:
            os.makedirs(os.path.dirname(parsed_tokenized_output_json_filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    # Write this dictionary to a json file
    with open(parsed_tokenized_output_json_filename, "w+") as o_fd:
        json.dump(url_text_dict, o_fd, indent=4)

    # return url_text_dict


def ignore_table_of_numbers(all_html_data, html_fname):
    """
    Function that will remove the table of numbers from the HTML file
    :param all_html_data: The entire HTML data passed in as string
    :param html_fname: The name of the html file that we are parsing
    :return: string after ignoring / discarding the table of numbers
    """
    # Note: In each of the HTML files, the table of numbers begin
    # after the string "AM" or "PM"
    # Idea : Consider text only till last occurrence of "AM" or "PM"
    # Ignore the rest

    # Convert the entire string to a list
    list_html_data = all_html_data.split()

    if html_fname == "CACM-0189.html":
        last_index = len(list_html_data) - 1 - list_html_data[::-1].index('9:57PM')
        # Ignore everything after this
        return " ".join(list_html_data[:last_index + 1])

    if html_fname == "CACM-1621.html":
        last_index = len(list_html_data) - 1 - list_html_data[::-1].index('PMB')
        # Ignore everything after this
        return " ".join(list_html_data[:last_index + 1])

    # Check for occurrence of PM first
    if "PM" in list_html_data:
        # Get the last index of PM
        index_of_PM = len(list_html_data) - 1 - list_html_data[::-1].index('PM')

        # Ignore everything after this
        return " ".join(list_html_data[:index_of_PM + 1])

    elif "AM" in list_html_data:
        # Get the last index of PM
        index_of_AM = len(list_html_data) - 1 - list_html_data[::-1].index('AM')

        # Ignore everything after this
        return " ".join(list_html_data[:index_of_AM + 1])

    else:
        print("The document ", html_fname, "doesn't have either PM or AM")

    return None


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

    # print("The folder path is ", folder_path)

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

            # Now, we have received the entire data present in the HTML file
            # But, we have to ignore the last digits part
            raw_html_data = ignore_table_of_numbers(raw_html_data, html_file)

            if raw_html_data is None:
                # i.e the function ignore_table_of_numbers returned None
                # which happens if PM or AM is not present in the text of the
                # HTML file then we will not consider such a file at all
                # Just continue
                continue

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


def parse_user_arguments():
    """
    Helper function to parse user arguments
    :return: a dictionary containing user arguments as key value pairs
    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-j", "--all_paths_json_fname",
                    help="Enter the path to the json file "
                         "which stores all the relative paths", required=True)

    return vars(ap.parse_args())


# Accept the user arguments
user_args = parse_user_arguments()
all_paths_json_fname = user_args["all_paths_json_fname"]

# Now create the collection data and write it to a json file
store_data(all_paths_json_fname)