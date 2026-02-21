from fastapi import APIRouter, Request, Path, Query, status, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from math import ceil

from src.database import SessionLocal
from src.models.post_model import Post
from src.models.contact_model import Contact
from src.models.user_usage_model import ToolUsage
from src.core.templates import templates
from src.core.params import params
from src.core.flash import flash
from src.core.context import get_global_context

from src.core.settings import settings

from fastapi import Form
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime
import os
import logging
from werkzeug.utils import secure_filename




router = APIRouter(
    prefix="/admin",
    tags=["pages"]
    )

POSTS_PER_PAGE = params["no_of_posts"]


def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception:
        yield None
    finally:
        try:
            db.close()
        except:
            pass

db_dependency = Annotated[Session, Depends(get_db)]


def redirect_to_login(request: Request):
    flash(request, "Please login to continue.", "warning")

    return RedirectResponse(
        url=request.url_for("login_page"),
        status_code=status.HTTP_302_FOUND,
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: db_dependency, page: int = Query(1, ge=1)):
    # Check session
    if request.session.get("admin") != settings.ADMIN_USERNAME:
        return redirect_to_login(request)

    if db is None:
        flash(request, "Database is currently unavailable.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "params": params,
            "posts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "dashboard.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        per_page = POSTS_PER_PAGE
        skip = (page - 1) * per_page

        total = db.query(Post).count()

        posts = (
            db.query(Post)
            .order_by(Post.date.desc())
            .offset(skip)
            .limit(per_page)
            .all()
        )

        total_pages = ceil(total / per_page)

        prev_page = (
            str(request.url_for("dashboard")) + f"?page={page - 1}"
            if page > 1 else "#"
        )

        next_page = (
            str(request.url_for("dashboard")) + f"?page={page + 1}"
            if page < total_pages else "#"
        )

        context = get_global_context(request)
        context.update({
            "request": request,
            "params": params,
            "posts": posts,
            "prev": prev_page,
            "next": next_page,
        })

        return templates.TemplateResponse("dashboard.html", context)

    except Exception:
        flash(request, "Something went wrong. Please visit again later.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "params": params,
            "posts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "dashboard.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.get("/dashboard-edit-blog/{post_id}", response_class=HTMLResponse)
async def dashboard_edit_blog(request: Request, db: db_dependency, post_id: int = Path(ge=1)):
    # Check session for admin
    if request.session.get("admin") != settings.ADMIN_USERNAME:
        return redirect_to_login(request)
    
    post = db.query(Post).filter(Post.sno == post_id).first()

    context = get_global_context(request)

    context.update({
        "request": request,
        "posts":post
    })

    return templates.TemplateResponse("edit.html", context)

@router.get("/dashboard-add-blog", response_class=HTMLResponse)
async def dashboard_add_blog(request: Request):
    # Check session
    if request.session.get("admin") != settings.ADMIN_USERNAME:
        return redirect_to_login(request)

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("add.html", context)

@router.get("/dashboard-inbox", response_class=HTMLResponse)
async def dashboard_inbox(request: Request, db:db_dependency, page: int = Query(1, ge=1)):
    # Check session
    if request.session.get("admin") != settings.ADMIN_USERNAME:
        return redirect_to_login(request)

    if db is None:
        flash(request, "Database is currently unavailable.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "contacts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "inbox/inbox.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        per_page = POSTS_PER_PAGE
        skip = (page - 1) * per_page

        total = db.query(Contact).count()

        contacts = (
            db.query(Contact)
            .order_by(Contact.date.desc())
            .offset(skip)
            .limit(per_page)
            .all()
        )

        total_pages = ceil(total / per_page)

        prev_page = (
            str(request.url_for("dashboard_inbox")) + f"?page={page - 1}"
            if page > 1
            else "#"
        )

        next_page = (
            str(request.url_for("dashboard_inbox")) + f"?page={page + 1}"
            if page < total_pages
            else "#"
        )

        context = get_global_context(request)
        context.update({
                "request": request,
                "contacts": contacts,
                "prev": prev_page,
                "next": next_page,
            })

        return templates.TemplateResponse(
            "inbox/inbox.html",
            context,
        )

    except Exception as e:
        print(str(e))
        flash(request, "Something went wrong. Please visit again later.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "contacts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "inbox/inbox.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.get("/dashboard-inbox/{contact_id}", response_class=HTMLResponse)
async def dashboard_inbox_message(request: Request, db:db_dependency, contact_id: int = Path(ge=1)):
    # Check session
    if request.session.get("admin") != settings.ADMIN_USERNAME:
        return redirect_to_login(request)

    if db is None:
        flash(request, "Database is currently unavailable.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "contacts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "inbox/message.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        contact = db.query(Contact).filter(Contact.sno == contact_id).first()

        context = get_global_context(request)

        context.update({
            "request": request,
            "contact": contact
        })

        return templates.TemplateResponse(
            "inbox/message.html",
            context
        )

    except Exception as e:
        print(str(e))
        flash(request, "Something went wrong. Please visit again later.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "contact": [],
        })

        return templates.TemplateResponse(
            "inbox/message.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.get("/dashboard-analytics", response_class=HTMLResponse)
async def dashboard_analytics(request: Request, db: db_dependency, page: int = Query(1, ge=1)):
    # Check session
    if request.session.get("admin") != settings.ADMIN_USERNAME:
        return redirect_to_login(request)

    if db is None:
        flash(request, "Database is currently unavailable.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "usageData": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "dashboard/analytics.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        per_page = POSTS_PER_PAGE
        skip = (page - 1) * per_page

        total = db.query(ToolUsage).count()

        usageData = (
            db.query(ToolUsage)
            .order_by(ToolUsage.timestamp.desc())
            .offset(skip)
            .limit(per_page)
            .all()
        )

        total_pages = ceil(total / per_page)

        prev_page = (
            str(request.url_for("dashboard_analytics")) + f"?page={page - 1}"
            if page > 1
            else "#"
        )

        next_page = (
            str(request.url_for("dashboard_analytics")) + f"?page={page + 1}"
            if page < total_pages
            else "#"
        )

        context = get_global_context(request)
        context.update({
                "request": request,
                "usageData": usageData,
                "prev": prev_page,
                "next": next_page,
            })

        return templates.TemplateResponse(
            "dashboard/analytics.html",
            context,
        )

    except Exception as e:
        print(str(e))
        flash(request, "Something went wrong. Please visit again later.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "usageData": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "dashboard/analytics.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )