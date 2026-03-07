import pdfplumber
from vector_store import insert_document


# ==========================================================
# CHUNK SETTINGS
# ==========================================================

CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 100   # overlap between chunks


# ==========================================================
# TEXT CHUNKING FUNCTION
# ==========================================================

def chunk_text(text: str):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]

        chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ==========================================================
# PDF → CHUNKS → VECTOR DB
# ==========================================================

def insert_pdf(file_path: str, domain: str):

    with pdfplumber.open(file_path) as pdf:

        full_text = ""

        for page in pdf.pages:
            text = page.extract_text()

            if text:
                full_text += text + "\n"

    # Split into chunks
    chunks = chunk_text(full_text)

    print(f"📄 Extracted {len(chunks)} chunks from {file_path}")

    for chunk in chunks:

        insert_document(
            text=chunk,
            metadata={
                "domain": domain,
                "source_file": file_path
            },
            domain=domain,
        )

    print(f"✅ Inserted {len(chunks)} chunks from '{file_path}' into '{domain}' collection")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    files_to_insert = [
        ("car_booking", "Car details.pdf"),
        # ("car_booking", "car_booking_policy_mahindra.pdf"),
        # ("ecommerce", "returns_policy.pdf"),
    ]

    for domain, path in files_to_insert:
        insert_pdf(path, domain)import pdfplumber
from vector_store import insert_document


# ==========================================================
# CHUNK SETTINGS
# ==========================================================

CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 100   # overlap between chunks


# ==========================================================
# TEXT CHUNKING FUNCTION
# ==========================================================

def chunk_text(text: str):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]

        chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ==========================================================
# PDF → CHUNKS → VECTOR DB
# ==========================================================

def insert_pdf(file_path: str, domain: str):

    with pdfplumber.open(file_path) as pdf:

        full_text = ""

        for page in pdf.pages:
            text = page.extract_text()

            if text:
                full_text += text + "\n"

    # Split into chunks
    chunks = chunk_text(full_text)

    print(f"📄 Extracted {len(chunks)} chunks from {file_path}")

    for chunk in chunks:

        insert_document(
            text=chunk,
            metadata={
                "domain": domain,
                "source_file": file_path
            },
            domain=domain,
        )

    print(f"✅ Inserted {len(chunks)} chunks from '{file_path}' into '{domain}' collection")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    files_to_insert = [
        ("car_booking", "Car details.pdf"),
        # ("car_booking", "car_booking_policy_mahindra.pdf"),
        # ("ecommerce", "returns_policy.pdf"),
    ]

    for domain, path in files_to_insert:
        insert_pdf(path, domain)