#!/usr/bin/env python3

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import inch
from pdf2image import convert_from_path

from PIL import Image as PILImage
from PIL import ImageDraw, ImageEnhance, ImageFilter
import random
import os
import math
import subprocess
from pathlib import Path

def generate_geometric_pattern(width=200, height=150, filename="/tmp/dummy.jpg"):
    """Genera imagen con formas geométricas aleatorias"""
    img = PILImage.new('RGB', (width, height), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(img)
    
    # Dibujar círculos aleatorios
    for _ in range(random.randint(3, 10)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(10, 80)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    # Dibujar rectángulos aleatorios
    for _ in range(random.randint(2, 8)):
        w = random.randint(0, math.floor(width*0.7))
        h = random.randint(0, math.floor(height*0.75))
        x1 = random.randint(0, width-1)
        y1 = random.randint(0, height-1) 
        x2 = min(math.floor(x1 + w), width)
        y2 = min(math.floor(y1 + h), height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([x1, y1, x2, y2], fill=color)
    
    img_blured = img.filter(ImageFilter.GaussianBlur(radius=5))
    enhancer = ImageEnhance.Color(img_blured)
    img_desaturated = enhancer.enhance(0.4)
    img_desaturated.save(filename, 'JPEG')
    #return filename

page_number_text=f"200"
def add_page_number(canvas, doc):
    """Adds a page number to the bottom center of each page."""
    canvas.saveState()
    canvas.setFont('Times-Roman', 10)
    #page_number_text = f"Page {doc.page}"
    #page_number_text = f"235"
    canvas.drawCentredString(doc.width / 2.0 + doc.leftMargin, 1 * inch, page_number_text)
    canvas.restoreState()

def subtitle_if_no_subtitle_yet(elementos, paragraph_style, there_is_no_subtitle_yet):
    if there_is_no_subtitle_yet and random.random() < 0.25:
        elementos.append(Paragraph("<b>" + build_random_title_text() + "</b>", paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))
        return False
    else:
        return True

def generar_pdf_justificado(destination="./dummy_page.jpg", type="right", pagination="123"):
    """
    Genera un archivo PDF con un párrafo de texto justificado.

    Args:
        texto (str): El texto que se incluirá en el PDF.
        pdf_path (str, optional): El nombre del archivo PDF a generar.
                                         Por defecto es "pdf_justificado.pdf".
    """

    if type == "right":
        leftM = 0.6
        rightM = 1.2
    else:
        leftM = 1.2
        rightM = 0.6

    pdf_path="/tmp/dummy_pdf.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A5,
        leftMargin=leftM*inch,
        rightMargin=rightM*inch,
        topMargin=0.9*inch,
        bottomMargin=1.4*inch
    )

    global page_number_text 
    page_number_text = pagination

   # Registrar y usar fuente TrueType
    pdfmetrics.registerFont(TTFont('Georgia', 'Georgia.ttf'))
    pdfmetrics.registerFont(TTFont('Georgia-Bold', 'Georgia_Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Georgia-Italic', 'Georgia_Italic.ttf'))
    pdfmetrics.registerFont(TTFont('Georgia-BoldItalic', 'Georgia_Bold_Italic.ttf'))

    styles = getSampleStyleSheet()
    paragraph_style = styles['Normal']
    paragraph_style.alignment = TA_JUSTIFY
    paragraph_style.fontName = 'Georgia'
    title_style = styles['Heading1']
    subtitle_style = styles['Heading4']

    img_filename = "/tmp/dummy.jpg"

    there_is_no_image_yet = True
    there_is_no_subtitle_yet = True

    elementos = []
    if random.random() < 0.15:
        elementos.append(Paragraph(build_random_title_text(), title_style))
        elementos.append(Spacer(1, 1 * inch))
        elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))
    elif random.random() < 0.15:   
        generate_geometric_pattern(width=275, height=150, filename=img_filename)
        img1 = Image(img_filename, width=275, height=150)
        elementos.append(img1)
        elementos.append(Spacer(1, 0.3 * inch))
        there_is_no_image_yet = False
    else:
        elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))

    if there_is_no_image_yet and random.random() < 0.15:
        elementos.append(Spacer(1, 0.3 * inch))
        generate_geometric_pattern(width=200, height=150, filename=img_filename)
        img1 = Image(img_filename, width=200, height=150)
        elementos.append(img1)
        elementos.append(Spacer(1, 0.3 * inch))
    else:
        there_is_no_subtitle_yet = \
            subtitle_if_no_subtitle_yet(elementos, paragraph_style, there_is_no_subtitle_yet)
        elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))
           
    there_is_no_subtitle_yet = subtitle_if_no_subtitle_yet(elementos, paragraph_style, there_is_no_subtitle_yet)
    elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
    elementos.append(Spacer(1, 0.1 * inch))

    there_is_no_subtitle_yet = subtitle_if_no_subtitle_yet(elementos, paragraph_style, there_is_no_subtitle_yet)
    elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
    elementos.append(Spacer(1, 0.1 * inch))

    if random.random() < 0.75:
        elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))
        elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))
        elementos.append(Paragraph(build_random_paragraph_text(), paragraph_style))
        elementos.append(Spacer(1, 0.1 * inch))

    doc.build(elementos, onFirstPage=add_page_number)

    pages = convert_from_path(pdf_path)
    if pages:
        dummy_page = pages[0]
        dummy_page.save(f'/tmp/dummy_page.jpg', 'JPEG')
    else:
        return False

    script_folder = os.path.dirname(os.path.abspath(__file__))
    if not script_folder.endswith('/'):
        script_folder = script_folder + '/'
    script_path = script_folder + "vintage2.sh"  # Reemplaza con la ruta real
    argumentos_script = ["/tmp/dummy_page.jpg", destination]  # Lista de argumentos
    
    try:
        resultado = subprocess.run(
            [script_path] + argumentos_script,
            capture_output=True,
            text=True,
            check=True  # Lanza excepción si el código de salida no es 0
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        return False
    except Exception as e:
        print(str(e))
        return False

    return True
    # Build the document with pagination
    #doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

LOREM_IPSUM_FRASES = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Integer risus odio, auctor non pulvinar id, gravida ac arcu.",
    "Phasellus tempus odio vel metus tincidunt, quis dictum risus dignissim.",
    "Cras fringilla dictum velit, quis imperdiet ante luctus vel.",
    "Phasellus vestibulum neque eu est interdum vehicula.",
    "Curabitur tincidunt vestibulum dui, nec posuere sem condimentum sed.",
    "Donec in pharetra nunc.",
    "Duis in ligula interdum, dictum ipsum non, mattis enim.",
    "Vestibulum interdum orci eget nisi fringilla, vel convallis ligula molestie.",
    "Aliquam faucibus ex vel iaculis rutrum.",
    "Fusce quis metus eleifend, rutrum leo a, laoreet erat.",
    "In gravida dignissim sodales.",
    "Sed quis sapien volutpat, sollicitudin risus ut, porttitor diam.",
    "Pellentesque lobortis vehicula nibh nec fermentum.",
    "Integer quis dolor nibh.",
    "Duis non justo at quam placerat vulputate et nec justo.",
    "Ut id nulla sodales, tincidunt ex nec, accumsan elit.",
    "Aliquam erat volutpat.",
    "Proin a tellus nec leo placerat aliquet ut quis justo.",
    "Interdum et malesuada fames ac ante ipsum primis in faucibus.",
    "Nunc sed dignissim nisi.",
    "Cras nisl orci, vehicula eget tempus vel, pretium id nisi.",
    "Etiam dictum suscipit tortor in pellentesque.",
    "Vestibulum in metus in tellus tempus venenatis viverra eu ante.",
    "Ut non dui sit amet urna imperdiet luctus.",
    "Donec nec metus lacinia, egestas eros sed, tempus sapien.",
    "Cras rutrum eu enim eu pellentesque.",
    "Quisque id egestas dui.",
    "Duis feugiat in enim eget ultricies.",
    "Phasellus semper odio ipsum, id sodales dui vestibulum nec.",
    "Curabitur tincidunt varius lacus in elementum.",
    "Cras at risus ac justo consequat egestas vitae ac leo.",
    "Nunc faucibus tincidunt rutrum.",
    "Nulla pellentesque fringilla diam sit amet pellentesque.",
    "Morbi at sem id tellus ullamcorper pellentesque.",
    "Nullam commodo ut risus at porttitor.",
    "Ut tempus mauris purus, ut ullamcorper enim volutpat eget.",
    "Fusce id lacinia nisl.",
    "Quisque sed auctor nisi, sed ultricies quam.",
    "Cras vitae venenatis orci, cursus auctor est.",
    "Maecenas rutrum odio eget augue hendrerit blandit.",
    "Aenean vel imperdiet tellus.",
    "In feugiat sodales dignissim.",
    "Aenean convallis porta egestas.",
    "Aliquam fermentum finibus mi nec sagittis.",
    "Nunc egestas metus odio.",
    "Aliquam vel orci fringilla, maximus risus nec, egestas nunc.",
    "Nunc odio elit, mollis vel posuere vel, blandit sed nisl.",
    "Nullam et urna ac nisl ultrices pellentesque.",
    "In gravida libero eget suscipit molestie.",
    "Suspendisse potenti."
]

