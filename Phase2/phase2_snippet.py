import json
import os

from bs4 import BeautifulSoup


def getTextFromHTML(fileName):
    """
    parses a return the list of terms present the HTML file
    :param fileName: the HTML file which is searched for
    :return: the list of terms
    """
    f = open(CORPUS_PATH + "/" + fileName + ".html")
    soup = BeautifulSoup(f,'html.parser')
    text_list = soup.pre.text.split()
    text_list[:] = (value for value in text_list if value != "of")
    text_list[:] = (value for value in text_list if value != "or")
    text_list[:] = (value for value in text_list if value != "in")
    text_list[:] = (value for value in text_list if value != "the")
    text_list[:] = (value for value in text_list if value != "and")
    text_list[:] = (value for value in text_list if value != "for")
    # text_list[:] = (value for value in text_list if value != "by")
    # text_list[:] = (value for value in text_list if value != "The")
    # text_list[:] = (value for value in text_list if value != "I")
    # text_list[:] = (value for value in text_list if value != "to")
    # text_list[:] = (value for value in text_list if value != "a")
    
    return text_list

def getCleanTerm(term):
    """
    case folds and strips the terms of punctuations
    :param term: the term to clean
    :return: the cleaned term
    """
    clean = term.lower()
    clean.strip('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
    return clean

def getSigList(query_list, text_list):
    """
    get a list with 1 or 0, 1 representing if the term is significant wrt to the query, 0 otherwise
    :param query_list: the list with the query terms
    :param text_list: the list with the text terms
    :return: the significance list
    """
    sig_list = []
    for term in text_list:
        if getCleanTerm(term) in query_list:
            # print(getCleanTerm(term))
            sig_list.append(1)
        else:
            sig_list.append(0)
    return sig_list

def generate_snippet_for_one_query(query, file_name):
    """
    generates the snippet
    :param query: the query
    :param file_name: the file in which is query is searched for
    :return: the snippet
    """

    query_list = query.split()
    text_list = getTextFromHTML(file_name)
    window_len = min(50, len(text_list))
    num_win = len(text_list) - window_len
    significance_list = getSigList(query_list, text_list)

    maxSig = 0
    maxIndex = 0

    for i in range(num_win):
        sig = (sum(significance_list[i:i+window_len]))**2 / window_len
        if maxSig < sig:
            maxSig = sig
            maxIndex = i
    snippet_list = text_list[maxIndex:maxIndex+window_len]
    # print(maxIndex)
    # print(len(significance_list))
    # print(text_list)
    # print(file_name)
    for i in range(len(snippet_list)):
        if significance_list[i+maxIndex] == 1:
            # print("\033[45;30m"+snippet_list[i]+"\033[m",end=' ')
            f.write(" <b>" + snippet_list[i] + "</b> ")
        else:
            # print(term,end=' ')
            f.write(" " + snippet_list[i])
    # print("\n")
    f.write("<br />")

def get_list_of_files(query_id):
    """
    get the list of top 100 DocID which are in the bm_25_scores for each query
    :param query_id: the query id for the query searched for
    :return: the list of filename which are in the top 100
    """
    file_list = []
    score_list = []
    doc_score_file = open(DOC_SCORE_PATH+"/bm_25_scores.txt")
    for line in doc_score_file.readlines():
        params = line.split()
        if params[0] == str(query_id):
            file_list.append(params[2])
            score_list.append(params[4])
    doc_score_file.close()
    return file_list, score_list


def snippet_generation():
    """
    Snippet generation into an HTML files with format:
        Query
            DocID
            Snippet
    :return: null
    """
    # load parsed queries for matching of queries with text
    query_file = open(QUERY_PATH + 'parsed_query_dict.json', 'r')
    query_dict = json.load(query_file)

    # load unparsed queries for display the result
    query_file_unparsed = open(QUERY_PATH + "unparsed_query_dict.json", "r")
    query_dict_unparsed = json.load(query_file_unparsed)

    # parsed_tokenized_file = open("parsed_tokenized_json_output.json",'r')
    # text_dict = json.load(parsed_tokenized_file)

    for query_id, query  in query_dict.items():
        list_of_files, score_list = get_list_of_files(query_id)
        f.write("<br /><b>" + query_dict_unparsed[query_id] + "</b><br />")
        for i in range(len(list_of_files)):
            # print("\033[01;31m " +file_name +"  \033[00;34m"+query + "\033[m")
            f.write("<br /><b>" + list_of_files[i] + "</b>  Score: "+ score_list[i] +"<br />")
            generate_snippet_for_one_query(query, list_of_files[i])


if __name__ == "__main__":

    cwd = os.getcwd()
    # CACM = path = os.path.join(cwd, '../cacm')
    QUERY_PATH = '../Outputs/Query_terms/'
    DOC_SCORE_PATH = '../Outputs/Phase1/Task1'
    CORPUS_PATH = '../test_collection/CACM_Collection'
    OUTPUT_PATH = '../Outputs/Phase2'
    f = open(OUTPUT_PATH + "/snippet_bm_25.html", "w")
    f.write("<html>")
    snippet_generation()
    f.write("</html>")
    f.close()
