# src/virtual_wallet.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from logging_utils import logger

@dataclass
class Trade:
    """Trade record"""
    timestamp: datetime
    side: str  # 'BUY' or 'SELL'
    quantity: float
    entry_price: float
    exit_price: float = None
    pnl: float = None
    reason: str = ""
    outcome: str = None  # 'WIN' or 'LOSS'

class VirtualWallet:
    """Paper trading wallet"""
    
    def __init__(self, initial_balance: float):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions: Dict[str, tuple] = {}  # {symbol: (qty, avg_price)}
        self.trade_history: List[Trade] = []
        self.consecutive_losses = 0
        self.loss_reasons: Dict[str, int] = {}
    
    def buy(self, symbol: str, quantity: float, price: float, reason: str = "") -> tuple:
        """Execute buy order"""
        cost = quantity * price
        
        if cost > self.balance:
            return False, f"Insufficient balance: need {cost}, have {self.balance}"
        
        self.balance -= cost
        
        if symbol in self.positions:
            old_qty, old_price = self.positions[symbol]
            new_qty = old_qty + quantity
            new_avg_price = (old_qty * old_price + quantity * price) / new_qty
            self.positions[symbol] = (new_qty, new_avg_price)
        else:
            self.positions[symbol] = (quantity, price)
        
        trade = Trade(
            timestamp=datetime.now(),
            side='BUY',
            quantity=quantity,
            entry_price=price,
            reason=reason
        )
        self.trade_history.append(trade)
        
        logger.info(f"✅ BUY: {quantity} {symbol} @ ${price:.4f} - Reason: {reason}")
        return True, "BUY executed"
    
    def sell(self, symbol: str, quantity: float, price: float) -> tuple:
        """Execute sell order"""
        if symbol not in self.positions or self.positions[symbol][0] < quantity:
            return False, f"Insufficient position: {symbol}"
        
        old_qty, entry_price = self.positions[symbol]
        self.balance += quantity * price
        pnl = (price - entry_price) * quantity
        
        # Update last trade
        if self.trade_history:
            self.trade_history[-1].exit_price = price
            self.trade_history[-1].pnl = pnl
            self.trade_history[-1].outcome = "WIN" if pnl > 0 else "LOSS"
        
        # Track consecutive losses
        if pnl < 0:
            self.consecutive_losses += 1
            reason = self.trade_history[-1].reason if self.trade_history else "unknown"
            self.loss_reasons[reason] = self.loss_reasons.get(reason, 0) + 1
        else:
            self.consecutive_losses = 0
        
        # Update position
        remaining_qty = old_qty - quantity
        if remaining_qty > 0:
            self.positions[symbol] = (remaining_qty, entry_price)
        else:
            del self.positions[symbol]
        
        logger.info(f"✅ SELL: {quantity} {symbol} @ ${price:.4f} - PnL: ${pnl:.2f}")
        return True, f"SELL executed, PnL: ${pnl:.2f}"
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Get total portfolio value"""
        value = self.balance
        for symbol, (qty, _) in self.positions.items():
            if symbol in current_prices:
                value += qty * current_prices[symbol]
        return value
    
    def get_stats(self) -> Dict:
        """Get wallet statistics"""
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t.outcome == "WIN")
        losing_trades = total_trades - winning_trades
        total_pnl = sum(t.pnl or 0 for t in self.trade_history)
        
        return {
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'roi': (self.balance - self.initial_balance) / self.initial_balance if self.initial_balance > 0 else 0,
            'consecutive_losses': self.consecutive_losses,
            'loss_reasons': self.loss_reasons,
            'open_positions': len(self.positions)
        }
