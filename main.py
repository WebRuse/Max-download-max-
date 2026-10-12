from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app.models import User, FriendRequest, Item, InventoryItem
from app.auth import hash_password, verify_password
from app.sessions import (
    create_session,
    get_user_id_from_token,
    delete_session,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="WebRuse")

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


class RegisterRequest(BaseModel):
    birth_date: str
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AvatarRequest(BaseModel):
    avatar: str


ALLOWED_AVATARS = [
    "skin_very_light",
    "skin_light",
    "skin_light_warm",
    "skin_light_tan",
    "skin_tan",
    "skin_medium_light",
    "skin_medium",
    "skin_medium_warm",
    "skin_medium_tan",
    "skin_warm_brown",
    "skin_brown",
    "skin_dark_brown",
    "skin_deep_brown",
    "skin_deep",
    "skin_very_deep",
    "skin_very_deep_warm",
]


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    token = request.cookies.get("webruse_session")

    if token:
        db: Session = SessionLocal()

        try:
            user_id = get_user_id_from_token(db, token)

            if user_id:
                user = (
                    db.query(User)
                    .filter(User.id == user_id)
                    .first()
                )

                if user:
                    return templates.TemplateResponse(
                        request=request,
                        name="index.html",
                        context={
                            "user": user,
                        },
                    )

        finally:
            db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": None,
        },
    )


# ---------------------------------------------------------
# REGISTER PAGE
# ---------------------------------------------------------

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={},
    )


# ---------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={},
    )


# ---------------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------------

@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):

    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="settings.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.get("/settings/password", response_class=HTMLResponse)
def change_password_page(request: Request):

    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="change_password.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.get("/settings/username", response_class=HTMLResponse)
def change_username_page(request: Request):

    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="change_username.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):

    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(db, token)

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "user": user,
                "avatars": ALLOWED_AVATARS,
            },
        )

    finally:
        db.close()


# ---------------------------------------------------------
# PUBLIC PLAYER PROFILE
# ---------------------------------------------------------

@app.get("/profile/{user_id}", response_class=HTMLResponse)
def public_profile_page(
    user_id: int,
    request: Request,
):

    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        viewer_id = get_user_id_from_token(
            db,
            token,
        )

        if not viewer_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        viewer = (
            db.query(User)
            .filter(User.id == viewer_id)
            .first()
        )

        target_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not target_user:
            return templates.TemplateResponse(
                request=request,
                name="404.html",
                context={},
                status_code=404,
            )

        return templates.TemplateResponse(
            request=request,
            name="public_profile.html",
            context={
                "user": target_user,
                "viewer": viewer,
                "is_own_profile": viewer.id == target_user.id,
            },
        )

    finally:
        db.close()

@app.post("/api/inventory/equip/{item_id}")
def toggle_equip(
    item_id: int,
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Необходимо войти в аккаунт",
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Сессия недействительна",
            )

        inventory_item = (
            db.query(InventoryItem)
            .filter(
                InventoryItem.id == item_id,
                InventoryItem.user_id == user_id,
            )
            .first()
        )

        if not inventory_item:
            raise HTTPException(
                status_code=404,
                detail="Предмет не найден в инвентаре",
            )

        inventory_item.equipped = (
            0 if inventory_item.equipped else 1
        )

        db.commit()

        return {
            "success": True,
            "equipped": bool(inventory_item.equipped),
        }

    finally:
        db.close()

@app.post("/api/friends/request/{user_id}")
def send_friend_request(
    user_id: int,
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Необходимо войти в аккаунт",
        )

    db: Session = SessionLocal()

    try:
        sender_id = get_user_id_from_token(
            db,
            token,
        )

        if not sender_id:
            raise HTTPException(
                status_code=401,
                detail="Сессия недействительна",
            )

        if sender_id == user_id:
            raise HTTPException(
                status_code=400,
                detail="Нельзя добавить самого себя",
            )

        target_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not target_user:
            raise HTTPException(
                status_code=404,
                detail="Игрок не найден",
            )

        existing_request = (
            db.query(FriendRequest)
            .filter(
                FriendRequest.sender_id == sender_id,
                FriendRequest.receiver_id == user_id,
                FriendRequest.status == "pending",
            )
            .first()
        )

        if existing_request:
            raise HTTPException(
                status_code=400,
                detail="Заявка уже отправлена",
            )

        reverse_request = (
            db.query(FriendRequest)
            .filter(
                FriendRequest.sender_id == user_id,
                FriendRequest.receiver_id == sender_id,
                FriendRequest.status == "pending",
            )
            .first()
        )

        if reverse_request:
            raise HTTPException(
                status_code=400,
                detail="Этот игрок уже отправил вам заявку",
            )

        friend_request = FriendRequest(
            sender_id=sender_id,
            receiver_id=user_id,
            status="pending",
        )

        db.add(friend_request)
        db.commit()

        return {
            "success": True,
            "message": "Заявка в друзья отправлена",
        }

    finally:
        db.close()

