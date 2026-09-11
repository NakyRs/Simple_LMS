from fastapi import UploadFile

from pathlib import Path

CHUNK_SIZE = 1024 * 1024  # 1 MB

async def save_upload_file(
    file: UploadFile,
    destination: Path,
):
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    total_size = 0

    with open(destination, "wb") as buffer:
        while chunk := await file.read(CHUNK_SIZE):
            buffer.write(chunk)
            total_size += len(chunk)

    return total_size
