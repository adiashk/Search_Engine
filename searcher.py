import re

from parser_module import Parse
from ranker import Ranker
import utils
from word2vec import Word2vec


class Searcher:

    def __init__(self, inverted_index, stemming):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse(stemming)
        self.ranker = Ranker()
        self.inverted_index = inverted_index

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        word2vec = Word2vec()
        # TODO - send only words from query, the rest of the word search alone
        # t = ' '
        # query_text = t.join(query)
        # query_words = re.compile(r"[a-zA-Z]+").findall(query_text)
        # query_words = []
        # for q in query:
        #     if all(x.isalpha() or x.isspace() for x in q):
        #         query_words.append(q)

        similar_words = word2vec.get_most_similar_words(query, 3)
        query_and_similar = []
        query_and_similar.extend(query)
        query_and_similar.extend(similar_words)
        # posting = utils.load_obj("posting")
        posting = {}
        relevant_docs = {}
        for term in query_and_similar:
            try:  # an example of checks that you have to do

                posting_doc = posting[term]
                for doc_tuple in posting_doc:  # list: [(tweet_id, amount_in_tweet), ...()] #TODO- search term.lower & term.upper
                    doc = doc_tuple[0]
                    if doc not in relevant_docs.keys():
                        relevant_docs[doc] = 1
                    else:
                        relevant_docs[doc] += 1
            except:
                print('term {} not found in posting'.format(term))
        return relevant_docs
