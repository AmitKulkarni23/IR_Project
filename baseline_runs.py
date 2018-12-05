"""
Python file which conatins functions to perform baseline runs given the indexer
"""
import json
from parse_queries import parse_query_text_file
import collections
import math


def get_relevance_information(rel_info_fname):
    """
    Function that reads the cac.rel file and gets the relevance information that
    will be used for the BM25 model
    :param rel_info_fname: The path to the file containing the relevance information
    : Will return a dictionary of the form
    {query_numb : [ <list of all docs relevant to query 1] }
    """

    rel_docs_dict = collections.defaultdict(list)

    # How to read the cac.rel.txt file
    # 1 Q0 CACM - 1410 1
    # 1 - query number
    # Q0 - fixed literal
    # CACM-1410 - filename
    # 1 - which indicates that the file is relevant

    # We will read this file and convert it into a dictionary
    with open(rel_info_fname) as rel_fd:

        for line in rel_fd:
            # print("the line is ", line)
            items = line.split()

            # print("Split items = ", items)
            # So items will be ["1", "Q0", "CACM-1410", "1"]
            # Store this in a dictionary
            if int(items[0]) in rel_docs_dict:
                rel_docs_dict[int(items[0])].append(items[2])
            else:
                rel_docs_dict[int(items[0])] = [items[2]]

    rel_fd.close()
    return rel_docs_dict


def bm_25(collection_data, indexed_data, query_text_file_name, relevant_docs_fname):
    """
    Function that performs BM25 ranking
    :param collection_data: A dictionary containing the parsed output of teh entire
    collection. This dictionary is of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    :param indexed_data: The inverted index
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param query_text_file_name: The path to the file containing all the queries
    :param relevant_docs_fname: The text file containing the relevance file
    i.e cacm.rel.txt
    """

    # Create another dictionary that will hold the doc_id and their BM25 score
    # Note: We will maintain the bm_25scores dictionary in the form
    # {query_1 : {doc_id_1 : score_for_doc_id_1, doc_id_2: score_for_doc_id_2}...query_64 : {}}
    bm25_scores = {}

    # Populate the dictionary with empty inner dictionaries
    for i in range(1, 65):
        bm25_scores[i] = {}

    # Note: Indexed data is of the form
    # { term : { doc_id : count_in_doc } }

    # Now the json data is present in the dictionaries
    # Note: There is information given about relevance in file cacm.rel.txt
    # file. We need to get the relevance information
    # rel_docs_dict i sof the form:
    # {query_numb: [ < list of all docs relevant to query 1]}
    rel_docs_dict = get_relevance_information(relevant_docs_fname)

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    query_dict = parse_query_text_file(query_text_file_name)

    # N -> Total number of collections in the data
    N = len(collection_data)
    # print("The number of documnets in the collection is ", N)

    # The constants
    k1 = 1.2
    b = 0.75
    k2 = 100

    avg_doc_length = get_avg_doc_length(collection_data)

    for q in query_dict:
        # R ->  Total number of relevant documents for this query
        print("We are considering query ", q)
        R = len(rel_docs_dict[q])
        print("The total number of relevant documents for this query is ", R)

        # Store the relevant documents in a list
        rel_docs_list = rel_docs_dict[q]

        print("the relevant docs list is ", rel_docs_list)

        for doc_id in collection_data:
            # For each document calculate the score
            score = 0
            for term in query_dict[q].split():
                # ri -> Number of relevant documents containing term i
                r_i = 0

                # n_i -> number of documents containing term i
                n_i = 0

                # frequency of this term in the entire query
                q_fi = query_dict[q].split().count(term)
                # print("q_fi = ", q_fi, "term = ", term)

                # f_i => Frequency of term i in document
                if term in indexed_data and doc_id in indexed_data[term]:
                    f_i = indexed_data[term][doc_id]
                else:
                    f_i = 0

                if term in indexed_data:
                    # If such a term is present in our collection
                    # Calculate r_i
                    for item in indexed_data[term]:
                        # Increment n_i -> number of documents
                        # containing this term
                        n_i += 1
                        if item in rel_docs_list:
                            # If the same document is present in
                            # relevant doc list
                            r_i += 1

                if f_i > 0:
                    K = k1 * ((1 - b) + b * len(collection_data[doc_id].split()) / avg_doc_length)
                    z = ((k1 + 1) * f_i / (K + f_i)) * ((k2 + 1) * q_fi) / (k2 + q_fi)
                    numerator = ((r_i + 0.5) / (R - r_i + 0.5)) * z
                    denominator = ((n_i - r_i + 0.5) / (N - n_i - R + r_i + 0.5))
                    score += math.log(numerator / denominator)

            # Store this score w.r.t this document ID
            if q not in bm25_scores:
                bm25_scores[q] = {}

            bm25_scores[q][doc_id] = score

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

