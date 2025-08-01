import sqlite3
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager

class DataStorage:
    """数据存储管理类"""
    
    def __init__(self, db_path: str = "lottery_data.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建彩票历史记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS lottery_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        term TEXT UNIQUE NOT NULL,
                        open_date DATE NOT NULL,
                        front_zone TEXT NOT NULL,
                        back_zone TEXT NOT NULL,
                        url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建预测记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        term TEXT NOT NULL,
                        prediction_date DATE NOT NULL,
                        front_zone_predict TEXT NOT NULL,
                        back_zone_predict TEXT NOT NULL,
                        confidence REAL,
                        strategy TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建分析结果表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_date DATE NOT NULL,
                        data_count INTEGER NOT NULL,
                        front_zone_stats TEXT,
                        back_zone_stats TEXT,
                        hot_numbers TEXT,
                        cold_numbers TEXT,
                        odd_even_ratio TEXT,
                        sum_range TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_lottery_history_term ON lottery_history(term)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_lottery_history_date ON lottery_history(open_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_term ON predictions(term)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_date ON analysis_results(analysis_date)')
                
                conn.commit()
                self.logger.info("数据库初始化完成")
                
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def insert_lottery_record(self, record: Dict) -> bool:
        """
        插入单条彩票记录
        
        Args:
            record: 彩票记录字典
            
        Returns:
            是否成功插入
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查记录是否已存在
                cursor.execute('''
                    SELECT COUNT(*) FROM lottery_history WHERE term = ?
                ''', (record['term'],))
                
                if cursor.fetchone()[0] > 0:
                    self.logger.info(f"期号 {record['term']} 已存在，跳过插入")
                    return False
                
                # 插入新记录
                cursor.execute('''
                    INSERT INTO lottery_history (term, open_date, front_zone, back_zone, url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    record['term'],
                    record['open_date'],
                    record['front_zone'],
                    record['back_zone'],
                    record.get('url', '')
                ))
                
                conn.commit()
                self.logger.info(f"成功插入期号 {record['term']} 的数据")
                return True
                
        except sqlite3.IntegrityError as e:
            self.logger.error(f"数据完整性错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"插入数据失败: {e}")
            return False
    
    def batch_insert_records(self, records: List[Dict]) -> Dict[str, int]:
        """
        批量插入彩票记录
        
        Args:
            records: 彩票记录列表
            
        Returns:
            插入统计结果
        """
        stats = {'total': len(records), 'inserted': 0, 'skipped': 0, 'failed': 0}
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for record in records:
                    try:
                        # 检查记录是否已存在
                        cursor.execute('''
                            SELECT COUNT(*) FROM lottery_history WHERE term = ?
                        ''', (record['term'],))
                        
                        if cursor.fetchone()[0] > 0:
                            stats['skipped'] += 1
                            continue
                        
                        # 插入新记录
                        cursor.execute('''
                            INSERT INTO lottery_history (term, open_date, front_zone, back_zone, url)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            record['term'],
                            record['open_date'],
                            record['front_zone'],
                            record['back_zone'],
                            record.get('url', '')
                        ))
                        
                        stats['inserted'] += 1
                        
                    except Exception as e:
                        self.logger.warning(f"单条记录插入失败: {record.get('term', 'unknown')} - {e}")
                        stats['failed'] += 1
                
                conn.commit()
                self.logger.info(f"批量插入完成: {stats}")
                
        except Exception as e:
            self.logger.error(f"批量插入失败: {e}")
        
        return stats
    
    def get_latest_records(self, limit: int = 300) -> List[Dict]:
        """
        获取最新的彩票记录
        
        Args:
            limit: 返回记录数量
            
        Returns:
            彩票记录列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM lottery_history
                    ORDER BY open_date DESC, term DESC
                    LIMIT ?
                ''', (limit,))
                
                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    records.append(record)
                
                return records
                
        except Exception as e:
            self.logger.error(f"获取最新记录失败: {e}")
            return []
    
    def get_records_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        按日期范围获取彩票记录
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            彩票记录列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM lottery_history
                    WHERE open_date BETWEEN ? AND ?
                    ORDER BY open_date ASC
                ''', (start_date, end_date))
                
                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    records.append(record)
                
                return records
                
        except Exception as e:
            self.logger.error(f"按日期范围获取记录失败: {e}")
            return []