# ---------------------------------------------------------
# INVENTORY PAGE
# ---------------------------------------------------------

@app.get("/create/item/shirt", response_class=HTMLResponse)
def create_shirt_page(
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        return templates.TemplateResponse(
            request=request,
            name="create_shirt.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.get("/create/item/pants", response_class=HTMLResponse)
def create_pants_item_page(
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        return templates.TemplateResponse(
            request=request,
            name="create_pants_item.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.post("/api/create/pants")
async def create_pants(
    request: Request,
    name: str = Form(...),
    price: int = Form(...),
    currency: str = Form(...),
    template: UploadFile = File(...),
):
    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in."
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid session."
            )

        if not name.strip():
            raise HTTPException(
                status_code=400,
                detail="Item name is required."
            )

        if price < 0:
            raise HTTPException(
                status_code=400,
                detail="Price cannot be negative."
            )

        if currency not in ("tix", "webbux"):
            raise HTTPException(
                status_code=400,
                detail="Invalid currency."
            )

        if template.content_type not in (
            "image/png",
            "image/jpeg",
        ):
            raise HTTPException(
                status_code=400,
                detail="Only PNG and JPG images are allowed."
            )

        extension = ".png"

        if template.content_type == "image/jpeg":
            extension = ".jpg"

        import uuid
        import os

        filename = (
            f"pants_{uuid.uuid4().hex}{extension}"
        )

        upload_dir = "static/uploads/clothing"

        os.makedirs(
            upload_dir,
            exist_ok=True,
        )

        file_path = os.path.join(
            upload_dir,
            filename,
        )

        with open(
            file_path,
            "wb",
        ) as file:

            while True:

                chunk = await template.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file.write(chunk)

        item = Item(
            name=name.strip(),
            item_type="pants",
            description="WebRuse pants",
            price=price,
            currency=currency,
            creator_id=user_id,
            template_path=(
                f"/static/uploads/clothing/{filename}"
            ),
        )

        db.add(item)

        db.commit()

        db.refresh(item)

        return {
            "success": True,
            "item_id": item.id,
            "message": "Pants created successfully.",
        }

    finally:
        db.close()

@app.post("/api/create/shirt")
async def create_shirt(
    request: Request,
    name: str = Form(...),
    price: int = Form(...),
    currency: str = Form(...),
    template: UploadFile = File(...),
):
    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in.",
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid session.",
            )

        if not name.strip():
            raise HTTPException(
                status_code=400,
                detail="Item name is required.",
            )

        if price < 0:
            raise HTTPException(
                status_code=400,
                detail="Price cannot be negative.",
            )

        if currency not in ("tix", "webbux"):
            raise HTTPException(
                status_code=400,
                detail="Invalid currency.",
            )

        if template.content_type not in (
            "image/png",
            "image/jpeg",
        ):
            raise HTTPException(
                status_code=400,
                detail="Only PNG and JPG images are allowed.",
            )

        extension = ".png"

        if template.content_type == "image/jpeg":
            extension = ".jpg"

        import uuid
        import os

        filename = (
            f"shirt_{uuid.uuid4().hex}"
            f"{extension}"
        )

        upload_dir = (
            "static/uploads/clothing"
        )

        os.makedirs(
            upload_dir,
            exist_ok=True,
        )

        file_path = os.path.join(
            upload_dir,
            filename,
        )

        with open(file_path, "wb") as file:
            while True:
                chunk = await template.read(1024 * 1024)

                if not chunk:
                    break

                file.write(chunk)

        item = Item(
            name=name.strip(),
            item_type="shirt",
            description="WebRuse shirt",
            price=price,
            currency=currency,
            creator_id=user_id,
            template_path=(
                f"/static/uploads/clothing/{filename}"
            ),
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return {
            "success": True,
            "item_id": item.id,
            "message": "Shirt created successfully.",
        }

    finally:
        db.close()

@app.get("/create/item", response_class=HTMLResponse)
def create_item_page(
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        return templates.TemplateResponse(
            request=request,
            name="create_item.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.get("/create", response_class=HTMLResponse)
def create_page(
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        return templates.TemplateResponse(
            request=request,
            name="create.html",
            context={
                "user": user,
            },
        )

    finally:
        db.close()

@app.get("/create/shirts", response_class=HTMLResponse)
def create_shirts_page(
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        shirts = (
            db.query(Item)
            .filter(
                Item.creator_id == user_id,
                Item.item_type == "shirt",
            )
            .order_by(Item.id.desc())
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="create_shirts.html",
            context={
                "user": user,
                "shirts": shirts,
            },
        )

    finally:
        db.close()

@app.get("/create/pants", response_class=HTMLResponse)
def create_pants_page(
    request: Request,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        pants = (
            db.query(Item)
            .filter(
                Item.creator_id == user_id,
                Item.item_type == "pants",
            )
            .order_by(Item.id.desc())
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="create_pants.html",
            context={
                "user": user,
                "pants": pants,
            },
        )

    finally:
        db.close()

@app.get("/catalog", response_class=HTMLResponse)
def catalog_page(
    request: Request,
    type: str | None = None,
):
    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        query = (
    db.query(Item)
    .filter(
        ~Item.name.in_([
            "Starter Hat",
            "Classic Shirt",
            "Classic Pants",
            "Default Face",
        ])
    )
)

        if type:
            if type == "shirt":
                query = query.filter(
                    Item.item_type.in_(["shirt", "pants"])
                )
            else:
                query = query.filter(
                    Item.item_type == type
                )

        items = query.order_by(Item.id).all()

        owned_item_ids = {
            inventory_item.item_id
            for inventory_item in (
                db.query(InventoryItem)
                .filter(
                    InventoryItem.user_id == user_id
                )
                .all()
            )
        }

        catalog_items = []

        for item in items:
            item.owned = item.id in owned_item_ids
            catalog_items.append(item)

        return templates.TemplateResponse(
            request=request,
            name="catalog.html",
            context={
                "user": user,
                "items": catalog_items,
            },
        )

    finally:
        db.close()

@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request):

    token = request.cookies.get("webruse_session")

    if not token:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(db, token)

        if not user_id:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        inventory = (
            db.query(InventoryItem, Item)
            .join(
                Item,
                InventoryItem.item_id == Item.id
            )
            .filter(
                InventoryItem.user_id == user.id
            )
            .all()
        )

        items = []

        for inventory_item, item in inventory:
            items.append({
                "id": item.id,
                "name": item.name,
                "item_type": item.item_type,
                "description": item.description,
                "price": item.price,
                "icon": item.icon,
                "equipped": inventory_item.equipped,
            })

        return templates.TemplateResponse(
            request=request,
            name="inventory.html",
            context={
                "user": user,
                "items": items,
            },
        )

    finally:
        db.close()


# ---------------------------------------------------------
# GAMES PAGE
# ---------------------------------------------------------

@app.get("/games", response_class=HTMLResponse)
def games_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="games.html",
        context={},
    )


# ---------------------------------------------------------
# REGISTER API
# ---------------------------------------------------------

@app.post("/api/register")
def register(data: RegisterRequest):
    from datetime import datetime, date

    db: Session = SessionLocal()

    try:
        username = data.username.strip()
        email = data.email.strip().lower()

        if not username:
            raise HTTPException(
                status_code=400,
                detail="Username is required."
            )

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email is required."
            )

        if len(data.password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least 6 characters."
            )

        # Validate date of birth
        try:
            birth_date = datetime.strptime(
                data.birth_date,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date of birth."
            )

        today = date.today()

        if birth_date > today:
            raise HTTPException(
                status_code=400,
                detail="Date of birth cannot be in the future."
            )

        # Calculate age
        age = (
            today.year
            - birth_date.year
            - (
                (today.month, today.day)
                < (birth_date.month, birth_date.day)
            )
        )

        if age < 10:
            raise HTTPException(
                status_code=403,
                detail="You must be at least 10 years old to use WebRuse."
            )

        existing_username = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already exists."
            )

        existing_email = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(data.password),
            tix=100,
            webbux=10,
            avatar="default",
            birth_date=birth_date,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        starter_items = (
            db.query(Item)
            .filter(
                Item.name.in_([
                    "Starter Hat",
                    "Classic Shirt",
                    "Classic Pants",
                    "Default Face",
                ])
            )
            .all()
        )

        for item in starter_items:
            inventory_item = InventoryItem(
                user_id=user.id,
                item_id=item.id,
                equipped=0,
            )
            db.add(inventory_item)

        db.commit()

        return {
            "success": True,
            "message": "Account created successfully.",
            "user_id": user.id,
        }

    finally:
        db.close()


# ---------------------------------------------------------
# LOGIN API
# ---------------------------------------------------------

@app.post("/api/login")
def login(data: LoginRequest):

    db: Session = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == data.username)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password.",
            )

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password.",
            )

        token = create_session(
            db,
            user.id,
        )

        result = JSONResponse(
            content={
                "success": True,
                "message": "Login successful!",
            }
        )

        result.set_cookie(
            key="webruse_session",
            value=token,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )

        return result

    finally:
        db.close()


# ---------------------------------------------------------
# CURRENT USER API
# ---------------------------------------------------------

@app.get("/api/me")
def me(request: Request):

    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not logged in.",
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Not logged in.",
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found.",
            )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tix": user.tix,
            "avatar": user.avatar,
        }

    finally:
        db.close()


