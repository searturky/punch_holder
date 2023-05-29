from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, UnauthenticatedUser

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
    