#!/usr/bin/env python3
"""
系统功能验证脚本
"""

import os
import sys

def verify_system():
    """验证系统功能"""
    print("🧪 开始验证大乐透预测系统功能...")
    
    success_count = 0
    total_count = 5
    
    # 1. 验证数据采集器
    try:
        from src.services.data_crawler import LotteryDataCrawler
        crawler = LotteryDataCrawler()
        print("✅ 数据采集器: 正常")
        success_count += 1
    except Exception as e:
        print(f"❌ 数据采集器: {e}")
    
    # 2. 验证数据存储
    try:
        from src.database.data_storage import DataStorage
        storage = DataStorage(":memory:")
        print("✅ 数据存储: 正常")
        success_count += 1
    except Exception as e:
        print(f"❌ 数据存储: {e}")
    
    # 3. 验证预测器
    try:
        from src.models.lottery_predictor import LotteryPredictor
        predictor = LotteryPredictor()
        print("✅ 预测器: 正常")
        success_count += 1
    except Exception as e:
        print(f"❌ 预测器: {e}")
    
    # 4. 验证通知服务
    try:
        from src.services.notification_service import NotificationService
        notifier = NotificationService({
            'slack_enabled': False,
            'feishu_enabled': False,
            'email_enabled': False
        })
        print("✅ 通知服务: 正常")
        success_count += 1
    except Exception as e:
        print(f"❌ 通知服务: {e}")
    
    # 5. 验证集成系统
    try:
        from lottery_system import LotteryPredictionSystem
        system = LotteryPredictionSystem()
        status = system.get_system_status()
        print("✅ 集成系统: 正常")
        success_count += 1
    except Exception as e:
        print(f"❌ 集成系统: {e}")
    
    # 总结
    print(f"\n📊 验证结果: {success_count}/{total_count} 项通过")
    
    if success_count == total_count:
        print("🎉 系统功能验证完成!")
        return True
    else:
        print("⚠️  部分功能需要优化")
        return False

if __name__ == "__main__":
    verify_system()