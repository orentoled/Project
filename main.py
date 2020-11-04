
import NLPInObject

text = "texttext"
expressions = "\"machine group\": (\"coffee machine\", \"product\", \"machine\"), \"button group\": (\"Power button\", \"Control Knob\")"


nlp = NLPInObject.NLPInObject(text, expressions)
nlp.expressionTxtToDict()