# ---------------------------------------------------------
# CHANGE AVATAR API
# ---------------------------------------------------------

class UsernameChangeRequest(BaseModel):
    username: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class UsernameChangeRequest(BaseModel):
    username: str


@app.post("/api/username")
def change_username(
    request: Request,
    data: UsernameChangeRequest,
):
    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in.",
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid session.",
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        new_username = data.username.strip()

        if len(new_username) < 3:
            raise HTTPException(
                status_code=400,
                detail="Username must contain at least 3 characters.",
            )

        if len(new_username) > 32:
            raise HTTPException(
                status_code=400,
                detail="Username is too long.",
            )

        if new_username == user.username:
            raise HTTPException(
                status_code=400,
                detail="This is already your username.",
            )

        existing_user = (
            db.query(User)
            .filter(
                User.username == new_username,
                User.id != user.id,
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists.",
            )

        # Account ID 1 changes username for free.
        # Every other account pays 1000 WebBux.
        username_change_price = 1000

        if user.id != 1:

            if user.webbux < username_change_price:
                raise HTTPException(
                    status_code=400,
                    detail="You need 1000 WebBux to change your username.",
                )

            user.webbux -= username_change_price

        user.username = new_username

        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "username": user.username,
            "webbux": user.webbux,
            "message": "Username changed successfully.",
        }

    finally:
        db.close()

