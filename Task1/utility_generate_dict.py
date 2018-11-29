"""
Python file that will be used to generate a json file of the form
{cacm_file_name_1 : parsed_taokenized_data_file_1,
cacm_file_name_2 : parse_tokenized_data_file_2....}
"""

# Import Statements
import json
import os
from pathlib import Path


def read_json_document(json_file_name):
    """
    Helper function to read all tyhe path variables form the json file
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


def parse_tokenize_store_data(json_file_name):
    """
    Function that will parse and tokenize all HTML files in the CACM collection
    :param json_file_name: The path to the json file containing all the absolute
    paths to test collection
    the test_collection
    """
    # Note : Refer the json_file all_paths.json for
    # the exact form of the dictionary
    all_paths_dict = read_json_document(json_file_name)

    # Get the absolute path of the folder containing the 3024 HTML documents
    # Note : The paths stored in the
    # all_paths.json file are relative to the folder
    # IR_Project

    # To get the absolute path we are using os.path.realpath("..")
    # which will give us the current path ( be it Mac, Windows, Linux)

    # To this we are appending the string obtained
    # from the the all_paths.json file
    # Note: The strings in these json files all use
    # Windows specific separators(\)
    # Therefore to get non_dependent_os_path we are using the pathlib library

    os_specific_path = os.path.realpath("..") + all_paths_dict["test_data"]["test_collection_path"]
    non_dependent_path = Path(os_specific_path)






# Store the path of the json file containing the paths
# of the other required files
# in a global variable

all_paths_json_file_name = "..\\all_paths.json"
parse_tokenize_store_data(json_file_name=all_paths_json_file_name)
