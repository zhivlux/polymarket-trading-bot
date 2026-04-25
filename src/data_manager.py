# src/data_manager.py
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from config import Config
from logging_utils import logger

class DataManager:
    """Manage SQLite database for market data and trades"""
    
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Market data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                market_id TEXT NOT NULL,
                price REAL,
                bid_depth REAL,
                ask_depth REAL,
                spread REAL,
                volume REAL,
                whale_activity REAL,
                UNIQUE(timestamp, market_id)
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                side TEXT,
                quantity REAL,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                reason TEXT,
                outcome TEXT
            )
        """)
        
        # Model metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model_name TEXT,
                accuracy REAL,
                auc REAL,
                total_samples INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    def insert_market_data(self, market_id: str, data: Dict):
        """Insert market data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO market_data 
                (market_id, price, bid_depth, ask_depth, spread, volume, whale_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                market_id,
                data.get('price', 0),
                data.get('bid_depth', 0),
                data.get('ask_depth', 0),
                data.get('spread', 0),
                data.get('volume', 0),
                data.get('whale_activity', 0)
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error inserting market data: {e}")
        finally:
            conn.close()
    
    def insert_trade(self, trade_data: Dict):
        """Insert trade record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO trades 
                (side, quantity, entry_price, exit_price, pnl, reason, outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_data.get('side'),
                trade_data.get('quantity'),
                trade_data.get('entry_price'),
                trade_data.get('exit_price'),
                trade_data.get('pnl'),
                trade_data.get('reason'),
                trade_data.get('outcome')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error inserting trade: {e}")
        finally:
            conn.close()
    
    def get_recent_data(self, market_id: str, hours: int = 24) -> pd.DataFrame:
        """Get recent market data"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            df = pd.read_sql_query(f"""
                SELECT * FROM market_data 
                WHERE market_id = ? AND timestamp > datetime('now', '-{hours} hours')
                ORDER BY timestamp DESC
            """, conn, params=(market_id,))
            return df
        except Exception as e:
            logger.error(f"❌ Error fetching data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_trade_stats(self) -> Dict:
        """Get trading statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total trades
            cursor.execute("SELECT COUNT(*) FROM trades")
            total_trades = cursor.fetchone()[0]
            
            # Winning trades
            cursor.execute("SELECT COUNT(*) FROM trades WHERE outcome = 'WIN'")
            winning_trades = cursor.fetchone()[0]
            
            # Total PnL
            cursor.execute("SELECT SUM(pnl) FROM trades")
            total_pnl = cursor.fetchone()[0] or 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
                'total_pnl': total_pnl
            }
        except Exception as e:
            logger.error(f"❌ Error getting trade stats: {e}")
            return {}
        finally:
            conn.close()
    
    def cleanup_old_data(self, days: int = 30):
        """Delete data older than N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                DELETE FROM market_data 
                WHERE timestamp < datetime('now', '-{days} days')
            """)
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"✅ Deleted {deleted} old records")
        except Exception as e:
            logger.error(f"❌ Error cleaning up: {e}")
        finally:
            conn.close()
