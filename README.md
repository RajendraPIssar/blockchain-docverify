# DocVerify Chain

> **Blockchain-backed document verification system** — SHA-256 document hashing, Ethereum smart contracts, Flask REST API, and a zero-dependency HTML frontend.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [1. Start the Database (optional)](#1-start-the-database-optional)
  - [2. Start the Local Blockchain](#2-start-the-local-blockchain)
  - [3. Deploy the Smart Contract](#3-deploy-the-smart-contract)
  - [4. Configure the Backend](#4-configure-the-backend)
  - [5. Start the Backend](#5-start-the-backend)
  - [6. Open the Frontend](#6-open-the-frontend)
  - [7. Promote Yourself to Admin](#7-promote-yourself-to-admin)
- [Environment Variables](#environment-variables)
- [Smart Contract](#smart-contract)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Known Issues & Recommended Improvements](#known-issues--recommended-improvements)
- [Team](#team)
- [License](#license)

---

## Overview

DocVerify Chain is a decentralized document verification platform built for a Masters in Computer Science group project. It allows institutions to upload documents whose integrity is anchored on the Ethereum blockchain, and lets verifiers check authenticity without a central authority.

**Core flow:**

```
Upload document → SHA-256 hash → Store hash on Ethereum (smart contract)
Verify document → Recompute hash → Compare against on-chain record → ✅ / ❌
```

**Key capabilities:**

- Role-based access control (admin, issuer, verifier)
- SHA-256 document hashing via Python (`hashlib`)
- Ethereum smart contract (`DocumentRegistry.sol`) on a local Hardhat node
- AI-assisted fraud detection (`fraud_service.py`)
- Lightweight HTML/JS frontend — no build step required
- SQLite persistence for user accounts and document metadata

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│              frontend/index.html                    │
│         (Vanilla HTML + JS, fetch API)              │
└────────────────────┬────────────────────────────────┘
                     │ HTTP REST
┌────────────────────▼────────────────────────────────┐
│              Flask Backend (:5000)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ auth_routes  │  │ doc_routes   │  │   models  │ │
│  └──────────────┘  └──────┬───────┘  └─────┬─────┘ │
│                           │                │        │
│  ┌────────────────────────▼───────────┐   │        │
│  │           Services Layer           │   │        │
│  │  hash_service  │  fraud_service    │   │        │
│  │  blockchain_service               │   │        │
│  └───────────────────┬───────────────┘   │        │
│                      │                   │        │
│               Web3.py │              SQLite        │
└──────────────────────┼────────────────────────────┘
                       │ JSON-RPC
┌──────────────────────▼────────────────────────────┐
│          Hardhat Local Node (:8545)               │
│       DocumentRegistry.sol (Solidity)             │
└───────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Blockchain | Ethereum (Hardhat local node), Solidity, Ethers.js |
| Backend | Python 3.11+, Flask, Web3.py, PyMuPDF |
| Database | SQLite (via Flask-SQLAlchemy or raw sqlite3) |
| Frontend | Vanilla HTML5 + JavaScript (no framework, no build step) |
| Dev Tools | Hardhat, Node.js 20+, Docker (optional, for PostgreSQL GUI) |

---

## Project Structure

```
blockchain-docverify/
├── backend/
│   ├── main.py                    # Flask app entrypoint
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   │   └── database.py            # SQLite schema & ORM models
│   ├── routes/
│   │   ├── auth_routes.py         # Register, login, JWT
│   │   └── document_routes.py     # Upload, verify, list
│   └── services/
│       ├── hash_service.py        # SHA-256 hashing
│       ├── blockchain_service.py  # Web3.py ↔ Hardhat
│       └── fraud_service.py       # AI fraud detection
├── blockchain/
│   ├── contracts/
│   │   └── DocumentRegistry.sol   # Solidity smart contract
│   ├── scripts/
│   │   └── deploy.js              # Hardhat deploy script
│   ├── test/                      # Hardhat/Mocha tests
│   ├── hardhat.config.js
│   └── package.json
├── frontend/
│   └── index.html                 # Single-file UI
├── DEPLOY.md
└── README.md
```

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | 20+ LTS | [nodejs.org](https://nodejs.org) |
| Python | 3.11+ | [python.org](https://python.org/downloads) |
| Docker Desktop | Any | [docker.com](https://docker.com) — optional |

Verify your environment:

```bash
node --version    # v20.x.x
python3 --version # 3.11.x or 3.12.x
```

---

## Quick Start

Clone the repo and follow the steps below. You will need **three terminal windows** running simultaneously.

```bash
git clone https://github.com/RajendraPIssar/blockchain-docverify.git
cd blockchain-docverify
```

### 1. Start the Database (optional)

SQLite is used by default — no setup needed. If you want a PostgreSQL browser via Docker:

```bash
docker run --name docverify-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=docverify \
  -p 5432:5432 \
  -d postgres:15-alpine

docker ps   # confirm it is running
```

> This is only needed for GUI inspection with SQLTools (VS Code extension). The app uses SQLite regardless.

---

### 2. Start the Local Blockchain

Open **Terminal 1** and label it `BLOCKCHAIN`:

```bash
cd blockchain
npm install
npx hardhat node
```

Leave this running. You will see 20 test wallet addresses and private keys printed. **Copy the private key for Account #0** — you need it in Step 4.

---

### 3. Deploy the Smart Contract

Open **Terminal 2** and label it `DEPLOY`:

```bash
cd blockchain
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```

Expected output:

```
✅ Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

**Copy the contract address** — you need it in Step 4.

---

### 4. Configure the Backend

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
WEB3_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=<paste address from Step 3>
PRIVATE_KEY=<paste Account #0 key from Step 2>
SECRET_KEY=change-me-in-production
```

---

### 5. Start the Backend

Open **Terminal 3** and label it `BACKEND`:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip3 install -r requirements.txt

python3 -m flask --app main run --debug --port 5000
```

Expected output:

```
 * Running on http://127.0.0.1:5000
```

The SQLite database file `docverify.db` is created automatically on first run.

---

### 6. Open the Frontend

No build step needed:

```bash
open frontend/index.html
```

Or in VS Code: right-click `frontend/index.html` → **Open with Live Server**.

The app loads at `http://127.0.0.1:5500/frontend/index.html`.

---

### 7. Promote Yourself to Admin

1. Register an account through the web UI.
2. In any terminal (with the venv active or from the `backend/` directory):

```bash
cd backend
python3 - <<'EOF'
import sqlite3
conn = sqlite3.connect('docverify.db')
conn.execute("UPDATE users SET role='admin' WHERE email='your@email.com'")
conn.commit()
conn.close()
print('Done — log out and log back in.')
EOF
```

3. Log out and back in — the **Admin** tab will appear.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `WEB3_URL` | ✅ | JSON-RPC URL of the Ethereum node (e.g. `http://127.0.0.1:8545`) |
| `CONTRACT_ADDRESS` | ✅ | Deployed `DocumentRegistry` contract address |
| `PRIVATE_KEY` | ✅ | Ethereum account private key for signing transactions |
| `SECRET_KEY` | ✅ | Flask session secret — change before any deployment |

---

## Smart Contract

**`DocumentRegistry.sol`** stores a mapping of document hashes to their on-chain metadata.

```solidity
// Simplified interface
function registerDocument(bytes32 docHash, string memory metadata) external;
function verifyDocument(bytes32 docHash) external view returns (bool exists, address registrar, uint256 timestamp);
```

- Document hashes are `bytes32` (SHA-256).
- Only authorized uploaders can call `registerDocument`.
- Anyone can call `verifyDocument` — fully public, no gas cost (view function).

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | None | Register a new user |
| `POST` | `/auth/login` | None | Login, returns JWT |
| `POST` | `/documents/upload` | JWT | Upload & register a document |
| `POST` | `/documents/verify` | None | Verify a document hash |
| `GET` | `/documents/` | JWT | List documents for current user |

---

## Testing

Run the Hardhat smart contract test suite:

```bash
cd blockchain
npx hardhat test
```

Expected: **6 passing** ✓

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Contract not initialized` | Hardhat node crashed. Re-run `npx hardhat node`, re-deploy, and update `CONTRACT_ADDRESS` in `.env`. |
| Port 5000 in use | `lsof -ti:5000 \| xargs kill -9` |
| `ModuleNotFoundError` | Activate venv: `source venv/bin/activate`, then `pip3 install -r requirements.txt` |
| `PyMuPDF install error` | `pip3 install PyMuPDF==1.24.1` |
| Frontend shows `Failed to fetch` | Backend is not running. Check Terminal 3 for errors. |

---

## Known Issues & Recommended Improvements

This is a Master's group project in its current form. Below are gaps and production-readiness concerns to address before any real deployment:

**Security**
- `.DS_Store` is committed — add it to `.gitignore` immediately.
- `SECRET_KEY` has a hardcoded default in `DEPLOY.md` — must never ship in production.
- Private key is stored in a plain `.env` file — use a secrets manager (AWS Secrets Manager, HashiCorp Vault) in production.
- Admin promotion is done via raw SQL in the terminal — replace with a seeded admin account or a proper admin CLI command.

**Architecture**
- The frontend is a single `index.html` with no bundler — fine for a demo, but would benefit from Vite + React or Vue for maintainability.
- No IPFS integration — documents are not actually stored; only hashes are anchored. For full decentralization, add Pinata or web3.storage.
- SQLite is not suitable for concurrent writes in production — migrate to PostgreSQL.
- No CI/CD pipeline, no Dockerfile for the backend, no Hardhat testnet config (Sepolia/Mumbai) for staging.

**Code Quality**
- Only one git commit (`1 Commit`) — use feature branches, pull requests, and meaningful commit messages.
- No `README.md` existed before this — add it to the root (this file).
- `fraud_service.py` purpose is undocumented — clarify what model or heuristic is used.
- Test coverage is only at the smart contract level — add Flask API tests (pytest + `flask test client`).

---

## Team

| Role | Responsibilities | Files |
|---|---|---|
| Member 1 | Authentication & Database | `backend/routes/auth_routes.py`, `backend/models/database.py` |
| Member 2 | Document Upload & Hashing | `backend/routes/document_routes.py`, `backend/services/hash_service.py` |
| Member 3 | Blockchain Integration | `backend/services/blockchain_service.py`, `blockchain/contracts/DocumentRegistry.sol`, `blockchain/scripts/deploy.js` |
| Member 4 | AI Fraud Detection & Frontend | `backend/services/fraud_service.py`, `frontend/index.html` |

---

## License

This project was developed as a Masters in Computer Science group assignment. All rights reserved by the authors unless otherwise specified.
