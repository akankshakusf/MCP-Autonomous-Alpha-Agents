import os
import gradio as gr
import pandas as pd
from util import css, js, Color
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
        holdings = self.account.get_holdings()
        if not holdings:
            return pd.DataFrame(columns=["Symbol", "Quantity"])
        df = pd.DataFrame([{"Symbol": symbol, "Quantity": quantity} for symbol, quantity in holdings.items()])
        return df
    
    def get_transactions_df(self) -> pd.DataFrame:
        transactions = self.account.list_transactions()
        if not transactions:
            return pd.DataFrame(columns=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"])
        return pd.DataFrame(transactions)
    
    def get_portfolio_value(self) -> str:
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
    import asyncio
    from trading_floor import create_traders
    from tracers import LogTracer
    from agents import add_trace_processor
    from market import is_market_open

    try:
        if not is_market_open():
            return "⚠️ Market is currently closed"
        add_trace_processor(LogTracer())
        traders = create_traders()
        async def run_trading():
            await asyncio.gather(*[trader.run() for trader in traders])
        asyncio.run(run_trading())
        return "✅ Trading round completed for all agents"
    except Exception as e:
        return f"❌ Error running trades: {str(e)}"


def start_trading():
    return "🔄 Agents are trading. Please wait..."

def generate_trading_summary():
    import pandas as pd
    from datetime import datetime
    from accounts import Account

    try:
        from trading_floor import names, lastnames, short_model_names
        summary_data = []
        for name, lastname, model_name in zip(names, lastnames, short_model_names):
            account = Account.get(name)
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
        df = pd.DataFrame(summary_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trading_summary_{timestamp}.csv"
        df.to_csv(filename, index=False)
        return filename  # <-- Return the file path for Gradio download!
    except Exception as e:
        # If error, return an empty file (optional: handle better)
        errorfile = "trading_summary_error.txt"
        with open(errorfile, "w") as f:
            f.write(str(e))
        return errorfile


def create_ui():
    traders = [Trader(trader_name, lastname, model_name) for trader_name, lastname, model_name in zip(names, lastnames, short_model_names)]    
    trader_views = [TraderView(trader) for trader in traders]
  
    with gr.Blocks(title="Traders", css=css, js=js, theme=gr.themes.Default(primary_hue="sky"), fill_width=True) as ui:
        # App Header
        gr.Markdown("""
            <div style='text-align: center;'>
            <h1>🚀 Autonomous Alpha Agents Trading Simulator</h1>
            <em>Welcome to the next-gen trading playground!</em>
            </div>""")
        
        # Trade button (top)
        with gr.Row():
            with gr.Column(scale=1):
                trade_button = gr.Button("🔄 Run Trades Now", variant="primary", size="sm")
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

        with gr.Row():
            for trader_view in trader_views:
                trader_view.make_ui()

        # === FOOTER with Download Button ===
        with gr.Row():
            gr.Markdown("#### Download your trading summary:")
            file_output = gr.File(label="Download CSV", interactive=False)
            download_button = gr.Button("📊 Download Summary", variant="secondary", size="sm")
            download_button.click(
                fn=generate_trading_summary,
                inputs=[],
                outputs=[file_output],
                show_progress=True
            )
    return ui

# if __name__ == "__main__":
#     ui = create_ui()
#     ui.launch(inbrowser=True,  share=True)

if __name__ == "__main__":
    ui = create_ui()
    ui.launch()
