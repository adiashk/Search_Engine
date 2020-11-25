import gensim
import gzip
import shutil


class Word2vec:
    def __init__(self):
        pass

    # def open_file(self):
    #     with gzip.open('C:\\Users\\Yuval Mor Yosef\\Desktop\\יובל מור יוסף\\בן גוריון\\סמסטר ה\\אחזור\\GoogleNews-vectors-negative300.bin.gz') as f_in:
    #         with open('GoogleNews-vectors-negative300.bin', 'wb') as f_out:
    #             shutil.copyfileobj(f_in, f_out)


    def get_most_similar_words(self, words_list):
        model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)

        # dog = model['dog']
        # print(dog.shape)
        # print(dog[:10])

        result = model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
        # result = model.most_similar(positive=words_list, negative=['skirt'], topn=3)
        print(result)
        return result


# word2vec = Word2vec()
# word2vec.open_file()
# word2vec.get_most_similar_words(['winter', 'dressed'])