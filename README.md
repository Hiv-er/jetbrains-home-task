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
   
5. **Run tests**:
   ```bash
    pytest -q --alluredir=./allure-results

6. **Open allure report**:
   ```bash
    allure serve .\allure-results  