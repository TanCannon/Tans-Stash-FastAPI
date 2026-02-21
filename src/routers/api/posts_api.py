from fastapi import Depends, APIRouter, HTTPException, Path, Query, Request, UploadFile, File
from src.models.post_model import Post
from src.database import SessionLocal
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated, List
from src.schemas import post_schemas
from datetime import datetime, timezone

from src.admin.auth import require_admin

import os
import logging
from werkzeug.utils import secure_filename  # I can keep using this
from src.services.optimise_images_service import save_responsive_images

from src.core.settings import settings



router = APIRouter(
    prefix="/api",
    tags=["blogs"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]

#paginated route
@router.get("/get-paginated-blogs", response_model=post_schemas.PaginatedPosts, status_code=status.HTTP_200_OK)
async def read_all_posts_paginated(db: db_dependency, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    skip = (page - 1) * size
    total = db.query(Post).count()
    posts = (
        db.query(Post)
        .order_by(Post.date.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No blogs available.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    return {
        "items": posts,
        "total": total,
        "skip": skip,
        "limit": size,
    }

@router.get("/blog/{blog_sno}", response_model=post_schemas.PostResponse, status_code=status.HTTP_200_OK)
async def read_a_post( blog_sno: int = Path(gt=0), db: db_dependency = None):
    post = db.query(Post).filter(Post.sno == blog_sno).first()

    if post is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return post

#create a post
@router.put("/create-blog", response_model=post_schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: post_schemas.PostCreate, db: db_dependency, admin: str = Depends(require_admin)):
    # Check if slug already exists
    existing = db.query(Post).filter(Post.slug == post.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists"
        )

    new_post = Post(**post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

#update a post
@router.put("/update-blog/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(post_id: int, updated_data: post_schemas.PostCreate, db: db_dependency, admin: str = Depends(require_admin)):
    post = db.query(Post).filter(Post.sno == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Prevent slug duplication
    if updated_data.slug != post.slug:
        existing = db.query(Post).filter(Post.slug == updated_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug already exists"
            )

    for key, value in updated_data.model_dump().items():
        setattr(post, key, value)

    post.last_modified = datetime.now(timezone.utc)

    db.commit()
    db.refresh(post)

#delete a post
@router.delete("/delete-blog/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: db_dependency,admin: str = Depends(require_admin)):
    post = db.query(Post).filter(Post.sno == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )

    db.delete(post)
    db.commit()

    return None

#upload post hero banner
@router.post("/upload-blog-banner", status_code=status.HTTP_201_CREATED)
async def upload_image(file1: UploadFile = File(...), _: str = Depends(require_admin)):
    #Validate file presence
    if not file1.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )

    try:
        #Secure filename
        filename = secure_filename(file1.filename)
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )

        # upload_dir = settings.UPLOAD_LOCATION
        # upload_dir = "D:\\Documents\\professional docs\\PROJECTS\\My projects\\posts website\\post-website-FastAPI\\src\\static\\assets\\img"
        upload_dir = settings.BANNER_UPLOAD_PATH
        print(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as buffer:
            content = await file1.read()
            buffer.write(content)

        #Post-processing (your existing function)
        base_name, _ = os.path.splitext(filename)
        save_responsive_images(file_path, upload_dir, base_name)

    except PermissionError:
        logging.exception("Upload directory permission error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload directory not writable"
        )

    except OSError:
        logging.exception("File system error during upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File system error"
        )

    except Exception:
        logging.exception("Unexpected error during image upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed"
        )

    #Success response
    return {
        "success": True,
        "message": "Image uploaded successfully",
        "filename": filename
    }
