#!/usr/bin/env python3
"""
大乐透预测自动化系统 - 主系统入口
集成数据采集、预测分析、通知服务的完整工作流
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.data_crawler import LotteryDataCrawler
from src.database.data_storage import DataStorage
from src.models.lottery_predictor import LotteryPredictor
from src.services.notification_service import NotificationService
from src.services.system_monitor import SystemMonitor
from src.utils.error_logger import ErrorLogger
from src.utils.config import Config

class LotteryPredictionSystem:
    """
    大乐透预测自动化系统主类
    集成所有功能模块，提供统一的操作接口
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化系统
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self.logger = ErrorLogger()
        self.system_monitor = SystemMonitor()
        
        # 初始化各个组件
        self.data_crawler = None
        self.data_storage = None
        self.data_analyzer = None
        self.predictor = None
        self.notification_service = None
        
        # 系统状态
        self.initialized = False
        self.last_run_time = None
        self.run_count = 0
    
    def initialize(self) -> bool:
        """
        初始化系统各个组件
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.log_info("开始初始化大乐透预测系统...")
            
            # 初始化数据存储
            self.data_storage = DataStorage(self.config.database.path)
            
            # 初始化数据采集器
            self.data_crawler = LotteryDataCrawler()
            
            # 初始化预测器
            self.predictor = LotteryPredictor()
            
            # 初始化通知服务
            self.notification_service = NotificationService(self.config.notifications)
            
            self.initialized = True
            self.system_monitor.record_system_event("system_initialized", "系统初始化成功")
            
            self.logger.log_info("系统初始化完成")
            return True
            
        except Exception as e:
            error_msg = f"系统初始化失败: {str(e)}"
            self.logger.log_error(error_msg)
            self.system_monitor.record_system_event("system_error", error_msg)
            return False
    
    async def run_data_collection(self) -> bool:
        """
        运行数据采集流程
        
        Returns:
            bool: 数据采集是否成功
        """
        if not self.initialized:
            self.logger.log_error("系统未初始化，无法运行数据采集")
            return False
        
        try:
            self.logger.log_info("开始数据采集...")
            
            # 获取最新开奖数据
            latest_data = await self.data_crawler.fetch_latest_data()
            
            if latest_data:
                # 保存数据到数据库
                for record in latest_data:
                    self.data_storage.insert_lottery_record(record)
                
                self.logger.log_info(f"成功采集并保存 {len(latest_data)} 条开奖记录")
                self.system_monitor.record_system_event(
                    "data_collected", 
                    f"采集了 {len(latest_data)} 条记录"
                )
                return True
            else:
                self.logger.log_warning("未获取到新的开奖数据")
                return False
                
        except Exception as e:
            error_msg = f"数据采集失败: {str(e)}"
            self.logger.log_error(error_msg)
            self.system_monitor.record_system_event("data_collection_error", error_msg)
            return False
    
    async def run_prediction_analysis(self) -> Optional[Dict[str, Any]]:
        """
        运行预测分析
        
        Returns:
            dict: 预测结果，失败返回None
        """
        if not self.initialized:
            self.logger.log_error("系统未初始化，无法运行预测分析")
            return None
        
        try:
            self.logger.log_info("开始预测分析...")
            
            # 获取历史数据
            historical_data = self.data_storage.get_latest_records(limit=100)
            
            if not historical_data:
                self.logger.log_warning("没有足够的历史数据进行预测")
                return None
            
            # 运行预测
            prediction_result = self.predictor.predict_next_numbers(historical_data)
            
            if prediction_result:
                self.logger.log_info("预测分析完成")
                self.system_monitor.record_system_event(
                    "prediction_completed", 
                    f"生成了预测结果: {prediction_result}"
                )
                return prediction_result
            else:
                self.logger.log_warning("预测分析未能生成结果")
                return None
                
        except Exception as e:
            error_msg = f"预测分析失败: {str(e)}"
            self.logger.log_error(error_msg)
            self.system_monitor.record_system_event("prediction_error", error_msg)
            return None
    
    async def send_notifications(self, prediction_result: Dict[str, Any]) -> bool:
        """
        发送预测结果通知
        
        Args:
            prediction_result: 预测结果
            
        Returns:
            bool: 通知是否成功发送
        """
        if not self.initialized:
            self.logger.log_error("系统未初始化，无法发送通知")
            return False
        
        try:
            self.logger.log_info("开始发送通知...")
            
            # 构建通知消息
            message = self._build_notification_message(prediction_result)
            
            # 发送通知
            success = await self.notification_service.send_notification(
                title="大乐透预测结果",
                message=message,
                level="info"
            )
            
            if success:
                self.logger.log_info("通知发送成功")
                self.system_monitor.record_system_event("notification_sent", "预测结果通知已发送")
            else:
                self.logger.log_warning("通知发送失败")
            
            return success
            
        except Exception as e:
            error_msg = f"通知发送失败: {str(e)}"
            self.logger.log_error(error_msg)
            self.system_monitor.record_system_event("notification_error", error_msg)
            return False
    
    def _build_notification_message(self, prediction_result: Dict[str, Any]) -> str:
        """构建通知消息内容"""
        front_numbers = prediction_result.get('front_numbers', [])
        back_numbers = prediction_result.get('back_numbers', [])
        confidence = prediction_result.get('confidence', 0)
        
        message = f"""
