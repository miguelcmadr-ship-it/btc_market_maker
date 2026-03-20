BTC Market Maker
Windows setup & run guide

Setup
1. Download and extract the project folder
2. Open Command Prompt — press Win, type cmd, press Enter
3. Navigate to the project folder:
   cd "C:\Users\<your-path>\btc_market_maker"
4. Install dependencies:
   py -m pip install -r requirements.txt
5. Run
   py main.py

--- Running tests ---
1. Open Command Prompt and navigate to the project folder (steps 2–3 above)
2. Install pytest:
py -m pip install pytest
3. Run the test suite:
py -m pytest
