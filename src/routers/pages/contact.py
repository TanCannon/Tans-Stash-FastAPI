from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import RedirectResponse

from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from src.models.contact_model import Contact
from datetime import datetime

from src.core.templates import templates

from src.core.flash import flash
from src.core.context import get_global_context

router = APIRouter(prefix="/contact", tags=["pages"])

def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception:
        # Yield None if DB fails
        yield None
    finally:
        try:
            db.close()
        except:
            pass


'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("", name="contact.contact")
async def contact(db: db_dependency, request: Request):
    if db is None:
        flash(request, "Database is currently unavailable.", "danger")

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("contact.html", context)

@router.post("/create-contact", name="contact.create-contact")
async def create_contact(
    request: Request,
    db: db_dependency,
    name: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...),
    email: str = Form(...)
):
    if db is None:
        flash(request, "Database is currently unavailable.", "danger")
        return RedirectResponse(url="/contact", status_code=303)

    try:
        entry = Contact(
            name=name,
            phone_no=phone,
            msg=message,
            email=email,
            date=datetime.now()
        )

        db.add(entry)
        db.commit()

        flash(request, "Your message has been sent successfully!", "success")

    except Exception as e:
        print(f'Error in contact submit: {str(e)}')
        flash(request, "Something went wrong. Please visit again later.", "danger")

    return RedirectResponse(url="/contact", status_code=303)
