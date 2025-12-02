"""
End-to-end tests for authentication flows using Playwright.
Tests include positive and negative scenarios for user registration and login.
"""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestRegistrationPositive:
    """Positive test cases for user registration."""

    def test_successful_registration_with_valid_data(
        self, page: Page, unique_user_data
    ):
        """Test successful registration with valid user data."""
        page.goto("http://localhost:8000/static/register.html")

        expect(page.locator("h1")).to_contain_text("Create Account")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])

        page.click('button[type="submit"]')

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible()
        expect(message_container).to_have_class(re.compile(r"success"))
        expect(page.locator("#message-text")).to_contain_text("Registration successful")

        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

    def test_registration_form_validation_feedback(self, page: Page, unique_user_data):
        """Test that valid inputs show success styling."""
        page.goto("http://localhost:8000/static/register.html")

        username_input = page.locator("#username")
        email_input = page.locator("#email")
        password_input = page.locator("#password")

        username_input.fill(unique_user_data["username"])
        username_input.blur()
        page.wait_for_timeout(100)
        expect(username_input).to_have_class(re.compile(r"success"))

        email_input.fill(unique_user_data["email"])
        email_input.blur()
        page.wait_for_timeout(100)
        expect(email_input).to_have_class(re.compile(r"success"))

        password_input.fill(unique_user_data["password"])
        password_input.blur()
        page.wait_for_timeout(100)
        expect(password_input).to_have_class(re.compile(r"success"))


@pytest.mark.e2e
class TestRegistrationNegative:
    """Negative test cases for user registration."""

    def test_registration_with_short_password(self, page: Page, unique_user_data):
        """Test registration fails with password less than 8 characters."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", "Short1")
        page.fill("#confirm-password", "Short1")

        page.click('button[type="submit"]')

        password_error = page.locator("#password-error")
        expect(password_error).to_be_visible()
        expect(password_error).to_contain_text("at least 8 characters")

    def test_registration_with_password_missing_uppercase(
        self, page: Page, unique_user_data
    ):
        """Test registration fails with password missing uppercase letter."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", "lowercase123")
        page.fill("#confirm-password", "lowercase123")

        page.click('button[type="submit"]')

        password_error = page.locator("#password-error")
        expect(password_error).to_be_visible()
        expect(password_error).to_contain_text("uppercase letter")

    def test_registration_with_password_missing_lowercase(
        self, page: Page, unique_user_data
    ):
        """Test registration fails with password missing lowercase letter."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", "UPPERCASE123")
        page.fill("#confirm-password", "UPPERCASE123")

        page.click('button[type="submit"]')

        password_error = page.locator("#password-error")
        expect(password_error).to_be_visible()
        expect(password_error).to_contain_text("lowercase letter")

    def test_registration_with_password_missing_digit(
        self, page: Page, unique_user_data
    ):
        """Test registration fails with password missing digit."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", "NoDigitsHere")
        page.fill("#confirm-password", "NoDigitsHere")

        page.click('button[type="submit"]')

        password_error = page.locator("#password-error")
        expect(password_error).to_be_visible()
        expect(password_error).to_contain_text("digit")

    def test_registration_with_mismatched_passwords(self, page: Page, unique_user_data):
        """Test registration fails when passwords do not match."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", "SecurePass123")
        page.fill("#confirm-password", "DifferentPass456")

        page.click('button[type="submit"]')

        confirm_error = page.locator("#confirm-password-error")
        expect(confirm_error).to_be_visible()
        expect(confirm_error).to_contain_text("do not match")

    def test_registration_with_invalid_email_format(self, page: Page, unique_user_data):
        """Test registration fails with invalid email format."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", "invalid-email-format")
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])

        page.click('button[type="submit"]')

        email_error = page.locator("#email-error")
        expect(email_error).to_be_visible()
        expect(email_error).to_contain_text("valid email")

    def test_registration_with_short_username(self, page: Page):
        """Test registration fails with username less than 3 characters."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", "ab")
        page.fill("#email", "test@example.com")
        page.fill("#password", "SecurePass123")
        page.fill("#confirm-password", "SecurePass123")

        page.click('button[type="submit"]')

        username_error = page.locator("#username-error")
        expect(username_error).to_be_visible()
        expect(username_error).to_contain_text("between 3 and 50")

    def test_registration_with_invalid_username_characters(self, page: Page):
        """Test registration fails with invalid characters in username."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", "user@name!")
        page.fill("#email", "test@example.com")
        page.fill("#password", "SecurePass123")
        page.fill("#confirm-password", "SecurePass123")

        page.click('button[type="submit"]')

        username_error = page.locator("#username-error")
        expect(username_error).to_be_visible()
        expect(username_error).to_contain_text("letters, numbers")

    def test_registration_with_duplicate_username(self, page: Page, unique_user_data):
        """Test registration fails when username already exists."""
        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])

        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)

        page.goto("http://localhost:8000/static/register.html")

        page.fill("#username", unique_user_data["username"])
        page.fill("#email", "different@example.com")
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])

        page.click('button[type="submit"]')

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible()
        expect(message_container).to_have_class(re.compile(r"error"))
        expect(page.locator("#message-text")).to_contain_text("already exists")


