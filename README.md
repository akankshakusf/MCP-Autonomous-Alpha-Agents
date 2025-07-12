# 🧠 Autonomous Alpha Agents Trading Simulator

> **A Multi-Agent, Multi-MCP, LLM-Powered Stock Trading System**

---

<img src="https://github.com/akankshakusf/Autonomous-MultiAgent-AWS-Incident-Jira-Automation/blob/main/images/arch%202.png" width="100%" />

---

## 🚀 Project Overview

This project implements a fully autonomous multi-agent trading simulator leveraging LLMs (Large Language Models), the Model Context Protocol (MCP), and modular microservices.  
It enables agents to research, decide, execute trades, and send notifications in a realistic, modular, and resilient simulation.

---

## 🛠️ Key Components

- **Chat Interface (UI):**  
  User submits trading queries (e.g., _"Buy 10 shares of TSLA"_).

- **LLM Trader Agent:**  
  Interprets user intent, orchestrates the workflow, and delegates tasks to specialized MCP servers.

- **MCP Servers:**  
  - **Market MCP:** Retrieves real-time or fallback share prices and market status.
  - **Account MCP:** Handles buying/selling, funds verification, and account state updates.
  - **Push MCP:** Sends push notifications upon trade success or failure.

- **Resilience:**  
  Handles all failure modes (market closed, insufficient funds, price unavailable, push notification failure, or MCP server unavailable) and provides user-facing feedback for each scenario.

---

## 📊 Example Flow

1. **User:**  
   _"Buy 10 shares of TSLA"_

2. **LLM Trader Agent:**  
   - Checks if the query can be answered directly or if market/account/push MCP interaction is needed.
   - Queries the Market MCP for current price and market status.
   - Calls Account MCP to execute trade if possible.
   - Invokes Push MCP to notify user upon trade completion.
   - Handles and returns errors if any MCP server fails (with explicit error messaging).

3. **User:**  
   - Sees a clear response:  
     - “TSLA shares bought!” (Success)  
     - “Trade failed: insufficient funds”  
     - “Trade failed: market closed”  
     - “Trade failed: price unavailable”  
     - “Push notification failed”  
     - “Trade failed: system unavailable”  

---

## 🖼️ Architecture Diagram

- **Solid lines:** Successful operation flow  
- **Dashed lines:** Error/exception handling and user feedback  
- **Green:** Success path  
- **Red:** Error/exception messages  
- **MCP blocks:** Modular protocol servers for decoupled, scalable design

---

## 📦 Tech Stack

- **Python** (Gradio, FastAPI, Pydantic, asyncio, sqlite)
- **OpenAI/LLM/Agents** (Orchestration via custom agentic framework)
- **MCP (Model Context Protocol)** – Modular tool/server-based integration
- **Polygon.io** – Market data (with fallback logic)
- **Pushover** – Push notification microservice

---

## 🧑‍💻 How to Run

1. **Clone the repo** and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. **Set environment variables** in a `.env` file:
    ```
    POLYGON_API_KEY=...
    POLYGON_PLAN=...
    PUSHOVER_USER=...
    PUSHOVER_TOKEN=...
    # (other keys as needed)
    ```

3. **Launch the UI:**
    ```bash
    python app.py
    # Or use 'uv' if set up for hot-reload
    ```

4. **Interact via web interface** or programmatic API.

---

## 💡 Features

- LLM-powered agentic workflow
- Modular, observable, and scalable with MCP servers
- Complete end-to-end error handling (market, price, account, notification, or system failures)
- Realistic user feedback
- Can be extended with new agents or data sources

---

## 📎 Diagram Attribution

- Architecture diagram inspired by [@Aurimas_Gr](https://www.linkedin.com/in/aurimas-griciunas/), reimagined for this project.

---

## 📣 Connect

Built by **[Your Name]**  
- [LinkedIn](https://www.linkedin.com/in/YOUR-PROFILE)  
- [GitHub](https://github.com/YOUR-GITHUB)  

---

> **If you like this project, give it a star! ⭐️**  
> For questions, open an issue or connect with me on LinkedIn.