LOREM_IPSUM_WORDS = "lorem ipsum dolor sit amet consectetur adipiscing elit integer risus odio auctor non pulvinar id gravida ac arcu hasellus tempus odio vel metus tincidunt quis dictum risus dignissim"

def build_random_title_text():
    num_words = random.randint(3, 8)
    words = LOREM_IPSUM_WORDS.split()
    selected_words = random.sample(words, min(num_words, len(words)))
    selected_words = " ".join(selected_words)
    return selected_words.capitalize()

def build_random_paragraph_text():
    num_frases = random.randint(3, 10)    
    frases_seleccionadas = random.sample(LOREM_IPSUM_FRASES, min(num_frases, len(LOREM_IPSUM_FRASES)))
    return " ".join(frases_seleccionadas)

def get_dummy_capture(path_left, path_right):
    if generar_pdf_justificado(path_left, type="left", pagination=f"22"):
        print(f"left generado ok")
        if generar_pdf_justificado(path_right, type="right", pagination=f"23"):
            print(f"right generado ok")
            return True
        else:
            return False
    else:
        return False

if __name__ == '__main__':
    #generar_pdf_justificado(type="left", pagination=f"23")
    if get_dummy_capture("left.jpg", "right.jpg"):
        print(f"dummy generado OK!")
