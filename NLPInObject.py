
import docx

class NLPInObject:
    def __init__(self, text_object, expressions):
        self.text = text_object
        self.expressions = expressions
        self.name = "TEMP"
    def makeExpressionsDict(self):
        s = "\"machine group\": (\"coffee machine\", \"product\", \"machine\"), \"button group\": (\"Power button\", \"Control Knob\"), \"shiran group\": (\"Power shiran\", \"Control shiran\")"
        words = s.replace("\"", "")
        words = words.split("),")
        # for i in range(len(words)):
        #     if i < len(words) - 1:
        #         words[i] += ")"
        #     print(i)
        #     print(words[i])


        # for i in range(len(words)):
        #     temp = words[i].split(":")
        #     print(temp)
        #     expressions[temp[0]] = temp[1]
        # print(expressions)
