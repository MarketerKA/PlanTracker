from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conftest import BASE_URL

class TasksPage:
    # URL - Tasks is the main page at root URL
    URL = f"{BASE_URL}/"
    
    # Header Locators
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "button._button_xmbw2_1._secondary_xmbw2_24")
    USER_EMAIL = (By.CSS_SELECTOR, ".userEmail")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button._button_xmbw2_1._primary_xmbw2_19._submitButton_ou5mw_22")
    
    # Tasks Tab Locators
    TASKS_TAB = (By.XPATH, "//button[contains(text(), 'Tasks')]")
    STATISTICS_TAB = (By.XPATH, "//button[contains(text(), 'Statistics')]")
    
    # Task Form Locators
    TASK_TITLE_INPUT = (By.CSS_SELECTOR, "input[placeholder='Add new task...']._input_dg8be_23")
    # Fallback selectors in case the class name changes
    TASK_TITLE_INPUT_ALT1 = (By.CSS_SELECTOR, "input[placeholder='Add new task...']")
    TASK_TITLE_INPUT_ALT2 = (By.XPATH, "//input[@placeholder='Add new task...']")
    
    # Due date input with fallbacks
    DUE_DATE_INPUT = (By.CSS_SELECTOR, "input[type='datetime-local']")
    DUE_DATE_INPUT_ALT = (By.XPATH, "//label[contains(text(), 'Due Date')]//input")
    
    # Tag inputs with fallbacks
    TAG_INPUT = (By.CSS_SELECTOR, "#tag-input")
    TAG_INPUT_ALT = (By.XPATH, "//input[@placeholder='Add tag...']")
    ADD_TAG_BUTTON = (By.CSS_SELECTOR, "button.addTagButton")
    ADD_TAG_BUTTON_ALT = (By.XPATH, "//div[contains(@class, 'tagInput')]//button[text()='+']")
    
    # Submit button with fallbacks
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button.submitButton")
    SUBMIT_BUTTON_ALT1 = (By.XPATH, "//button[text()='Add Task']")
    SUBMIT_BUTTON_ALT2 = (By.CSS_SELECTOR, "button[type='submit']")
    
    TAGS_CONTAINER = (By.CSS_SELECTOR, ".tagsContainer")
    TAG = (By.CSS_SELECTOR, ".tag")
    
    # Task List Locators
    TASK_ITEMS = (By.CSS_SELECTOR, "div[role='button']")
    TASK_TITLE = (By.CSS_SELECTOR, ".title")
    TASK_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    DELETE_BUTTON = (By.CSS_SELECTOR, ".deleteBtn")
    TASK_TAGS = (By.CSS_SELECTOR, ".tags .tag")
    
    # Page identification elements
    MAIN_TITLE = (By.CSS_SELECTOR, "h1.title")
    
    # Timer Locators
    TIMER_DISPLAY = (By.CSS_SELECTOR, ".display")
    TIMER_START_BUTTON = (By.XPATH, "//div[contains(@class, 'timer')]//button[contains(text(), 'Start')]")
    TIMER_PAUSE_BUTTON = (By.XPATH, "//div[contains(@class, 'timer')]//button[contains(text(), 'Pause')]")
    TIMER_FINISH_BUTTON = (By.XPATH, "//div[contains(@class, 'timer')]//button[contains(text(), 'Finish')]")
    
    # Dialog Locators
    CONFIRM_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
    CONFIRM_BUTTON = (By.CSS_SELECTOR, "div[role='dialog'] button[class*='primary']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "div[role='dialog'] button[class*='secondary']")
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        
    def navigate(self):
        """Navigate to the tasks page (main page)"""
        self.driver.get(self.URL)
        return self
    
    def is_at_tasks_page(self):
        """Check if we're on the tasks page using multiple indicators"""
        print("Checking if we're on the Tasks page...")
        print(f"Current URL: {self.driver.current_url}")
        
        # Take a screenshot for debugging
        self.driver.save_screenshot("tasks_page_check.png")
        
        # Method 1: Check URL
        if "tasks" in self.driver.current_url or self.driver.current_url.endswith('/'):
            print("URL suggests we're on the Tasks page")
            return True
            
        # Method 2: Look for the main title
        try:
            title_element = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.MAIN_TITLE)
            )
            if "My Tasks" in title_element.text:
                print(f"Found title element with text: {title_element.text}")
                return True
        except Exception as e:
            print(f"Title check failed: {str(e)}")
        
        # Method 3: Look for task input field
        try:
            task_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Add new task...']")
            if task_input.is_displayed():
                print("Found task input field")
                return True
        except Exception as e:
            print(f"Task input check failed: {str(e)}")
            
        # If none of the methods above worked, print page source for debugging
        print("Page source (first 500 chars):")
        print(self.driver.page_source[:500])
        
        print("Failed to verify we're on the Tasks page")
        return False
    
    def navigate_to_home(self):
        """Navigate to the home page where header is also present"""
        self.driver.get(BASE_URL)
        return self
        
    # Header related methods
    def click_logout(self):
        """Click the logout button in the header"""
        try:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.LOGOUT_BUTTON)
            )
            logout_button.click()
            time.sleep(1)  # Allow time for logout action to complete
        except:
            print("Logout button not found or not clickable")
        return self
    
    def is_logged_in(self):
        """Check if the user is logged in by looking for the user email display"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.USER_EMAIL)
            )
            return True
        except:
            return False
    
    def wait_for_logout_completed(self, timeout=10):
        """Wait for the logout process to complete (login button appears)"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.USER_EMAIL)
            )
            # Verify login button appears
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.LOGIN_BUTTON)
            )
            return True
        except:
            return False
    
    def get_user_email(self):
        """Get the displayed user email if logged in"""
        try:
            return self.driver.find_element(*self.USER_EMAIL).text
        except:
            return None
            
    # Tasks Tab methods
    def switch_to_tasks_tab(self):
        """Switch to the Tasks tab"""
        try:
            self.driver.find_element(*self.TASKS_TAB).click()
            time.sleep(0.5)  # Wait for tab switch
        except:
            print("Tasks tab not found or not clickable")
        return self
        
    def switch_to_statistics_tab(self):
        """Switch to the Statistics tab"""
        try:
            self.driver.find_element(*self.STATISTICS_TAB).click()
            time.sleep(0.5)  # Wait for tab switch
        except:
            print("Statistics tab not found or not clickable")
        return self
    
    # Task Form methods
    def set_task_title(self, title):
        """Set the task title in the task form"""
        print(f"Attempting to set task title: {title}")
        
        # Try multiple selectors to find the input field
        input_field = None
        try:
            print("Trying primary selector...")
            input_field = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.TASK_TITLE_INPUT)
            )
        except Exception as e:
            print(f"Primary selector failed: {str(e)}")
            try:
                print("Trying alternative selector 1...")
                input_field = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.TASK_TITLE_INPUT_ALT1)
                )
            except Exception as e:
                print(f"Alternative selector 1 failed: {str(e)}")
                try:
                    print("Trying alternative selector 2...")
                    input_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(self.TASK_TITLE_INPUT_ALT2)
                    )
                except Exception as e:
                    print(f"Alternative selector 2 failed: {str(e)}")
                    print("Taking a screenshot for debugging...")
                    self.driver.save_screenshot("debug_input_field.png")
                    print(f"Current URL: {self.driver.current_url}")
                    print("Page source:")
                    print(self.driver.page_source[:1000])  # Print first 1000 chars of page source
                    raise Exception("Could not find task input field with any selector")
        
        print(f"Found input field: {input_field}")
        
        # Now focus and click the input field
        self.driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
        time.sleep(0.5)
        
        try:
            print("Clicking input field...")
            input_field.click()
            print("Click successful")
        except Exception as e:
            print(f"Click failed: {str(e)}")
            try:
                print("Trying JavaScript click...")
                self.driver.execute_script("arguments[0].click();", input_field)
                print("JavaScript click successful")
            except Exception as e:
                print(f"JavaScript click failed: {str(e)}")
                raise
        
        time.sleep(1)  # Wait for form to expand
        
        # Clear and set text
        try:
            print("Clearing field...")
            input_field.clear()
            print("Field cleared")
            
            if title:
                print(f"Entering text: {title}")
                input_field.send_keys(title)
                print("Text entered")
        except Exception as e:
            print(f"Text entry failed: {str(e)}")
            raise
        
        return self
        
    def ensure_form_expanded(self):
        """Make sure the form is expanded before interacting with it"""
        print("Ensuring form is expanded...")
        if not self.is_form_expanded():
            print("Form not expanded, attempting to click input field...")
            
            # Try different methods to click the input field
            try:
                # Try the original selector
                input_field = self.driver.find_element(*self.TASK_TITLE_INPUT_ALT1)
                print("Found input field with alt selector 1")
            except:
                try:
                    # Try the XPath selector
                    input_field = self.driver.find_element(*self.TASK_TITLE_INPUT_ALT2)
                    print("Found input field with alt selector 2")
                except Exception as e:
                    print(f"Failed to find input field: {str(e)}")
                    self.driver.save_screenshot("debug_form_expansion.png")
                    raise
            
            # Try regular click
            try:
                print("Attempting to click...")
                input_field.click()
                print("Click successful")
            except:
                # Try JavaScript click
                try:
                    print("Using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", input_field)
                    print("JavaScript click successful")
                except Exception as e:
                    print(f"JavaScript click failed: {str(e)}")
                    raise
            
            time.sleep(1)  # Wait for form to expand
        else:
            print("Form already expanded")
        
        return self
    
    def set_due_date(self, days_from_now=1, hours=0):
        """Set the due date in the task form"""
        # Ensure the form is expanded
        self.ensure_form_expanded()
        
        print(f"Setting due date to {days_from_now} days from now...")
        
        # Calculate a future date (default: 1 day from now)
        future_date = datetime.now() + timedelta(days=days_from_now, hours=hours)
        date_string = future_date.strftime("%d-%m-%Y %H:%M")
        
        # Try to find the date input with multiple selectors
        input_field = None
        try:
            print("Trying primary date selector...")
            input_field = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.DUE_DATE_INPUT)
            )
        except Exception as e:
            print(f"Primary date selector failed: {str(e)}")
            try:
                print("Trying alternative date selector...")
                input_field = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.DUE_DATE_INPUT_ALT)
                )
            except Exception as e:
                print(f"Alternative date selector failed: {str(e)}")
                self.driver.save_screenshot("debug_date_field.png")
                raise Exception("Could not find date input field with any selector")
        
        print(f"Found date input field: {input_field}")
        
        try:
            print("Clearing date field...")
            input_field.clear()
            print("Date field cleared")
            
            print(f"Entering date: {date_string}")
            input_field.send_keys(date_string)
            print("Date entered")
            
            # Press Enter to close the calendar
            print("Pressing Enter to close calendar")
            input_field.send_keys(Keys.ENTER)
            print("Enter key pressed")
            time.sleep(1)  # Wait for calendar to close
        except Exception as e:
            print(f"Setting date failed: {str(e)}")
            raise
        
        return self
    
    
    def add_tag(self, tag_name):
        """Add a tag to the task"""
        # Ensure the form is expanded
        self.ensure_form_expanded()
        
        print(f"Adding tag: {tag_name}")
        
        # Try to find the tag input with multiple selectors
        tag_input = None
        try:
            print("Trying primary tag input selector...")
            tag_input = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.TAG_INPUT)
            )
        except Exception as e:
            print(f"Primary tag input selector failed: {str(e)}")
            try:
                print("Trying alternative tag input selector...")
                tag_input = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.TAG_INPUT_ALT)
                )
            except Exception as e:
                print(f"Alternative tag input selector failed: {str(e)}")
                self.driver.save_screenshot("debug_tag_input.png")
                raise Exception("Could not find tag input field with any selector")
        
        print(f"Found tag input field: {tag_input}")
        
        try:
            print("Clearing tag field...")
            tag_input.clear()
            print("Tag field cleared")
            
            print(f"Entering tag: {tag_name}")
            tag_input.send_keys(tag_name)
            print("Tag entered")
            
            # Try pressing Enter to add the tag
            print("Pressing Enter to add tag")
            tag_input.send_keys(Keys.ENTER)
            print("Enter key pressed")
            time.sleep(0.5)  # Wait for tag to be added
            
            # If Enter key doesn't work, try clicking the add button
            if self.get_tag_count() == 0:
                print("Enter key didn't work, trying to click add button...")
                
                # Try to find and click the add tag button
                try:
                    print("Looking for add tag button...")
                    try:
                        print("Trying primary add tag button selector...")
                        add_button = self.driver.find_element(*self.ADD_TAG_BUTTON)
                    except:
                        print("Trying alternative add tag button selector...")
                        add_button = self.driver.find_element(*self.ADD_TAG_BUTTON_ALT)
                        
                    print(f"Found add tag button: {add_button}")
                    
                    try:
                        print("Clicking add tag button...")
                        add_button.click()
                        print("Add tag button click successful")
                    except:
                        print("Using JavaScript to click add tag button...")
                        self.driver.execute_script("arguments[0].click();", add_button)
                        print("JavaScript click successful")
                except Exception as e:
                    print(f"Add tag button interaction failed: {str(e)}")
                    self.driver.save_screenshot("debug_add_tag_button.png")
                    raise
        except Exception as e:
            print(f"Setting tag failed: {str(e)}")
            raise
                
        time.sleep(0.5)  # Wait for tag to be added
        return self
    
    def is_form_expanded(self):
        """Check if the form is expanded"""
        try:
            return self.driver.find_element(*self.DUE_DATE_INPUT).is_displayed()
        except:
            return False
    
    def click_add_task(self):
        """Click the Add Task button to submit the form"""
        try:
            # Make sure form is expanded first
            self.ensure_form_expanded()
            
            print("Attempting to click Add Task button...")
            
            # Take screenshot before clicking
            self.driver.save_screenshot("debug_add_tag_button.png")
            
            # Try multiple approaches to find and click the button
            
            # Approach 1: Try the primary selector
            try:
                print("Approach 1: Trying primary submit button selector...")
                submit_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.SUBMIT_BUTTON)
                )
                print(f"Found submit button: {submit_button}")
                
                # Try regular click first
                try:
                    print("Clicking submit button...")
                    submit_button.click()
                    print("Submit button click successful")
                    time.sleep(1)  # Wait for form submission
                    return True
                except Exception as e:
                    print(f"Submit button click failed: {str(e)}")
            except Exception as e:
                print(f"Primary submit button selector failed: {str(e)}")
            
            # Approach 2: Try alternative selectors
            try:
                print("Approach 2: Trying alternative submit button selector...")
                submit_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.SUBMIT_BUTTON_ALT1)
                )
                print(f"Found submit button with alt selector 1: {submit_button}")
                
                # Try regular click first
                try:
                    print("Clicking submit button...")
                    submit_button.click()
                    print("Submit button click successful")
                    time.sleep(1)  # Wait for form submission
                    return True
                except Exception as e:
                    print(f"Submit button click failed: {str(e)}")
            except Exception as e:
                print(f"Alternative submit button selector 1 failed: {str(e)}")
            
            # Approach 3: Try JavaScript click on any button that looks like a submit button
            try:
                print("Approach 3: Trying to find any button with 'Add Task' text...")
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        button_text = button.text.strip()
                        print(f"Found button with text: '{button_text}'")
                        if "add task" in button_text.lower():
                            print(f"Found button with 'Add Task' text: {button}")
                            try:
                                print("Clicking button with JavaScript...")
                                self.driver.execute_script("arguments[0].click();", button)
                                print("JavaScript click successful")
                                time.sleep(1)  # Wait for form submission
                                return True
                            except Exception as e:
                                print(f"JavaScript click failed: {str(e)}")
                    except:
                        print("Could not get button text")
            except Exception as e:
                print(f"Button search failed: {str(e)}")
            
            # Approach 4: Try to submit the form directly
            try:
                print("Approach 4: Trying to submit the form directly...")
                forms = self.driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    form = forms[0]
                    print(f"Found form: {form}")
                    try:
                        print("Submitting form with JavaScript...")
                        self.driver.execute_script("arguments[0].submit();", form)
                        print("Form submission successful")
                        time.sleep(1)  # Wait for form submission
                        return True
                    except Exception as e:
                        print(f"Form submission failed: {str(e)}")
            except Exception as e:
                print(f"Form search failed: {str(e)}")
            
            # Approach 5: Try to press Enter in the last input field
            try:
                print("Approach 5: Trying to press Enter in the last input field...")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if inputs:
                    last_input = inputs[-1]
                    print(f"Found last input: {last_input}")
                    try:
                        print("Sending Enter key...")
                        last_input.send_keys(Keys.ENTER)
                        print("Enter key sent")
                        time.sleep(1)  # Wait for form submission
                        return True
                    except Exception as e:
                        print(f"Enter key failed: {str(e)}")
            except Exception as e:
                print(f"Input search failed: {str(e)}")
            
            # If all approaches fail, take a screenshot and return False
            self.driver.save_screenshot("submit_button_failure.png")
            print("All approaches to submit the form failed")
            return False
            
        except Exception as e:
            print(f"Submit button not found or not clickable: {str(e)}")
            self.driver.save_screenshot("submit_button_failure.png")
            return False
    
    def get_tag_count(self):
        """Get the number of tags added to the task form"""
        try:
            # First check if the tags container exists
            containers = self.driver.find_elements(*self.TAGS_CONTAINER)
            if not containers:
                return 0
            
            tags = containers[0].find_elements(*self.TAG)
            return len(tags)
        except:
            return 0
    
    # Task List methods
    def get_tasks(self):
        """Get all tasks in the task list"""
        print("Getting all tasks...")
        
        # First try the original selector
        tasks = self.driver.find_elements(*self.TASK_ITEMS)
        
        if not tasks:
            print("No tasks found with primary selector, trying alternative approaches")
            
            # Try a more generic selector for task items
            try:
                print("Trying generic task selector...")
                tasks = self.driver.find_elements(By.CSS_SELECTOR, ".task")
                if tasks:
                    print(f"Found {len(tasks)} tasks with generic selector")
                    return tasks
            except Exception as e:
                print(f"Generic task selector failed: {str(e)}")
            
            # Try to find any elements that might be tasks
            try:
                print("Looking for any possible task elements...")
                # Look for elements with role=button that might be tasks
                tasks = self.driver.find_elements(By.CSS_SELECTOR, "[role='button']")
                if tasks:
                    print(f"Found {len(tasks)} potential task elements with [role='button']")
                    return tasks
            except Exception as e:
                print(f"Role-based selector failed: {str(e)}")
            
            # If still no tasks, take a screenshot and save page source
            print("Could not find any task elements, taking screenshot for debugging")
            self.driver.save_screenshot("no_tasks_found.png")
            
            # Save a snippet of the page source
            with open("task_list_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source[:10000])  # Save first 10000 chars
            print("Saved page source snippet to task_list_source.html")
            
            # Return empty list if no tasks found
            return []
        
        print(f"Found {len(tasks)} tasks with primary selector")
        return tasks
    
    def get_task_count(self):
        """Get the number of tasks in the task list"""
        return len(self.get_tasks())
    
    def get_task_by_title(self, title):
        """Get a task by its title"""
        tasks = self.get_tasks()
        for task in tasks:
            task_title = task.find_element(*self.TASK_TITLE).text
            if title in task_title:  # Use 'in' to match partial titles
                return task
        return None
    
    def select_task(self, title):
        """Select a task by its title"""
        task = self.get_task_by_title(title)
        if task:
            task.click()
            time.sleep(0.5)  # Wait for selection to take effect
            return True
        return False
    
    def is_task_selected(self, title):
        """Check if a task is selected"""
        task = self.get_task_by_title(title)
        if task:
            return "selected" in task.get_attribute("class")
        return False
    
    # Timer methods
    def get_timer_display(self):
        """Get the current timer display value"""
        try:
            return self.driver.find_element(*self.TIMER_DISPLAY).text
        except:
            return None
    
    def start_timer(self):
        """Click the start timer button"""
        try:
            self.driver.find_element(*self.TIMER_START_BUTTON).click()
            time.sleep(0.5)  # Wait for timer to start
            return True
        except:
            print("Start button not found or not clickable")
            return False
    
    def pause_timer(self):
        """Click the pause timer button"""
        try:
            self.driver.find_element(*self.TIMER_PAUSE_BUTTON).click()
            time.sleep(0.5)  # Wait for timer to pause
            return True
        except:
            print("Pause button not found or not clickable")
            return False
    
    def finish_timer(self):
        """Click the finish timer button"""
        try:
            self.driver.find_element(*self.TIMER_FINISH_BUTTON).click()
            time.sleep(0.5)  # Wait for confirmation dialog
            return True
        except:
            print("Finish button not found or not clickable")
            return False
    
    def confirm_finish(self):
        """Confirm finishing the timer"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.CONFIRM_BUTTON)
            ).click()
            time.sleep(1)  # Wait for confirmation to process
            return True
        except:
            print("Confirm button not found or not clickable")
            return False
    
    def cancel_finish(self):
        """Cancel finishing the timer"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.CANCEL_BUTTON)
            ).click()
            time.sleep(0.5)  # Wait for dialog to close
            return True
        except:
            print("Cancel button not found or not clickable")
            return False
    
    def wait_for_timer_change(self, initial_value, timeout=5):
        """Wait for the timer display to change from the initial value"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_value = self.get_timer_display()
            if current_value != initial_value:
                return True
            time.sleep(0.5)
        return False
    
    def is_timer_running(self):
        """Check if the timer is currently running by looking at the start button state"""
        try:
            start_button = self.driver.find_element(*self.TIMER_START_BUTTON)
            return start_button.get_attribute("disabled") == "true"
        except:
            return False 