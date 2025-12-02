"""
End-to-end tests for calculation BREAD operations using Playwright.
Tests include positive and negative scenarios for creating, browsing,
reading, editing, and deleting calculations.
"""

import re

import pytest
from playwright.sync_api import Page, expect


def register_and_login(page: Page, user_data):
    """Helper function to register and login a user."""
    page.goto("http://localhost:8000/static/register.html")
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm-password", user_data["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

    page.fill("#username", user_data["username"])
    page.fill("#password", user_data["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:8000/static/dashboard.html", timeout=3000)


@pytest.mark.e2e
class TestCalculationPositive:
    """Positive test cases for calculation BREAD operations."""

    def test_create_calculation_addition(self, page: Page, unique_user_data):
        """Test successful creation of an addition calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")

        preview = page.locator("#calculation-preview")
        expect(preview).to_be_visible()
        expect(preview).to_contain_text("15")

        page.click("#create-calc-btn")

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible(timeout=3000)
        expect(message_container).to_have_class(re.compile(r"success"))
        expect(page.locator("#message-text")).to_contain_text(
            "Calculation created successfully"
        )

        calculations_table = page.locator(".calculations-table")
        expect(calculations_table).to_be_visible(timeout=2000)
        expect(page.locator(".calculation-expression").first).to_contain_text("10 + 5")
        expect(page.locator(".calculation-result").first).to_contain_text("15")

    def test_create_calculation_subtraction(self, page: Page, unique_user_data):
        """Test successful creation of a subtraction calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "20")
        page.select_option("#operation-type", "SUBTRACT")
        page.fill("#operand-b", "8")

        page.click("#create-calc-btn")

        page.wait_for_function(
            "document.querySelector('.calculations-table') !== null",
            timeout=10000
        )

        expect(page.locator(".calculation-expression").first).to_contain_text(
            "20 - 8", timeout=5000
        )
        expect(page.locator(".calculation-result").first).to_contain_text(
            "12", timeout=5000
        )

    def test_create_calculation_multiplication(self, page: Page, unique_user_data):
        """Test successful creation of a multiplication calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "6")
        page.select_option("#operation-type", "MULTIPLY")
        page.fill("#operand-b", "7")

        page.click("#create-calc-btn")

        expect(page.locator("#message-container")).to_be_visible(timeout=3000)
        expect(page.locator(".calculation-expression").first).to_contain_text("6 × 7")
        expect(page.locator(".calculation-result").first).to_contain_text("42")

    def test_create_calculation_division(self, page: Page, unique_user_data):
        """Test successful creation of a division calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "100")
        page.select_option("#operation-type", "DIVIDE")
        page.fill("#operand-b", "4")

        page.click("#create-calc-btn")

        expect(page.locator("#message-container")).to_be_visible(timeout=3000)
        expect(page.locator(".calculation-expression").first).to_contain_text("100 ÷ 4")
        expect(page.locator(".calculation-result").first).to_contain_text("25")

    def test_browse_calculations_empty(self, page: Page, unique_user_data):
        """Test browsing calculations when none exist."""
        register_and_login(page, unique_user_data)

        empty_state = page.locator(".empty-state")
        expect(empty_state).to_be_visible(timeout=2000)
        expect(empty_state).to_contain_text("No calculations yet")

    def test_browse_multiple_calculations(self, page: Page, unique_user_data):
        """Test browsing multiple calculations."""
        register_and_login(page, unique_user_data)

        calculations = [
            ("10", "ADD", "5"),
            ("20", "SUBTRACT", "8"),
            ("6", "MULTIPLY", "7"),
        ]

        for i, (a, op, b) in enumerate(calculations):
            page.fill("#operand-a", a)
            page.select_option("#operation-type", op)
            page.fill("#operand-b", b)
            page.click("#create-calc-btn")

            page.wait_for_function(
                f"document.querySelectorAll('.calculations-table tbody tr')"
                f".length >= {i + 1}",
                timeout=10000
            )

        calculations_rows = page.locator(".calculations-table tbody tr")
        expect(calculations_rows).to_have_count(3, timeout=5000)

    def test_edit_calculation(self, page: Page, unique_user_data):
        """Test editing an existing calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        edit_button = page.locator(".btn-edit").first
        edit_button.click()

        edit_modal = page.locator("#edit-modal")
        expect(edit_modal).to_be_visible()

        expect(page.locator("#edit-operand-a")).to_have_value("10")
        expect(page.locator("#edit-operand-b")).to_have_value("5")

        page.fill("#edit-operand-a", "15")
        page.fill("#edit-operand-b", "10")

        page.locator("#edit-calculation-form button[type='submit']").click()

        expect(page.locator("#message-container")).to_be_visible(timeout=3000)
        expect(page.locator("#message-text")).to_contain_text(
            "Calculation updated successfully"
        )

        expect(page.locator(".calculation-expression").first).to_contain_text("15 + 10")
        expect(page.locator(".calculation-result").first).to_contain_text("25")

    def test_delete_calculation(self, page: Page, unique_user_data):
        """Test deleting a calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        delete_button = page.locator(".btn-danger").first
        delete_button.click()

        delete_modal = page.locator("#delete-modal")
        expect(delete_modal).to_be_visible()

        delete_info = page.locator("#delete-calc-info")
        expect(delete_info).to_contain_text("10 + 5")

        page.locator("#confirm-delete-btn").click()

        expect(page.locator("#message-container")).to_be_visible(timeout=3000)
        expect(page.locator("#message-text")).to_contain_text(
            "Calculation deleted successfully"
        )

        empty_state = page.locator(".empty-state")
        expect(empty_state).to_be_visible(timeout=2000)

    def test_edit_modal_cancel(self, page: Page, unique_user_data):
        """Test canceling edit modal does not modify calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        edit_button = page.locator(".btn-edit").first
        edit_button.click()

        edit_modal = page.locator("#edit-modal")
        expect(edit_modal).to_be_visible()

        page.fill("#edit-operand-a", "99")

        page.locator(".modal-cancel").first.click()

        expect(edit_modal).not_to_be_visible()
        expect(page.locator(".calculation-expression").first).to_contain_text("10 + 5")

    def test_delete_modal_cancel(self, page: Page, unique_user_data):
        """Test canceling delete modal does not delete calculation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        delete_button = page.locator(".btn-danger").first
        delete_button.click()

        delete_modal = page.locator("#delete-modal")
        expect(delete_modal).to_be_visible()

        page.locator(".modal-cancel").nth(1).click()

        expect(delete_modal).not_to_be_visible()
        expect(page.locator(".calculations-table")).to_be_visible()


