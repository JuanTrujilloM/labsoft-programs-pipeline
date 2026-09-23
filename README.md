# labsoft-programs-pipeline

Genera, a partir de los `.doc`/`.docx` de programas de asignatura de `programs.zip`,
los archivos listos para importar en el admin de `labsoft-courseprogram`:

- `cursos_<slug>.xlsx` (hoja "Cursos": código | nombre | programas)
- `programas_asignatura_<slug>.xlsx` (hoja "Programas de asignatura": código | versión | fecha | responsable | semestre)
- `<slug>_pdfs.zip` con un PDF por materia (`{código}_{semestre}.pdf`), para subir junto al segundo xlsx

Los PDFs no quedan sueltos en el proyecto: se generan en una carpeta temporal, se
empacan en el zip y esa carpeta temporal se borra sola al terminar.

## Requisitos

- [LibreOffice](https://www.libreoffice.org) instalado (`brew install --cask libreoffice` en macOS) — se usa en modo headless (`soffice --headless --convert-to pdf`) para convertir `.doc`/`.docx` a PDF, sin abrir ninguna ventana.
- Python 3.

## Uso

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. Descomprime `programs.zip` dentro de `input/` (con toda la estructura que trae, no hace falta acomodar nada — `main.py` busca la carpeta del programa en cualquier nivel dentro de `input/`).
2. Completa un CSV con columnas `archivo,codigo,nombre`: una fila por materia disciplinar, con la ruta del archivo relativa a la carpeta del programa (ej. `4_Disciplinar/3_MecánicaExperimental.doc`), su código oficial y su nombre. La columna `codigo` empieza vacía a propósito — esos códigos no están en los documentos, hay que tomarlos del catálogo oficial de la escuela.
3. Corre, pasando el nombre exacto del programa (igual al de su carpeta y al del `Program` en la base de datos) y el CSV que llenaste:

```bash
python3 main.py --program "Ingeniería mecánica (014-20241)" --codes codesIngMecanica.csv
```

El nombre del programa también nombra los archivos de salida (`cursos_<slug>.xlsx`, etc.), así que para cambiar de materia/programa solo se tocan los parámetros de la línea de comandos, nada del código. `--input-dir` y `--output-dir` son opcionales (por defecto `input/` y `output/`) por si algún día cambia esa estructura de carpetas.

### Materias incompletas

Si a un documento le falta "Fecha elaboración", "Versión número" o "Responsable", o la fecha no tiene formato `DD/MM/AAAA`, esa materia se salta (no se genera su PDF ni sus filas en los Excel) y queda listada al final con el motivo exacto. El resto de materias sí se procesan normalmente — no hay que arreglar el CSV para poder correr el resto.

Los resultados quedan en `output/`. Sube `cursos_<slug>.xlsx` primero por el admin de `Course`, y luego `programas_asignatura_<slug>.xlsx` + `<slug>_pdfs.zip` por el admin de `CourseProgram` ("Cargar programas de asignatura").

## Nota

`input/` y `output/` están en `.gitignore`: son documentos curriculares internos de la
universidad y no deberían quedar en el historial de git.
