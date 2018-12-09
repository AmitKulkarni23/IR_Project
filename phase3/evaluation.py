SCORE_FILE = "../Extras/bm_25_scores.txt"
RELEVENCE_FILE = "../test_collection/cacm.rel.txt"

f_score = open(SCORE_FILE,"r")


def read_rel_file(file_name):
    #read revelance information
    relevant_dict = {}
    with open(file_name, "r") as f_rel:
    # f_rel_data = f_rel.read()
        for line in f_rel:
            line_list = line.split()
            if int(line_list[0]) not in relevant_dict:
                relevant_dict[int(line_list[0])] = [line_list[2]]
            else:
                relevant_dict[int(line_list[0])].append(line_list[2])
    return relevant_dict

def read_score_file(file_name):
    # read score information
    score_dict = {}
    with open(file_name, "r") as f_score:
        # f_rel_data = f_rel.read()
        for line in f_score:
            if "----" in line:
                continue
            line_list = line.split()
            if int(line_list[0]) not in score_dict:
                score_dict[int(line_list[0])] = [line_list[2]]
            else:
                score_dict[int(line_list[0])].append(line_list[2])
    return score_dict


def get_precision_recall_table(relevance_file, score_file,out_file_name):
    score_dict = read_score_file(score_file)
    relevance_dict = read_rel_file(relevance_file)
    average_precision_total = 0
    total_queries = 64
    f_out = open(out_file_name+"_precision_recall.txt","w")
    f_p5 = open(out_file_name+"_p@5.txt","w")
    f_p20 = open(out_file_name+"_p@20.txt","w")
    f_out.write("Query \t DocID \t Rel \tRecall \t Precision\n")
    for query, doc_list in score_dict.items():
        if query not in relevance_dict:
            f_out.write("Query " + str(query) + " is not present in relevant set. Hence precision and recall is 0.0\n\n")
            total_queries -= 1
            continue
        relevance_list = relevance_dict[query]
        num_total_relevant = len(relevance_list)
        num_relevant = 0
        num_retrieved = 0
        precision_at_R = 0
        for i in range(len(doc_list)):
            num_retrieved += 1
            if doc_list[i] in relevance_list:
                num_relevant += 1
                recall = num_relevant/float(num_total_relevant)
                precision = num_relevant/float(num_retrieved)
                precision_at_R += precision
                f_out.write(str(query) + "\t" + doc_list[i] + "\t R \t\t" + str(recall) +"\t\t" + str(precision)+"\n")

            else:
                recall = num_relevant / float(num_total_relevant)
                precision = num_relevant / float(num_retrieved)
                f_out.write(str(query) + "\t" + doc_list[i] + "\t N \t\t" + str(recall) + "\t\t" + str(precision) +"\n")
            if i+1 == 5:
                f_p5.write(str(query) + "\t" + str(precision) + "\t" + out_file_name + "\n")
            if i+1 == 20:
                f_p20.write(str(query) + "\t" + str(precision)  + "\t" + out_file_name  + "\n")
        avg_precision = precision_at_R/float(num_total_relevant)
        average_precision_total += avg_precision
        f_out.write("\nAverage precision for query " + str(query) + " : " + str(avg_precision) + "\n\n")
    f_out.write("\nMean average precision is :" + str(average_precision_total/total_queries ) + "\n\n")
    f_out.close()
    f_p5.close()
    f_p20.close()

def get_MRR(relevance_file, score_file,out_file_name):
    score_dict = read_score_file(score_file)
    relevance_dict = read_rel_file(relevance_file)
    total_rank = 0
    total_RR = 0
    total_queries = 64
    f_out = open(out_file_name+"_MRR.txt", "w")

    for query, doc_list in score_dict.items():
        if query not in relevance_dict:
            f_out.write("\nQuery " + str(query) + " is not present in relevant set. Hence reciprocal rank is N/A\n\n")
            total_queries -= 1
            continue
        relevance_list = relevance_dict[query]
        rank = 0
        for i in range(len(doc_list)):
            if doc_list[i] in relevance_list:
                rank = i+1
                reciprocal_rank = 1/float(rank)
                total_RR += reciprocal_rank
                f_out.write(str(query) + "\t" + doc_list[i] + "\t RR \t\t" + str(rank)+ "\t"+ str(reciprocal_rank) +"\n")
                break
        # f_out.write("\nAverage precision for query " + str(query) + " : " + str(avg_precision) + "\n\n")
    f_out.write("\nMean reciprocal rank is :" + str(total_RR/total_queries) + "\n\n")
    f_out.close()


get_precision_recall_table(RELEVENCE_FILE,SCORE_FILE,"bm_25")
get_MRR(RELEVENCE_FILE,SCORE_FILE,"bm_25")


