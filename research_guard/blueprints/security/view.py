from sanic import Blueprint
from sanic_security.authentication import (
    login,
    logout,
    register,
)
from sanic_security.utils import json

security_bp = Blueprint("security")
security_bp.static("/login", "static/security/index.html", name="index")
security_bp.static("/register", "static/security/register.html", name="register")


@security_bp.post("security/register")
async def on_register(request):
    account = await register(request, verified=True)
    response = json("Registration successful!", account.json)
    return response


@security_bp.post("security/login")
async def on_login(request):
    authentication_session = await login(request)
    response = json("Login successful.", authentication_session.json)
    authentication_session.encode(response)
    return response


@security_bp.put("security/logout")
async def on_logout(request):
    authentication_session = await logout(request)
    return json("Logout successful.", authentication_session.bearer.json)
