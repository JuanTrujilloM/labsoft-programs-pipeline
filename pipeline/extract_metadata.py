import re
import subprocess

FECHA_PATTERN = re.compile(r'^fecha\s*elaboraci[oó]n\s*:[ \t]*(.*)$', re.IGNORECASE | re.MULTILINE)
VERSION_PATTERN = re.compile(r'^versi[oó]n\s*n[uú]mero\s*:[ \t]*(.*)$', re.IGNORECASE | re.MULTILINE)
RESPONSABLE_PATTERN = re.compile(r'^responsable\s*:[ \t]*(.*)$', re.IGNORECASE | re.MULTILINE)


def find_field(pattern, text):
    match = pattern.search(text)
    if match is None:
        return None

    value = match.group(1).strip()
    if not value:
        return None

    return value


def extract_metadata(document_path):
    result = subprocess.run(
        ['textutil', '-convert', 'txt', '-stdout', str(document_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    text = result.stdout

    raw_fecha = find_field(FECHA_PATTERN, text)
    raw_version = find_field(VERSION_PATTERN, text)
    responsable = find_field(RESPONSABLE_PATTERN, text)

    missing_fields = []
    if raw_fecha is None:
        missing_fields.append('fecha elaboración')
    if raw_version is None:
        missing_fields.append('versión número')
    if responsable is None:
        missing_fields.append('responsable')

    if missing_fields:
        fields_text = ', '.join(missing_fields)
        raise ValueError(f'{document_path}: falta completar en el Word: {fields_text}')

    fecha_parts = raw_fecha.split('/')
    if len(fecha_parts) != 3:
        raise ValueError(f'{document_path}: fecha "{raw_fecha}" no tiene el formato DD/MM/AAAA')

    day = fecha_parts[0]
    month = fecha_parts[1]
    year = fecha_parts[2]
    fecha = f'{year}-{month.zfill(2)}-{day.zfill(2)}'

    if int(month) <= 6:
        semestre = f'{year}-1'
    else:
        semestre = f'{year}-2'

    version = raw_version
    if version.isdigit() and len(version) == 1:
        version = version.zfill(2)

    metadata = {'fecha': fecha, 'version': version, 'responsable': responsable, 'semestre': semestre}
    return metadata
