from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from motor.core import AgnosticDatabase
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, UnauthenticatedUser
from app.crud.user import get_user

# class UserInfoMiddleware(BaseHTTPMiddleware):

#     def __init__(self, app, db: AgnosticDatabase):
#         super().__init__(app)
#         self.db = db

#     async def dispatch(self, request: Request, call_next):
#         token = request.headers.get('token')
#         user = await get_user(self.db, token)
#         request.app.context['user'] = user
#         response = await call_next(request)
        
#         return response
    

class BasicAuthBackend(AuthenticationBackend):

    def __init__(self, db: AgnosticDatabase):
        super().__init__()
        self.db = db

    async def authenticate(self, conn):

        token = conn.headers.get('Token')
        user = await get_user(self.db, token)
        return AuthCredentials(["authenticated"]), user if user else UnauthenticatedUser()