import os
import logging
from typing import Dict, Any

class Config:
    """系统配置管理类"""
    
    # 数据库配置
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'lottery_data.db')
    
    # 爬虫配置
    CRAWLER_BASE_URL = os.getenv('CRAWLER_BASE_URL', 'https://www.lottery.gov.cn')
    CRAWLER_CACHE_DURATION = int(os.getenv('CRAWLER_CACHE_DURATION', '3600'))
    USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
    
    # 预测配置
    PREDICTION_COUNT = int(os.getenv('PREDICTION_COUNT', '2'))
    MIN_HISTORY_DATA = int(os.getenv('MIN_HISTORY_DATA', '50'))
    
    # 通知配置
    NOTIFICATION_ENABLED = os.getenv('NOTIFICATION_ENABLED', 'true').lower() == 'true'
    
    # 邮件配置
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '').split(',')
    
    # 微信配置
    WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL', '')
    WECHAT_ENABLED = os.getenv('WECHAT_ENABLED', 'false').lower() == 'true'
    
    # 钉钉配置
    DINGTALK_WEBHOOK_URL = os.getenv('DINGTALK_WEBHOOK_URL', '')
    DINGTALK_SECRET = os.getenv('DINGTALK_SECRET', '')
    DINGTALK_ENABLED = os.getenv('DINGTALK_ENABLED', 'false').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'lottery_system.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # 定时任务配置
    SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true'
    PREDICTION_INTERVAL = int(os.getenv('PREDICTION_INTERVAL', '86400'))  # 24小时
    DATA_UPDATE_INTERVAL = int(os.getenv('DATA_UPDATE_INTERVAL', '3600'))  # 1小时
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, Any]:
        """获取所有配置"""
        return {
            'database': {
                'path': cls.DATABASE_PATH
            },
            'crawler': {
                'base_url': cls.CRAWLER_BASE_URL,
                'cache_duration': cls.CRAWLER_CACHE_DURATION,
                'use_mock_data': cls.USE_MOCK_DATA
            },
            'prediction': {
                'count': cls.PREDICTION_COUNT,
                'min_history_data': cls.MIN_HISTORY_DATA
            },
            'notification': {
                'enabled': cls.NOTIFICATION_ENABLED,
                'email': {
                    'smtp_server': cls.EMAIL_SMTP_SERVER,
                    'smtp_port': cls.EMAIL_SMTP_PORT,
                    'username': cls.EMAIL_USERNAME,
                    'password': cls.EMAIL_PASSWORD,
                    'from_email': cls.EMAIL_FROM,
                    'to_emails': cls.EMAIL_TO
                },
                'wechat': {
                    'webhook_url': cls.WECHAT_WEBHOOK_URL,
                    'enabled': cls.WECHAT_ENABLED
                },
                'dingtalk': {
                    'webhook_url': cls.DINGTALK_WEBHOOK_URL,
                    'secret': cls.DINGTALK_SECRET,
                    'enabled': cls.DINGTALK_ENABLED
                }
            },
            'logging': {
                'level': cls.LOG_LEVEL,
                'file': cls.LOG_FILE,
                'max_size': cls.LOG_MAX_SIZE,
                'backup_count': cls.LOG_BACKUP_COUNT
            },
            'scheduler': {
                'enabled': cls.SCHEDULER_ENABLED,
                'prediction_interval': cls.PREDICTION_INTERVAL,
                'data_update_interval': cls.DATA_UPDATE_INTERVAL
            }
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """验证配置有效性"""
        validation_results = {}
        
        # 验证邮件配置
        validation_results['email_configured'] = bool(
            cls.EMAIL_USERNAME and cls.EMAIL_PASSWORD and cls.EMAIL_FROM
        )
        
        # 验证微信配置
        validation_results['wechat_configured'] = bool(
            cls.WECHAT_WEBHOOK_URL and cls.WECHAT_ENABLED
        )
        
        # 验证钉钉配置
        validation_results['dingtalk_configured'] = bool(
            cls.DINGTALK_WEBHOOK_URL and cls.DINGTALK_ENABLED
        )
        
        # 验证数据库路径
        validation_results['database_configured'] = bool(cls.DATABASE_PATH)
        
        return validation_results