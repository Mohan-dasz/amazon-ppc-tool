import aiohttp
import asyncio
from typing import List, Dict, Optional
import json
import urllib.parse
import random
from services.ai_bidding import enhanced_ai_predictor

class AmazonIndiaScraper:
    def __init__(self):
        # Updated for Amazon India
        self.base_url = "https://completion.amazon.in/api/2017/suggestions"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-IN,en;q=0.9',
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Indian marketplace configuration
        self.marketplace_config = {
            'marketplace_id': 'A21TJRUUN4KGV',  # Amazon India
            'locale': 'en_IN',
            'currency': 'INR',
            'country': 'India'
        }
        
        # Keyword expansion data for Indian market
        self.indian_modifiers = {
            'prefixes': [
                "best", "cheap", "top", "branded", "original", "quality", "premium", 
                "new", "latest", "good", "popular", "trending", "recommended", 
                "affordable", "budget", "luxury", "professional", "commercial"
            ],
            'suffixes': [
                "online", "india", "price", "deal", "offer", "sale", "review", 
                "buy", "shop", "brand", "cost", "rate", "flipkart", "amazon",
                "discount", "wholesale", "retail", "market", "store", "purchase"
            ],
            'intent_words': [
                "buy", "purchase", "order", "shop", "get", "find", "search",
                "compare", "vs", "versus", "review", "rating", "feedback"
            ],
            'location_words': [
                "india", "delhi", "mumbai", "bangalore", "chennai", "kolkata",
                "hyderabad", "pune", "online", "nationwide", "local"
            ]
        }
    
    async def get_keyword_suggestions(self, seed_keyword: str, limit: int = 10) -> List[str]:
        """Get expanded keyword suggestions beyond Amazon's 10-item limit"""
        
        suggestions = []
        
        # Step 1: Get real Amazon autocomplete suggestions (max ~10)
        amazon_suggestions = await self._get_amazon_autocomplete(seed_keyword)
        suggestions.extend(amazon_suggestions)
        
        # Step 2: If user wants more than what Amazon provides, generate additional variations
        if limit > len(suggestions):
            additional_needed = limit - len(suggestions)
            
            # Generate expanded suggestions using multiple strategies
            expanded_suggestions = self._generate_expanded_suggestions(
                seed_keyword, 
                additional_needed,
                existing_suggestions=suggestions
            )
            suggestions.extend(expanded_suggestions)
        
        # Step 3: Remove duplicates while preserving order
        unique_suggestions = []
        seen = set()
        
        for suggestion in suggestions:
            suggestion_clean = suggestion.strip().lower()
            if suggestion_clean and suggestion_clean not in seen and len(suggestion_clean) > 2:
                unique_suggestions.append(suggestion.strip())
                seen.add(suggestion_clean)
        
        return unique_suggestions[:limit]
    
    async def _get_amazon_autocomplete(self, seed_keyword: str) -> List[str]:
        """Get Amazon's native autocomplete suggestions"""
        try:
            params = {
                'mid': self.marketplace_config['marketplace_id'],
                'alias': 'aps',  # All departments
                'prefix': seed_keyword,
                'suggestion-type': 'KEYWORD',
                'page-type': 'Search',
                'lop': self.marketplace_config['locale'],
                'site-variant': 'desktop',
                'client-info': 'search-ui'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                try:
                    async with session.get(
                        self.base_url, 
                        params=params, 
                        headers=self.headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            suggestions = []
                            
                            # Extract suggestions from response
                            if 'suggestions' in data:
                                for suggestion in data['suggestions']:
                                    if 'value' in suggestion:
                                        keyword = suggestion['value'].strip()
                                        if keyword and keyword not in suggestions:
                                            suggestions.append(keyword)
                            
                            return suggestions
                            
                        else:
                            print(f"Amazon API returned status: {response.status}")
                            
                except aiohttp.ClientError as e:
                    print(f"Network error connecting to Amazon: {e}")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse Amazon response: {e}")
                    
        except Exception as e:
            print(f"Error in _get_amazon_autocomplete: {e}")
        
        return []
    
    def _generate_expanded_suggestions(self, seed_keyword: str, count: int, existing_suggestions: List[str] = None) -> List[str]:
        """Generate additional keyword variations using multiple expansion strategies"""
        
        if existing_suggestions is None:
            existing_suggestions = []
        
        existing_lower = [s.lower() for s in existing_suggestions]
        variations = []
        
        # Strategy 1: Prefix combinations
        for prefix in self.indian_modifiers['prefixes']:
            variation = f"{prefix} {seed_keyword}"
            if variation.lower() not in existing_lower:
                variations.append(variation)
        
        # Strategy 2: Suffix combinations
        for suffix in self.indian_modifiers['suffixes']:
            variation = f"{seed_keyword} {suffix}"
            if variation.lower() not in existing_lower:
                variations.append(variation)
        
        # Strategy 3: Intent-based combinations
        for intent_word in self.indian_modifiers['intent_words']:
            variations.extend([
                f"{intent_word} {seed_keyword}",
                f"{seed_keyword} to {intent_word}",
                f"how to {intent_word} {seed_keyword}"
            ])
        
        # Strategy 4: Location-specific variations
        for location in self.indian_modifiers['location_words']:
            variations.extend([
                f"{seed_keyword} in {location}",
                f"{seed_keyword} {location}",
                f"{location} {seed_keyword}"
            ])
        
        # Strategy 5: Commercial intent variations
        commercial_patterns = [
            f"{seed_keyword} for sale",
            f"{seed_keyword} best price",
            f"buy {seed_keyword} online",
            f"{seed_keyword} lowest price",
            f"{seed_keyword} amazon india",
            f"{seed_keyword} flipkart",
            f"cheap {seed_keyword} online",
            f"{seed_keyword} with discount",
            f"{seed_keyword} bulk order",
            f"wholesale {seed_keyword}",
            f"{seed_keyword} home delivery",
            f"{seed_keyword} cash on delivery"
        ]
        variations.extend(commercial_patterns)
        
        # Strategy 6: Question-based variations
        question_patterns = [
            f"what is {seed_keyword}",
            f"how to use {seed_keyword}",
            f"where to buy {seed_keyword}",
            f"which {seed_keyword} is best",
            f"why buy {seed_keyword}",
            f"when to use {seed_keyword}"
        ]
        variations.extend(question_patterns)
        
        # Strategy 7: Comparison variations
        comparison_patterns = [
            f"{seed_keyword} vs",
            f"{seed_keyword} comparison",
            f"{seed_keyword} alternative",
            f"{seed_keyword} substitute",
            f"better than {seed_keyword}",
            f"{seed_keyword} or"
        ]
        variations.extend(comparison_patterns)
        
        # Filter out duplicates and existing suggestions
        unique_variations = []
        for variation in variations:
            variation_clean = variation.strip()
            if (variation_clean.lower() not in existing_lower and 
                variation_clean not in unique_variations and 
                len(variation_clean) > 2):
                unique_variations.append(variation_clean)
        
        # Shuffle to provide variety and return requested count
        random.shuffle(unique_variations)
        return unique_variations[:count]
    
    async def get_enhanced_keyword_data(self, keyword: str) -> Dict:
        """Get comprehensive keyword data using enhanced AI prediction"""
        
        try:
            # Get enhanced AI prediction with all Helium 10 features
            ai_data = await enhanced_ai_predictor.predict_optimal_bid_enhanced(keyword)
            
            return {
                'keyword': keyword,
                'search_volume': ai_data['search_volume'],
                'competition': ai_data['competition_data']['competition_level'],
                'competition_score': ai_data['competition_data']['competition_score'],
                'organic_competitors': ai_data['competition_data']['organic_competitors'],
                'sponsored_competitors': ai_data['competition_data']['sponsored_competitors'],
                'estimated_cpc_inr': ai_data['estimated_cpc'],
                'suggested_bids': ai_data['suggested_bids'],
                'magnet_iq_score': ai_data['magnet_iq_score'],
                'intent_score': self._calculate_intent_score(keyword),
                'trend_percentage': ai_data['trend_data']['trend_percentage'],
                'trend_direction': ai_data['trend_data']['trend_direction'],
                'seasonal_factor': ai_data['trend_data']['seasonal_factor'],
                'aba_click_share': ai_data['aba_data']['click_share'],
                'aba_conversion_share': ai_data['aba_data']['conversion_share'],
                'sponsored_rank': ai_data['aba_data']['sponsored_rank'],
                'category': ai_data['category'],
                'confidence': ai_data['confidence'],
                'reasoning': ai_data['reasoning'],
                'currency': 'INR',
                'market': 'India',
                'data_source': 'Enhanced AI + Amazon Data'
            }
            
        except Exception as e:
            print(f"Error in get_enhanced_keyword_data: {e}")
            return self._get_basic_keyword_data(keyword)
    
    def _get_basic_keyword_data(self, keyword: str) -> Dict:
        """Fallback basic keyword data if enhanced prediction fails"""
        
        # Generate consistent but varied data based on keyword hash
        keyword_hash = abs(hash(keyword))
        
        return {
            'keyword': keyword,
            'search_volume': (keyword_hash % 8000) + 2000,  # 2000-10000 range
            'competition': ['low', 'medium', 'high'][keyword_hash % 3],
            'competition_score': round((keyword_hash % 100) / 100, 2),
            'organic_competitors': (keyword_hash % 40) + 10,
            'sponsored_competitors': (keyword_hash % 20) + 5,
            'estimated_cpc_inr': round(8 + (keyword_hash % 15), 2),
            'suggested_bids': {
                'conservative': round(8 + (keyword_hash % 15) * 0.8, 2),
                'optimal': round(8 + (keyword_hash % 15) * 1.1, 2),
                'aggressive': round(8 + (keyword_hash % 15) * 1.4, 2)
            },
            'magnet_iq_score': (keyword_hash % 80) + 20,  # 20-100 range
            'intent_score': self._calculate_intent_score(keyword),
            'trend_percentage': (keyword_hash % 40) - 20,  # -20 to +20
            'trend_direction': ['up', 'stable', 'down'][keyword_hash % 3],
            'seasonal_factor': round(0.8 + (keyword_hash % 40) / 100, 2),
            'aba_click_share': round((keyword_hash % 500) / 100, 2),
            'aba_conversion_share': round((keyword_hash % 400) / 100, 2),
            'sponsored_rank': (keyword_hash % 40) + 1,
            'category': 'default',
            'confidence': round(0.5 + (keyword_hash % 30) / 100, 2),
            'reasoning': 'Fallback estimation - API unavailable',
            'currency': 'INR',
            'market': 'India',
            'data_source': 'Fallback Algorithm'
        }
    
    async def estimate_search_metrics_inr(self, keyword: str) -> Dict:
        """Main method for getting all search metrics (maintains backward compatibility)"""
        return await self.get_enhanced_keyword_data(keyword)
    
    def _calculate_intent_score(self, keyword: str) -> int:
        """Calculate purchase intent score (1-10) with Indian market specifics"""
        keyword_lower = keyword.lower()
        score = 5  # Base score
        
        # High intent indicators (Indian market specific)
        high_intent_words = ['buy', 'purchase', 'order', 'booking', 'shop', 'get']
        price_words = ['price', 'cost', 'cheap', 'deal', 'offer', 'discount', 'sale', 'rate']
        research_words = ['best', 'top', 'review', 'compare', 'vs', 'good', 'quality', 'rating']
        brand_words = ['original', 'genuine', 'authentic', 'brand', 'official', 'authorized']
        
        # Calculate intent based on word presence
        if any(word in keyword_lower for word in high_intent_words):
            score += 3
        elif any(word in keyword_lower for word in price_words):
            score += 2
        elif any(word in keyword_lower for word in research_words):
            score += 1
        
        # Brand indicators suggest commercial intent
        if any(word in keyword_lower for word in brand_words):
            score += 1
        
        # Long-tail bonus (more specific = higher intent)
        word_count = len(keyword.split())
        if word_count >= 4:
            score += 1
        elif word_count >= 6:
            score += 2
        
        # Location-specific intent (Indian market)
        location_words = ['india', 'delhi', 'mumbai', 'bangalore', 'online', 'delivery']
        if any(word in keyword_lower for word in location_words):
            score += 1
        
        # E-commerce platform mentions
        platform_words = ['amazon', 'flipkart', 'myntra', 'snapdeal']
        if any(word in keyword_lower for word in platform_words):
            score += 2
        
        return min(10, max(1, score))
    
    async def get_bulk_keyword_analysis(self, keywords: List[str]) -> List[Dict]:
        """Analyze multiple keywords efficiently with concurrency control"""
        
        if not keywords:
            return []
        
        # Limit concurrent requests to avoid overwhelming the system
        semaphore = asyncio.Semaphore(5)
        
        async def analyze_with_semaphore(keyword):
            async with semaphore:
                return await self.get_enhanced_keyword_data(keyword)
        
        # Execute all analysis tasks concurrently
        tasks = [analyze_with_semaphore(keyword) for keyword in keywords]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error analyzing keyword '{keywords[i]}': {result}")
                # Add basic fallback data for failed keywords
                successful_results.append(self._get_basic_keyword_data(keywords[i]))
            else:
                successful_results.append(result)
        
        return successful_results
    
    async def get_competitor_analysis(self, primary_keyword: str, limit: int = 20) -> Dict:
        """Get competitor keyword analysis (Cerebro-style feature)"""
        
        # Get related keywords with expansion
        related_keywords = await self.get_keyword_suggestions(primary_keyword, limit)
        
        if not related_keywords:
            return {
                'primary_keyword': primary_keyword,
                'competitor_keywords': [],
                'total_found': 0,
                'analysis_summary': 'No competitor keywords found',
                'market': 'India'
            }
        
        # Analyze each related keyword
        competitor_data = await self.get_bulk_keyword_analysis(related_keywords)
        
        # Sort by opportunity (Magnet IQ Score)
        competitor_data.sort(key=lambda x: x.get('magnet_iq_score', 0), reverse=True)
        
        # Calculate comprehensive summary statistics
        if competitor_data:
            total_volume = sum(item['search_volume'] for item in competitor_data)
            avg_cpc = sum(item['estimated_cpc_inr'] for item in competitor_data) / len(competitor_data)
            avg_magnet_iq = sum(item['magnet_iq_score'] for item in competitor_data) / len(competitor_data)
            avg_competition = sum(item['competition_score'] for item in competitor_data) / len(competitor_data)
            
            # Find best opportunities (high volume, low competition)
            opportunities = [
                kw for kw in competitor_data 
                if kw['magnet_iq_score'] > 70 and kw['competition_score'] < 0.6
            ]
            
            analysis_summary = {
                'total_search_volume': total_volume,
                'average_cpc': round(avg_cpc, 2),
                'average_magnet_iq': round(avg_magnet_iq, 1),
                'average_competition': round(avg_competition, 2),
                'top_opportunity': competitor_data[0],
                'high_opportunity_count': len(opportunities),
                'low_competition_keywords': len([kw for kw in competitor_data if kw['competition'] == 'low']),
                'high_volume_keywords': len([kw for kw in competitor_data if kw['search_volume'] > 5000])
            }
        else:
            analysis_summary = {
                'total_search_volume': 0,
                'average_cpc': 0,
                'average_magnet_iq': 0,
                'average_competition': 0,
                'top_opportunity': None,
                'high_opportunity_count': 0,
                'low_competition_keywords': 0,
                'high_volume_keywords': 0
            }
        
        return {
            'primary_keyword': primary_keyword,
            'competitor_keywords': competitor_data,
            'total_found': len(competitor_data),
            'analysis_summary': analysis_summary,
            'market': 'India',
            'currency': 'INR',
            'timestamp': asyncio.get_event_loop().time()
        }
    
    def get_marketplace_info(self) -> Dict:
        """Get comprehensive marketplace configuration info"""
        return {
            'marketplace': 'Amazon India',
            'marketplace_id': self.marketplace_config['marketplace_id'],
            'locale': self.marketplace_config['locale'],
            'currency': self.marketplace_config['currency'],
            'country': self.marketplace_config['country'],
            'api_endpoints': {
                'suggestions': self.base_url
            },
            'features': {
                'keyword_expansion': True,
                'bulk_analysis': True,
                'competitor_analysis': True,
                'magnet_iq_scoring': True,
                'trend_analysis': True,
                'aba_simulation': True
            },
            'limits': {
                'amazon_autocomplete_max': 10,
                'expanded_suggestions_max': 1000,
                'concurrent_analysis': 5
            }
        }

# Create global enhanced instance
amazon_india_scraper = AmazonIndiaScraper()