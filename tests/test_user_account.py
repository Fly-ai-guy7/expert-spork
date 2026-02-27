"""Tests for user_account module."""

import pytest
from src.user_account import UserAccount, find_user


class TestUserAccountCreation:
    def test_valid_user_created(self):
        user = UserAccount(username="alice", email="alice@example.com")
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.is_active is True
        assert user.roles == []

    def test_username_too_short_raises(self):
        with pytest.raises(ValueError, match="at least 3 characters"):
            UserAccount(username="ab", email="ab@example.com")

    def test_empty_username_raises(self):
        with pytest.raises(ValueError):
            UserAccount(username="", email="x@example.com")

    @pytest.mark.parametrize("bad_name", ["user name", "user@name", "user-name", "user.name"])
    def test_username_invalid_chars_raises(self, bad_name):
        with pytest.raises(ValueError, match="letters, digits, and underscores"):
            UserAccount(username=bad_name, email="x@example.com")

    @pytest.mark.parametrize("bad_email", [
        "notanemail",
        "missing@tld",
        "@nodomain.com",
        "no-at-sign",
        "",
    ])
    def test_invalid_email_raises(self, bad_email):
        with pytest.raises(ValueError, match="Invalid email"):
            UserAccount(username="alice", email=bad_email)

    def test_roles_can_be_set_at_construction(self):
        user = UserAccount(username="admin", email="admin@example.com", roles=["admin"])
        assert user.roles == ["admin"]


class TestPassword:
    def test_correct_password_accepted(self):
        user = UserAccount(username="bob", email="bob@example.com")
        user.set_password("securepassword")
        assert user.check_password("securepassword") is True

    def test_wrong_password_rejected(self):
        user = UserAccount(username="bob", email="bob@example.com")
        user.set_password("securepassword")
        assert user.check_password("wrongpassword") is False

    def test_short_password_raises(self):
        user = UserAccount(username="bob", email="bob@example.com")
        with pytest.raises(ValueError, match="at least 8 characters"):
            user.set_password("short")

    def test_password_not_stored_in_plaintext(self):
        user = UserAccount(username="bob", email="bob@example.com")
        user.set_password("securepassword")
        assert "securepassword" not in str(user)

    def test_no_password_set_rejects_any_input(self):
        user = UserAccount(username="bob", email="bob@example.com")
        assert user.check_password("anything") is False


class TestRoleManagement:
    def setup_method(self):
        self.user = UserAccount(username="charlie", email="charlie@example.com")

    def test_add_role(self):
        self.user.add_role("editor")
        assert self.user.has_role("editor") is True

    def test_has_role_false_when_not_assigned(self):
        assert self.user.has_role("admin") is False

    def test_add_duplicate_role_is_noop(self):
        self.user.add_role("editor")
        self.user.add_role("editor")
        assert self.user.roles.count("editor") == 1

    def test_remove_role(self):
        self.user.add_role("editor")
        self.user.remove_role("editor")
        assert self.user.has_role("editor") is False

    def test_remove_nonexistent_role_is_noop(self):
        self.user.remove_role("admin")  # should not raise
        assert self.user.roles == []

    def test_multiple_roles(self):
        self.user.add_role("viewer")
        self.user.add_role("editor")
        assert self.user.has_role("viewer") is True
        assert self.user.has_role("editor") is True
        assert self.user.has_role("admin") is False


class TestAccountActivation:
    def test_new_account_is_active(self):
        user = UserAccount(username="dave", email="dave@example.com")
        assert user.is_active is True

    def test_deactivate(self):
        user = UserAccount(username="dave", email="dave@example.com")
        user.deactivate()
        assert user.is_active is False

    def test_activate_after_deactivate(self):
        user = UserAccount(username="dave", email="dave@example.com")
        user.deactivate()
        user.activate()
        assert user.is_active is True

    def test_activate_already_active_is_noop(self):
        user = UserAccount(username="dave", email="dave@example.com")
        user.activate()
        assert user.is_active is True


class TestFindUser:
    def test_finds_existing_user(self):
        users = [UserAccount("alice", "alice@example.com")]
        found = find_user(users, "alice")
        assert found is not None
        assert found.username == "alice"

    def test_returns_none_when_not_found(self):
        users = [UserAccount("alice", "alice@example.com")]
        assert find_user(users, "bob") is None

    def test_returns_none_on_empty_list(self):
        assert find_user([], "alice") is None

    def test_returns_first_match(self):
        users = [
            UserAccount("alice", "alice@example.com"),
            UserAccount("bob", "bob@example.com"),
        ]
        found = find_user(users, "bob")
        assert found.email == "bob@example.com"
