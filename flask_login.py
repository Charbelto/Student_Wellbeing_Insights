from functools import wraps
from typing import Callable, Optional
from flask import session, current_app, g, redirect, url_for
from werkzeug.local import LocalProxy


class UserMixin:
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self):
        return str(getattr(self, "id", None))


class AnonymousUser(UserMixin):
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return False

    def get_id(self):
        return None


def _get_login_manager():
    return current_app.extensions.get("login_manager")


def _get_current_user():
    return getattr(g, "_current_user", AnonymousUser())


current_user = LocalProxy(_get_current_user)


class LoginManager:
    def __init__(self):
        self.login_view: Optional[str] = None
        self._user_callback: Optional[Callable[[str], object]] = None

    def init_app(self, app):
        app.extensions["login_manager"] = self

        @app.before_request
        def load_user():
            user = AnonymousUser()
            user_id = session.get("_user_id")
            if user_id is not None and self._user_callback is not None:
                loaded = self._user_callback(user_id)
                if loaded:
                    user = loaded
            g._current_user = user

        @app.context_processor
        def inject_user():
            return {"current_user": current_user}

    def user_loader(self, callback: Callable[[str], object]):
        self._user_callback = callback
        return callback

    def unauthorized(self):
        if self.login_view:
            return redirect(url_for(self.login_view))
        return redirect("/")


def login_user(user):
    session["_user_id"] = user.get_id()
    g._current_user = user


def logout_user():
    session.pop("_user_id", None)
    g._current_user = AnonymousUser()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            manager = _get_login_manager()
            if manager:
                return manager.unauthorized()
            return redirect("/")
        return func(*args, **kwargs)

    return wrapper
