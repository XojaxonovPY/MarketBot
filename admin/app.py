from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from admin.provider import UsernameAndPasswordProvider
from db import engine
from db.models import User, Product, Category, Order, Channel

app = Starlette()
admin = Admin(
    engine=engine,
    title='P_29Admin',
    base_url='/',
    auth_provider=UsernameAndPasswordProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key="sdgfhjhhsfdghn")]
)
admin.add_view(ModelView(User))
admin.add_view(ModelView(Category))
admin.add_view(ModelView(Product))
admin.add_view(ModelView(Order))
admin.add_view(ModelView(Channel))
admin.mount_to(app)
