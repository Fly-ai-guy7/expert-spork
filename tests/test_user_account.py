"""Tests for user_account module — very thin coverage intentionally.

Coverage gaps:
  - UserAccount.__post_init__: validation error paths not tested
  - set_password / check_password: wrong password case not tested
  - Role management (add_role, remove_role, has_role): not tested at all
  - activate / deactivate: not tested at all
  - find_user: user-not-found (None) path not tested
"""

import pytest
from src.user_account import UserAccount, find_user


class TestUserAccountCreation:
    def test_valid_user_created(self):
        user = UserAccount(username="alice", email="alice@example.com")
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.is_active is True

    # Missing: username too short -> ValueError
    # Missing: username with invalid chars -> ValueError
    # Missing: invalid email format -> ValueError


class TestPassword:
    def test_correct_password_accepted(self):
        user = UserAccount(username="bob", email="bob@example.com")
        user.set_password("securepassword")
        assert user.check_password("securepassword") is True

    # Missing: check_password with wrong password -> False
    # Missing: set_password with too-short password -> ValueError


class TestFindUser:
    def test_finds_existing_user(self):
        users = [UserAccount("alice", "alice@example.com")]
        found = find_user(users, "alice")
        assert found is not None
        assert found.username == "alice"

    # Missing: find_user when username doesn't exist -> None
    # Missing: find_user on empty list -> None


# Completely untested areas:
# - add_role / remove_role / has_role
# - activate / deactivate (and checking is_active state transitions)
# - roles initialized from constructor
