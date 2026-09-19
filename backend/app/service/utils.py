from fastapi import UploadFile
from pathlib import Path

from app.models import Forum,ForumResponse

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

def forum_to_response(forum: Forum) -> ForumResponse:
    return ForumResponse(
        id=forum.id,
        user_id=forum.user_id,
        title=forum.title,
        content=forum.content,
        reply_level=forum.reply_level,
        post_type=forum.post_type,
        created_at=forum.created_at,
        replies=[
            forum_to_response(reply)
            for reply in forum.replies
        ]
    )