🔮 大乐透最新预测结果

前区推荐号码: {', '.join(map(str, front_numbers))}
后区推荐号码: {', '.join(map(str, back_numbers))}

预测置信度: {confidence:.2f}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ 温馨提示：彩票预测仅供参考，请理性投注
"""
        return message.strip()
    
    async def run_full_workflow(self) -> bool:
        """
        运行完整的工作流程
        
        Returns:
            bool: 整个流程是否成功
        """
        try:
            self.logger.log_info("开始运行完整工作流...")
            
            # 1. 数据采集
            collection_success = await self.run_data_collection()
            
            # 2. 预测分析
            prediction_result = await self.run_prediction_analysis()
            
            # 3. 发送通知（如果有预测结果）
            if prediction_result:
                notification_success = await self.send_notifications(prediction_result)
            else:
                notification_success = False
            
            # 更新运行统计
            self.last_run_time = datetime.now()
            self.run_count += 1
            
            # 记录工作流完成情况
            self.system_monitor.record_system_event(
                "workflow_completed", 
                f"工作流完成，采集: {collection_success}, 预测: {bool(prediction_result)}, 通知: {notification_success}"
            )
            
            success = collection_success and bool(prediction_result) and notification_success
            self.logger.log_info(f"完整工作流运行完成，状态: {'成功' if success else '部分成功'}")
            
            return success
            
        except Exception as e:
            error_msg = f"工作流运行失败: {str(e)}"
            self.logger.log_error(error_msg)
            self.system_monitor.record_system_event("workflow_error", error_msg)
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            dict: 系统状态信息
        """
        return {
            "initialized": self.initialized,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "run_count": self.run_count,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "data_crawler": bool(self.data_crawler),
                "data_storage": bool(self.data_storage),
                "predictor": bool(self.predictor),
                "notification_service": bool(self.notification_service)
            }
        }
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.data_storage:
                self.data_storage.close()
            
            self.logger.log_info("系统资源清理完成")
            self.system_monitor.record_system_event("system_cleanup", "系统资源已清理")
            
        except Exception as e:
            self.logger.log_error(f"清理资源时出错: {str(e)}")

async def main():
    """主函数 - 用于直接运行系统"""
    system = LotteryPredictionSystem()
    
    try:
        # 初始化系统
        if system.initialize():
            # 运行完整工作流
            success = await system.run_full_workflow()
            
            if success:
                print("🎉 大乐透预测系统运行成功！")
            else:
                print("⚠️  系统运行完成，但部分功能可能未成功")
        else:
            print("❌ 系统初始化失败")
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断运行")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")
    finally:
        system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())