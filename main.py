
import re
import NLPInObject
import GUI
import sys

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_COLOR_INDEX
from termcolor import colored

if __name__ == "__main__":
    GUI.start_app(sys.argv[1], sys.argv[2])

# GUI.start_app('C:/Users/User\PycharmProjects\ProjectNLP\demo3.txt', 'C:/Users/User\PycharmProjects\ProjectNLP\json.txt')
