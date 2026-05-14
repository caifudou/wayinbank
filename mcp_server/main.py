"""
WayinBank - 金融工具 MCP 服务入口

提供标准化的金融数据查询、技术指标计算等 MCP 工具服务。
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("wayinbank-mcp")

# 加载环境变量
load_dotenv()

# 初始化 MCP Server
app = Server("wayinbank")


@app.tool()
async def get_stock_quote(symbol: str, source: str = "akshare") -> list[TextContent]:
    """
    获取股票实时行情数据
    
    Args:
        symbol: 股票代码，如 "000001.SZ" 或 "600519.SH"
        source: 数据源，可选 "akshare"（默认）、"yfinance"、"tushare"
    
    Returns:
        包含行情数据的 JSON 字符串
    """
    try:
        from skills.market_data import get_realtime_quote
        
        df = await asyncio.to_thread(get_realtime_quote, symbol=symbol, source=source)
        
        if df.empty:
            return [TextContent(type="text", text=json.dumps({"error": "未找到数据"}, ensure_ascii=False))]
        
        result = {
            "symbol": symbol,
            "source": source,
            "data": df.to_dict(orient="records")
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]
        
    except Exception as e:
        logger.error(f"获取行情失败: {symbol} - {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


@app.tool()
async def calculate_technical_indicator(
    symbol: str,
    indicator: str = "MACD",
    period: str = "daily",
    source: str = "akshare"
) -> list[TextContent]:
    """
    计算股票技术指标
    
    Args:
        symbol: 股票代码
        indicator: 指标名称，可选 MACD、KDJ、RSI、BOLL 等
        period: 周期，可选 daily、weekly、monthly
        source: 数据源
    
    Returns:
        包含指标数据的 JSON 字符串
    """
    try:
        from skills.indicators import calculate_indicator
        
        df = await asyncio.to_thread(
            calculate_indicator,
            symbol=symbol,
            indicator=indicator,
            period=period,
            source=source
        )
        
        result = {
            "symbol": symbol,
            "indicator": indicator,
            "period": period,
            "data": df.tail(20).to_dict(orient="records")  # 返回最近20条
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]
        
    except Exception as e:
        logger.error(f"计算指标失败: {symbol} - {indicator} - {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


@app.tool()
async def get_market_index(index_code: str = "000300.SH") -> list[TextContent]:
    """
    获取市场指数数据（如沪深300、上证指数等）
    
    Args:
        index_code: 指数代码，如 "000300.SH"（沪深300）、"000001.SH"（上证指数）
    
    Returns:
        包含指数数据的 JSON 字符串
    """
    try:
        from skills.market_data import get_index_data
        
        df = await asyncio.to_thread(get_index_data, index_code=index_code)
        
        result = {
            "index_code": index_code,
            "data": df.tail(10).to_dict(orient="records")
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]
        
    except Exception as e:
        logger.error(f"获取指数数据失败: {index_code} - {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def main():
    """MCP 服务主入口"""
    logger.info("WayinBank MCP Server 启动中...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options=app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