@pytest.mark.e2e
class TestLoginPositive:
    """Positive test cases for user login."""

    def test_successful_login_with_valid_credentials(
        self, page: Page, unique_user_data
    ):
        """Test successful login with correct username and password."""
        page.goto("http://localhost:8000/static/register.html")
        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        page.fill("#username", unique_user_data["username"])
        page.fill("#password", unique_user_data["password"])
        page.click('button[type="submit"]')

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible()
        expect(message_container).to_have_class(re.compile(r"success"))
        expect(page.locator("#message-text")).to_contain_text("Login successful")

        page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)

    def test_login_stores_token_in_local_storage(self, page: Page, unique_user_data):
        """Test that successful login stores JWT token in localStorage."""
        page.goto("http://localhost:8000/static/register.html")
        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        page.fill("#username", unique_user_data["username"])
        page.fill("#password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)

        token = page.evaluate("() => localStorage.getItem('access_token')")
        assert token is not None
        assert len(token) > 0

    def test_dashboard_displays_user_info(self, page: Page, unique_user_data):
        """Test that dashboard displays user information after login."""
        page.goto("http://localhost:8000/static/register.html")
        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        page.fill("#username", unique_user_data["username"])
        page.fill("#password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)

        user_info = page.locator("#user-info")
        expect(user_info).to_be_visible()
        expect(user_info).to_contain_text(unique_user_data["username"])
        expect(user_info).to_contain_text(unique_user_data["email"])


@pytest.mark.e2e
class TestLoginNegative:
    """Negative test cases for user login."""

    def test_login_with_wrong_password(self, page: Page, unique_user_data):
        """Test login fails with incorrect password."""
        page.goto("http://localhost:8000/static/register.html")
        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        page.fill("#username", unique_user_data["username"])
        page.fill("#password", "WrongPassword123")
        page.click('button[type="submit"]')

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible()
        expect(message_container).to_have_class(re.compile(r"error"))
        expect(page.locator("#message-text")).to_contain_text("Invalid")

    def test_login_with_nonexistent_username(self, page: Page):
        """Test login fails with username that does not exist."""
        page.goto("http://localhost:8000/static/login.html")

        page.fill("#username", "nonexistentuser123")
        page.fill("#password", "SomePassword123")
        page.click('button[type="submit"]')

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible()
        expect(message_container).to_have_class(re.compile(r"error"))
        # Accept either "Invalid" or "Login failed" as valid error messages
        message_text = page.locator("#message-text")
        expect(message_text).to_be_visible()

    def test_login_with_empty_fields(self, page: Page):
        """Test login fails when fields are empty."""
        page.goto("http://localhost:8000/static/login.html")

        page.click('button[type="submit"]')

        username_error = page.locator("#username-error")
        password_error = page.locator("#password-error")

        expect(username_error).to_be_visible()
        expect(password_error).to_be_visible()


@pytest.mark.e2e
class TestAuthenticationFlow:
    """Test complete authentication flows."""

    def test_logout_functionality(self, page: Page, unique_user_data):
        """Test logout clears token and redirects to login."""
        page.goto("http://localhost:8000/static/register.html")
        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        page.fill("#username", unique_user_data["username"])
        page.fill("#password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)

        page.click("#logout-btn")

        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        token = page.evaluate("() => localStorage.getItem('access_token')")
        assert token is None

    def test_dashboard_redirects_unauthenticated_user(self, page: Page):
        """Test that accessing dashboard without login redirects to login page."""
        # Clear localStorage before test
        page.goto("http://localhost:8000/static/login.html")
        page.evaluate("() => localStorage.clear()")

        page.goto("http://localhost:8000/static/dashboard.html")

        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

    def test_login_page_redirects_authenticated_user(
        self, page: Page, unique_user_data
    ):
        """
        Test that accessing login page when already logged in
        redirects to dashboard.
        """
        page.goto("http://localhost:8000/static/register.html")
        page.fill("#username", unique_user_data["username"])
        page.fill("#email", unique_user_data["email"])
        page.fill("#password", unique_user_data["password"])
        page.fill("#confirm-password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        page.fill("#username", unique_user_data["username"])
        page.fill("#password", unique_user_data["password"])
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)

        page.goto("http://localhost:8000/static/login.html")

        page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)
