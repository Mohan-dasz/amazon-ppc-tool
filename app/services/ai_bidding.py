import math
import re
from typing import Dict, List
import asyncio
import random
from datetime import datetime

class EnhancedAIBiddingPredictor:
    def __init__(self):
        # Realistic Indian market CPC ranges (in INR) - calibrated
        self.category_base_cpc = {
            'electronics': {'min': 8, 'max': 25},
            'fashion': {'min': 5, 'max': 15},
            'books': {'min': 3, 'max': 12},
            'home_kitchen': {'min': 6, 'max': 18},
            'health': {'min': 10, 'max': 30},
            'beauty': {'min': 8, 'max': 22},
            'sports': {'min': 7, 'max': 20},
            'default': {'min': 5, 'max': 18}
        }
        
        # Calibrated search volume ranges based on Indian market
        self.category_volume_multipliers = {
            'electronics': {'base': 8000, 'multiplier': 2.5},
            'fashion': {'base': 6000, 'multiplier': 2.0},
            'books': {'base': 3000, 'multiplier': 1.2},
            'home_kitchen': {'base': 5000, 'multiplier': 1.8},
            'health': {'base': 7000, 'multiplier': 2.2},
            'beauty': {'base': 6500, 'multiplier': 2.1},
            'sports': {'base': 4500, 'multiplier': 1.6},
            'default': {'base': 4000, 'multiplier': 1.5}
        }
        
        # High-intent keywords that justify higher bids
        self.high_intent_words = ['buy', 'price', 'cost', 'cheap', 'best', 'top', 'deal', 'discount', 'offer']
        self.brand_indicators = ['brand', 'original', 'genuine', 'authentic']
        
        # Trend patterns (simulated seasonality)
        self.seasonal_trends = {
            'electronics': [5, 10, 15, 20, 25, 30, 35, 40, 45, 35, 25, 15],  # Peak in festive seasons
            'fashion': [20, 25, 30, 35, 40, 30, 20, 15, 25, 35, 40, 45],  # Wedding/festival seasons
            'health': [40, 35, 30, 25, 20, 15, 20, 25, 30, 35, 40, 45],  # New year resolutions
            'default': [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25]  # Consistent
        }

    def categorize_keyword(self, keyword: str) -> str:
        """Determine product category from keyword"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ['phone', 'mobile', 'laptop', 'tablet', 'headphone', 'speaker', 'camera']):
            return 'electronics'
        elif any(word in keyword_lower for word in ['shirt', 'dress', 'saree', 'jeans', 'shoes', 'bag']):
            return 'fashion'
        elif any(word in keyword_lower for word in ['book', 'novel', 'guide', 'manual']):
            return 'books'
        elif any(word in keyword_lower for word in ['kitchen', 'home', 'furniture', 'decor']):
            return 'home_kitchen'
        elif any(word in keyword_lower for word in ['vitamin', 'supplement', 'medicine', 'health']):
            return 'health'
        elif any(word in keyword_lower for word in ['cream', 'lotion', 'makeup', 'beauty', 'skin']):
            return 'beauty'
        elif any(word in keyword_lower for word in ['sports', 'fitness', 'gym', 'exercise']):
            return 'sports'
        else:
            return 'default'

    def calculate_magnet_iq_score(self, keyword: str, search_volume: int, competition_score: float) -> int:
        """Calculate Magnet IQ Score (Helium 10 style) - 1-100"""
        
        # Base score factors
        volume_score = min(40, search_volume / 500)  # Volume contribution
        competition_penalty = competition_score * 30   # Competition penalty
        intent_bonus = 20 if any(word in keyword.lower() for word in self.high_intent_words) else 0
        length_bonus = max(0, 15 - len(keyword.split()) * 2)  # Long-tail bonus
        
        # Calculate final score
        magnet_score = volume_score - competition_penalty + intent_bonus + length_bonus
        
        return max(1, min(100, int(magnet_score)))

    def calculate_search_volume_trend(self, keyword: str, category: str) -> Dict:
        """Calculate search volume trend (Helium 10 style)"""
        current_month = datetime.now().month - 1  # 0-indexed
        
        # Get seasonal pattern for category
        seasonal_pattern = self.seasonal_trends.get(category, self.seasonal_trends['default'])
        current_trend = seasonal_pattern[current_month]
        previous_trend = seasonal_pattern[(current_month - 1) % 12]
        
        # Calculate trend percentage
        trend_change = ((current_trend - previous_trend) / previous_trend) * 100
        
        # Add some keyword-specific variation
        keyword_hash = abs(hash(keyword)) % 20 - 10  # -10 to +10
        trend_change += keyword_hash
        
        return {
            'trend_percentage': round(trend_change, 0),
            'trend_direction': 'up' if trend_change > 0 else 'down' if trend_change < 0 else 'stable',
            'seasonal_factor': current_trend / 25  # Normalized seasonal strength
        }

    def estimate_enhanced_search_volume(self, keyword: str, category: str) -> Dict:
        """Enhanced search volume estimation with trend analysis"""
        
        volume_config = self.category_volume_multipliers[category]
        base_volume = volume_config['base']
        multiplier = volume_config['multiplier']
        
        # Keyword length factor (longer = more specific = lower volume)
        length_factor = max(0.3, 1 - (len(keyword.split()) - 2) * 0.15)
        
        # Brand vs generic factor
        is_branded = any(brand in keyword.lower() for brand in self.brand_indicators)
        brand_factor = 0.7 if is_branded else 1.0
        
        # Intent factor (high intent = higher volume)
        intent_factor = 1.3 if any(word in keyword.lower() for word in self.high_intent_words) else 1.0
        
        # Calculate base volume
        estimated_volume = int(base_volume * multiplier * length_factor * brand_factor * intent_factor)
        
        # Add keyword-specific variation
        keyword_variation = abs(hash(keyword)) % 5000
        final_volume = estimated_volume + keyword_variation
        
        # Get trend analysis
        trend_data = self.calculate_search_volume_trend(keyword, category)
        
        return {
            'search_volume': final_volume,
            'trend_data': trend_data,
            'volume_factors': {
                'base': base_volume,
                'category_multiplier': multiplier,
                'length_factor': length_factor,
                'brand_factor': brand_factor,
                'intent_factor': intent_factor
            }
        }

    def calculate_competition_analysis(self, keyword: str) -> Dict:
        """Detailed competition analysis (Helium 10 style)"""
        
        # Competition factors
        factors = {
            'length': max(0, 1 - (len(keyword.split()) - 2) * 0.1),
            'generic': 0.8 if len(keyword.split()) <= 2 else 0.4,
            'brand': 0.6 if any(brand in keyword.lower() for brand in self.brand_indicators) else 0.3,
            'intent': 0.7 if any(intent in keyword.lower() for intent in self.high_intent_words) else 0.4
        }
        
        competition_score = min(1.0, sum(factors.values()) / len(factors))
        
        # Simulate organic and sponsored competition
        organic_competition = int(competition_score * 50 + abs(hash(keyword)) % 30)
        sponsored_competition = int(competition_score * 20 + abs(hash(keyword + "ads")) % 15)
        
        return {
            'competition_score': competition_score,
            'competition_level': 'low' if competition_score < 0.4 else 'medium' if competition_score < 0.7 else 'high',
            'organic_competitors': organic_competition,
            'sponsored_competitors': sponsored_competition,
            'competition_factors': factors
        }

    async def predict_optimal_bid_enhanced(self, keyword: str) -> Dict:
        """Enhanced AI-powered bid prediction with Helium 10 features"""
        
        category = self.categorize_keyword(keyword)
        
        # Get enhanced search volume data
        volume_data = self.estimate_enhanced_search_volume(keyword, category)
        search_volume = volume_data['search_volume']
        
        # Get competition analysis
        competition_data = self.calculate_competition_analysis(keyword)
        competition_score = competition_data['competition_score']
        
        # Calculate Magnet IQ Score
        magnet_iq = self.calculate_magnet_iq_score(keyword, search_volume, competition_score)
        
        # Get base CPC range for category
        cpc_range = self.category_base_cpc[category]
        
        # Calculate base CPC using competition
        base_cpc = cpc_range['min'] + (cpc_range['max'] - cpc_range['min']) * competition_score
        
        # Volume adjustment (higher volume = slightly higher CPC)
        volume_multiplier = 1 + min(0.3, search_volume / 10000 * 0.1)
        base_cpc *= volume_multiplier
        
        # Trend adjustment
        trend_multiplier = 1 + (volume_data['trend_data']['seasonal_factor'] - 1) * 0.1
        base_cpc *= trend_multiplier
        
        # Round to realistic values
        estimated_cpc = round(base_cpc, 2)
        
        # Calculate suggested bids
        suggested_bids = {
            'conservative': round(estimated_cpc * 0.8, 2),
            'optimal': round(estimated_cpc * 1.1, 2),
            'aggressive': round(estimated_cpc * 1.4, 2)
        }
        
        # Simulate ABA data (Amazon Brand Analytics style)
        aba_data = {
            'click_share': round(random.uniform(0.1, 5.0), 2),
            'conversion_share': round(random.uniform(0.05, 3.0), 2),
            'sponsored_rank': random.randint(1, 50)
        }
        
        return {
            'keyword': keyword,
            'category': category,
            'search_volume': search_volume,
            'estimated_cpc': estimated_cpc,
            'suggested_bids': suggested_bids,
            'magnet_iq_score': magnet_iq,
            'competition_data': competition_data,
            'trend_data': volume_data['trend_data'],
            'aba_data': aba_data,
            'confidence': round(0.85 - (competition_score * 0.2), 2),
            'reasoning': self._generate_enhanced_reasoning(keyword, category, competition_score, estimated_cpc, magnet_iq),
            'market': 'India',
            'currency': 'INR'
        }

    def _generate_enhanced_reasoning(self, keyword: str, category: str, competition: float, cpc: float, magnet_iq: int) -> str:
        """Generate detailed reasoning for the predictions"""
        reasons = []
        
        if magnet_iq > 70:
            reasons.append("High-opportunity keyword")
        elif magnet_iq < 30:
            reasons.append("Low-opportunity keyword")
        
        if competition > 0.7:
            reasons.append("High competition market")
        elif competition < 0.4:
            reasons.append("Low competition opportunity")
            
        if len(keyword.split()) > 3:
            reasons.append("Long-tail advantage")
        
        if any(word in keyword.lower() for word in self.high_intent_words):
            reasons.append("High purchase intent")
            
        reasons.append(f"{category.replace('_', ' ').title()} category analysis")
        
        return " | ".join(reasons)

# Global enhanced instance
enhanced_ai_predictor = EnhancedAIBiddingPredictor()