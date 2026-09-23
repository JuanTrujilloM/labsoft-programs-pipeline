import argparse
import csv
import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path

from pipeline.convert_to_pdf import convert_to_pdf
from pipeline.extract_metadata import extract_metadata
from pipeline.xlsx import write_xlsx


def parse_args():
    parser = argparse.ArgumentParser(description='Genera PDFs y Excels de programas de asignatura.')
    parser.add_argument('--program', required=True, help='Nombre exacto del programa, igual al de la carpeta en input/ y al del Program en la base de datos, ej. "Ingeniería mecánica (014-20241)"')
    parser.add_argument('--codes', default='codes.csv', help='CSV con columnas archivo,codigo,nombre de las materias disciplinares')
    parser.add_argument('--input-dir', default='input', help='Carpeta donde buscar (en cualquier nivel) la carpeta del programa, ej. el ZIP completo descomprimido')
    parser.add_argument('--output-dir', default='output', help='Carpeta donde se escriben los resultados')
    args = parser.parse_args()
    return args


def find_program_directory(input_dir, program_name):
    matches = [path for path in input_dir.rglob(program_name) if path.is_dir()]

    if not matches:
        raise ValueError(f'No se encontró la carpeta "{program_name}" dentro de {input_dir}')

    if len(matches) > 1:
        matches_text = ', '.join(str(match) for match in matches)
        raise ValueError(f'"{program_name}" aparece en más de una carpeta dentro de {input_dir}: {matches_text}')

    program_directory = matches[0]
    return program_directory


def slugify_program_name(program_name):
    name_without_code = re.sub(r'\s*\([^)]*\)\s*$', '', program_name).strip()
    normalized_name = unicodedata.normalize('NFKD', name_without_code.lower())
    ascii_name = normalized_name.encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '_', ascii_name).strip('_')
    return slug


def zip_pdfs(pdf_directory, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as archive:
        for pdf_file in sorted(pdf_directory.glob('*.pdf')):
            archive.write(pdf_file, arcname=pdf_file.name)


def main():
    args = parse_args()
    base_directory = Path(__file__).parent
    input_directory = base_directory / args.input_dir
    program_directory = find_program_directory(input_directory, args.program)
    output_directory = base_directory / args.output_dir
    output_directory.mkdir(parents=True, exist_ok=True)

    codes_path = base_directory / args.codes
    with open(codes_path, newline='', encoding='utf-8') as csv_file:
        courses = list(csv.DictReader(csv_file))

    for course in courses:
        if not course['codigo']:
            raise ValueError(f"Falta el código en {codes_path.name} para: {course['archivo']}")

    slug = slugify_program_name(args.program) + '_disciplinar'

    cursos_rows = []
    programas_rows = []
    incomplete_courses = []

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_directory = Path(temp_dir)

        for course in courses:
            document_path = program_directory / course['archivo']

            try:
                metadata = extract_metadata(document_path)

                pdf_path = pdf_directory / f"{course['codigo']}_{metadata['semestre']}.pdf"
                convert_to_pdf(document_path, pdf_path)
            except Exception as error:
                incomplete_courses.append((course['archivo'], str(error)))
                continue

            cursos_rows.append([course['codigo'], course['nombre'], args.program])
            programas_row = [
                course['codigo'],
                metadata['version'],
                metadata['fecha'],
                metadata['responsable'],
                metadata['semestre'],
            ]
            programas_rows.append(programas_row)

        cursos_path = output_directory / f'cursos_{slug}.xlsx'
        programas_path = output_directory / f'programas_asignatura_{slug}.xlsx'
        zip_path = output_directory / f'{slug}_pdfs.zip'

        write_xlsx('Cursos', ['código', 'nombre', 'programas'], cursos_rows, cursos_path)
        write_xlsx(
            'Programas de asignatura',
            ['código', 'versión', 'fecha', 'responsable', 'semestre'],
            programas_rows,
            programas_path,
        )
        zip_pdfs(pdf_directory, zip_path)

    print(f'Listo: {len(cursos_rows)} materias procesadas.')
    print(f'  {cursos_path}')
    print(f'  {programas_path}')
    print(f'  {zip_path}')

    if incomplete_courses:
        print(f'Materias incompletas ({len(incomplete_courses)}), no se generaron:')
        for archivo, error in incomplete_courses:
            print(f'  {archivo}: {error}')


if __name__ == '__main__':
    main()
