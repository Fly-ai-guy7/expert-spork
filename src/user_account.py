"""User account management."""

import hashlib
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserAccount:
    username: str
    email: str
    _password_hash: str = field(default="", repr=False)
    is_active: bool = True
    roles: list[str] = field(default_factory=list)

    def __post_init__(self):
        self._validate_username(self.username)
        self._validate_email(self.email)

    @staticmethod
    def _validate_username(username: str) -> None:
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValueError("Username may only contain letters, digits, and underscores")

    @staticmethod
    def _validate_email(email: str) -> None:
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email address: {email}")

    def set_password(self, password: str) -> None:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self._password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self._password_hash == hashlib.sha256(password.encode()).hexdigest()

    def add_role(self, role: str) -> None:
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: str) -> None:
        if role in self.roles:
            self.roles.remove(role)

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True


def find_user(users: list[UserAccount], username: str) -> Optional[UserAccount]:
    for user in users:
        if user.username == username:
            return user
    return None
