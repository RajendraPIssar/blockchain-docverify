# DocVerify Chain — Mac Deployment Guide
# Group Project — Masters in Computer Science

This guide takes you from zero to a fully running project on your Mac.
Total setup time: approximately 30–45 minutes.

══════════════════════════════════════════════════
 WHAT YOU NEED TO HAVE INSTALLED
══════════════════════════════════════════════════

1. VS Code        — already have it ✓
2. Docker Desktop — already have it ✓
3. Node.js 20+    — go to nodejs.org, click LTS, install the .pkg
4. Python 3.11+   — go to python.org/downloads, install

Verify in VS Code terminal (Ctrl+`):
  node --version       # must show v20.x.x
  python3 --version    # must show 3.11.x or 3.12.x

══════════════════════════════════════════════════
 STEP 1 — Start the PostgreSQL database (Docker)
══════════════════════════════════════════════════

Make sure Docker Desktop is open and running (whale icon in menu bar).

In VS Code terminal run:

  docker run --name docverify-db \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=docverify \
    -p 5432:5432 \
    -d postgres:15-alpine

This creates and starts a PostgreSQL container.
The database "docverify" is created automatically.

To check it is running:
  docker ps
  # You should see: docverify-db ... Up ... 0.0.0.0:5432->5432/tcp

To stop and restart later:
  docker stop docverify-db
  docker start docverify-db

NOTE: SQLite is used by the Flask backend — no PostgreSQL config needed
      in the backend. The docverify.db file is created automatically
      in the backend folder when you first run the app.

      The Docker PostgreSQL above is optional — included only if you want
      to use SQLTools to browse the database visually in VS Code.

══════════════════════════════════════════════════
 STEP 2 — Set up the blockchain
══════════════════════════════════════════════════

Open a NEW terminal in VS Code (click + in terminal panel).
Label it "BLOCKCHAIN".

  cd blockchain
  npm install
  # Installs Hardhat, Ethers.js — takes 1-2 minutes

Start the local Hardhat blockchain node:
  npx hardhat node

You will see 20 test wallets printed. LEAVE THIS RUNNING.
Copy the private key next to "Account #0". It looks like:
  0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

══════════════════════════════════════════════════
 STEP 3 — Deploy the smart contract
══════════════════════════════════════════════════

Open ANOTHER new terminal (4th terminal). Label it "DEPLOY".

  cd blockchain
  npx hardhat compile
  npx hardhat run scripts/deploy.js --network localhost

The output prints:
  ✅  Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3

Copy that address. You need it in Step 4.

Run the tests to prove the contract is working:
  npx hardhat test
  # Should show: 6 passing ✓

══════════════════════════════════════════════════
 STEP 4 — Configure the backend .env file
══════════════════════════════════════════════════

In VS Code, open backend/.env.example
Copy it and rename to backend/.env
Fill in the two blank lines:

  WEB3_URL=http://127.0.0.1:8545
  CONTRACT_ADDRESS=<paste address from Step 3>
  PRIVATE_KEY=<paste Account #0 private key from Step 2>
  SECRET_KEY=docverify2024groupproject

Save the file.

══════════════════════════════════════════════════
 STEP 5 — Start the backend
══════════════════════════════════════════════════

Open ANOTHER new terminal. Label it "BACKEND".

  cd backend
  python3 -m venv venv
  source venv/bin/activate
  # You will see (venv) at the start of the prompt

  pip3 install -r requirements.txt
  # Installs Flask, Web3.py, PyMuPDF etc — takes 3-5 minutes

  python3 -m flask --app main run --debug --port 5000

You should see:
   * Running on http://127.0.0.1:5000

The SQLite database file (docverify.db) is created automatically.
You can view it in VS Code with the SQLite Viewer extension.

══════════════════════════════════════════════════
 STEP 6 — Open the frontend
══════════════════════════════════════════════════

The frontend is a single HTML file — no React, no npm needed.

Simply open frontend/index.html in your browser:

  open frontend/index.html

Or in VS Code:
  Right-click on frontend/index.html → Open with Live Server
  (Install Live Server extension first: ritwickdey.LiveServer)

The app loads at http://127.0.0.1:5500/frontend/index.html

══════════════════════════════════════════════════
 STEP 7 — Create your admin account
══════════════════════════════════════════════════

1. Register a new account through the web app.
2. Then in any terminal run:

  cd backend
  python3 -c "
  import sqlite3
  conn = sqlite3.connect('docverify.db')
  conn.execute(\"UPDATE users SET role='admin' WHERE email='your@email.com'\")
  conn.commit()
  conn.close()
  print('Done')
  "

Replace your@email.com with the email you registered.
Log out and log back in — the Admin tab will appear.

══════════════════════════════════════════════════
 ALL SERVICES CHECKLIST
══════════════════════════════════════════════════

Before calling your professor:

  ✓ BLOCKCHAIN terminal — shows "eth_chainId" logs
  ✓ BACKEND terminal   — shows "Running on http://127.0.0.1:5000"
  ✓ Browser             — frontend/index.html is open and login page shows
  ✓ docker ps           — docverify-db shows as Up (if using SQLTools)

══════════════════════════════════════════════════
 TROUBLESHOOTING
══════════════════════════════════════════════════

Backend says "Contract not initialized":
  → Hardhat node crashed. Restart: npx hardhat node
  → Redeploy: npx hardhat run scripts/deploy.js --network localhost
  → Update CONTRACT_ADDRESS in backend/.env
  → Restart the backend

Port 5000 already in use:
  lsof -ti:5000 | xargs kill -9

ModuleNotFoundError:
  source venv/bin/activate
  pip3 install -r requirements.txt

PyMuPDF install error:
  pip3 install PyMuPDF==1.24.1

Frontend shows "Failed to fetch":
  → Backend is not running. Check BACKEND terminal for errors.
  → Make sure backend is running on port 5000.

══════════════════════════════════════════════════
 TEAM MEMBER RESPONSIBILITIES
══════════════════════════════════════════════════

Member 1 — Authentication & Database
  Files: backend/routes/auth_routes.py
         backend/models/database.py

Member 2 — Document Upload & Hashing
  Files: backend/routes/document_routes.py
         backend/services/hash_service.py

Member 3 — Blockchain Integration
  Files: backend/services/blockchain_service.py
         blockchain/contracts/DocumentRegistry.sol
         blockchain/scripts/deploy.js

Member 4 — AI Fraud Detection & Frontend
  Files: backend/services/fraud_service.py
         frontend/index.html
