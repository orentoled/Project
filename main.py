import re
import NLPInObject
import GUI

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from termcolor import colored


start_app()

"""

text = "After shiran carefully unpacking your 14-03-2020 espresso machine machine, wash all removable parts with warm soapy water and rinse thoroughly. The Power Button button will light solid blue while the indicator light on the Control Knob button will start to blink, indicating the machine machine is heating up."

expressions = "\"machine group\": (\"coffee machine\", \"product\", \"machine\"), \"button group\": (\"Power button\", \"Control Knob\"), \"shiran group\": (\"Power shiran\", \"Control shiran\")"


def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )



nlp = NLPInObject.NLPInObject(text, expressions)
nlp.expression_txt_to_dict()
nlp.get_words_to_mark()


document = Document()
document.add_heading('Text HighLighter', 0)
p = document.add_paragraph(text)

# Setup regex
patterns = [r'\b' + word + r'\b' for word in nlp.words_to_mark]
re_highlight = re.compile('(' + '|'.join(p for p in patterns) + ')+',
                          re.IGNORECASE)


def highlight_words(document_input):
    for para in document_input.paragraphs:
        text_item = para.text
        if len(re_highlight.findall(text_item)) > 0:
            matches = re_highlight.finditer(text_item)
            para.text = ''
            p3 = 0
            for match in matches:
                p1 = p3
                p2, p3 = match.span()
                para.add_run(text_item[p1:p2])
                run = para.add_run(text_item[p2:p3])
                run.font.highlight_color = WD_COLOR_INDEX.YELLOW
            para.add_run(text_item[p3:])


document.save('demo.docx')
doc = Document('demo.docx')
doc.save('demo.docx')

"""
"""

for paragraph in document.paragraphs:
    for word in paragraph.text:
        #for run in paragraph.runs:
        if word in nlp.words_to_mark:
            #x = run.text.split()
           # run.clear()
           # for i in range(len(x)-1):
                #run.add_text(x[i])
                #run.add_text(word)
            font = word.add_run().font
            font.highlight_color = WD_COLOR_INDEX.YELLOW
            word.font.highlight_color = WD_COLOR_INDEX.YELLOW





formattedText = []
for word in text.lower().split():
    if word in nlp.words_to_mark:
        formattedText.append(colored(word, 'red', 'on_yellow'))
    else:
        formattedText.append(word)

text2 = ""
for word in formattedText:
    text2 += word + " "
text2 += " "
print(text2)

result = "".join(c for c in text2 if valid_xml_char_ordinal(c))

p2 = document.add_paragraph(result)
"""



#font = p.add_run().font
#font.highlight_color = WD_COLOR_INDEX.YELLOW







