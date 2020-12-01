import json
import operator

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import TweetTokenizer
from document import Document
import re
import utils
import spacy
from collections import Counter
from nltk.stem import PorterStemmer
import json
from emoji import UNICODE_EMOJI


class Parse:

    def __init__(self, stemming):
        self.stop_words = stopwords.words('english')
        self.stemming = stemming
        self.named_entity = None
        self.re_tweet_set = set()

    def parse_query(self, query):
        tokenized_text = self.parse_sentence(query)
        parse_query = []
        split_url = self.find_url(tokenized_text)  # create set of terms from URL or full text
        split_hashtag = self.find_hashtags(tokenized_text)
        index = 0
        while index < len(tokenized_text):
            term = tokenized_text[index]
            # term = self.remove_signs(term)
            if term == '':
                index += 1
                continue

            # roles :
            term, skip = self.convert_numbers(index, term, tokenized_text)

            if self.stemming:
                term = self.convert_stemming(term)

            parse_query.append(term)
            index += (skip + 1)

        for term in split_url:
            if self.stemming:
                term = self.convert_stemming(term)
            parse_query.append(term)

        for term in split_hashtag:
            if self.stemming:
                term = self.convert_stemming(term)
            parse_query.append(term)

        parse_query.extend(self.named_entity)
        return list(set(parse_query))
        # return [p for p in parse_query if p not in parse_query]

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # text_tokens = word_tokenize(text)
        # text_tokens = TweetTokenizer().tokenize(text)
        # test = 'www.yu.il/it/ RT (RTAF!) ~? 3533 yuval'
        self.named_entity = self.Named_Entity_Recognition(text)
        text = re.sub('(?<=\D)[.,!?()~:;"]|[\u0080-\uFFFF]|[.,](?=\D)', '', text)
        # test = re.sub('(?<=\D)[.,)(?:!]|[\u007B-\uFFFF]|[.,!](?=\D)', '', test)
        # test = re.compile(r"[a-zA-Z]+").findall(test)
        # mylist = ['spam', 'ham', 'eggs']
        # t = ' '
        # t = t.join(mylist)
        # print(t)
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        # text_tokens = WhitespaceTokenizer().tokenize(text)
        text_tokens = text.split(" ")

        # self.named_entity = self.Named_Entity_Recognition(text_tokens)
        # self.named_entity = self.Named_Entity_Recognition(text)

        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        text_tokens_without_stopwords = [w for w in text_tokens if w.lower() not in self.stop_words and len(w) > 0]

        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        quote_indices = doc_as_list[10]
        retweet_quoted_text = doc_as_list[11]
        retweet_quoted_urls = doc_as_list[12]
        retweet_quoted_indices = doc_as_list[13]
        term_dict = {}
        named_entity = None
        # named_entity = self.Named_Entity_Recognition(full_text)

        if full_text[0] == 'R' and full_text[1] == 'T':
            if retweet_url is not None:
                last_slash_index = retweet_url.rfind('/')
                if last_slash_index > 0:
                    original_tweet_id = retweet_url[last_slash_index + 1:len(retweet_url) - 2]
                    if len(original_tweet_id) > 0 and original_tweet_id.isdigit():
                        if original_tweet_id not in self.re_tweet_set:
                            self.re_tweet_set.add(original_tweet_id)
                        else:
                            return {}

        tokenized_text = self.parse_sentence(full_text)

        # doc_length = len(tokenized_text)  # after text operations.

        # for term in tokenized_text:  # enumerate---------------->
        tokenized_text_len = len(tokenized_text)
        temp_split_url = []
        #      temp_split_url = self.convert_full_url(url)  # get list of terms from URL
        temp_split_url = self.convert_full_url(url)  # get list of terms from URL
        skip = 0
        temp_split_hashtag = []
        index = 0
        doc_length = 0
        counter_rt = 0
        while index < len(tokenized_text):
            term = tokenized_text[index]
            term = self.remove_signs(term)
            # if term == 'RT' or term == 'rt':
            #     counter_rt += 1
            #     break
            if term == '' or not term.isascii():
                index += 1
                continue

            # index = tokenized_text_len - 1 - i
            # term = self.covert_words(index, term, tokenized_text)  # replace: Number percent To Number%

            # roles :
            term, skip = self.convert_numbers(index, term, tokenized_text)
            temp_split_hashtag, to_delete_Hash = self.convert_hashtag(term, temp_split_hashtag)
            temp_split_url, to_delete_URL = self.convert_url(term, temp_split_url)  # create set of terms from URL or full text
            #   temp_split_url, to_delete_URL = self.convert_url(term, temp_split_url)  # create set of terms from URL or full text

            if self.stemming:
                term = self.convert_stemming(term)
            if not to_delete_Hash:
                if not to_delete_URL:
                    if term not in term_dict.keys():
                        term_dict[term] = 1
                    else:
                        term_dict[term] += 1

            index += (skip + 1)

        for term in temp_split_hashtag:
            if self.stemming:
                term = self.convert_stemming(term)
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        for term in temp_split_url:
            if self.stemming:
                term = self.convert_stemming(term)
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        doc_length = doc_length + len(temp_split_url) + len(temp_split_hashtag)

        amount_of_unique_words = len(term_dict)

        if len(term_dict) > 0:
            most_frequent_term = max(term_dict, key=term_dict.get)
            max_tf = term_dict[most_frequent_term]

        else:
            most_frequent_term = ""
            max_tf = 0

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, amount_of_unique_words, max_tf, most_frequent_term, self.named_entity)
        return document

    def remove_signs(self, term):
        if type(term) is str:
            # check if can add to regex
            term = term.replace(':', '')
            # term = term.replace('?', '')
            # term = term.replace('!', '')
            # term = term.replace('(', '')
            # term = term.replace(')', '')
            # new_term=''
            # for c in term:
            #     new_term += c if len(c.encode(encoding='utf_8')) == 1 else ''
            # if re.search(u'[\u0000–\u007f]', term.encode('utf-8')) is True:
            #     term = new_term
            # if '②' in term:
            #     term = term.replace('②', '')
            # for t in term:
            #     if t in UNICODE_EMOJI:
            #         term = term.replace(t, '')
        return term

    def convert_hashtag(self, term, temp_split_hashtag):
        if "#" in term:
            split_hashtag = self.split_hashtag(term)
            temp_split_hashtag.extend(split_hashtag)
            return temp_split_hashtag, True
        return temp_split_hashtag, False

    def split_hashtag(self, tag):
        temp_tag = tag
        pattern = []
        tag = tag.replace('#', '')
        if "_" in tag:  # we_are -> we are
            pattern = tag.split("_")
            new_pattern = []
            for i in pattern:
                new_pattern.extend(re.compile(r"[a-z]+|[A-Z][a-z]+|\d+|[A-Z]+(?![a-z])").findall(i))
            new_term_tag = " "
            new_term_tag = new_term_tag.join(new_pattern)  # #letItBe->let it be
            new_term_tag = new_term_tag.lower()
            new_pattern.append(new_term_tag)
            new_term_tag = new_term_tag.replace(' ', '')
            new_pattern.append("#" + new_term_tag.lower())  # #letItBe-> #letitbe
            pattern = []
            pattern.extend(new_pattern)

        else:
            pattern = re.compile(r"[a-z]+|[A-Z][a-z]+|\d+|[A-Z]+(?![a-z])").findall(tag)
            new_term_tag = " "
            new_term_tag = new_term_tag.join(pattern)  # #letItBe->let it be
            new_term_tag = new_term_tag.lower()
            pattern.append(new_term_tag)
            pattern.append("#" + tag.lower())  # #letItBe-> #letitbe

        pattern = [i for i in pattern if i]
        pattern = [i.lower() for i in pattern if i.lower() not in self.stop_words]
        return pattern

    def find_hashtags(self, text_tokens):
        hashtags = [s for s in text_tokens if "#" in s]
        split_hashtags = []
        # word = []
        for h in hashtags:
            # word = self.split_hashtag(h)
            split_hashtags.extend(self.split_hashtag(h))
        return split_hashtags

    def convert_full_url(self, url):
        if url != "{}":
            tempSplitURL = []
            url = json.loads(url)
            for u in url:
                tempSplitURL.extend(self.split_url(url[u]))
            tempSplitURL = set(tempSplitURL)
            return list(tempSplitURL)
        else:
            return []

    def convert_url(self, term, temp_split_url):
        if "http" in term:
            if len(temp_split_url) > 0:  # there was long URL
                return temp_split_url, True

            urlstokens = self.split_url(term)
            temp_split_url.extend(urlstokens)
            temp_split_url = set(temp_split_url)
            temp_split_url = list(temp_split_url)
            return temp_split_url, True

        return temp_split_url, False

    def split_url(self, tag):

        # pattern = re.compile(r'[\:/?=\-&]+', re.UNICODE)
        # return pattern.findall(self, tag)
        pattern = []
        if tag is None:
            return pattern
        if "www." in tag:
            # tag = tag.replace('www.', '')
            tag = tag.replace('www.', '')
            pattern = re.compile(r'[\//\:/?=\-&+]', re.UNICODE).split(tag)
            # pattern += ["www"]
        else:
            pattern = re.compile(r'[\:/?=\-&+]', re.UNICODE).split(tag)
        pattern = [i for i in pattern if i]
        pattern = [i for i in pattern if i.lower() not in self.stop_words and i != "status" and i != "web"]
        return pattern


    def find_url(self, text_tokens):
        url = [s for s in text_tokens if "http" in s]
        split_urls = []
        # word = []
        for h in url:
            # word = self.split_hashtag(h)
            split_urls.extend(self.split_url(h))
        return split_urls

    def remove_url_from_token(self, text_tokens):
        text_tokens = [x for x in text_tokens if "http" not in x]
        return text_tokens


    def convert_numbers(self, index, term, tokenized_text):
        skip = 0
        if term[0].isdigit():
            term = term.replace(',', '')
            if term.isdigit():  # no dots or signs
                term, skip = self.convert_big_numbers(index, term, tokenized_text, skip)

            else:
                try:

                    float(term)  # decimal number
                    term, skip = self.convert_small_numbers(index, term, tokenized_text, skip)
                except:  # sings
                    if not term[len(term) - 1].isdigit():
                        sign = term[len(term) - 1]
                        if term[0:len(term) - 1].isdigit():  # no dots or signs
                            term = term[0:len(term) - 1]
                            new_term, skip = self.convert_big_numbers(index, term, tokenized_text, skip)
                            if new_term == term:
                                term, skip = self.convert_small_numbers(index, term, tokenized_text, skip)
                            else:
                                term = new_term
                            term += sign
            #  unique words
            if index < len(tokenized_text) - 1 - skip:
                after_term = tokenized_text[index + 1 + skip]
                if after_term.lower() == "percent" or after_term.lower() == "percentage":
                    term += '%'
                    skip += 1
                if after_term.lower() == "dollar" or after_term.lower() == "dollars":
                    term += '$'
                    skip += 1
                if after_term.lower() == "thousand":
                    term += 'K'
                    skip += 1
                if after_term.lower() == "million":
                    term += 'M'
                    skip += 1
                if after_term.lower() == "billion":
                    term += 'B'
                    skip += 1

        return term, skip

    def convert_big_numbers(self, index, term, tokenized_text, skip):  # get term that it only digits
        is_changed = False
        number = int(float(term))
        if 1000 <= number < 1000000:
            # new_num = round(number / 1000, 3)  # keep 3 digits
            new_num = number / 1000
            dot_index = str(new_num).index('.')
            new_num_small = str(new_num)[0:dot_index + 4]
            new_num = str(new_num)[0:dot_index]
            try:
                if int(new_num) == float(new_num_small):
                    term = new_num + "K"
                else:
                    term = new_num_small + "K"
            except:
                term = new_num_small + "K"
            is_changed = True
        elif 1000000 <= number < 1000000000:
            new_num = number / 1000000
            dot_index = str(new_num).index('.')
            new_num_small = str(new_num)[0:dot_index + 4]
            new_num = str(new_num)[0:dot_index]
            try:
                if int(new_num) == float(new_num_small):
                    term = new_num + "M"
                else:
                    term = new_num_small + "M"
            except:
                term = new_num_small + "M"

            is_changed = True
        elif 1000000000 <= number:
            new_num = number / 1000000000
            dot_index = str(new_num).index('.')
            new_num_small = str(new_num)[0:dot_index + 4]
            new_num = str(new_num)[0:dot_index]
            try:
                if int(new_num) == float(new_num_small):
                    term = new_num + "B"
                else:
                    term = new_num_small + "B"
            except:
                term = new_num_small + "B"

            is_changed = True

        term, skip = self.convert_divided_numbers(index, term, tokenized_text, skip,
                                                  is_changed)  # 2000 1/3 --> 2K skip in the 1/3
        return term, skip

    def convert_small_numbers(self, index, term, tokenized_text, skip):
        if '.' in term:
            if float(term) > 999:
                term, skip = self.convert_big_numbers(index, term, tokenized_text, skip)
            else:
                dot_index = term.index('.')
                term = term[0:dot_index + 4]
        return term, skip

    def convert_divided_numbers(self, index, term, tokenized_text, skip, is_big):
        if index < len(tokenized_text) - 1:
            after_term = tokenized_text[index + 1]
            if '/' in after_term:
                slash_index = after_term.index('/')
                # if after_term[slash_index-1] is not None and after_term[slash_index + 1] is not None:
                if len(after_term) >= 3:
                    if after_term[slash_index - 1].isdigit():
                        if slash_index + 1 < len(after_term) - 1:
                            if after_term[slash_index + 1].isdigit():
                                if not is_big:
                                    term += ' ' + after_term
                            skip += 1
        return term, skip


    # def Named_Entity_Recognition(self, text_tokens):
    #     names = []
    #     # upper_words = re.compile(r"[A-Z][a-z]+|[A-Z]+(?![a-z])").findall(text)
    #     # upper_words = [w for w in text_tokens if w[0].isupper() and len(w) > 0]
    #     upper_words = []
    #     index = 0
    #     while index < len(text_tokens):
    #         term = text_tokens[index]
    #         if len(term) > 0 and term[0].isupper():
    #         # if len(term) > 0 and (term[0].isupper() or term[0].isdigit()):
    #             next_index = index + 1
    #             while next_index < len(text_tokens):
    #                 next_term = text_tokens[next_index]
    #                 if len(next_term) > 0 and next_term[0].isupper():
    #                 # if len(next_term) > 0 and (next_term[0].isupper() or next_term[0].isdigit()):
    #                     if '-' in next_term:
    #                         next_term = next_term.replace('-', ' ')
    #                     # if term[0].isdigit() and next_term[0].isdigit():
    #                     #     continue
    #                     term += ' ' + next_term  # add the next word
    #                     next_index += 1
    #                 else:
    #                     break
    #             index = next_index
    #             if term.lower() not in self.stop_words:
    #                 if ' ' in term:
    #                     names.append(term)
    #         else:
    #             index += 1
    #
    #     counter_names = Counter(names)
    #     return counter_names


    def Named_Entity_Recognition(self, text):

        # update_text = re.sub('(?<=\D)[!?()~:;]|[\u0080-\uFFFF]|(?:\s)http[^, ]*|(?:\s)[a-z][^, ]*|(?:\s)#[^, ]*|(?:\s)@[^, ]*|[!?()~:;](?=\D)', '', text)
        update_text = re.sub('(?<=\D)[!?()~"”“:;]|[\u0080-\uFFFF]|[\u201C]|[!?()~:;](?=\D)', '', text)
        update_text = re.sub('(?:\s)http[^, ]*|(?:\s)[a-z][^, ]*|(?:\s)#[^, ]*|(?:\s)&[^, ]*|@\w*\s*|#\w*\s*|', '', text)

        update_text = update_text.replace('\n', ' ')
        update_text = update_text.replace('\t', ' ')
        # update_text = update_text.replace('-', ' ')
        update_text = update_text.replace("RT", '')
        update_text = update_text.replace(':', '')
        update_text = update_text.replace("”", '')
        update_text = update_text.replace('"', '')
        char = "'"
        update_text = update_text.replace(char, ' ')
        # text_tokens = WhitespaceTokenizer().tokenize(text)
        text_tokens = update_text.split(" ")
        text_tokens = [i for i in text_tokens if i]
        for term in text_tokens:
            if term[0] == "“":
                term = term[1:len(term)]
        text_tokens = [i for i in text_tokens if i.isascii() and (i[0].isdigit() or i[0].isupper())]
        origin = text.split(" ")

        names = []
        index_in_text_tokens = 0
        index_in_origin = 0

        while index_in_text_tokens < len(text_tokens):
            term = text_tokens[index_in_text_tokens]
            if term.isascii():
                new_term = term
            else:
                index_in_text_tokens += 1
                continue
            while index_in_origin < len(origin) and term not in origin[index_in_origin]:
                index_in_origin += 1
            # upper_words.append(term)
            next_index_in_text_tokens = index_in_text_tokens + 1
            index_in_origin += 1 #location of next term
            if len(text_tokens)-next_index_in_text_tokens > 0:
                # next_index += 1
                next_term = text_tokens[next_index_in_text_tokens]
                while index_in_origin < len(origin) and len(text_tokens)-next_index_in_text_tokens > 0 and next_term in origin[index_in_origin]:
                    # upper_words.append(next_term)
                    new_term += ' ' + next_term
                    next_index_in_text_tokens += 1
                    if len(text_tokens) - next_index_in_text_tokens > 0:
                        next_term = text_tokens[next_index_in_text_tokens]
                        index_in_origin += 1
                    else:
                        break
            if new_term.find(" ") != -1:
                # new_term = new_term.replace('-', ' ')
                temp_new_term = new_term.split(" ")
                if temp_new_term[0].isdigit():
                    names.append(new_term) #with numbers
                    new_term = new_term.replace(str(temp_new_term[0]) + ' ', '')
                    names.append(new_term)  # without numbers
                else:
                    names.append(new_term)
            index_in_text_tokens = next_index_in_text_tokens

        return Counter(names)


    def convert_stemming(self, term):
        ps = PorterStemmer()
        if term[0].isupper():
            term = ps.stem(term).upper()
        else:
            term = ps.stem(term)
        return term
