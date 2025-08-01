import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import random

class LotteryDataCrawler:
    """大乐透数据爬虫类"""
    
    def __init__(self, base_url: str = "https://www.lottery.gov.cn", cache_duration: int = 3600):
        self.base_url = base_url
        self.cache_duration = cache_duration  # 缓存时间（秒）
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        })
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fetch_lottery_history(self, start_date: str = None, end_date: str = None, limit: int = 100) -> List[Dict]:
        """
        获取大乐透历史开奖数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回记录数量限制
            
        Returns:
            历史开奖数据列表
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # 检查是否使用模拟数据
            if os.getenv('USE_MOCK_DATA', 'true').lower() == 'true':
                self.logger.info("使用模拟数据")
                return self._generate_mock_data(limit)
            
            # 构造API请求URL（这里使用模拟URL，实际使用时需要替换为真实体彩API）
            api_url = f"{self.base_url}/api/lottery/dlt/history"
            
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit,
                'format': 'json'
            }
            
            # 添加缓存机制
            cache_key = f"lottery_history_{start_date}_{end_date}_{limit}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                self.logger.info("使用缓存数据")
                return cached_data
            
            # 发送请求
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # 验证数据格式
            validated_data = self._validate_data(data)
            
            # 缓存数据
            self._save_to_cache(cache_key, validated_data)
            
            self.logger.info(f"成功获取 {len(validated_data)} 条历史数据")
            return validated_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}，使用模拟数据")
            return self._generate_mock_data(limit)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}，使用模拟数据")
            return self._generate_mock_data(limit)
        except Exception as e:
            self.logger.error(f"获取数据时发生错误: {e}，使用模拟数据")
            return self._generate_mock_data(limit)
    
    def _validate_data(self, data: Dict) -> List[Dict]:
        """验证并格式化返回的数据"""
        validated_data = []
        
        # 这里使用模拟数据格式，实际使用时需要根据体彩官网API调整
        if isinstance(data, dict) and 'data' in data:
            records = data['data']
        elif isinstance(data, list):
            records = data
        else:
            self.logger.warning("未知的数据格式")
            return []
        
        for record in records:
            try:
                # 验证必需字段
                required_fields = ['term', 'open_date', 'front_zone', 'back_zone']
                if not all(field in record for field in required_fields):
                    continue
                
                # 验证号码格式
                front_zone = self._parse_numbers(record['front_zone'])
                back_zone = self._parse_numbers(record['back_zone'])
                
                if len(front_zone) != 5 or len(back_zone) != 2:
                    continue
                
                # 验证号码范围
                if not all(1 <= num <= 35 for num in front_zone):
                    continue
                if not all(1 <= num <= 12 for num in back_zone):
                    continue
                
                validated_record = {
                    'term': str(record['term']),
                    'open_date': record['open_date'],
                    'front_zone': ','.join(map(str, front_zone)),
                    'back_zone': ','.join(map(str, back_zone)),
                    'url': record.get('url', '')
                }
                
                validated_data.append(validated_record)
                
            except Exception as e:
                self.logger.warning(f"数据验证失败: {e}")
                continue
        
        return validated_data
    
    def _parse_numbers(self, numbers_str: str) -> List[int]:
        """解析号码字符串为整数列表"""
        try:
            if isinstance(numbers_str, str):
                return [int(num.strip()) for num in numbers_str.split(',')]
            elif isinstance(numbers_str, list):
                return [int(num) for num in numbers_str]
            else:
                return []
        except ValueError:
            return []
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """从缓存获取数据"""
        cache_file = f"cache/{cache_key}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # 检查缓存是否过期
                if time.time() - cache_data.get('timestamp', 0) < self.cache_duration:
                    return cache_data.get('data', [])
            except Exception as e:
                self.logger.warning(f"读取缓存失败: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: List[Dict]):
        """保存数据到缓存"""
        os.makedirs('cache', exist_ok=True)
        cache_file = f"cache/{cache_key}.json"
        
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存缓存失败: {e}")
    
    def _generate_mock_data(self, count: int) -> List[Dict]:
        """生成模拟数据用于测试"""
        mock_data = []
        base_date = datetime.now()
        
        for i in range(count):
            # 生成期号（从最新往前推）
            term_number = 1000 - i
            term = f"2024{str(term_number).zfill(3)}"
            
            # 生成日期（每周3期，周一、三、六开奖）
            days_ago = (count - i - 1) * 2  # 简化为每2天一期的模拟
            open_date = (base_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # 生成前区号码（5个不重复的1-35的数）
            front_zone = sorted(random.sample(range(1, 36), 5))
            
            # 生成后区号码（2个不重复的1-12的数）
            back_zone = sorted(random.sample(range(1, 13), 2))
            
            mock_record = {
                'term': term,
                'open_date': open_date,
                'front_zone': ','.join(map(str, front_zone)),
                'back_zone': ','.join(map(str, back_zone)),
                'url': f"https://www.lottery.gov.cn/dlt/{term}.html"
            }
            
            mock_data.append(mock_record)
        
        return mock_data
    
    def get_latest_term(self) -> Optional[str]:
        """获取最新期号"""
        try:
            data = self.fetch_lottery_history(limit=1)
            if data:
                return data[0]['term']
            return None
        except Exception as e:
            self.logger.error(f"获取最新期号失败: {e}")
            return None
    
    def get_missing_terms(self, existing_terms: List[str]) -> List[str]:
        """获取缺失的期号列表"""
        try:
            all_data = self.fetch_lottery_history(limit=1000)
            all_terms = [record['term'] for record in all_data]
            
            missing_terms = [term for term in all_terms if term not in existing_terms]
            return missing_terms
            
        except Exception as e:
            self.logger.error(f"获取缺失期号失败: {e}")
            return []