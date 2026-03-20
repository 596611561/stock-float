# Stock Float - 股价悬浮窗

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

在 Windows 任务栏上方显示实时股价的悬浮小工具。

## 功能特性

- 📊 实时显示股价和涨跌幅
- 🔄 自动刷新（默认 30 秒，可配置）
- 🎨 红涨绿跌配色（符合A股习惯）
- 🖱️ 鼠标滚轮上下滚动切换股票
- 🔧 支持自定义股票列表
- 🌐 支持 A股、美股、港股、加密货币

## 界面预览

悬浮窗显示效果：
- 股票名称（大红色=涨，绿色=跌）
- 当前价格（大字体）
- 涨跌幅百分比

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/596611561/stock-float.git
cd stock-float
```

### 2. 安装依赖

```bash
pip install requests pywin32
```

### 3. 运行程序

```bash
python stock_float.py
```

程序会在屏幕左下角（任务栏上方）显示一个悬浮窗。

## 配置说明

编辑 `stock_config.json` 文件自定义股票列表：

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
| 美股 | 直接写代码 | `AAPL`, `TSLA`, `NVDA` |
| 港股 | 直接写代码 | `00700` |
| 加密货币 | `代码-USD` | `BTC-USD`, `ETH-USD` |

### 参数说明

- `stocks`: 股票列表，可添加任意数量
- `refresh_interval`: 刷新间隔，单位秒，默认 30 秒
- 修改配置后需重启程序

## 使用方法

| 操作 | 效果 |
|------|------|
| 鼠标滚轮向上 | 切换到上一只股票 |
| 鼠标滚轮向下 | 切换到下一只股票 |
| 右键点击 | 弹出菜单（刷新/切换/退出） |
| 拖动窗口 | 自由移动悬浮窗位置 |

## 数据来源

- A股：新浪财经接口
- 美股/港股/加密：腾讯财经接口

## 环境要求

- Windows 系统
- Python 3.8 或更高版本

## 依赖库

```
requests    # HTTP 请求
pywin32     # Windows API 调用
```

## 常见问题

**Q: 启动报错 "ModuleNotFoundError"**
A: 请运行 `pip install requests pywin32` 安装依赖

**Q: 显示"无数据"**
A: 检查网络连接，或者股票代码是否正确

**Q: 想开机自启**
A: 把 `python stock_float.py` 的快捷方式放到开始菜单的启动文件夹

## 开源协议

MIT License

---

有问题欢迎提交 Issue！
