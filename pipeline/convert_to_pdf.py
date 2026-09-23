from docx2pdf import convert


def convert_to_pdf(document_path, output_pdf_path):
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    convert(str(document_path), str(output_pdf_path))
