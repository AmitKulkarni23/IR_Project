"""
Python file which conatins functions to perform baseline runs given the indexer
"""
import json
from Task1.parse_queries import parse_query_text_file
import collections


def get_relevance_information(rel_info_fname):
    """
    Function that reads the cac.rel file and gets the relevance information that
    will be used for the BM25 model
    :param rel_info_fname: The path to the file containing the relevance information
    : Will return a dictionary of the form
    {query_numb : [ <list of all docs relevant to query 1] }
    """

    rel_docs_dict = collections.defaultdict(list)

    # How to read the cac.re;.txt file
    # 1 Q0 CACM - 1410 1
    # 1 - query number
    # Q0 - fixed literal
    # CACM-1410 - filename
    # 1 - which indicates that the file is relevant

    # We will read this file and convert it into a dictionary
    rel_fd = open(rel_info_fname)

    for line in rel_fd.readline():
        items = line.split()

        # So items will be ["1", "Q0", "CACM-1410", "1"]
        # Store this in a dictionary
        if int(items[0]) in rel_docs_dict:
            rel_docs_dict[int(items[0])].append(items[2])
        else:
            rel_docs_dict[int(items[0])] = [items[2]]

    rel_fd.close()
    return rel_docs_dict


def bm_25(collection_json_file, index_json_file, query_text_file_name):
    """
    Function that performs BM25 ranking
    :param collection_json_file: The json file containing the parsed output
    of all the 3024 HTML collections
    :param index_json_file: The json file containing the index
    :param query_text_file_name: The path to the file containing all the queries
    """

    # Create another dictionary that will hold the doc_id and their BM25 score
    bm25_scores = {}

    # Read the json files into the above 2 dictionaries
    with open(collection_json_file) as c_fd:
        collection_data = json.load(c_fd)

    with open(index_json_file) as i_fd:
        indexed_data = json.load(i_fd)

    # Note: Indexed data is of the form
    # { term : { doc_id : count_in_doc } }

    # Now the json data is present in the dictionaries
    # Note: There is information given about relevance in file cacm.rel.txt
    # file. We need to get the relevance information

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    query_dict = parse_query_text_file(query_text_file_name)

    # N -> Total number of collections in the data
    N = len(collection_data)

    # The constants
    k1 = 1.2
    b = 0.75
    k2 = 100

    avg_doc_length = get_avg_doc_length(collection_data)

    for q in query_dict:
        # R ->  Total number of relevant documents for this query
        R = len(query_dict[q])

        # Store the relevant documents in a list
        rel_docs_list = query_dict[q]

        for doc_id in collection_data:

            score = 0

            for term in query_dict[q].split():
                # ri -> Number of relevant documents containing term i
                r_i = 0

                # n_i -> number of documents containing term i
                n_i = 0

                # frequency of this term in the entire query
                q_fi = query_dict[q].split().count(term)

                # f_i => Frequency of term i in document
                f_i = collection_data[doc_id].split().count(term)

                # Calculate r_i
                for item in indexed_data[term]:

                    # Increment n_i -> means the
                    n_i += 1
                    if item in rel_docs_list:
                        r_i += 1

                K = k1 * ((1 - b) + b * len(collection_data[doc_id].split()) / avg_doc_length)
                z = ((k1 + 1) * f_i / (K + f_i)) * ((k2 + 1) * q_fi) / (k2 + q_fi)
                score += ((r_i + 0.5) / (R - r_i + 0.5)) / ((n_i - r_i + 0.5) / (N - n_i - R + r_i + 0.5)) * z

            # Store this score w.r.t this document ID
            bm25_scores[doc_id] = score

    return bm25_scores


def get_avg_doc_length(col_data):
    """
    helper function which returns the average document length in the entire collection
    :param col_data: dictionary of the form
    {doc_id 1 : contnet_doc_id_1, doc_id_2 : content_doc_id_2 ....}
    :return: average document length in this collection
    """

    total_length = 0
    for doc in col_data:
        total_length += len(col_data[doc].split())

    return total_length / len(col_data)