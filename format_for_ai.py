"""
将财报数据格式化为AI友好的格式
减少token消耗，提高AI理解能力
"""

def format_number(value):
    """将大数字转换为易读格式"""
    if value is None or value == "-":
        return "-"
    try:
        value = float(value)
        if abs(value) >= 100000000:  # 亿
            return f"{value/100000000:.2f}亿"
        elif abs(value) >= 10000:  # 万
            return f"{value/10000:.2f}万"
        else:
            return f"{value:.2f}"
    except:
        return str(value)


def calculate_key_metrics(financial_data):
    """计算核心财务指标"""
    try:
        # 获取最新季度数据
        latest_balance = financial_data['balance_sheet'][0] if financial_data['balance_sheet'] else {}
        latest_income = financial_data['income_statement'][0] if financial_data['income_statement'] else {}
        latest_cashflow = financial_data['cash_flow'][0] if financial_data['cash_flow'] else {}
        
        # 获取去年同期数据（用于同比计算）
        yoy_income = financial_data['income_statement'][4] if len(financial_data['income_statement']) > 4 else {}
        
        metrics = {}
        
        # 1. 规模指标
        if 'TOTAL_ASSETS' in latest_balance:
            metrics['总资产'] = format_number(latest_balance['TOTAL_ASSETS'])
        
        if 'OPERATE_INCOME' in latest_income:
            metrics['营业收入'] = format_number(latest_income['OPERATE_INCOME'])
            
        if 'PARENT_NETPROFIT' in latest_income:
            metrics['归母净利润'] = format_number(latest_income['PARENT_NETPROFIT'])
        
        # 2. 盈利能力
        if 'OPERATE_INCOME' in latest_income and 'OPERATE_COST' in latest_income:
            try:
                revenue = float(latest_income['OPERATE_INCOME'])
                cost = float(latest_income['OPERATE_COST'])
                if revenue > 0:
                    metrics['毛利率'] = f"{(revenue - cost) / revenue * 100:.2f}%"
            except:
                pass
        
        if 'PARENT_NETPROFIT' in latest_income and 'OPERATE_INCOME' in latest_income:
            try:
                profit = float(latest_income['PARENT_NETPROFIT'])
                revenue = float(latest_income['OPERATE_INCOME'])
                if revenue > 0:
                    metrics['净利率'] = f"{profit / revenue * 100:.2f}%"
            except:
                pass
        
        if 'PARENT_NETPROFIT' in latest_income and 'TOTAL_EQUITY' in latest_balance:
            try:
                profit = float(latest_income['PARENT_NETPROFIT'])
                equity = float(latest_balance['TOTAL_EQUITY'])
                if equity > 0:
                    # 注意：这里是单季度净利润，年化需要×4（如果是季报）
                    metrics['ROE_单季'] = f"{profit / equity * 100:.2f}%"
            except:
                pass
        
        # 3. 偿债能力
        if 'TOTAL_LIABILITIES' in latest_balance and 'TOTAL_ASSETS' in latest_balance:
            try:
                liab = float(latest_balance['TOTAL_LIABILITIES'])
                assets = float(latest_balance['TOTAL_ASSETS'])
                if assets > 0:
                    metrics['资产负债率'] = f"{liab / assets * 100:.2f}%"
            except:
                pass
        
        if 'MONETARYFUNDS' in latest_balance and 'TOTAL_ASSETS' in latest_balance:
            try:
                cash = float(latest_balance['MONETARYFUNDS'])
                assets = float(latest_balance['TOTAL_ASSETS'])
                if assets > 0:
                    metrics['现金占比'] = f"{cash / assets * 100:.2f}%"
            except:
                pass
        
        # 4. 增长能力
        if 'OPERATE_INCOME' in latest_income and 'OPERATE_INCOME' in yoy_income:
            try:
                current = float(latest_income['OPERATE_INCOME'])
                last_year = float(yoy_income['OPERATE_INCOME'])
                if last_year > 0:
                    metrics['营收同比增长'] = f"{(current - last_year) / last_year * 100:.2f}%"
            except:
                pass
        
        if 'PARENT_NETPROFIT' in latest_income and 'PARENT_NETPROFIT' in yoy_income:
            try:
                current = float(latest_income['PARENT_NETPROFIT'])
                last_year = float(yoy_income['PARENT_NETPROFIT'])
                if last_year > 0:
                    metrics['利润同比增长'] = f"{(current - last_year) / last_year * 100:.2f}%"
            except:
                pass
        
        # 5. 现金流
        if 'NETCASH_OPERATE' in latest_cashflow:
            metrics['经营现金流'] = format_number(latest_cashflow['NETCASH_OPERATE'])
        
        if 'NETCASH_OPERATE' in latest_cashflow and 'PARENT_NETPROFIT' in latest_income:
            try:
                ocf = float(latest_cashflow['NETCASH_OPERATE'])
                profit = float(latest_income['PARENT_NETPROFIT'])
                if profit > 0:
                    metrics['现金流/净利润'] = f"{ocf / profit:.2f}"
            except:
                pass
        
        return metrics
    except Exception as e:
        print(f"计算指标出错: {e}")
        return {}


