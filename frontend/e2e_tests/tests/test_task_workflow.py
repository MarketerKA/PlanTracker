import pytest
from datetime import datetime, timedelta
import uuid
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.task_page import TaskPage

class TestTaskWorkflow:
    """End-to-end tests for the complete task workflow"""

    @pytest.fixture(scope="function")
    def test_user(self):
        """Create unique test user credentials"""
        return {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123"
        }

    def test_complete_workflow(self, driver, base_url, test_user):
        """Test complete workflow: register -> login -> create task -> use timer"""
        # 1. Register
        register_page = RegisterPage(driver, base_url)
        register_page.open_register_page()
        success = register_page.register(test_user["email"], test_user["password"])
        assert success, "Registration should be successful"

        # 2. Login
        login_page = LoginPage(driver, base_url)
        login_page.open_login_page()
        success = login_page.login(test_user["email"], test_user["password"])
        assert success, "Login should be successful"

        # 3. Create and manage tasks
        task_page = TaskPage(driver, base_url)
        task_page.open_tasks_page()

        # Try creating task with past date (should fail)
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        task_title = f"Test Task {uuid.uuid4().hex[:6]}"
        task_page.create_task(task_title, past_date, ["test", "important"])
        error_msg = task_page.get_error_message()
        assert error_msg is not None, "Should show error for past date"

        # Create task with valid future date
        future_date = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
        task_title = f"Valid Task {uuid.uuid4().hex[:6]}"
        success = task_page.create_task(task_title, future_date, ["test", "important"])
        assert success, "Task creation should be successful"

        # Select task and use timer
        task_page.select_task(task_title)
        
        # Start timer
        assert task_page.start_timer(), "Should start timer"
        
        # Pause timer
        assert task_page.pause_timer(), "Should pause timer"
        
        # Start again and stop
        assert task_page.start_timer(), "Should restart timer"
        assert task_page.stop_timer(), "Should stop timer"