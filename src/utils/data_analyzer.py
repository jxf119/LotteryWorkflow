import logging
import statistics
from typing import Dict, List, Tuple
from collections import Counter
import json

class DataAnalyzer:
    """数据分析工具类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_lottery_data(self, records: List[Dict]) -> Dict:
        """
        分析彩票历史数据
        
        Args:
            records: 历史记录列表
            
        Returns:
            分析结果字典
        """
        if not records:
            return {}
        
        try:
            # 提取前区和后区号码
            front_zone_numbers = []
            back_zone_numbers = []
            
            for record in records:
                front_str = record.get('front_zone', '')
                back_str = record.get('back_zone', '')
                
                if front_str and back_str:
                    front_nums = [int(x) for x in front_str.split(',')]
                    back_nums = [int(x) for x in back_str.split(',')]
                    
                    front_zone_numbers.extend(front_nums)
                    back_zone_numbers.extend(back_nums)
            
            # 统计分析
            front_zone_stats = self._calculate_number_stats(front_zone_numbers, 1, 35)
            back_zone_stats = self._calculate_number_stats(back_zone_numbers, 1, 12)
            
            # 冷热号分析
            hot_numbers = self._identify_hot_cold_numbers(front_zone_numbers, back_zone_numbers)
            
            # 奇偶比例分析
            odd_even_ratio = self._calculate_odd_even_ratio(records)
            
            # 和值范围分析
            sum_range = self._calculate_sum_range(records)
            
            analysis_result = {
                'data_count': len(records),
                'front_zone_stats': front_zone_stats,
                'back_zone_stats': back_zone_stats,
                'hot_numbers': hot_numbers,
                'cold_numbers': hot_numbers.get('cold', {}),
                'odd_even_ratio': odd_even_ratio,
                'sum_range': sum_range,
                'analysis_date': None  # 将在外部设置
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"数据分析失败: {e}")
            return {}
    
    def _calculate_number_stats(self, numbers: List[int], min_num: int, max_num: int) -> Dict[int, int]:
        """计算号码出现频率统计"""
        counter = Counter(numbers)
        stats = {i: counter.get(i, 0) for i in range(min_num, max_num + 1)}
        return stats
    
    def _identify_hot_cold_numbers(self, front_numbers: List[int], back_numbers: List[int]) -> Dict:
        """识别冷热号码"""
        
        # 前区冷热号
        front_counter = Counter(front_numbers)
        front_hot = [num for num, count in front_counter.most_common(5)]
        front_cold = [num for num, count in front_counter.most_common()[-5:]]
        
        # 后区冷热号
        back_counter = Counter(back_numbers)
        back_hot = [num for num, count in back_counter.most_common(2)]
        back_cold = [num for num, count in back_counter.most_common()[-2:]]
        
        return {
            'hot': {
                'front_zone': front_hot,
                'back_zone': back_hot
            },
            'cold': {
                'front_zone': front_cold,
                'back_zone': back_cold
            }
        }
    
    def _calculate_odd_even_ratio(self, records: List[Dict]) -> Dict:
        """计算奇偶比例"""
        front_odd_count = 0
        front_even_count = 0
        back_odd_count = 0
        back_even_count = 0
        
        for record in records:
            front_str = record.get('front_zone', '')
            back_str = record.get('back_zone', '')
            
            if front_str and back_str:
                front_nums = [int(x) for x in front_str.split(',')]
                back_nums = [int(x) for x in back_str.split(',')]
                
                front_odd = sum(1 for n in front_nums if n % 2 == 1)
                front_even = len(front_nums) - front_odd
                
                back_odd = sum(1 for n in back_nums if n % 2 == 1)
                back_even = len(back_nums) - back_odd
                
                front_odd_count += front_odd
                front_even_count += front_even
                back_odd_count += back_odd
                back_even_count += back_even
        
        total_records = len(records)
        
        return {
            'front_zone': {
                'odd': front_odd_count,
                'even': front_even_count,
                'odd_avg': front_odd_count / total_records if total_records > 0 else 2.5,
                'even_avg': front_even_count / total_records if total_records > 0 else 2.5
            },
            'back_zone': {
                'odd': back_odd_count,
                'even': back_even_count,
                'odd_avg': back_odd_count / total_records if total_records > 0 else 1,
                'even_avg': back_even_count / total_records if total_records > 0 else 1
            }
        }
    
    def _calculate_sum_range(self, records: List[Dict]) -> Dict:
        """计算和值范围"""
        front_sums = []
        back_sums = []
        
        for record in records:
            front_str = record.get('front_zone', '')
            back_str = record.get('back_zone', '')
            
            if front_str and back_str:
                front_nums = [int(x) for x in front_str.split(',')]
                back_nums = [int(x) for x in back_str.split(',')]
                
                front_sums.append(sum(front_nums))
                back_sums.append(sum(back_nums))
        
        return {
            'front_zone': {
                'min': min(front_sums) if front_sums else 15,
                'max': max(front_sums) if front_sums else 165,
                'avg': statistics.mean(front_sums) if front_sums else 90,
                'median': statistics.median(front_sums) if front_sums else 90
            },
            'back_zone': {
                'min': min(back_sums) if back_sums else 3,
                'max': max(back_sums) if back_sums else 23,
                'avg': statistics.mean(back_sums) if back_sums else 13,
                'median': statistics.median(back_sums) if back_sums else 13
            }
        }
    
    def generate_report(self, analysis_result: Dict) -> str:
        """生成分析报告"""
        if not analysis_result:
            return "无数据可供分析"
        
        report_lines = []
        report_lines.append("📊 大乐透数据分析报告")
        report_lines.append("=" * 30)
        report_lines.append("")
        
        # 基础统计
        data_count = analysis_result.get('data_count', 0)
        report_lines.append(f"📈 分析数据量: {data_count} 期")
        report_lines.append("")
        
        # 冷热号分析
        hot_numbers = analysis_result.get('hot_numbers', {})
        if hot_numbers:
            report_lines.append("🔥 热门号码:")
            report_lines.append(f"前区: {hot_numbers.get('hot', {}).get('front_zone', [])}")
            report_lines.append(f"后区: {hot_numbers.get('hot', {}).get('back_zone', [])}")
            report_lines.append("")
            
            report_lines.append("❄️ 冷门号码:")
            report_lines.append(f"前区: {hot_numbers.get('cold', {}).get('front_zone', [])}")
            report_lines.append(f"后区: {hot_numbers.get('cold', {}).get('back_zone', [])}")
            report_lines.append("")
        
        # 奇偶比例
        odd_even = analysis_result.get('odd_even_ratio', {})
        if odd_even:
            front = odd_even.get('front_zone', {})
            back = odd_even.get('back_zone', {})
            
            report_lines.append("⚖️ 奇偶比例:")
            report_lines.append(f"前区 - 奇数: {front.get('odd_avg', 0):.1f}, 偶数: {front.get('even_avg', 0):.1f}")
            report_lines.append(f"后区 - 奇数: {back.get('odd_avg', 0):.1f}, 偶数: {back.get('even_avg', 0):.1f}")
            report_lines.append("")
        
        # 和值范围
        sum_range = analysis_result.get('sum_range', {})
        if sum_range:
            front_sum = sum_range.get('front_zone', {})
            back_sum = sum_range.get('back_zone', {})
            
            report_lines.append("🔢 和值范围:")
            report_lines.append(f"前区和值: {front_sum.get('min', 0)}-{front_sum.get('max', 0)} (平均: {front_sum.get('avg', 0):.1f})")
            report_lines.append(f"后区和值: {back_sum.get('min', 0)}-{back_sum.get('max', 0)} (平均: {back_sum.get('avg', 0):.1f})")
        
        return "\n".join(report_lines)