@pytest.mark.e2e
class TestCalculationNegative:
    """Negative test cases for calculation operations."""

    def test_division_by_zero_preview(self, page: Page, unique_user_data):
        """Test that division by zero shows error in preview."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "DIVIDE")
        page.fill("#operand-b", "0")

        preview = page.locator("#calculation-preview")
        expect(preview).to_be_visible()
        expect(preview).to_contain_text("Cannot divide by zero")
        expect(preview.locator(".preview-error")).to_be_visible()

    def test_division_by_zero_submission(self, page: Page, unique_user_data):
        """Test that division by zero is prevented on submission."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "DIVIDE")
        page.fill("#operand-b", "0")

        page.click("#create-calc-btn")

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible(timeout=2000)
        expect(message_container).to_have_class(re.compile(r"error"))
        expect(page.locator("#message-text")).to_contain_text("Cannot divide by zero")

        expect(page.locator(".empty-state")).to_be_visible()

    def test_edit_division_by_zero(self, page: Page, unique_user_data):
        """Test that editing to division by zero shows error."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        edit_button = page.locator(".btn-edit").first
        edit_button.click()

        page.select_option("#edit-operation-type", "DIVIDE")
        page.fill("#edit-operand-b", "0")

        preview = page.locator("#edit-calculation-preview")
        expect(preview).to_be_visible()
        expect(preview).to_contain_text("Cannot divide by zero")

        page.locator("#edit-calculation-form button[type='submit']").click()

        message_container = page.locator("#message-container")
        expect(message_container).to_be_visible(timeout=2000)
        expect(message_container).to_have_class(re.compile(r"error"))

    def test_calculation_requires_authentication(self, page: Page):
        """Test that calculation endpoints require authentication."""
        page.goto("http://localhost:8000/static/dashboard.html")

        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

    def test_user_isolation(self, page: Page, unique_user_data, context):
        """Test that users can only see their own calculations."""
        import random
        import string

        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        page.locator("#logout-btn").click()
        page.wait_for_url("http://localhost:8000/static/login.html", timeout=3000)

        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        user2_data = {
            "username": f"testuser_{suffix}",
            "email": f"test_{suffix}@example.com",
            "password": "SecurePass123",
        }

        register_and_login(page, user2_data)

        empty_state = page.locator(".empty-state")
        expect(empty_state).to_be_visible(timeout=2000)
        expect(empty_state).to_contain_text("No calculations yet")

    def test_invalid_calculation_operation(self, page: Page, unique_user_data):
        """Test that calculation form requires operation selection."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.fill("#operand-b", "5")

        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        expect(page.locator(".empty-state")).to_be_visible()

    def test_form_reset_after_creation(self, page: Page, unique_user_data):
        """Test that form is reset after successful calculation creation."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        expect(page.locator("#operand-a")).to_have_value("")
        expect(page.locator("#operand-b")).to_have_value("")
        expect(page.locator("#operation-type")).to_have_value("")


@pytest.mark.e2e
class TestCalculationWorkflow:
    """End-to-end workflow tests for calculations."""

    def test_complete_calculation_workflow(self, page: Page, unique_user_data):
        """Test complete workflow: create, browse, edit, and delete calculations."""
        register_and_login(page, unique_user_data)

        expect(page.locator(".empty-state")).to_be_visible(timeout=2000)

        page.fill("#operand-a", "10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        expect(page.locator(".calculations-table")).to_be_visible()
        expect(page.locator(".calculation-expression").first).to_contain_text("10 + 5")

        page.fill("#operand-a", "20")
        page.select_option("#operation-type", "MULTIPLY")
        page.fill("#operand-b", "3")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        calculations_rows = page.locator(".calculations-table tbody tr")
        expect(calculations_rows).to_have_count(2)

        edit_button = page.locator(".btn-edit").first
        edit_button.click()

        page.fill("#edit-operand-a", "30")
        page.locator("#edit-calculation-form button[type='submit']").click()

        page.wait_for_timeout(500)

        expect(page.locator(".calculation-expression").first).to_contain_text("30 × 3")

        delete_button = page.locator(".btn-danger").first
        delete_button.click()

        page.locator("#confirm-delete-btn").click()

        page.wait_for_timeout(500)

        calculations_rows = page.locator(".calculations-table tbody tr")
        expect(calculations_rows).to_have_count(1)

        expect(page.locator(".calculation-expression").first).to_contain_text("10 + 5")

    def test_decimal_calculations(self, page: Page, unique_user_data):
        """Test calculations with decimal numbers."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "10.5")
        page.select_option("#operation-type", "MULTIPLY")
        page.fill("#operand-b", "2.5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        expect(page.locator(".calculation-result").first).to_contain_text("26.25")

    def test_negative_numbers(self, page: Page, unique_user_data):
        """Test calculations with negative numbers."""
        register_and_login(page, unique_user_data)

        page.fill("#operand-a", "-10")
        page.select_option("#operation-type", "ADD")
        page.fill("#operand-b", "5")
        page.click("#create-calc-btn")

        page.wait_for_timeout(500)

        expect(page.locator(".calculation-result").first).to_contain_text("-5")
