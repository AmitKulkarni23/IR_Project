"""
Python file which is used to parse queries from the cacm.query.txt or
the cacm_stem.query
"""

import string
import re


def parse_query_text_file(fname):
    """
    Function that is used to parse queries given a text file
    :param fname: The name of the file which contains the queries
    :return: a dictionary of the form
    {q_id : <Parsed Query>, q_id_2 : <Parse Query 2>}
    """

    # We will extract the queries from the .txt file
    # and store it in a dictionary
    # The format of teh dictionary will be { query_id: actual_parsed_query }
    queries = {}

    # Open the file
    q_fd = open(fname)

    # Read the contents of the file
    file_contents = q_fd.read()

    # Note the query is structured in a particular manner
    # Example:
    # < DOC >
    # < DOCNO > 1 < / DOCNO >
    #
    # What articles exist which deal with TSS(Time Sharing System), an operating system for IBM computers?
    #
    # < / DOC >

    # Approach: We will try to find the index of < DOC > in the file_contents
    # string using the find() method. find() will return the first index of the
    # substring if found. else -1

    # Given this index we will extract the actual query and ignore all the tags
    # Then move on to the next < DOC >
    # Do this until find() return -1 ( There are no more < DOC > )

    opening_doc_str = "<DOC>"
    closing_doc_str = "</DOC>"

    while True:
        doc_tag_index = file_contents.find(opening_doc_str)

        if doc_tag_index == -1:
            # Reached the end of the text file, no more queries
            break

        query_numb, actual_query = get_one_single_query(file_contents)

        # Now add this key value pair to the dictionary
        queries[query_numb] = actual_query

        # Note: We are still in the while loop
        # We need to move on to the next query
        # There our file_contents has to be changed so that we skip the
        # entire contents of the <DOC></DOC> that we read

        # Changing file_contents variables
        file_contents = file_contents[file_contents.find(closing_doc_str) + len(
            closing_doc_str):]

    return queries


def get_one_single_query(all_text):
    """
    Helper function to get the query given the query text with all its
    <DOC> and </DOC> tags
    Eg:
    # < DOC >
    # < DOCNO > 1 < / DOCNO >
    #
    # What articles exist which deal with TSS(Time Sharing System), an operating system for IBM computers?
    #
    # < / DOC >
    will return 1, What articles exist which deal with TSS(Time Sharing System), an operating system for IBM computers?
    :return: a tuple of the form query_id, actual query
    """
    doc_numb_opening_tag = "<DOCNO>"
    doc_numb_closing_tag = "</DOCNO>"
    doc_closing_tag = "</DOC>"

    # Query number is usually the 13th character from the start of the text
    query_number = int(all_text[all_text.find(doc_numb_opening_tag) + len(
        doc_numb_opening_tag) + 1])

    # Now actual query starts from the end of the </DOCNO> string and
    # extends up until the </DOC> closing tag

    actual_query = all_text[all_text.find(doc_numb_closing_tag) + len(
        doc_numb_closing_tag): all_text.find(doc_closing_tag)]

    # Now we have modified the query
    actual_query = modify_query(actual_query)

    return query_number, actual_query


def modify_query(whole_query):
    """
    Helper function which modifies the given query
    i.e converts it to lower case, removes punctuation, removes trailing spaces
    from both ends
    :param whole_query: the whole query passed in as a string
    :return: a string with all the modifications performed
    """

    # Strip trailing spaces on both the left and right sides
    whole_query = whole_query.lstrip().rstrip()

    # Create a set for puctuations
    exclude = set(string.punctuation)

    whole_query_puc_removed = "".join(
        ch for ch in whole_query if ch not in exclude)

    return re.sub(' +', ' ', whole_query_puc_removed.replace("\n", " "))


file_name = "my_dummy.txt"
parse_query_text_file(file_name)