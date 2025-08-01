"""
大乐透预测模型 - 基于历史数据生成预测号码
"""
import logging
import random
import statistics
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class LotteryPredictor:
    """大乐透预测器"""
    
    def __init__(self):
        pass
    
    def _calculate_weights(self, analysis_result: Dict) -> Tuple[List[float], List[float]]:
        """
        根据分析结果计算号码权重
        
        Args:
            analysis_result: 数据分析结果
            
        Returns:
            前区和后区的权重列表
        """
        # 获取频率统计
        front_stats = analysis_result.get('front_zone_stats', {})
        back_stats = analysis_result.get('back_zone_stats', {})
        
        # 获取冷热号信息
        hot_numbers = analysis_result.get('hot_numbers', {})
        cold_numbers = analysis_result.get('cold_numbers', {})
        
        # 计算前区权重
        front_weights = []
        for i in range(1, 36):
            base_weight = 1.0
            
            # 基于频率调整权重
            frequency = front_stats.get(i, 0)
            if frequency > 0:
                base_weight += frequency * 0.1
            
            # 热号增加权重
            if i in hot_numbers.get('front_zone', []):
                base_weight += 0.3
            
            # 冷号减少权重
            if i in cold_numbers.get('front_zone', []):
                base_weight *= 0.7
            
            front_weights.append(max(0.1, base_weight))
        
        # 计算后区权重
        back_weights = []
        for i in range(1, 13):
            base_weight = 1.0
            
            # 基于频率调整权重
            frequency = back_stats.get(i, 0)
            if frequency > 0:
                base_weight += frequency * 0.1
            
            # 热号增加权重
            if i in hot_numbers.get('back_zone', []):
                base_weight += 0.3
            
            # 冷号减少权重
            if i in cold_numbers.get('back_zone', []):
                base_weight *= 0.7
            
            back_weights.append(max(0.1, base_weight))
        
        return front_weights, back_weights
    
    def _apply_odd_even_balance(self, numbers: List[int], target_odd_count: int) -> List[int]:
        """
        应用奇偶平衡策略
        
        Args:
            numbers: 候选号码列表
            target_odd_count: 目标奇数数量
            
        Returns:
            平衡后的号码列表
        """
        if len(numbers) < 5:
            return numbers
        
        odd_numbers = [n for n in numbers if n % 2 == 1]
        even_numbers = [n for n in numbers if n % 2 == 0]
        
        result = []
        
        # 根据目标奇偶比例选择号码
        odd_needed = min(target_odd_count, len(odd_numbers))
        even_needed = min(5 - target_odd_count, len(even_numbers))
        
        if odd_needed > 0:
            result.extend(random.sample(odd_numbers, odd_needed))
        if even_needed > 0:
            result.extend(random.sample(even_numbers, even_needed))
        
        # 如果数量不足，补充其他号码
        while len(result) < 5:
            remaining = [n for n in numbers if n not in result]
            if remaining:
                result.append(random.choice(remaining))
            else:
                break
        
        return sorted(result[:5])
    
    def _apply_sum_range_strategy(self, numbers: List[int], target_sum: int) -> List[int]:
        """
        应用和值范围策略
        
        Args:
            numbers: 候选号码列表
            target_sum: 目标和值
            
        Returns:
            符合和值范围的号码列表
        """
        if len(numbers) < 5:
            return numbers
        
        best_combination = None
        best_diff = float('inf')
        
        # 尝试多个组合找到最接近目标和值的
        for _ in range(100):
            combination = sorted(random.sample(numbers, 5))
            current_sum = sum(combination)
            diff = abs(current_sum - target_sum)
            
            if diff < best_diff:
                best_diff = diff
                best_combination = combination
                
                # 如果找到完全匹配的和值，直接返回
                if diff == 0:
                    break
        
        return best_combination or sorted(random.sample(numbers, 5))
    
    def generate_predictions(self, analysis_result: Dict, count: int = 2) -> List[Dict]:
        """
        生成预测号码
        
        Args:
            analysis_result: 数据分析结果
            count: 需要生成的预测组数
            
        Returns:
            预测结果列表
        """
        if not analysis_result:
            logger.warning("分析结果为空，使用随机策略")
            return self._generate_random_predictions(count)
        
        # 计算权重
        front_weights, back_weights = self._calculate_weights(analysis_result)
        
        # 获取奇偶比例和和值范围信息
        odd_even_ratio = analysis_result.get('odd_even_ratio', {})
        sum_range = analysis_result.get('sum_range', {})
        
        # 计算目标奇偶比例和和值
        front_odd_avg = odd_even_ratio.get('front_zone', {}).get('odd_avg', 2.5)
        target_front_odd = int(round(front_odd_avg))
        
        front_sum_avg = sum_range.get('front_zone', {}).get('avg', 85)
        target_front_sum = int(front_sum_avg)
        
        # 使用纯Python实现权重随机选择
        
        predictions = []
        
        for i in range(count):
            # 基于权重选择前区号码
            front_candidates = list(range(1, 36))
            front_numbers = random.choices(
                front_candidates,
                weights=front_weights,
                k=10
            )
            front_numbers = list(set(front_numbers))  # 去重
            
            # 应用策略优化
            front_numbers = self._apply_odd_even_balance(front_numbers, target_front_odd)
            front_numbers = self._apply_sum_range_strategy(front_numbers, target_front_sum)
            
            # 基于权重选择后区号码
            back_candidates = list(range(1, 13))
            back_numbers = random.choices(
                back_candidates,
                weights=back_weights,
                k=4
            )
            back_numbers = list(set(back_numbers))  # 去重
            back_numbers = sorted(back_numbers[:2])  # 取前2个
            
            prediction = {
                'prediction_id': f"pred_{i+1}",
                'front_zone': front_numbers,
                'back_zone': back_numbers,
                'strategy': 'weight_based',
                'confidence': self._calculate_confidence(analysis_result, front_numbers, back_numbers)
            }
            
            predictions.append(prediction)
        
        return predictions
    
    def _calculate_confidence(self, analysis_result: Dict, front_numbers: List[int], back_numbers: List[int]) -> float:
        """计算预测置信度"""
        if not analysis_result:
            return 0.5
        
        # 基于历史频率计算置信度
        front_stats = analysis_result.get('front_zone_stats', {})
        back_stats = analysis_result.get('back_zone_stats', {})
        
        front_confidence = sum(front_stats.get(num, 0) for num in front_numbers) / len(front_numbers) if front_numbers else 0
        back_confidence = sum(back_stats.get(num, 0) for num in back_numbers) / len(back_numbers) if back_numbers else 0
        
        # 归一化置信度
        max_front = max(front_stats.values()) if front_stats else 1
        max_back = max(back_stats.values()) if back_stats else 1
        
        normalized_front = front_confidence / max_front if max_front > 0 else 0.5
        normalized_back = back_confidence / max_back if max_back > 0 else 0.5
        
        # 综合置信度
        confidence = (normalized_front + normalized_back) / 2
        return min(1.0, max(0.1, confidence))
    
    def _generate_random_predictions(self, count: int) -> List[Dict]:
        """生成随机预测"""
        predictions = []
        
        for i in range(count):
            front_numbers = sorted(random.sample(range(1, 36), 5))
            back_numbers = sorted(random.sample(range(1, 13), 2))
            
            prediction = {
                'prediction_id': f"pred_{i+1}",
                'front_zone': front_numbers,
                'back_zone': back_numbers,
                'strategy': 'random',
                'confidence': 0.3
            }
            
            predictions.append(prediction)
        
        return predictions