def format_for_ai_summary(stock_info, financial_data):
    """
    生成AI分析摘要（Level 1）
    最精简，最易读，最适合AI快速理解
    """
    
    report_date = financial_data['balance_sheet'][0].get('REPORT_DATE', '未知') if financial_data['balance_sheet'] else '未知'
    
    summary = f"""
# {stock_info['name']}（{stock_info['code']}）财务分析摘要

**最新报告期**: {report_date}

## 核心指标

"""
    
    metrics = calculate_key_metrics(financial_data)
    
    if metrics:
        summary += "### 规模\n"
        for key in ['总资产', '营业收入', '归母净利润']:
            if key in metrics:
                summary += f"- {key}: {metrics[key]}\n"
        
        summary += "\n### 盈利能力\n"
        for key in ['毛利率', '净利率', 'ROE_单季']:
            if key in metrics:
                summary += f"- {key}: {metrics[key]}\n"
        
        summary += "\n### 财务健康\n"
        for key in ['资产负债率', '现金占比']:
            if key in metrics:
                summary += f"- {key}: {metrics[key]}\n"
        
        summary += "\n### 增长性\n"
        for key in ['营收同比增长', '利润同比增长']:
            if key in metrics:
                summary += f"- {key}: {metrics[key]}\n"
        
        summary += "\n### 现金流\n"
        for key in ['经营现金流', '现金流/净利润']:
            if key in metrics:
                summary += f"- {key}: {metrics[key]}\n"
    
    return summary


def format_for_ai_detailed(financial_data, periods=3):
    """
    生成AI分析详细数据（Level 2）
    包含最近N个季度的趋势数据
    """
    
    output = "\n## 趋势数据（最近3个季度）\n\n"
    
    # 资产负债表趋势
    output += "### 资产负债表\n\n"
    output += "| 日期 | 总资产 | 总负债 | 股东权益 | 货币资金 | 负债率 |\n"
    output += "|------|--------|--------|----------|----------|--------|\n"
    
    for i in range(min(periods, len(financial_data['balance_sheet']))):
        item = financial_data['balance_sheet'][i]
        date = str(item.get('REPORT_DATE', '-'))[:10]
        assets = format_number(item.get('TOTAL_ASSETS'))
        liab = format_number(item.get('TOTAL_LIABILITIES'))
        equity = format_number(item.get('TOTAL_EQUITY'))
        cash = format_number(item.get('MONETARYFUNDS'))
        
        # 计算负债率
        debt_ratio = "-"
        try:
            if item.get('TOTAL_ASSETS') and item.get('TOTAL_LIABILITIES'):
                debt_ratio = f"{float(item['TOTAL_LIABILITIES']) / float(item['TOTAL_ASSETS']) * 100:.1f}%"
        except:
            pass
        
        output += f"| {date} | {assets} | {liab} | {equity} | {cash} | {debt_ratio} |\n"
    
    # 利润表趋势
    output += "\n### 利润表\n\n"
    output += "| 日期 | 营业收入 | 营业成本 | 净利润 | 毛利率 | 净利率 |\n"
    output += "|------|----------|----------|--------|--------|--------|\n"
    
    for i in range(min(periods, len(financial_data['income_statement']))):
        item = financial_data['income_statement'][i]
        date = str(item.get('REPORT_DATE', '-'))[:10]
        revenue = format_number(item.get('OPERATE_INCOME'))
        cost = format_number(item.get('OPERATE_COST'))
        profit = format_number(item.get('PARENT_NETPROFIT'))
        
        # 计算毛利率和净利率
        gross_margin = "-"
        net_margin = "-"
        try:
            if item.get('OPERATE_INCOME') and item.get('OPERATE_COST'):
                rev = float(item['OPERATE_INCOME'])
                cst = float(item['OPERATE_COST'])
                if rev > 0:
                    gross_margin = f"{(rev - cst) / rev * 100:.1f}%"
            
            if item.get('PARENT_NETPROFIT') and item.get('OPERATE_INCOME'):
                pft = float(item['PARENT_NETPROFIT'])
                rev = float(item['OPERATE_INCOME'])
                if rev > 0:
                    net_margin = f"{pft / rev * 100:.1f}%"
        except:
            pass
        
        output += f"| {date} | {revenue} | {cost} | {profit} | {gross_margin} | {net_margin} |\n"
    
    # 现金流趋势
    output += "\n### 现金流量表\n\n"
    output += "| 日期 | 经营现金流 | 投资现金流 | 筹资现金流 |\n"
    output += "|------|------------|------------|------------|\n"
    
    for i in range(min(periods, len(financial_data['cash_flow']))):
        item = financial_data['cash_flow'][i]
        date = str(item.get('REPORT_DATE', '-'))[:10]
        ocf = format_number(item.get('NETCASH_OPERATE'))
        icf = format_number(item.get('NETCASH_INVEST'))
        fcf = format_number(item.get('NETCASH_FINANCE'))
        
        output += f"| {date} | {ocf} | {icf} | {fcf} |\n"
    
    return output


# 示例使用
if __name__ == "__main__":
    # 模拟数据
    stock_info = {
        "code": "600585",
        "name": "海螺水泥",
        "symbol": "SH600585",
        "market": "A"
    }
    
    # 这里需要从API获取真实数据
    print("请配合 main.py 使用，获取真实财报数据")
