"""
Python file which creates the index based on stem queries
"""
import argparse
import json
import os
from pathlib import Path
from create_index import create_inverted_index
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


def parse_user_arguments():
    """
    Function that passes the arguments passed by the user on the command line
    :return: a dictionary with all the user arguments in the form of key
    value pairs
    """

    ap = argparse.ArgumentParser()

    ap.add_argument("-j", "--json_fname", help="Enter the path to the json "
                                               "filename containing"
                                               "all the paths to the "
                                               "test_collection", required=True)

    return vars(ap.parse_args())


# ToDO: This code is repeated from one the files. Remove redundant code
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
        last_index = len(list_html_data) - 1 - list_html_data[::-1].index(
            '57pm')
        # Ignore everything after this
        return " ".join(list_html_data[:last_index + 1])

    if html_fname == "CACM-1621.html":
        last_index = len(list_html_data) - 1 - list_html_data[::-1].index('pmb')
        # Ignore everything after this
        return " ".join(list_html_data[:last_index + 1])

    # Check for occurrence of PM first
    if "pm" in list_html_data:
        # Get the last index of PM
        index_of_PM = len(list_html_data) - 1 - list_html_data[::-1].index('pm')

        # Ignore everything after this
        return " ".join(list_html_data[:index_of_PM + 1])

    elif "am" in list_html_data:
        # Get the last index of PM
        index_of_AM = len(list_html_data) - 1 - list_html_data[::-1].index('am')

        # Ignore everything after this
        return " ".join(list_html_data[:index_of_AM + 1])

    else:
        print("The document ", html_fname, "doesn't have either PM or AM")

    return None


def parse_stemmed_version_of_corpus(stem_file_path):
    """
    Function that parses the stemmed version of the corpus
    :param stem_file_path: The path to the text file containing the
    :return: a dictionary of the form
    { doc_id : doc_id contents}
    """

    fp = open(stem_file_path)

    line = fp.readline()

    final_dict = {}

    doc_id = ""
    while line:
        line = line.strip("\n")
        line_list = line.split()

        if line_list[0] == "#":
            doc_id = get_proper_doc_id(line_list[1]) + ".html"
            line = fp.readline()
        while line[0] != "#":
            line_list.append(line.strip("\n"))
            line = fp.readline()

            if not line:
                break

        final_dict[doc_id] = " ".join(line_list[2:])

    # Note: This final dictionary will have all the doc_ids and their respective
    # contents including the the numbers. We have to excliude these numbers

    for item in final_dict:
        final_dict[item] = ignore_table_of_numbers(final_dict[item], item)

    result_dict = {}
    # Now, we have ignored the table of numbers
    for k, v in final_dict.items():
        # Ignore the .html part in all the keys of the final_dict
        result_dict[k[:-5]] = v

    return result_dict


def get_proper_doc_id(given_doc_id):
    """
    Helper function which returns the proper doc ID given a string
    :param given_doc_id: is a string
    :return: a string
    """

    # Note: The file format of the cacm.stem.txt is something as below:

    # # 1
    # ....

    # # 2
    # .....

    # 3204
    # ....

    # We need to extract these numbers
    # The input to the functions are these numbers
    doc_id_len = len(given_doc_id)
    if doc_id_len == 1:
        return "CACM-000" + given_doc_id
    elif doc_id_len == 2:
        return "CACM-00" + given_doc_id
    elif doc_id_len == 3:
        return "CACM-0" + given_doc_id
    else:
        return "CACM-" + given_doc_id


user_args = parse_user_arguments()

json_fname_relative_paths = user_args["json_fname"]

# Note the file "all_paths.json" has all the relative paths
# We will read this file and store the json file in a dictionary
all_paths_dict = read_json_document(json_fname_relative_paths)

# Get the path to the text file which conatins the stemmed version of the corpus
stemmed_text_file_path = Path(os.path.realpath(".") +
                              all_paths_dict["test_data"]["cacm_stem"])

# Parse this text file and store it in a dictionary of the form:
# {doc_id : doc_id_contents}
parsed_corpus = parse_stemmed_version_of_corpus(stemmed_text_file_path)

# get the json file where this will be written
stemmed_corpus_output_json_fname = Path(os.path.realpath(".") +
                                        all_paths_dict[
                                            "stemmed_corpus_json_fname"])

print("The stemmed corpus output file name is ",
      stemmed_corpus_output_json_fname)

if not os.path.exists(os.path.dirname(stemmed_corpus_output_json_fname)):
    try:
        os.makedirs(os.path.dirname(stemmed_corpus_output_json_fname))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

# We will write this parsed_corpus to a json file
with open(stemmed_corpus_output_json_fname, "w+") as stem_out:
    json.dump(parsed_corpus, stem_out, indent=4)

# We will create an index out of this and write to a json file as well
stemmed_corpus_inverted_index_fname = Path(os.path.realpath(".") +
                                           all_paths_dict[
                                               "stemmed_inverted_index"])

print("The stemmed corpus output file name is ",
      stemmed_corpus_inverted_index_fname)


stemmed_inverted_index = create_inverted_index(stemmed_corpus_output_json_fname, stemmed_corpus_inverted_index_fname)