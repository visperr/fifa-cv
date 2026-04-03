import easyocr

print("Loading OCR AI... (This might take a few seconds...)")
ocr_reader = easyocr.Reader(['en'], gpu=False)
