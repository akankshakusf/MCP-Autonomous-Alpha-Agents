# 🧠 Autonomous Alpha Agents Trading Simulator

> **A Multi-Agent, Multi-MCP, LLM-Powered Stock Trading System**
> App link: https://huggingface.co/spaces/akankshakusf/autonomous-trading-sim
---

<img src="https://github.com/akankshakusf/MCP-Autonomous-Alpha-Agents/blob/master/arch%201.svg" width="70%" />

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

## 📦 Tech Stack

- **Python** (Gradio, FastAPI, Pydantic, asyncio, sqlite)
- **OpenAI/LLM/Agents** (Orchestration via custom agentic framework)
- **MCP (Model Context Protocol)** – Modular tool/server-based integration
- **Polygon.io** – Market data (with fallback logic)
- **Pushover** – Push notification microservice

---
## 💼 How Companies Can Use This System

1. **Automated Portfolio Management:**  
   Deploy autonomous agent teams to manage real or simulated investment portfolios, allowing for continuous, data-driven trading decisions across global markets.

2. **Rapid Prototyping of Trading Strategies:**  
   Experiment with new trading logic, agent behaviors, or market data sources in a modular, safe environment before rolling out to production.

3. **Resilient, Auditable Trade Execution:**  
   Leverage the built-in error handling and logging for compliance, real-time monitoring, and robust recovery from system or third-party failures.

4. **Intelligent Decision Support:**  
   Integrate the platform into existing finance operations to provide recommendations or real-time “what-if” analysis using AI-powered agents.

5. **Customizable Multi-Agent Simulations:**  
   Model and test different trader personas, risk policies, or notification flows for research, training, or investor education—simply by swapping agent logic or microservices.

---

