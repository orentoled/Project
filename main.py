import re

import NLPInObject
from docx import Document
from docx.enum.text import WD_COLOR_INDEX

text = "After carefully unpacking your 14-03-2020 espresso machine machine, wash all removable parts with warm soapy water and rinse thoroughly. The Power Button button will light solid blue while the indicator light on the Control Knob button will start to blink, indicating the machine machine is heating up."

expressions = "\"machine group\": (\"coffee machine\", \"product\", \"machine\"), \"button group\": (\"Power button\", \"Control Knob\"), \"shiran group\": (\"Power shiran\", \"Control shiran\")"


nlp = NLPInObject.NLPInObject(text, expressions)
nlp.expressionTxtToDict()


document = Document()
document.add_heading('Tryout', 0)
p = document.add_paragraph(text)

font = p.add_run().font
font.highlight_color = WD_COLOR_INDEX.YELLOW

document.save('demo.docx')

doc = Document('demo.docx')

for d in doc.paragraphs:
    for run in d.runs:
        date1 = re.findall("machine", run.text)
        print(date1)
        if date1:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW

doc.save('demo.docx')
