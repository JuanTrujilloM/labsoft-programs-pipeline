# labsoft-programs-pipeline

Genera, a partir de los `.doc`/`.docx` de programas de asignatura de `programs.zip`,
los archivos listos para importar en el admin de `labsoft-courseprogram`:

- `pdfs/{código}_{semestre}.pdf` (uno por materia)
- `cursos_<slug>.xlsx` (hoja "Cursos": código | nombre | programas)
- `programas_asignatura_<slug>.xlsx` (hoja "Programas de asignatura": código | versión | fecha | responsable | semestre)
- `<slug>_pdfs.zip` con todos los PDFs, para subir junto al segundo xlsx

## Requisitos

- macOS con Microsoft Word instalado (se usa para convertir `.doc`/`.docx` a PDF vía `docx2pdf`).
- Python 3.

## Uso

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. Copia la carpeta del programa (ej. `Ingeniería mecánica (014-20241)`) dentro de `input/`.
2. Completa un CSV con columnas `archivo,codigo,nombre`: una fila por materia disciplinar, con la ruta del archivo relativa a la carpeta del programa, su código oficial y su nombre. La columna `codigo` viene vacía a propósito en el ejemplo — esos códigos no están en los documentos, hay que tomarlos del catálogo oficial de la escuela.
3. Corre, pasando el nombre exacto del programa (igual al de la carpeta en `input/` y al del `Program` en la base de datos) y el CSV que llenaste:

```bash
python3 main.py --program "Ingeniería mecánica (014-20241)" --codes codes.csv
```

El nombre del programa también se usa para nombrar los archivos de salida (`cursos_<slug>.xlsx`, etc.), así que no hace falta tocar nada más para cambiar de materia/programa — solo los parámetros de la línea de comandos. Con `--input-dir` y `--output-dir` puedes además cambiar dónde busca la carpeta del programa y dónde escribe los resultados (por defecto `input/` y `output/`).

Los resultados quedan en `output/`. Sube `cursos_<slug>.xlsx` primero por el admin de `Course`, y luego `programas_asignatura_<slug>.xlsx` + `<slug>_pdfs.zip` por el admin de `CourseProgram` ("Cargar programas de asignatura").

## Nota

`input/` y `output/` están en `.gitignore`: son documentos curriculares internos de la
universidad y no deberían quedar en el historial de git.
