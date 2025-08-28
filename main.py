### 完整代码（含可视化逻辑）
```python
from web3 import Web3
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, pow

# -------------------- 核心配置信息（替换成你的参数） -------------------- #
# BSC 节点 RPC（public节点或自建节点，推荐用Alchemy/Infura的BSC节点）
BSC_RPC = "https://bsc-dataseed.binance.org/"  
# 目标 Pool 地址（示例：Pancake V3 BNB-USDT 0.3% 费率池，可替换成任意BSC上的V3池）
POOL_ADDRESS = "0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16"  
# 可视化参数：查询当前Tick前后的Tick范围（越大覆盖流动性越广，建议100-500）
TICK_RANGE = 200  
# 可视化图表标题
CHART_TITLE = "Pancake V3 BNB-USDT (0.3%) Liquidity Distribution"
# ------------------------------------------------------------------------ #

# Pancake V3/Uniswap V3 Pool 完整ABI（题目提供的ABI，已补全）
POOL_ABI = [
    {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"int24","name":"tickLower","type":"int24"},{"indexed":True,"internalType":"int24","name":"tickUpper","type":"int24"},{"indexed":False,"internalType":"uint128","name":"amount","type":"uint128"},{"indexed":False,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Burn","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":False,"internalType":"address","name":"recipient","type":"address"},{"indexed":True,"internalType":"int24","name":"tickLower","type":"int24"},{"indexed":True,"internalType":"int24","name":"tickUpper","type":"int24"},{"indexed":False,"internalType":"uint128","name":"amount0","type":"uint128"},{"indexed":False,"internalType":"uint128","name":"amount1","type":"uint128"}],"name":"Collect","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":True,"internalType":"address","name":"recipient","type":"address"},{"indexed":False,"internalType":"uint128","name":"amount0","type":"uint128"},{"indexed":False,"internalType":"uint128","name":"amount1","type":"uint128"}],"name":"CollectProtocol","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"address","name":"recipient","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"paid0","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"paid1","type":"uint256"}],"name":"Flash","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint16","name":"observationCardinalityNextOld","type":"uint16"},{"indexed":False,"internalType":"uint16","name":"observationCardinalityNextNew","type":"uint16"}],"name":"IncreaseObservationCardinalityNext","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"},{"indexed":False,"internalType":"int24","name":"tick","type":"int24"}],"name":"Initialize","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"sender","type":"address"},{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"int24","name":"tickLower","type":"int24"},{"indexed":True,"internalType":"int24","name":"tickUpper","type":"int24"},{"indexed":False,"internalType":"uint128","name":"amount","type":"uint128"},{"indexed":False,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint32","name":"feeProtocol0Old","type":"uint32"},{"indexed":False,"internalType":"uint32","name":"feeProtocol1Old","type":"uint32"},{"indexed":False,"internalType":"uint32","name":"feeProtocol0New","type":"uint32"},{"indexed":False,"internalType":"uint32","name":"feeProtocol1New","type":"uint32"}],"name":"SetFeeProtocol","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"addr","type":"address"}],"name":"SetLmPoolEvent","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":True,"internalType":"address","name":"recipient","type":"address"},{"indexed":False,"internalType":"int256","name":"amount0","type":"int256"},{"indexed":False,"internalType":"int256","name":"amount1","type":"int256"},{"indexed":False,"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"},{"indexed":False,"internalType":"uint128","name":"liquidity","type":"uint128"},{"indexed":False,"internalType":"int24","name":"tick","type":"int24"},{"indexed":False,"internalType":"uint128","name":"protocolFeesToken0","type":"uint128"},{"indexed":False,"internalType":"uint128","name":"protocolFeesToken1","type":"uint128"}],"name":"Swap","type":"event"},
    {"inputs":[{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint128","name":"amount","type":"uint128"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint128","name":"amount0Requested","type":"uint128"},{"internalType":"uint128","name":"amount1Requested","type":"uint128"}],"name":"collect","outputs":[{"internalType":"uint128","name":"amount0","type":"uint128"},{"internalType":"uint128","name":"amount1","type":"uint128"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint128","name":"amount0Requested","type":"uint128"},{"internalType":"uint128","name":"amount1Requested","type":"uint128"}],"name":"collectProtocol","outputs":[{"internalType":"uint128","name":"amount0","type":"uint128"},{"internalType":"uint128","name":"amount1","type":"uint128"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"fee","outputs":[{"internalType":"uint24","name":"","type":"uint24"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"feeGrowthGlobal0X128","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"feeGrowthGlobal1X128","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"flash","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint16","name":"observationCardinalityNext","type":"uint16"}],"name":"increaseObservationCardinalityNext","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"liquidity","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"lmPool","outputs":[{"internalType":"contract IPancakeV3LmPool","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"maxLiquidityPerTick","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint128","name":"amount","type":"uint128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"mint","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"observations","outputs":[{"internalType":"uint32","name":"blockTimestamp","type":"uint32"},{"internalType":"int56","name":"tickCumulative","type":"int56"},{"internalType":"uint160","name":"secondsPerLiquidityCumulativeX128","type":"uint160"},{"internalType":"bool","name":"initialized","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint32[]","name":"secondsAgos","type":"uint32"}],"name":"observe","outputs":[{"internalType":"int56[]","name":"tickCumulatives","type":"int56"},{"internalType":"uint160[]","name":"secondsPerLiquidityCumulativeX128s","type":"uint160"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"positions","outputs":[{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"feeGrowthInside0LastX128","type":"uint256"},{"internalType":"uint256","name":"feeGrowthInside1LastX128","type":"uint256"},{"internalType":"uint128","name":"tokensOwed0","type":"uint128"},{"internalType":"uint128","name":"tokensOwed1","type":"uint128"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"protocolFees","outputs":[{"internalType":"uint128","name":"token0","type":"uint128"},{"internalType":"uint128","name":"token1","type":"uint128"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint32","name":"feeProtocol0","type":"uint32"},{"internalType":"uint32","name":"feeProtocol1","type":"uint32"}],"name":"setFeeProtocol","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"_lmPool","type":"address"}],"name":"setLmPool","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"slot0","outputs":[{"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"},{"internalType":"int24","name":"tick","type":"int24"},{"internalType":"uint16","name":"observationIndex","type":"uint16"},{"internalType":"uint16","name":"observationCardinality","type":"uint16"},{"internalType":"uint16","name":"observationCardinalityNext","type":"uint16"},{"internalType":"uint32","name":"feeProtocol","type":"uint32"},{"internalType":"bool","name":"unlocked","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"}],"name":"snapshotCumulativesInside","outputs":[{"internalType":"int56","name":"tickCumulativeInside","type":"int56"},{"internalType":"uint160","name":"secondsPerLiquidityInsideX128","type":"uint160"},{"internalType":"uint32","name":"secondsInside","type":"uint32"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"bool","name":"zeroForOne","type":"bool"},{"internalType":"int256","name":"amountSpecified","type":"int256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[{"internalType":"int256","name":"amount0","type":"int256"},{"internalType":"int256","name":"amount1","type":"int256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"int16","name":"","type":"int16"}],"name":"tickBitmap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"tickSpacing","outputs":[{"internalType":"int24","name":"","type":"int24"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"int24","name":"","type":"int24"}],"name":"ticks","outputs":[{"internalType":"uint128","name":"liquidityGross","type":"uint128"},{"internalType":"int128","name":"liquidityNet","type":"int128"},{"internalType":"uint256","name":"feeGrowthOutside0X128","type":"uint256"},{"internalType":"uint256","name":"feeGrowthOutside1X128","type":"uint256"},{"internalType":"int56","name":"tickCumulativeOutside","type":"int56"},{"internalType":"uint160","name":"secondsPerLiquidityOutsideX128","type":"uint160"},{"internalType":"uint32","name":"secondsOutside","type":"uint32"},{"internalType":"bool","name":"initialized","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]

# -------------------- 核心工具函数 -------------------- #
def connect_web3(rpc_url):
    """连接BSC网络，返回web3实例"""
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError("无法连接BSC节点，请检查RPC地址是否有效")
    return w3

def get_pool_basic_info(w3, pool_addr, pool_abi):
    """获取Pool基础信息：当前Tick、Tick间隔、token0/token1地址"""
    pool_contract = w3.eth.contract(address=Web3.to_checksum_address(pool_addr), abi=pool_abi)
    slot0 = pool_contract.functions.slot0().call()  # slot0包含当前Tick和价格
    current_tick = slot0[1]  # 索引1是当前Tick
    tick_spacing = pool_contract.functions.tickSpacing().call()  # Tick间隔（如0.3%费率池间隔为60）
    token0_addr = pool_contract.functions.token0().call()
    token1_addr = pool_contract.functions.token1().call()
    return {
        "contract": pool_contract,
        "current_tick": current_tick,
        "tick_spacing": tick_spacing,
        "token0": token0_addr,
        "token1": token1_addr
    }

def tick_to_price(tick, token0_decimals=18, token1_decimals=18):
    """将V3的Tick转换为价格（price = token1 / token0）"""
    # V3 Tick公式：price = 1.0001^tick，需处理小数位数
    price = pow(1.0001, tick)
    # 调整token小数位数（默认18位，可根据实际token修改）
    price = price * (10 ** (token0_decimals - token1_decimals))
    return price

def get_tick_liquidity(pool_contract, start_tick, end_tick, tick_spacing):
    """获取指定Tick范围内的流动性数据（累计流动性）"""
    ticks = []  # 存储有效Tick
    liquidity_cumulative = []  # 存储累计流动性
    current_liquidity = 0  # 初始流动性为0

    # 按Tick间隔遍历（V3池只在间隔Tick上有流动性数据）
    for tick in range(start_tick, end_tick + tick_spacing, tick_spacing):
        try:
            # 读取当前Tick的流动性数据
            tick_data = pool_contract.functions.ticks(tick).call()
            liquidity_net = tick_data[1]  # 索引1是流动性净变化（+增加/-减少）
            is_initialized = tick_data[7]  # 索引7是Tick是否初始化（是否有流动性）
            
            # 只有初始化的Tick才会影响流动性累计
            if is_initialized:
                current_liquidity += liquidity_net  # 累计流动性 = 上一轮累计 + 当前净变化
                ticks.append(tick)
                liquidity_cumulative.append(current_liquidity)
        except Exception as e:
            # 忽略无效Tick（如未初始化的Tick）
            continue
    
    return ticks, liquidity_cumulative

def visualize_liquidity(ticks, liquidity_cumulative, current_tick, chart_title):
    """用matplotlib绘制流动性分布图"""
    # 将Tick转换为价格（默认token0/token1为18位小数，可根据实际修改）
    prices = [tick_to_price(tick) for tick in ticks]
    # 对流动性进行归一化（便于可视化，避免数值过大）
    max_liquidity = max(liquidity_cumulative) if liquidity_cumulative else 1
    normalized_liquidity = [liq / max_liquidity for liq in liquidity_cumulative]

    # 设置图表样式
    plt.rcParams['figure.figsize'] = (12, 8)
    fig, ax = plt.subplots()

    # 绘制流动性分布曲线（蓝色实线）
    ax.plot(prices, normalized_liquidity, color='#1f77b4', linewidth=2.5, label='Normalized Liquidity')
    # 标记当前价格对应的Tick（红色竖线）
    current_price = tick_to_price(current_tick)
    ax.axvline(x=current_price, color='#ff7f0e', linestyle='--', linewidth=2, label=f'Current Price: {current_price:.4f}')

    # 设置坐标轴标签和标题
    ax.set_xlabel('Price (Token1 / Token0)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Liquidity', fontsize=12, fontweight='bold')
    ax.set_title(chart_title, fontsize=14, fontweight='bold', pad=20)
    # 设置x轴为对数刻度（V3价格范围广，对数刻度更易读）
    ax.set_xscale('log')
    # 添加网格和图例
    ax.grid(True, alpha=0.3, linestyle='-')
    ax.legend(fontsize=10, loc='upper right')

    # 调整布局并显示
    plt.tight_layout()
    plt.show()

# -------------------- 主程序入口 -------------------- #
if __name__ == "__main__":
    try:
        # 1. 连接BSC网络
        w3 = connect_web3(BSC_RPC)
        print(f"✅ 成功连接BSC网络，当前区块高度：{w3.eth.block_number}")

        # 2. 获取Pool基础信息
        pool_info = get_pool_basic_info(w3, POOL_ADDRESS, POOL_ABI)
        current_tick = pool_info["current_tick"]
        tick_spacing = pool_info["tick_spacing"]
        token0 = pool_info["token0"]
        token1 = pool_info["token1"]
        print(f"✅ Pool信息：\n- 当前Tick: {current_tick}\n- Tick间隔: {tick_spacing}\n- Token0: {token0}\n- Token1: {token1}")

        # 3. 计算要查询的Tick范围（当前Tick ± TICK_RANGE）
        start_tick = current_tick - TICK_RANGE
        end_tick = current_tick + TICK_RANGE
        print(f"✅ 查询Tick范围：{start_tick} ~ {end_tick}")

        # 4. 获取Tick流动性数据
        ticks, liquidity = get_tick_liquidity(
            pool_contract=pool_info["contract"],
            start_tick=start_tick,
            end_tick=end_tick,
            tick_spacing=tick_spacing
        )
        if not ticks:
            raise ValueError("未查询到任何流动性数据，请检查Pool地址或扩大Tick范围")
        print(f"✅ 成功获取 {len(ticks)} 个有效Tick的流动性数据")

        # 5. 可视化流动性分布
        visualize_liquidity(
            ticks=ticks,
            liquidity_cumulative=liquidity,
            current_tick=current_tick,
            chart_title=CHART_TITLE
        )

    except Exception as e:
        print(f"❌ 程序出错：{str(e)}")
