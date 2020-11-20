from parser_module import Parse


def test_parser():
    p = Parse(stemming=False)
    text = 'Adi'
    # text1 = '1010.55112556 500% 35.66 22 1/3 35,000 1/3 77,000,200 1000 1/4 percent 5 Thousand 55 Million 66 Billion 890,123,414,854 Hello 10,123 10.56% 10,344.5 hello 123 percentage'
    # text1 += ' #LetItBe #I_Love_NewYork #we_are_here'
    text1 = ['https://www.instagram.com/p/CD7fAPWs3WM/?igshid=o9kf0ugp1l8x', 'https://www.geeksforgeeks.org/python-program-to-convert-a-list-to-string']
    input = ['1280966288253292546', 'Wed Jul 08 20:45:36 +0000 2020', text, text1, '', None, '', None]
    # Expected = ['1.01K', '500%', '35.66', '22 1/3', '35K', '77M', '1K%', '5K', '55M', '66B', '890.123B',
    #             'Hello', '10.123K', '10.56%', '10.344K', 'hello', '123%',
    #             '#letitbe', 'let it be', 'let', '#ilovenewyork', 'i love new york', 'love', 'new', 'york',
    #             '#wearehere', 'we are here',
    Expected = ['Adi', 'https', 'www', 'instagram.com', 'p', 'CD7fAPWs3WM', 'igshid', 'o9kf0ugp1l8x'
                'https', 'www', 'geeksforgeeks.org', 'python', 'program', 'convert', 'list', 'string'
                ]
    Actual = list(p.parse_doc(input).term_doc_dictionary.keys())
    assert set(Actual) == set(Expected)


test_parser()


#LetItBe --> 'let it be'

# text += " 123 Thousand bdjsnsa mdjas"
# text += " 123 percentage"
# text += " 10,123"
# text += " 1010.56"
# text += " 10.56%"
# text += " 35 3/4"
# text += " 1.5618"
# text += " 10,344.5"
# text += " Hello"
# text += " hello"