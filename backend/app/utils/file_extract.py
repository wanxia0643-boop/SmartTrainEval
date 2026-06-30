"""Best-effort text extraction for uploaded training evidence files."""
from pathlib import Path
from zipfile import ZipFile

TEXT_EXTENSIONS = {
    ".txt", ".md", ".markdown", ".json", ".xml", ".yaml", ".yml", ".csv",
    ".py", ".java", ".js", ".ts", ".vue", ".jsx", ".tsx", ".html", ".css",
    ".sql", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".php",
}

MAX_EXTRACT_CHARS = 80_000


def _trim(text: str) -> str:
    return text[:MAX_EXTRACT_CHARS]


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return _trim(path.read_text(encoding=encoding, errors="ignore"))
        except UnicodeDecodeError:
            continue
    return ""


def _extract_docx(path: Path) -> str:
    try:
        from docx import Document  # type: ignore
    except Exception:
        return ""
    doc = Document(str(path))
    return _trim("\n".join(p.text for p in doc.paragraphs if p.text.strip()))


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""
    reader = PdfReader(str(path))
    chunks = []
    for page in reader.pages[:20]:
        chunks.append(page.extract_text() or "")
    return _trim("\n".join(chunks))


def _extract_zip(path: Path) -> str:
    chunks: list[str] = []
    with ZipFile(path) as zf:
        for info in zf.infolist():
            if info.is_dir() or Path(info.filename).suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if info.file_size > 512_000:
                continue
            try:
                raw = zf.read(info)
            except Exception:
                continue
            text = raw.decode("utf-8", errors="ignore")
            chunks.append(f"\n--- {info.filename} ---\n{text}")
            if sum(len(c) for c in chunks) >= MAX_EXTRACT_CHARS:
                break
    return _trim("\n".join(chunks))


def extract_text(path: str | Path) -> str:
    """Return extracted text when possible; return an empty string for binary files."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return _read_text(file_path)
    if suffix == ".docx":
        return _extract_docx(file_path)
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix == ".zip":
        return _extract_zip(file_path)
    return ""
