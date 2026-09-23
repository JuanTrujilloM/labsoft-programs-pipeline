import subprocess
import tempfile
from pathlib import Path


def convert_to_pdf(document_path, output_pdf_path):
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', temp_dir, str(document_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f'{document_path}: falló la conversión a PDF: {result.stderr.strip()}')

        generated_path = Path(temp_dir) / (document_path.stem + '.pdf')
        generated_path.replace(output_pdf_path)
