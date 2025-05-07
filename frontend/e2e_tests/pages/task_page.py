from selenium.webdriver.common.by import By
from .base_page import BasePage

class TaskPage(BasePage):
    """Page Object for tasks page and operations"""
    
    # Locators
    TASK_TITLE_INPUT = (By.CSS_SELECTOR, "input[placeholder='Add new task...']")
    DUE_DATE_INPUT = (By.CSS_SELECTOR, "input[type='datetime-local']")
    TAG_INPUT = (By.ID, "tag-input")
    ADD_TAG_BUTTON = (By.CSS_SELECTOR, ".addTagButton")
    ADD_TASK_BUTTON = (By.CSS_SELECTOR, ".submitButton")
    TIMER_START_BUTTON = (By.XPATH, "//button[text()='Start']")
    TIMER_PAUSE_BUTTON = (By.XPATH, "//button[text()='Pause']")
    TIMER_STOP_BUTTON = (By.XPATH, "//button[text()='Stop']")
    CONFIRM_DIALOG_CONFIRM = (By.CSS_SELECTOR, ".confirmButton")
    TASK_ITEMS = (By.CSS_SELECTOR, ".task")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".errorMessage")
    
    def open_tasks_page(self):
        """Open tasks page"""
        self.open("tasks")
        return self.wait_for_url_to_contain("/tasks")
    
    def create_task(self, title: str, due_date: str, tags: list[str] = None) -> bool:
        """Create a new task with given parameters"""
        # Enter title
        self.type_text(self.TASK_TITLE_INPUT, title)
        
        # Set due date
        self.type_text(self.DUE_DATE_INPUT, due_date)
        
        # Add tags if provided
        if tags:
            for tag in tags:
                self.type_text(self.TAG_INPUT, tag)
                self.click(self.ADD_TAG_BUTTON)
        
        # Submit form
        self.click(self.ADD_TASK_BUTTON)
        
        # Check if task appears in list
        return len(self.find_elements(self.TASK_ITEMS)) > 0
    
    def select_task(self, task_title: str):
        """Select a task by its title"""
        task_locator = (By.XPATH, f"//div[contains(@class, 'task')]//div[contains(text(), '{task_title}')]")
        self.click(task_locator)
    
    def start_timer(self) -> bool:
        """Start timer for selected task"""
        self.click(self.TIMER_START_BUTTON)
        return True
    
    def pause_timer(self) -> bool:
        """Pause timer for running task"""
        self.click(self.TIMER_PAUSE_BUTTON)
        return True
    
    def stop_timer(self) -> bool:
        """Stop timer and confirm"""
        self.click(self.TIMER_STOP_BUTTON)
        self.click(self.CONFIRM_DIALOG_CONFIRM)
        return True
    
    def get_error_message(self) -> str:
        """Get error message if present"""
        if self.is_element_present(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return None