"""
技术指标计算模块

提供 MACD、KDJ、RSI、BOLL 等常用技术指标计算
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_indicator(
    symbol: str,
    indicator: str = "MACD",
    period: str = "daily",
    source: str = "akshare",
    lookback: int = 120
) -> pd.DataFrame:
    """
    计算技术指标
    
    Args:
        symbol: 股票代码
        indicator: 指标名称 (MACD, KDJ, RSI, BOLL, MA)
        period: 周期
        source: 数据源
        lookback: 回看天数
    
    Returns:
        DataFrame 包含指标数据
    """
    from skills.market_data import get_realtime_quote
    
    # 获取历史数据
    df = _get_history_data(symbol, lookback, source)
    
    if df.empty:
        return pd.DataFrame()
    
    # 计算指标
    indicator = indicator.upper()
    if indicator == "MACD":
        return calculate_macd(df)
    elif indicator == "KDJ":
        return calculate_kdj(df)
    elif indicator == "RSI":
        return calculate_rsi(df)
    elif indicator == "BOLL":
        return calculate_boll(df)
    elif indicator == "MA":
        return calculate_ma(df)
    else:
        raise ValueError(f"不支持的指标: {indicator}")


def _get_history_data(symbol: str, lookback: int, source: str) -> pd.DataFrame:
    """获取历史行情数据"""
    try:
        import akshare as ak
        
        symbol_clean = symbol.replace(".SZ", "").replace(".SH", "")
        
        if symbol_clean.startswith("6"):
            full_symbol = f"sh{symbol_clean}"
        else:
            full_symbol = f"sz{symbol_clean}"
        
        df = ak.stock_zh_a_hist(
            symbol=symbol_clean,
            period="daily",
            start_date="20200101",
            adjust="qfq"
        )
        
        return df.tail(lookback)
        
    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        return pd.DataFrame()


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    计算 MACD 指标
    
    Args:
        df: 包含 '收盘' 列的 DataFrame
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期
    
    Returns:
        DataFrame 添加 MACD、DIF、DEA 列
    """
    close = df["收盘"].astype(float)
    
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    
    result = df.copy()
    result["DIF"] = dif.round(4)
    result["DEA"] = dea.round(4)
    result["MACD"] = macd.round(4)
    
    return result


def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """
    计算 KDJ 指标
    
    Args:
        df: 包含 '最高'、'最低'、'收盘' 列的 DataFrame
        n: RSV 计算周期
        m1: K 值平滑周期
        m2: D 值平滑周期
    
    Returns:
        DataFrame 添加 K、D、J 列
    """
    high = df["最高"].astype(float)
    low = df["最低"].astype(float)
    close = df["收盘"].astype(float)
    
    low_n = low.rolling(window=n, min_periods=1).min()
    high_n = high.rolling(window=n, min_periods=1).max()
    
    rsv = (close - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)
    
    k = rsv.ewm(com=m1 - 1, adjust=False).mean()
    d = k.ewm(com=m2 - 1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    result = df.copy()
    result["K"] = k.round(2)
    result["D"] = d.round(2)
    result["J"] = j.round(2)
    
    return result


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    计算 RSI 指标
    
    Args:
        df: 包含 '收盘' 列的 DataFrame
        period: 计算周期
    
    Returns:
        DataFrame 添加 RSI 列
    """
    close = df["收盘"].astype(float)
    delta = close.diff()
    
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    result = df.copy()
    result["RSI"] = rsi.round(2)
    
    return result


def calculate_boll(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    计算 BOLL（布林带）指标
    
    Args:
        df: 包含 '收盘' 列的 DataFrame
        period: 移动平均周期
        std_dev: 标准差倍数
    
    Returns:
        DataFrame 添加 BOLL_UP、BOLL_MID、BOLL_LOW 列
    """
    close = df["收盘"].astype(float)
    
    mid = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    
    up = mid + std_dev * std
    low = mid - std_dev * std
    
    result = df.copy()
    result["BOLL_MID"] = mid.round(2)
    result["BOLL_UP"] = up.round(2)
    result["BOLL_LOW"] = low.round(2)
    
    return result


def calculate_ma(df: pd.DataFrame, periods: list = [5, 10, 20, 60]) -> pd.DataFrame:
    """
    计算移动平均线
    
    Args:
        df: 包含 '收盘' 列的 DataFrame
        periods: 周期列表
    
    Returns:
        DataFrame 添加 MA5、MA10、MA20、MA60 列
    """
    close = df["收盘"].astype(float)
    
    result = df.copy()
    for p in periods:
        result[f"MA{p}"] = close.rolling(window=p).mean().round(2)
    
    return result
