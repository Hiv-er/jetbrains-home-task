# How to run tests

1. **Install Python**

2. **Install Allure**

3. **Activate virtual environment**  
   - **Windows (PowerShell):**
     ```powershell
     .venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source .venv/bin/activate
     ```

4. **Clone the repo and install dependencies:**
   ```bash
   pip install -r requirements.txt
   
5. **Make sure that the following enviroment variables exist in the system**:
   - ADMIN_CUSTOMER_CODE
   - TEAM_ADMIN_CUSTOMER_CODE
   - TEAM_VIEWER_CUSTOMER_CODE
   - ADMIN_API_KEY
   - TEAM_ADMIN_API_KEY
   - TEAM_VIEWER_API_KEY

They can also be added in the ".env" file in the root directory of the project.
   
6. **Run tests**:
   ```bash
    pytest -q --alluredir=./allure-results

7. **Open allure report**:
   ```bash
    allure serve .\allure-results  