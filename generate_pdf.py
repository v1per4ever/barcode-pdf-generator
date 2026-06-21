import sys
import csv
import os
import argparse
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128

# Размеры страницы в мм
WIDTH_MM = 58
HEIGHT_MM = 40

# Размеры шрифта для каждой строки текста
FONT_SIZE_BARCODE = 8
FONT_SIZE_NAME = 6
FONT_SIZE_WB = 9
FONT_SIZE_SELLER = 7

# Параметры штрих-кода
BARCODE_HEIGHT_MM = 15
BARCODE_WIDTH_MM = 0.4

# Отступы в мм
MARGIN_TOP_MM = 3
SPACING_TEXT_MM = 5
SPACING_AFTER_BARCODE_MM = 2.5
SPACING_NAME_LINES_MM = 2

# Проценты размеров штрих-кода от размера страницы
BARCODE_WIDTH_PERCENT = 0.9
BARCODE_HEIGHT_PERCENT = 0.5

WIDTH = WIDTH_MM * mm
HEIGHT = HEIGHT_MM * mm

FONT_NAME = "Helvetica"
FONT_REGISTERED = False

def register_font():
    """Зарегистрировать шрифт с поддержкой кириллицы"""
    global FONT_NAME, FONT_REGISTERED
    
    if FONT_REGISTERED:
        return FONT_NAME
    
    montserrat_paths = [
        "~/Library/Fonts/Montserrat-Regular.ttf",
        "~/Library/Fonts/Montserrat.ttf",
        "/Library/Fonts/Montserrat-Regular.ttf",
        "/Library/Fonts/Montserrat.ttf",
        "/System/Library/Fonts/Supplemental/Montserrat-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Montserrat.ttf",
    ]
    
    for path in montserrat_paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            try:
                pdfmetrics.registerFont(TTFont('Montserrat', expanded))
                FONT_NAME = 'Montserrat'
                FONT_REGISTERED = True
                return FONT_NAME
            except Exception:
                continue
    
    arial_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Microsoft/Arial.ttf",
    ]
    
    for path in arial_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('Arial', path))
                FONT_NAME = 'Arial'
                FONT_REGISTERED = True
                return FONT_NAME
            except Exception:
                continue
    
    FONT_REGISTERED = True
    return FONT_NAME

def wrap_text_to_lines(canvas_obj, font_name, font_size, text, max_width):
    """Разбить текст на две строки, если он не помещается"""
    canvas_obj.setFont(font_name, font_size)
    text_width = canvas_obj.stringWidth(text, font_name, font_size)
    
    if text_width <= max_width:
        return [text]
    
    words = text.split()
    if len(words) <= 1:
        mid = len(text) // 2
        return [text[:mid], text[mid:]]
    
    line1_words = []
    line1_text = ""
    
    for i, word in enumerate(words):
        test_line = " ".join(words[:i+1])
        test_width = canvas_obj.stringWidth(test_line, font_name, font_size)
        if test_width <= max_width:
            line1_words = words[:i+1]
            line1_text = test_line
        else:
            break
            
    if not line1_words:
        mid = len(words) // 2
        line1_words = words[:mid]
        line1_text = " ".join(line1_words)
    
    line2_words = words[len(line1_words):]
    line2_text = " ".join(line2_words) if line2_words else ""
    return [line1_text, line2_text] if line2_text else [line1_text]

def create_barcode_object(barcode_value):
    try:
        return code128.Code128(
            str(barcode_value),
            barHeight=BARCODE_HEIGHT_MM*mm,
            barWidth=BARCODE_WIDTH_MM*mm,
            humanReadable=False
        )
    except Exception as e:
        print(f"Ошибка штрих-кода {barcode_value}: {e}", file=sys.stderr)
        return None

def create_pdf(output_file, barcode_value, name, article_wb, article_seller):
    font_name = register_font()
    c = canvas.Canvas(output_file, pagesize=(WIDTH, HEIGHT))
    barcode_obj = create_barcode_object(barcode_value)
    
    if barcode_obj:
        barcode_width, barcode_height = barcode_obj.wrap(WIDTH * BARCODE_WIDTH_PERCENT, HEIGHT * BARCODE_HEIGHT_PERCENT)
        x = (WIDTH - barcode_width) / 2
        y = HEIGHT - barcode_height - MARGIN_TOP_MM * mm
        
        barcode_obj.drawOn(c, x, y)
        y_text = y - SPACING_AFTER_BARCODE_MM * mm
        
        if barcode_value and str(barcode_value).strip():
            c.setFont(font_name, FONT_SIZE_BARCODE)
            c.drawCentredString(WIDTH / 2, y_text, str(barcode_value))
            y_text -= SPACING_TEXT_MM * mm
        
        if name and str(name).strip():
            c.setFont(font_name, FONT_SIZE_NAME)
            name_text = str(name).strip()
            max_text_width = WIDTH * 0.9
            name_lines = wrap_text_to_lines(c, font_name, FONT_SIZE_NAME, name_text, max_text_width)
            for i, line in enumerate(name_lines):
                c.drawCentredString(WIDTH / 2, y_text, line)
                if i < len(name_lines) - 1:
                    y_text -= SPACING_NAME_LINES_MM * mm
                else:
                    y_text -= SPACING_TEXT_MM * mm
                    
        if article_wb and str(article_wb).strip():
            c.setFont(font_name, FONT_SIZE_WB)
            wb_text = f"Артикул WB: {str(article_wb)}"
            c.drawCentredString(WIDTH / 2, y_text, wb_text)
            y_text -= SPACING_TEXT_MM * mm
            
        if article_seller and str(article_seller).strip():
            c.setFont(font_name, FONT_SIZE_SELLER)
            seller_text = f"Артикул продавца: {str(article_seller)}"
            c.drawCentredString(WIDTH / 2, y_text, seller_text)
    else:
        c.setFont(font_name, FONT_SIZE_BARCODE)
        c.drawCentredString(WIDTH / 2, HEIGHT / 2, str(barcode_value))
    
    c.save()
    return output_file

def generate_from_csv(csv_path, output_dir):
    """Функция для использования из Flask/UI"""
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']
    encoding = None
    
    for enc in encodings:
        try:
            with open(csv_path, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                if ('Артикул продавца' in reader.fieldnames and 
                    'Баркоды' in reader.fieldnames and 
                    'Наименование' in reader.fieldnames):
                    encoding = enc
                    break
        except Exception:
            continue
            
    if not encoding:
        raise ValueError("Не удалось определить кодировку или не найдены нужные столбцы")

    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            article_seller = row.get('Артикул продавца', '').strip()
            article_wb = row.get('Артикул WB', '').strip()
            barcode_value = row.get('Баркоды', '').strip()
            name = row.get('Наименование', '').strip()
            
            if not article_seller or not barcode_value:
                continue
                
            safe_filename = "".join(c for c in article_seller if c.isalnum() or c in ('-', '_', '.')).rstrip()
            if not safe_filename:
                safe_filename = f"barcode_{len(generated_files) + 1}"
                
            output_file = os.path.join(output_dir, f"{safe_filename}.pdf")
            create_pdf(output_file, barcode_value, name, article_wb, article_seller)
            generated_files.append(output_file)
            
    return generated_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация PDF штрихкодов из CSV")
    parser.add_argument("csv_file", help="Путь к CSV файлу")
    parser.add_argument("output_dir", help="Директория для сохранения PDF")
    args = parser.parse_args()
    
    try:
        files = generate_from_csv(args.csv_file, args.output_dir)
        print(f"Готово! Создано {len(files)} PDF файлов в {args.output_dir}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
