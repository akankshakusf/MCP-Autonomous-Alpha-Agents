import gradio as gr
from util import css, js, Color
import pandas as pd
from trading_floor import names, lastnames, short_model_names
import plotly.express as px
from accounts import Account
from database import read_log

mapper = {
    "trace": Color.WHITE,
    "agent": Color.CYAN,
    "function": Color.GREEN,
    "generation": Color.YELLOW,
    "response": Color.MAGENTA,
    "account": Color.RED,
}

class Trader:
    def __init__(self, name: str, lastname: str, model_name: str):
        self.name = name
        self.lastname = lastname
        self.model_name = model_name
        self.account = Account.get(name)

    def reload(self):
        self.account = Account.get(self.name)

    def get_title(self) -> str:
        return f"<div style='text-align: center;font-size:34px;'>{self.name}<span style='color:#ccc;font-size:24px;'> ({self.model_name}) - {self.lastname}</span></div>"

    def get_strategy(self) -> str:
        return self.account.get_strategy()

    def get_portfolio_value_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.account.portfolio_value_time_series, columns=["datetime", "value"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    
    def get_portfolio_value_chart(self):
        df = self.get_portfolio_value_df()
        fig = px.line(df, x="datetime", y="value")
        margin = dict(l=40, r=20, t=20, b=40) 
        fig.update_layout(height=300, margin=margin, xaxis_title=None, yaxis_title=None, paper_bgcolor="#bbb", plot_bgcolor="#dde")
        fig.update_xaxes(tickformat="%m/%d", tickangle=45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=8), tickformat=",.0f")
        return fig
        
    def get_holdings_df(self) -> pd.DataFrame:
        """Convert holdings to DataFrame for display"""
        holdings = self.account.get_holdings()
        if not holdings:
            return pd.DataFrame(columns=["Symbol", "Quantity"])
        
        df = pd.DataFrame([
            {"Symbol": symbol, "Quantity": quantity} 
            for symbol, quantity in holdings.items()
        ])
        return df
    
    def get_transactions_df(self) -> pd.DataFrame:
        """Convert transactions to DataFrame for display"""
        transactions = self.account.list_transactions()
        if not transactions:
            return pd.DataFrame(columns=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"])
        
        return pd.DataFrame(transactions)
    
    def get_portfolio_value(self) -> str:
        """Calculate total portfolio value based on current prices"""
        portfolio_value = self.account.calculate_portfolio_value() or 0.0
        pnl = self.account.calculate_profit_loss(portfolio_value) or 0.0
        color = "green" if pnl >= 0 else "red"
        emoji = "⬆" if pnl >= 0 else "⬇"
        return f"<div style='text-align: center;background-color:{color};'><span style='font-size:32px'>${portfolio_value:,.0f}</span><span style='font-size:24px'>&nbsp;&nbsp;&nbsp;{emoji}&nbsp;${pnl:,.0f}</span></div>"
    
    def get_logs(self, previous=None) -> str:
        logs = read_log(self.name, last_n=13)
        response = ""
        for log in logs:
            timestamp, type, message = log
            color = mapper.get(type, Color.WHITE).value
            response += f"<span style='color:{color}'>{timestamp} : [{type}] {message}</span><br/>"
        response = f"<div style='height:250px; overflow-y:auto;'>{response}</div>"
        if response != previous:
            return response
        return gr.update()
    
    
class TraderView:

    def __init__(self, trader: Trader):
        self.trader = trader
        self.portfolio_value = None
        self.chart = None
        self.holdings_table = None
        self.transactions_table = None

    def make_ui(self):
        with gr.Column():
            gr.HTML(self.trader.get_title())
            with gr.Row():
                self.portfolio_value = gr.HTML(self.trader.get_portfolio_value)
            with gr.Row():
                self.chart = gr.Plot(self.trader.get_portfolio_value_chart, container=True, show_label=False)
            with gr.Row(variant="panel"):
                self.log = gr.HTML(self.trader.get_logs)
            with gr.Row():
                self.holdings_table = gr.Dataframe(
                    value=self.trader.get_holdings_df,
                    label="Holdings",
                    headers=["Symbol", "Quantity"],
                    row_count=(10, "dynamic"),
                    col_count=2,
                    max_height=400,
                    wrap=True,
                    elem_classes=["dataframe-fix-small"]
                )
            with gr.Row():
                self.transactions_table = gr.Dataframe(
                    value=self.trader.get_transactions_df,
                    label="Recent Transactions",
                    headers=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"],
                    row_count=(10, "dynamic"),
                    col_count=5,
                    max_height=400,
                    wrap=True,
                    elem_classes=["dataframe-fix"]
                )
            

        timer = gr.Timer(value=120)
        timer.tick(fn=self.refresh, inputs=[], outputs=[self.portfolio_value, self.chart, self.holdings_table, self.transactions_table], show_progress="hidden", queue=False)
        log_timer = gr.Timer(value=0.5)
        log_timer.tick(fn=self.trader.get_logs, inputs=[self.log], outputs=[self.log], show_progress="hidden", queue=False)

    def refresh(self):
        self.trader.reload()
        return self.trader.get_portfolio_value(), self.trader.get_portfolio_value_chart(), self.trader.get_holdings_df(), self.trader.get_transactions_df()

def run_all_trades():
    """Run trades for all agents manually"""
    import asyncio
    from trading_floor import create_traders
    from tracers import LogTracer
    from agents import add_trace_processor
    from market import is_market_open
    
    try:
        # Check if market is open (optional - remove this check if you want to allow manual trades even when closed)
        if not is_market_open():
            return "⚠️ Market is currently closed"
        
        # Set up tracing
        add_trace_processor(LogTracer())
        
        # Create traders and run them
        traders = create_traders()
        
        # Run the async trading operations
        async def run_trading():
            await asyncio.gather(*[trader.run() for trader in traders])
        
        # Execute the async function
        asyncio.run(run_trading())
        
        return "✅ Trading round completed for all agents"
    except Exception as e:
        return f"❌ Error running trades: {str(e)}"

def start_trading():
    """Initial function to show loading message"""
    return "🔄 Agents are trading. Please wait..."

def generate_trading_summary():
    """Generate a summary of all agents' trading data for download, including transactions and rationale"""
    import pandas as pd
    from datetime import datetime
    from accounts import Account

    try:
        from trading_floor import names, lastnames, short_model_names

        summary_data = []
        all_transactions = []

        for name, lastname, model_name in zip(names, lastnames, short_model_names):
            account = Account.get(name)

            # Main summary
            portfolio_value = account.calculate_portfolio_value() or 0.0
            pnl = account.calculate_profit_loss(portfolio_value) or 0.0
            holdings = account.get_holdings()
            holdings_str = ", ".join([f"{symbol}: {qty}" for symbol, qty in holdings.items()]) if holdings else "None"
            transactions = account.list_transactions()
            recent_trades = len(transactions) if transactions else 0

            summary_data.append({
                "Agent": f"{name} ({model_name}) - {lastname}",
                "Portfolio Value": f"${portfolio_value:,.2f}",
                "P&L": f"${pnl:,.2f}",
                "Holdings": holdings_str,
                "Recent Trades": recent_trades,
                "Strategy": account.get_strategy() if hasattr(account, 'get_strategy') else "N/A"
            })

            # Detailed transactions
            if transactions:
                for txn in transactions:
                    txn_dict = dict(txn) if isinstance(txn, dict) else {}
                    # If list-of-dict, else it's probably a tuple; handle both
                    if not txn_dict:
                        txn_dict = {
                            "Timestamp": txn[0] if len(txn) > 0 else "",
                            "Symbol": txn[1] if len(txn) > 1 else "",
                            "Quantity": txn[2] if len(txn) > 2 else "",
                            "Price": txn[3] if len(txn) > 3 else "",
                            "Rationale": txn[4] if len(txn) > 4 else "",
                        }
                    txn_dict["Agent"] = f"{name} ({model_name}) - {lastname}"
                    all_transactions.append(txn_dict)

        # Save summary CSV
        df = pd.DataFrame(summary_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"trading_summary_{timestamp}.csv"
        df.to_csv(summary_filename, index=False)

        # Save transactions CSV
        if all_transactions:
            df_txn = pd.DataFrame(all_transactions)
            txn_filename = f"trading_transactions_{timestamp}.csv"
            df_txn.to_csv(txn_filename, index=False)
            return f"📊 Summary downloaded as {summary_filename}<br>📄 Detailed transactions (with rationale) downloaded as {txn_filename}"
        else:
            return f"📊 Summary downloaded as {summary_filename}<br>⚠️ No transactions found for any agent."

    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"
    
    
# Main UI construction
def create_ui():
    """Create the main Gradio UI for the trading simulation"""
    
    traders = [Trader(trader_name, lastname, model_name) for trader_name, lastname, model_name in zip(names, lastnames, short_model_names)]    
    trader_views = [TraderView(trader) for trader in traders]
  
    with gr.Blocks(title="Traders", css=css, js=js, theme=gr.themes.Default(primary_hue="sky"), fill_width=True) as ui:
        # Add App Header at the very top
        gr.Markdown("""
            <div style='text-align: center;'>
            <h1>🚀 Autonomous Alpha Agents Trading Simulator</h1>
            <em>Welcome to the next-gen trading playground!</em>
            </div>""")
        
        # Add manual trade button at the top
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    trade_button = gr.Button("🔄 Run Trades Now", variant="primary", size="sm")
                    download_button = gr.Button("📊 Download Summary", variant="secondary", size="sm")
                trade_status = gr.HTML("")
                
                trade_button.click(
                    fn=start_trading,
                    inputs=[],
                    outputs=[trade_status],
                    show_progress=False
                ).then(
                    fn=run_all_trades,
                    inputs=[],
                    outputs=[trade_status],
                    show_progress=True
                )
                
                download_button.click(
                    fn=generate_trading_summary,
                    inputs=[],
                    outputs=[trade_status],
                    show_progress=True
                )
        
        with gr.Row():
            for trader_view in trader_views:
                trader_view.make_ui()
        
    return ui

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser=True)