
import re

import NLPInObject

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_COLOR_INDEX






text = "After carefully unpacking your espresso  machine, wash all removable parts with warm soapy water and rinse thoroughly. The Power Button button will light solid blue while the indicator light on the Control Knob button will start to blink, indicating the machine machine is heating up."

expressions = "\"machine group\": (\"coffee machine\", \"product\", \"machine\"), \"button group\": (\"Power button\", \"Control Knob\"), \"shiran group\": (\"Power shiran\", \"Control shiran\")"


nlp = NLPInObject.NLPInObject(text, expressions)
nlp.expressionTxtToDict()


document = Document()
document.add_heading('Tryout', 0)
p = document.add_paragraph(text)

font = p.add_run().font
font.highlight_color = WD_COLOR_INDEX.YELLOW

document.save('demo.docx')




document = Document()



doc = Document('demo.docx')

pattern = "machine"

for p in doc.paragraphs:

    if re.findall(pattern, p.text):
        runs = list(p.runs)
        p.text = ''

        for run in runs:
            match = re.search(pattern, run.text)

            if not match:
                newrun = p.add_run(run.text)
                if run.bold:
                    newrun.bold = True
                if run.italic:
                    newrun.italic = True
            else:
                start, end = match.span()
                p.add_run(run.text[0:start])
                colored = p.add_run(run.text[start:end])
                colored.font.highlight_color = WD_COLOR_INDEX.YELLOW
                p.add_run(run.text[end:len(run.text)+1])

doc.save('demo.docx')
