import os

import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
plt.ylim(0.0,1.0)


def getPR(file_name):
    """
    gets the precision recall to plot
    :param file_name: the run file
    :return: x and y for the plot
    """
    f = open('../Outputs/Phase3/precision_recall_table/'+file_name)
    PR_per_query = {}
    lines = (line.strip() for line in f)
    for line in lines:
        if "Query" in line:
            continue
        if "precision" in line:
            continue
        if not line.strip():
            continue
        line_list = line.split()
        query = float(line_list[0])
        recall = float(line_list[4])
        recall = round(recall*10)/10
        precision = float(line_list[5])
        precision = round(precision*100)/100
        # print(recall,precision)
        if query in PR_per_query:
            if recall not in PR_per_query[query]:
                PR_per_query[query][recall] = precision
        else:
            PR_per_query[query] = {recall:precision}

    PR_plot_dict = {}
    for i in range(64):
        if float(i+1) in PR_per_query:
            for recall, precision in PR_per_query[float(i+1)].items():
                if recall in PR_plot_dict:
                    PR_plot_dict[recall].append(precision)
                else:
                    PR_plot_dict[recall] = [precision]
    x_plot = []
    y_plot = []
    for x, y_list in PR_plot_dict.items():
        PR_plot_dict.update({x:sum(y_list)/float(len(y_list))})

    for x in sorted(PR_plot_dict.keys()):
        x_plot.append(x)
        y_plot.append(PR_plot_dict[x])

    return x_plot, y_plot

def plotPR(x,y,c,run):
    """
    plots the PR curve
    :param x: the recall values
    :param y: the precision values
    :param c: the color code
    :param run: the name of the run
    :return:
    """
    colors = ['red','blue','green','cyan','black','magenta','violet','yellow']
    plt.plot(x, y,color=colors[c],label=run)


if __name__ == "__main__":
    PR_FILE_PATH = '../Outputs/Phase3/precision_recall_table'
    i = 0
    for f in os.listdir(PR_FILE_PATH):
        if ".txt" in f:
            x, y = getPR(f)
            run = f.replace(".txt","").replace("scores","").replace("query","").replace("queries","").\
                replace("precision","").replace("recall","").replace("_","")
            print(run)
            plotPR(x,y,i,run)
            i+=1
    plt.ylabel('Precision')
    plt.xlabel('Recall')
    plt.legend()
    plt.savefig("PRPlot.png")
    plt.show()