@app.post("/api/password")
def change_password(
    request: Request,
    data: PasswordChangeRequest,
):
    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in.",
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid session.",
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        if not verify_password(
            data.current_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect.",
            )

        if len(data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="New password must contain at least 6 characters.",
            )

        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="New passwords do not match.",
            )

        if data.current_password == data.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password must be different from the current password.",
            )

        user.password_hash = hash_password(
            data.new_password
        )

        db.commit()

        return {
            "success": True,
            "message": "Password changed successfully.",
        }

    finally:
        db.close()

@app.post("/api/avatar")
def change_avatar(
    data: AvatarRequest,
    request: Request,
):

    token = request.cookies.get("webruse_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not logged in.",
        )

    if data.avatar not in ALLOWED_AVATARS:
        raise HTTPException(
            status_code=400,
            detail="Invalid avatar.",
        )

    db: Session = SessionLocal()

    try:
        user_id = get_user_id_from_token(
            db,
            token,
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Not logged in.",
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        user.avatar = data.avatar

        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Avatar updated!",
            "avatar": user.avatar,
        }

    finally:
        db.close()


# ---------------------------------------------------------
# LOGOUT API
# ---------------------------------------------------------

@app.post("/api/logout")
def logout(request: Request):

    token = request.cookies.get("webruse_session")

    if token:
        db: Session = SessionLocal()

        try:
            delete_session(
                db,
                token,
            )

        finally:
            db.close()

    response = RedirectResponse(
        url="/",
        status_code=303,
    )

    response.delete_cookie(
        "webruse_session",
    )

    return response


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

@app.get("/api/status")
def status():

    return {
        "online": True,
        "version": "0.6.0",
    }

