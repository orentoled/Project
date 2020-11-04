
class NLPInObject:
    def __init__(self, text_object, expressions):
        self.text = text_object
        self.expressions = expressions
        self.name = "TEMP"

        # make dictionary of label: expressions from the input text
    def expressionTxtToDict(self):
        exps = self.expressions
        # parsing
        words = exps.replace("\"", "")
        words = words.split("),")
        expressions = dict()

        for i in range(len(words)):
            if i < len(words) - 1:
                # adding ) to end of each expressions
                words[i] += ")"
            # parsing
            temp = words[i].split(":")
            expressions[temp[0]] = temp[1]
        print(expressions)
