import math


class Ranker:
    def __init__(self, inverted_index):
        self.inverted_index = inverted_index

    @staticmethod
    def rank_relevant_doc(relevant_doc):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]

    def tf(self, doc, term):
        Fij = doc.term_doc_dictionary[term]  # the number of times the word i occurs in the document j
        Dj = doc.doc_length
        return Fij/Dj

    def idf(self, doc, term):
        N = len(self.inverted_index)
        dfi = self.inverted_index[term]
        return math.log2(N/dfi)
