from collections import defaultdict

class Indexer:

    def __init__(self, config):
        self.inverted_idx = defaultdict(int)
        self.postingDict = defaultdict(list)  # value = [(tweet_id, count_in_doc),...,(id, count)]
        self.named_entity_idx = defaultdict(list)
        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    if term == '':
                        print(term)
                    if term[0].isupper():
                        if term.lower() in self .inverted_idx.keys():  # this is upper and there was lower before -> insert as lower
                            new_term = term.lower()
                            self.inverted_idx[new_term] += 1
                            self.postingDict[new_term].append((document.tweet_id, document_dictionary[term], document.amount_of_unique_words, document.max_tf))
                        else:   # this is upper and there wad noting before -> insert as upper
                            self.inverted_idx[term] = 1
                            self.postingDict[term].append((document.tweet_id, document_dictionary[term], document.amount_of_unique_words, document.max_tf))

                    elif term[0].islower(): # this is lower and there wad upper before -> insert as lower and move what was at upper
                        if term.capitalize() in self.inverted_idx.keys():
                            self.inverted_idx[term] = self.inverted_idx[term.capitalize()] + 1
                            self.postingDict[term] = self.postingDict[term.capitalize()]
                            del self.inverted_idx[term.capitalize()]
                            del self.postingDict[term.capitalize()]

                        else:  # this is lower and there wad noting before -> insert as lower
                            self.inverted_idx[term] = 1
                    else:
                        self.inverted_idx[term] = 1
                        self.postingDict[term].append((document.tweet_id, document_dictionary[term], document.amount_of_unique_words, document.max_tf))
                else:  # term was in before in the same way
                    self.inverted_idx[term] += 1
                    self.postingDict[term].append((document.tweet_id, document_dictionary[term], document.amount_of_unique_words, document.max_tf))

            except:
                print('problem with the following key {}'.format(term[0]))
        self.add_named_entity(document)

    def add_named_entity(self, document):
        document_named_entity = document.named_entity
        if document_named_entity is not None:
            for name in document_named_entity:
                if name in self.named_entity_idx.keys():  # recognize as named_entity before
                    self.inverted_idx[name] += 1
                    self.postingDict[name].append((document.tweet_id, document_named_entity[name], document.amount_of_unique_words, document.max_tf))
                    self.postingDict[name].extend(self.named_entity_idx[name])

                else: # new possible entity
                    self.named_entity_idx[name].append((document.tweet_id, document_named_entity[name], document.amount_of_unique_words, document.max_tf))


