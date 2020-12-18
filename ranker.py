import math
import pathlib
import time
from collections import defaultdict

import numpy as np

import utils


class Ranker:
    def __init__(self):
        pass

    def rank_relevant_doc(self, relevant_docs, query, word2vec, stemming,output_path):  # {tweet_id: num_of_writes, tweet_id: num_of_writes}
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        # print("start similarity At: ", time.asctime(time.localtime(time.time())))
        # return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)
        similarity_dictionary = defaultdict(float)
        query_vector = self.get_doc_vector(query, word2vec)
        relevant_docs_sorted = dict(sorted(relevant_docs.items(), key=lambda x: x[1][1]))
        # path = pathlib.Path().absolute()
        path = output_path
        if stemming:
            save_path = str(path) + '\\documents_stem\\'
        else:
            save_path = str(path) + '\\documents\\'

        temp_num = 0
        for tweet_id_in_relevant_doc in relevant_docs_sorted:
            num_of_writes = relevant_docs_sorted[tweet_id_in_relevant_doc][1]
            if temp_num != num_of_writes:  # load new file
                temp_num = num_of_writes
                filename = str(save_path + str(num_of_writes))
                docs_dictionary = utils.load_obj(filename)
            for tweet_id in docs_dictionary:  # all the docs in this file
                if tweet_id == tweet_id_in_relevant_doc:
                    doc_tuple = docs_dictionary[tweet_id_in_relevant_doc]
                    term_doc = doc_tuple[0][2]
                    doc_vector = self.get_doc_vector(term_doc, word2vec)
                    try:
                        sim = np.dot(doc_vector, query_vector)/((np.linalg.norm(doc_vector) * np.linalg.norm(query_vector)))
                    except:
                        continue

                    similarity_dictionary[tweet_id_in_relevant_doc] = sim
                    break
        # print("finish similarity At: ", time.asctime(time.localtime(time.time())))
        return sorted(similarity_dictionary.items(), key=lambda x: x[1], reverse=True)


    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]

    def get_doc_vector(self, query, word2vec):
        doc_vec = 0
        counter = 0
        avg_vec = []
        for term in query:
            if term in word2vec.model.wv.vocab:
                doc_vec += word2vec.model[str(term)]
                counter += 1
            if counter > 0:
                avg_vec = doc_vec / counter
        return avg_vec

    # def tf(self, doc, term):
    #     Fij = doc.term_doc_dictionary[term]  # the number of times the word i occurs in the document j
    #     Dj = doc.doc_length
    #     return Fij/Dj
    #
    # def idf(self, doc, term):
    #     N = len(self.inverted_index)
    #     dfi = self.inverted_index[term]
    #     return math.log2(N/dfi)
