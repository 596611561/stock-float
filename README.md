# Stock Float - 股价悬浮窗

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

在 Windows 任务栏上方显示实时股价的悬浮小工具。

## 功能 Features

- 📊 实时显示股价和涨跌幅
- 🔄 自动刷新（默认 30 秒）
- 🎨 红涨绿跌配色（A股习惯）
- 🖱️ 鼠标滚轮切换股票
- 🔧 支持自定义股票列表
- 🌐 支持 A股、美股、加密货币

## 截图 Screenshots

悬浮窗显示效果：
- 左侧：股票名称
- 中间：当前价格（大字体）
- 右侧：涨跌幅（红涨绿跌）

## 安装 Installation

1. 克隆仓库：
```bash
git clone https://github.com/596611561/stock-float.git
cd stock-float
```

2. 安装依赖：
```bash
pip install requests pywin32
```

3. 运行：
```bash
python stock_float.py
```

## 配置 Configuration

编辑 `stock_config.json` 自定义股票：

```json
{
  "stocks": [
    {"symbol": "300274.SZ", "name": "阳光电源"},
    {"symbol": "600519.SS", "name": "贵州茅台"},
    {"symbol": "AAPL", "name": "苹果"},
    {"symbol": "TSLA", "name": "特斯拉"},
    {"symbol": "BTC-USD", "name": "比特币"}
  ],
  "refresh_interval": 30
}
```

### 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| A股 上交所 | `代码.SS` | `600519.SS` |
| A股 深交所 | `代码.SZ` | `000858.SZ` |
| 美股 | 直接写代码 | `AAPL`, `TSLA` |
| 加密货币 | `代码-USD` | `BTC-USD`, `ETH-USD` |

## 使用说明 Usage

| 操作 | 效果 |
|------|------|
| 鼠标滚轮 | 切换显示的股票 |
| 右键菜单 | 刷新 / 切换 / 退出 |
| 拖动 | 移动悬浮窗位置 |

## 依赖 Dependencies

- Python 3.8+
- requests
- pywin32

##  License

MIT License
