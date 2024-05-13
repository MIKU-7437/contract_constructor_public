import mammoth
from pypandoc import convert_text
from starlette.datastructures import UploadFile
from io import BytesIO
from pathlib import Path

from shared.file_transporter import create_path


class Converter:
    def docx_to_html(self, input_file: UploadFile) -> str:
        file = BytesIO(input_file.file.read())
        result = mammoth.convert_to_html(file)
        return result.value

    def html_to_docx(self, html: str, docx_path: Path) -> None:
        create_path(docx_path)
        convert_text(html, format='html', to='docx', outputfile=docx_path, extra_args=["+RTS", "-K64m", "-RTS"])
