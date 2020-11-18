
class NLPInObject:
    def __init__(self, text_object, expressions):
        self.text = text_object
        self.expressions = expressions
        self.name = "TEMP"
        self.words_to_mark = list()

        # make dictionary of label: expressions from the input text
    def expression_txt_to_dict(self):
        exps = self.expressions
        # parsing
        words = exps.replace("\"", "")
        words = words.split("),")
        global expressions_dict
        expressions_dict = dict()
        for i in range(len(words)):
            if i < len(words) - 1:
                # adding ) to end of each expressions
                words[i] += ")"
            # parsing
            temp = words[i].split(":")
            expressions_dict[temp[0]] = list(temp[1].split())
        print(expressions_dict)

    def get_words_to_mark(self):
        for key in expressions_dict:
            for value in expressions_dict[key]:
                value = value.replace(")", "")
                value = value.replace("(", "")
                value = value.replace(",", "")
                value = value.lower()
                print(value)
                self.words_to_mark.append(value)

