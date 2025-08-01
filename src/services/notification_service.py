import smtplib
import json
import logging
import os
import requests
from typing import List, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NotificationService:
    """通知服务类 - 支持邮件、微信、钉钉通知"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_config = self._load_email_config()
        self.wechat_config = self._load_wechat_config()
        self.dingtalk_config = self._load_dingtalk_config()
    
    def _load_email_config(self) -> Dict:
        """加载邮件配置"""
        return {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('EMAIL_FROM', ''),
            'to_emails': os.getenv('EMAIL_TO', '').split(',')
        }
    
    def _load_wechat_config(self) -> Dict:
        """加载微信配置"""
        return {
            'webhook_url': os.getenv('WECHAT_WEBHOOK_URL', ''),
            'enabled': os.getenv('WECHAT_ENABLED', 'false').lower() == 'true'
        }
    
    def _load_dingtalk_config(self) -> Dict:
        """加载钉钉配置"""
        return {
            'webhook_url': os.getenv('DINGTALK_WEBHOOK_URL', ''),
            'secret': os.getenv('DINGTALK_SECRET', ''),
            'enabled': os.getenv('DINGTALK_ENABLED', 'false').lower() == 'true'
        }
    
    def send_email(self, subject: str, content: str, html: bool = False) -> bool:
        """发送邮件通知"""
        try:
            if not self.email_config['username'] or not self.email_config['password']:
                self.logger.warning("邮件配置不完整，跳过邮件通知")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(content, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
            return False
    
    def send_wechat(self, message: str) -> bool:
        """发送微信通知"""
        try:
            if not self.wechat_config['enabled'] or not self.wechat_config['webhook_url']:
                self.logger.warning("微信配置未启用或配置不完整")
                return False
            
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(
                self.wechat_config['webhook_url'],
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.logger.info("微信通知发送成功")
                    return True
                else:
                    self.logger.error(f"微信API返回错误: {result}")
                    return False
            else:
                self.logger.error(f"微信通知请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"微信通知发送失败: {e}")
            return False
    
    def send_dingtalk(self, message: str) -> bool:
        """发送钉钉通知"""
        try:
            if not self.dingtalk_config['enabled'] or not self.dingtalk_config['webhook_url']:
                self.logger.warning("钉钉配置未启用或配置不完整")
                return False
            
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(
                self.dingtalk_config['webhook_url'],
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.logger.info("钉钉通知发送成功")
                    return True
                else:
                    self.logger.error(f"钉钉API返回错误: {result}")
                    return False
            else:
                self.logger.error(f"钉钉通知请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"钉钉通知发送失败: {e}")
            return False
    
    def send_prediction_notification(self, predictions: List[Dict], analysis_result: Dict) -> Dict[str, bool]:
        """发送预测结果通知"""
        try:
            # 构建通知内容
            notification_content = self._build_prediction_message(predictions, analysis_result)
            
            results = {
                'email': False,
                'wechat': False,
                'dingtalk': False
            }
            
            # 发送邮件
            results['email'] = self.send_email(
                f"大乐透预测结果 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                notification_content
            )
            
            # 发送微信
            results['wechat'] = self.send_wechat(notification_content)
            
            # 发送钉钉
            results['dingtalk'] = self.send_dingtalk(notification_content)
            
            return results
            
        except Exception as e:
            self.logger.error(f"发送预测通知失败: {e}")
            return {'email': False, 'wechat': False, 'dingtalk': False}
    
    def _build_prediction_message(self, predictions: List[Dict], analysis_result: Dict) -> str:
        """构建预测消息内容"""
        message_parts = []
        
        message_parts.append("📊 大乐透智能预测结果")
        message_parts.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        message_parts.append("")
        
        # 添加分析统计
        data_count = analysis_result.get('data_count', 0)
        message_parts.append(f"📈 分析数据: {data_count} 期历史数据")
        
        # 添加预测结果
        for i, pred in enumerate(predictions, 1):
            front = pred.get('front_zone', [])
            back = pred.get('back_zone', [])
            confidence = pred.get('confidence', 0)
            
            message_parts.append(f"\n🔮 预测方案 {i}:")
            message_parts.append(f"前区: {' '.join(map(str, front))}")
            message_parts.append(f"后区: {' '.join(map(str, back))}")
            message_parts.append(f"置信度: {confidence:.2%}")
        
        message_parts.append("")
        message_parts.append("⚠️ 温馨提示：")
        message_parts.append("• 彩票有风险，购买需谨慎")
        message_parts.append("• 预测仅供参考，不保证中奖")
        message_parts.append("• 理性投注，量力而行")
        
        return "\n".join(message_parts)
    
    def send_system_alert(self, alert_type: str, message: str) -> bool:
        """发送系统告警"""
        try:
            alert_content = f"🚨 系统告警 - {alert_type}\n\n{message}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 发送所有可用的通知方式
            email_sent = self.send_email(f"系统告警 - {alert_type}", alert_content)
            wechat_sent = self.send_wechat(alert_content)
            dingtalk_sent = self.send_dingtalk(alert_content)
            
            return email_sent or wechat_sent or dingtalk_sent
            
        except Exception as e:
            self.logger.error(f"发送系统告警失败: {e}")
            return False