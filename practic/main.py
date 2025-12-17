from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
import os
from dotenv import load_dotenv
import traceback
from auth.oauth import oauth
from services.external_api import data_service

load_dotenv()

app = FastAPI(title="Student Gradebook System")

config = Config('.env')
VK_CLIENT_ID = config('VK_CLIENT_ID')

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "random_string"),
    session_cookie="grades_session_id",
    same_site="lax",
    https_only=True
)

templates = Jinja2Templates(directory="templates")
VK_REDIRECT_URI = "https://localhost"


@app.get("/login", name="login")
async def login(request: Request):
    """Процесс авторизации VK ID."""
    return await oauth.vk.authorize_redirect(
        request,
        VK_REDIRECT_URI,
        state=os.urandom(16).hex(),
    )


@app.get("/logout", name="logout")
async def logout(request: Request):
    """Выход из системы. Удаляем все флаги сессии."""
    request.session.pop('user_full_name', None)
    request.session.pop('is_admin', None)
    return RedirectResponse(url='/')



@app.get("/", name="home")
async def home(request: Request):
    if 'code' in request.query_params:
        print("DEBUG: Received code from VK. Attempting exchange...")

        extra_params = {}
        if 'device_id' in request.query_params:
            extra_params['device_id'] = request.query_params['device_id']
            print(f"DEBUG: Found and adding device_id: {extra_params['device_id'][:10]}...")

        try:
            token = await oauth.vk.authorize_access_token(request, **extra_params)
            print("DEBUG: Token received successfully!")

            user_info = await oauth.vk.userinfo(
                token=token,
                params={'client_id': VK_CLIENT_ID}
            )
            print(f"DEBUG: User info raw: {user_info}")

            user_data = user_info.get('user', {})
            primary_email = user_data.get('email')

            admin_first_name = user_data.get('first_name', 'Проверенный')
            admin_last_name = user_data.get('last_name', 'Пользователь')
            user_full_name = f"{admin_first_name} {admin_last_name}"

        except Exception as e:
            print("\n!!! VK ID ERROR during Token Exchange or UserInfo !!!")
            print(f"Error: {e}")
            traceback.print_exc()
            return templates.TemplateResponse("login.html", {"request": request, "error": f"Ошибка: {e}"})

        if primary_email:
            request.session['user_full_name'] = user_full_name
            request.session['is_admin'] = True
            print(f"DEBUG: Session set for Admin ({user_full_name}). Redirecting to clean URL.")
            return RedirectResponse(url='/select_user', status_code=302)

    if request.session.get('is_admin'):
        return RedirectResponse(url='/select_user', status_code=302)

    print("DEBUG: Rendering login page (No session)")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/select_user", name="select_user")
async def select_user(request: Request):
    if not request.session.get('is_admin'):
        return RedirectResponse(url='/', status_code=302)

    all_users = data_service.get_all_users()
    admin_name = request.session.get('user_full_name', 'Администратор')

    return templates.TemplateResponse("select_user.html", {
        "request": request,
        "admin_name": admin_name,
        "users": all_users
    })


@app.get("/grades/{user_name}", name="grades_view")
async def grades_view(request: Request, user_name: str):
    if not request.session.get('is_admin'):
        return RedirectResponse(url='/', status_code=302)

    admin_name = request.session.get('user_full_name', 'Администратор')

    student_data = data_service.get_grades_for_user(user_name)

    return templates.TemplateResponse("grades.html", {
        "request": request,
        "admin_name": admin_name,
        "student_name": user_name,
        "data": student_data
    })