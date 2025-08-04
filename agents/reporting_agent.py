import os
import pandas as pd
import telegram
from .base_agent import BaseAgent
from config import Config
from utils.visualization import create_performance_plot
from dash_app.app import run_dashboard
from utils.visualization import create_performance_history, create_win_loss_pie

def send_telegram_report(self, report):
    # ... existing code ...
    
    # Send performance chart
    perf_fig = create_performance_history(self.conductor.performance_log)
    perf_img = perf_fig.to_image(format="png")
    self.bot.send_photo(chat_id=Config.TELEGRAM_CHAT_ID, photo=perf_img)
    
    # Send win/loss chart
    pie_fig = create_win_loss_pie(self.conductor.performance_log)
    pie_img = pie_fig.to_image(format="png")
    self.bot.send_photo(chat_id=Config.TELEGRAM_CHAT_ID, photo=pie_img)

class ReportingAgent(BaseAgent):
    def __init__(self, agent_id, conductor):
        super().__init__(agent_id, conductor)
        if Config.TELEGRAM_TOKEN:
            self.bot = telegram.Bot(token=Config.TELEGRAM_TOKEN)
    
    def execute(self):
        print(f"[{self.agent_id}] Generating reports")
        # Compile final report
        report = self.compile_report()
        
        # Send to Telegram
        if "telegram" in self.task_spec["platforms"]:
            self.send_telegram_report(report)
        
        # Update dashboard
        if "dashboard" in self.task_spec["platforms"]:
            self.update_dashboard(report)
        
        return {"status": "success"}
    
    def compile_report(self):
        # Get value bets from previous agent
        value_bets = self.conductor.task_history[-1]["result"]["value_bets"]
        
        # Calculate performance metrics
        win_rate, roi = self.calculate_performance()
        
        # Prepare visualization
        perf_plot = create_performance_plot(self.conductor.performance_log)
        
        return {
            "value_bets": value_bets,
            "performance": {
                "win_rate": win_rate,
                "roi": roi,
                "plot": perf_plot
            },
            "timestamp": pd.Timestamp.now()
        }
    
    def calculate_performance(self):
        wins = sum(1 for log in self.conductor.performance_log if log['result'] == 'win')
        total = len(self.conductor.performance_log)
        win_rate = wins / total if total > 0 else 0
        
        initial_budget = Config.INITIAL_BUDGET
        current_budget = self.conductor.budget
        roi = (current_budget - initial_budget) / initial_budget
        
        return win_rate, roi
    
    def send_telegram_report(self, report):
        try:
            message = "⚽ Sports Betting AI Report ⚽\n\n"
            message += f"✅ Win Rate: {report['performance']['win_rate']:.2%}\n"
            message += f"💰 ROI: {report['performance']['roi']:.2%}\n\n"
            message += "Top Value Bets:\n"
            
            for bet in report['value_bets'][:3]:
                status = "🔹" if bet['bet_type'] == "UNDERVALUE" else "🔺"
                message += (
                    f"{status} {bet['home_team']} vs {bet['away_team']}\n"
                    f"Type: {bet['bet_type']} | Confidence: {bet['confidence']:.0%}\n"
                    f"Odds: {bet['bookmaker_odds']} | Value: {bet['value_score']:.3f}\n\n"
                )
            
            self.bot.send_message(
                chat_id=Config.TELEGRAM_CHAT_ID, 
                text=message
            )
            
            # Send performance plot
            if report['performance']['plot']:
                self.bot.send_photo(
                    chat_id=Config.TELEGRAM_CHAT_ID,
                    photo=open(report['performance']['plot'], 'rb')
                )
        except Exception as e:
            print(f"Telegram error: {str(e)}")
    
    def update_dashboard(self, report):
        run_dashboard(report)
