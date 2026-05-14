"""
市场数据获取模块

支持多种数据源：akshare、yfinance、tushare
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def get_realtime_quote(symbol: str, source: str = "akshare") -> pd.DataFrame:
    """
    获取股票实时行情
    
    Args:
        symbol: 股票代码，如 "000001" 或 "000001.SZ"
        source: 数据源，默认 "akshare"
    
    Returns:
        DataFrame 包含行情数据
    """
    # 清理股票代码格式
    symbol = symbol.replace(".SZ", "").replace(".SH", "")
    
    if source == "akshare":
        return _get_quote_akshare(symbol)
    elif source == "yfinance":
        return _get_quote_yfinance(symbol)
    elif source == "tushare":
        return _get_quote_tushare(symbol)
    else:
        raise ValueError(f"不支持的数据源: {source}")


def _get_quote_akshare(symbol: str) -> pd.DataFrame:
    """使用 AKShare 获取行情"""
    try:
        import akshare as ak
        
        # 判断沪市还是深市
        if symbol.startswith("6"):
            full_symbol = f"{symbol}.SH"
        else:
            full_symbol = f"{symbol}.SZ"
        
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df["代码"] == symbol]
        
        if stock_data.empty:
            logger.warning(f"未找到股票: {symbol}")
            return pd.DataFrame()
        
        return stock_data[[
            "代码", "名称", "最新价", "涨跌幅", "涨跌额", "成交量",
            "成交额", "振幅", "最高", "最低", "今开", "昨收"
        ]]
        
    except ImportError:
        raise ImportError("请先安装 akshare: pip install akshare")
    except Exception as e:
        logger.error(f"AKShare 获取行情失败: {e}")
        return pd.DataFrame()


def _get_quote_yfinance(symbol: str) -> pd.DataFrame:
    """使用 yfinance 获取行情（适合美股/港股）"""
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(f"{symbol}.SS" if symbol.startswith("6") else f"{symbol}.SZ")
        info = ticker.info
        
        return pd.DataFrame([info])
        
    except ImportError:
        raise ImportError("请先安装 yfinance: pip install yfinance")


def _get_quote_tushare(symbol: str) -> pd.DataFrame:
    """使用 Tushare 获取行情"""
    try:
        import tushare as ts
        
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            raise ValueError("请设置环境变量 TUSHARE_TOKEN")
        
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 转换代码格式
        if symbol.startswith("6"):
            ts_code = f"{symbol}.SH"
        else:
            ts_code = f"{symbol}.SZ"
        
        df = pro.daily(ts_code=ts_code, limit=1)
        return df
        
    except ImportError:
        raise ImportError("请先安装 tushare: pip install tushare")


def get_index_data(index_code: str = "000300.SH") -> pd.DataFrame:
    """
    获取市场指数数据
    
    Args:
        index_code: 指数代码
    
    Returns:
        DataFrame 包含指数数据
    """
    symbol = index_code.replace(".SH", "").replace(".SZ", "")
    
    try:
        import akshare as ak
        
        if index_code.endswith(".SH"):
            df = ak.stock_zh_index_daily_em(symbol=f"sh{symbol}")
        else:
            df = ak.stock_zh_index_daily_em(symbol=f"sz{symbol}")
        
        return df.tail(30)
        
    except ImportError:
        raise ImportError("请先安装 akshare: pip install akshare")
