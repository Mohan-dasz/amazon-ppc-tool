import re
from typing import Dict, List, Optional
import random
import asyncio

class AmazonListingBuilder:
    def __init__(self):
        # Amazon listing compliance rules based on official guidelines
        self.title_rules = {
            'max_length': 200,
            'banned_words': [
                'best', 'cheapest', '#1', 'sale', 'deal', 'offer', 'promotion',
                'discount', 'free shipping', 'new', 'hot', 'wow', 'amazing',
                'perfect', 'guaranteed', 'ultimate', 'revolutionary'
            ],
            'required_elements': ['brand', 'product_type', 'key_feature'],
            'forbidden_symbols': ['!', '?', '®', '™', '©', '*', '$', '%'],
            'forbidden_phrases': ['money back', 'satisfaction guaranteed', 'best seller']
        }
        
        self.bullet_rules = {
            'max_length': 1000,
            'max_bullets': 5,
            'banned_phrases': [
                'money back guarantee', 'lifetime warranty', 'best price',
                'satisfaction guaranteed', 'free shipping', 'fast delivery',
                'lowest price', 'price match', 'call now', 'order today'
            ],
            'required_format': 'benefit_focused',
            'min_length': 50
        }
        
        self.description_rules = {
            'max_length': 2000,
            'min_length': 200,
            'banned_html': ['<script>', '<iframe>', '<object>', '<embed>', '<form>'],
            'allowed_html': ['<p>', '<br>', '<b>', '<strong>', '<i>', '<em>', '<ul>', '<li>', '<ol>'],
            'required_sections': ['product_overview', 'key_benefits'],
            'banned_content': [
                'contact information', 'phone numbers', 'email addresses',
                'external links', 'competitor mentions', 'pricing information'
            ]
        }

        # Indian market specific considerations
        self.indian_market_terms = {
            'positive_keywords': [
                'premium', 'quality', 'durable', 'authentic', 'genuine',
                'professional', 'reliable', 'efficient', 'comfortable'
            ],
            'local_preferences': [
                'easy to use', 'value for money', 'family friendly',
                'suitable for indian conditions', 'long lasting'
            ]
        }

    async def generate_compliant_title(self, product_info: Dict) -> Dict:
        """Generate Amazon-compliant product title for Indian market"""
        
        # Extract key information
        brand = product_info.get('brand', '').strip()
        product_type = product_info.get('product_type', '').strip()
        key_features = product_info.get('key_features', [])
        target_keywords = product_info.get('target_keywords', [])
        color = product_info.get('color', '')
        size = product_info.get('size', '')
        
        # Build title following Amazon's recommended structure
        title_parts = []
        
        # 1. Brand (required)
        if brand:
            title_parts.append(brand)
        
        # 2. Product Type (required)
        if product_type:
            title_parts.append(product_type)
        
        # 3. Primary keyword naturally integrated
        if target_keywords:
            primary_keyword = target_keywords[0]
            if primary_keyword.lower() not in ' '.join(title_parts).lower():
                title_parts.append(primary_keyword)
        
        # 4. Key distinguishing features
        added_features = 0
        for feature in key_features:
            current_title = ' '.join(title_parts + [feature])
            if len(current_title) < 150 and added_features < 2:  # Leave room for size/color
                title_parts.append(feature)
                added_features += 1
        
        # 5. Color and size if provided
        if color and len(' '.join(title_parts + [color])) < 180:
            title_parts.append(color)
        
        if size and len(' '.join(title_parts + [size])) < self.title_rules['max_length']:
            title_parts.append(size)
        
        # Join parts with proper formatting
        title = ' '.join(title_parts)
        title = self._clean_title_formatting(title)
        
        # Validate compliance
        compliance_check = self._validate_title_compliance(title)
        
        return {
            'title': title,
            'character_count': len(title),
            'compliance_score': compliance_check['score'],
            'compliance_issues': compliance_check['issues'],
            'suggestions': compliance_check['suggestions'],
            'amazon_policy_compliant': compliance_check['score'] >= 80
        }

    async def generate_compliant_bullets(self, product_info: Dict) -> Dict:
        """Generate 5 compliant bullet points focused on benefits"""
        
        features = product_info.get('features', [])
        benefits = product_info.get('benefits', [])
        target_keywords = product_info.get('target_keywords', [])
        specifications = product_info.get('specifications', {})
        use_cases = product_info.get('use_cases', [])
        
        bullets = []
        
        # Bullet 1: Primary benefit with main keyword
        if benefits and target_keywords:
            bullet1 = f"SUPERIOR QUALITY: {benefits[0]} with {target_keywords[0]} design for enhanced performance and reliability"
            bullets.append(bullet1)
        elif target_keywords:
            bullet1 = f"PREMIUM {target_keywords[0].upper()}: Professional grade quality ensures optimal performance for daily use"
            bullets.append(bullet1)
        
        # Bullet 2: Key feature with practical benefit
        if features:
            bullet2 = f"ADVANCED FEATURES: {features[0]} - engineered for durability and user convenience"
            bullets.append(bullet2)
        else:
            bullet2 = "DURABLE CONSTRUCTION: Built with high-quality materials for long-lasting performance"
            bullets.append(bullet2)
        
        # Bullet 3: Usage and application
        if use_cases:
            bullet3 = f"VERSATILE APPLICATION: Perfect for {use_cases[0]} - easy to use and maintain for everyday needs"
            bullets.append(bullet3)
        else:
            bullet3 = "USER-FRIENDLY DESIGN: Simple to operate with intuitive controls suitable for all skill levels"
            bullets.append(bullet3)
        
        # Bullet 4: Additional benefit or specification
        if len(benefits) > 1:
            bullet4 = f"ENHANCED PERFORMANCE: {benefits[1]} designed to exceed expectations with consistent results"
            bullets.append(bullet4)
        elif specifications:
            spec_key, spec_value = next(iter(specifications.items()))
            bullet4 = f"TECHNICAL EXCELLENCE: {spec_key} of {spec_value} ensures optimal functionality"
            bullets.append(bullet4)
        else:
            bullet4 = "RELIABLE PERFORMANCE: Consistent quality backed by rigorous testing standards"
            bullets.append(bullet4)
        
        # Bullet 5: Value proposition and support
        if 'warranty' in product_info:
            bullet5 = f"QUALITY ASSURANCE: {product_info['warranty']} with dedicated customer support for peace of mind"
            bullets.append(bullet5)
        else:
            bullet5 = "CUSTOMER SATISFACTION: Professional grade quality with responsive customer service support"
            bullets.append(bullet5)
        
        # Validate each bullet
        validated_bullets = []
        for i, bullet in enumerate(bullets):
            validation = self._validate_bullet_compliance(bullet)
            validated_bullets.append({
                'bullet': bullet,
                'bullet_number': i + 1,
                'character_count': len(bullet),
                'compliance_score': validation['score'],
                'issues': validation['issues'],
                'is_compliant': validation['score'] >= 80
            })
        
        overall_score = sum(b['compliance_score'] for b in validated_bullets) / len(validated_bullets)
        
        return {
            'bullets': validated_bullets,
            'total_bullets': len(bullets),
            'overall_compliance_score': round(overall_score, 1),
            'all_bullets_compliant': all(b['is_compliant'] for b in validated_bullets),
            'recommendations': self._get_bullet_recommendations(validated_bullets)
        }

    async def generate_compliant_description(self, product_info: Dict) -> Dict:
        """Generate Amazon-compliant product description with proper HTML"""
        
        product_type = product_info.get('product_type', 'Product')
        brand = product_info.get('brand', 'Premium Brand')
        features = product_info.get('features', [])
        benefits = product_info.get('benefits', [])
        specifications = product_info.get('specifications', {})
        target_keywords = product_info.get('target_keywords', [])
        use_cases = product_info.get('use_cases', [])
        
        # Build structured description with proper HTML
        description_sections = []
        
        # Section 1: Product Overview
        overview = f"<p><strong>Premium {product_type} by {brand}</strong></p>"
        if target_keywords:
            overview += f"<p>Experience the perfect {target_keywords[0]} designed specifically for discerning customers. "
        else:
            overview += f"<p>Experience the perfect {product_type.lower()} designed specifically for discerning customers. "
        overview += f"Our {product_type.lower()} combines innovative design, superior quality, and exceptional value to deliver outstanding performance.</p>"
        description_sections.append(overview)
        
        # Section 2: Key Benefits
        if benefits:
            benefits_section = "<p><strong>Why Choose This Product:</strong></p><ul>"
            for benefit in benefits[:4]:  # Max 4 benefits to avoid clutter
                benefits_section += f"<li>{benefit}</li>"
            benefits_section += "</ul>"
            description_sections.append(benefits_section)
        
        # Section 3: Features and Specifications
        if features or specifications:
            features_section = "<p><strong>Advanced Features:</strong></p><ul>"
            
            # Add features
            for feature in features[:3]:
                features_section += f"<li>{feature}</li>"
            
            # Add key specifications
            spec_count = 0
            for key, value in specifications.items():
                if spec_count < 3:  # Limit specifications
                    features_section += f"<li>{key}: {value}</li>"
                    spec_count += 1
            
            features_section += "</ul>"
            description_sections.append(features_section)
        
        # Section 4: Applications and Use Cases
        if use_cases:
            usage_section = "<p><strong>Perfect For:</strong></p><ul>"
            for use_case in use_cases[:3]:
                usage_section += f"<li>{use_case}</li>"
            usage_section += "</ul>"
            description_sections.append(usage_section)
        
        # Section 5: Quality Assurance
        quality_section = "<p><strong>Quality You Can Trust:</strong></p>"
        quality_section += "<p>Every product undergoes rigorous quality testing to ensure it meets our high standards. "
        quality_section += "Designed for the Indian market with attention to local preferences and usage patterns.</p>"
        description_sections.append(quality_section)
        
        # Section 6: Care Instructions (if applicable)
        care_section = "<p><strong>Usage Guidelines:</strong></p>"
        care_section += f"<p>For optimal performance and longevity, follow the included instructions. "
        care_section += f"Our {product_type.lower()} is designed for easy maintenance and long-term reliability.</p>"
        description_sections.append(care_section)
        
        # Combine all sections
        full_description = "\n\n".join(description_sections)
        
        # Validate compliance
        compliance_check = self._validate_description_compliance(full_description)
        keyword_analysis = self._calculate_keyword_density(full_description, target_keywords)
        
        return {
            'description': full_description,
            'character_count': len(full_description),
            'word_count': len(full_description.split()),
            'compliance_score': compliance_check['score'],
            'compliance_issues': compliance_check['issues'],
            'keyword_analysis': keyword_analysis,
            'html_validation': self._validate_html_tags(full_description),
            'is_compliant': compliance_check['score'] >= 80
        }

    def _clean_title_formatting(self, title: str) -> str:
        """Clean and format title according to Amazon standards"""
        # Remove extra spaces
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Ensure proper capitalization (title case for main words)
        words = title.split()
        cleaned_words = []
        
        # Words that should stay lowercase (unless first word)
        lowercase_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in lowercase_words:
                cleaned_words.append(word.capitalize())
            else:
                cleaned_words.append(word.lower())
        
        return ' '.join(cleaned_words)

    def _validate_title_compliance(self, title: str) -> Dict:
        """Validate title against Amazon's listing policies"""
        issues = []
        suggestions = []
        score = 100
        
        # Check length
        if len(title) > self.title_rules['max_length']:
            issues.append(f"Title exceeds maximum length: {len(title)}/{self.title_rules['max_length']} characters")
            suggestions.append("Shorten title by removing non-essential descriptive words")
            score -= 25
        elif len(title) < 20:
            issues.append("Title is too short - may not provide enough information")
            suggestions.append("Add more descriptive elements to reach 50-150 characters")
            score -= 15
        
        # Check banned words
        title_lower = title.lower()
        banned_found = []
        for banned_word in self.title_rules['banned_words']:
            if banned_word in title_lower:
                banned_found.append(banned_word)
        
        if banned_found:
            issues.append(f"Contains banned promotional words: {', '.join(banned_found)}")
            suggestions.append("Remove promotional language and focus on product features")
            score -= len(banned_found) * 10
        
        # Check forbidden symbols
        forbidden_found = []
        for symbol in self.title_rules['forbidden_symbols']:
            if symbol in title:
                forbidden_found.append(symbol)
        
        if forbidden_found:
            issues.append(f"Contains forbidden symbols: {', '.join(forbidden_found)}")
            suggestions.append("Remove special characters and symbols")
            score -= len(forbidden_found) * 5
        
        # Check for ALL CAPS (except for short brand names)
        words = title.split()
        all_caps_words = [word for word in words if word.isupper() and len(word) > 3]
        if len(all_caps_words) > 2:
            issues.append("Excessive use of capital letters")
            suggestions.append("Use proper title case instead of all capitals")
            score -= 10
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions
        }

    def _validate_bullet_compliance(self, bullet: str) -> Dict:
        """Validate bullet point compliance with Amazon policies"""
        issues = []
        score = 100
        
        # Check length
        if len(bullet) > self.bullet_rules['max_length']:
            issues.append(f"Bullet exceeds maximum length: {len(bullet)}/{self.bullet_rules['max_length']} characters")
            score -= 20
        elif len(bullet) < self.bullet_rules['min_length']:
            issues.append(f"Bullet is too short: {len(bullet)}/{self.bullet_rules['min_length']} characters minimum")
            score -= 10
        
        # Check banned phrases
        bullet_lower = bullet.lower()
        banned_found = []
        for banned_phrase in self.bullet_rules['banned_phrases']:
            if banned_phrase in bullet_lower:
                banned_found.append(banned_phrase)
        
        if banned_found:
            issues.append(f"Contains banned promotional phrases: {', '.join(banned_found)}")
            score -= len(banned_found) * 15
        
        # Check if bullet starts with benefit (good practice)
        benefit_starters = ['superior', 'advanced', 'premium', 'enhanced', 'professional', 'durable', 'reliable']
        starts_with_benefit = any(bullet.lower().startswith(starter) for starter in benefit_starters)
        
        if not starts_with_benefit and not bullet.isupper()[:20]:  # Unless it's a feature callout
            issues.append("Consider starting with a clear benefit statement")
            score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues
        }

    def _validate_description_compliance(self, description: str) -> Dict:
        """Validate description compliance with Amazon HTML and content policies"""
        issues = []
        score = 100
        
        # Check length limits
        if len(description) > self.description_rules['max_length']:
            issues.append(f"Description exceeds maximum length: {len(description)}/{self.description_rules['max_length']} characters")
            score -= 20
        elif len(description) < self.description_rules['min_length']:
            issues.append(f"Description too short: {len(description)}/{self.description_rules['min_length']} minimum")
            score -= 15
        
        # Check for banned HTML
        banned_html_found = []
        for banned_html in self.description_rules['banned_html']:
            if banned_html in description.lower():
                banned_html_found.append(banned_html)
        
        if banned_html_found:
            issues.append(f"Contains banned HTML elements: {', '.join(banned_html_found)}")
            score -= 30
        
        # Check for banned content
        description_lower = description.lower()
        banned_content_found = []
        
        # Check for contact info patterns
        if re.search(r'\b\d{10}\b|\b\d{3}-\d{3}-\d{4}\b', description):
            banned_content_found.append("phone numbers")
        
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', description):
            banned_content_found.append("email addresses")
        
        if 'http' in description_lower or 'www.' in description_lower:
            banned_content_found.append("external links")
        
        if banned_content_found:
            issues.append(f"Contains banned content: {', '.join(banned_content_found)}")
            score -= 25
        
        return {
            'score': max(0, score),
            'issues': issues
        }

    def _validate_html_tags(self, html_content: str) -> Dict:
        """Validate HTML tags in description"""
        # Find all HTML tags
        tags = re.findall(r'<[^>]+>', html_content)
        
        invalid_tags = []
        unclosed_tags = []
        
        # Check for allowed tags only
        for tag in tags:
            tag_name = re.search(r'</?(\w+)', tag)
            if tag_name:
                tag_name = tag_name.group(1).lower()
                if f'<{tag_name}>' not in self.description_rules['allowed_html']:
                    invalid_tags.append(tag)
        
        # Basic check for unclosed tags (simplified)
        open_tags = re.findall(r'<(\w+)>', html_content)
        close_tags = re.findall(r'</(\w+)>', html_content)
        
        for open_tag in open_tags:
            if open_tag.lower() not in ['br', 'p'] and close_tags.count(open_tag) < open_tags.count(open_tag):
                unclosed_tags.append(open_tag)
        
        return {
            'valid': len(invalid_tags) == 0 and len(unclosed_tags) == 0,
            'invalid_tags': invalid_tags,
            'unclosed_tags': unclosed_tags,
            'total_tags': len(tags)
        }

    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict:
        """Calculate keyword density for SEO optimization"""
        # Remove HTML tags for accurate word count
        clean_text = re.sub(r'<[^>]+>', '', text)
        words = clean_text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        keyword_analysis = {}
        
        for keyword in keywords[:5]:  # Analyze top 5 keywords
            keyword_lower = keyword.lower()
            
            # Count exact phrase occurrences
            exact_count = clean_text.lower().count(keyword_lower)
            
            # Count individual word occurrences
            keyword_words = keyword_lower.split()
            word_occurrences = sum(words.count(word) for word in keyword_words)
            
            # Calculate densities
            exact_density = (exact_count / total_words) * 100 if exact_count > 0 else 0
            word_density = (word_occurrences / total_words) * 100
            
            keyword_analysis[keyword] = {
                'exact_phrase_count': exact_count,
                'individual_word_count': word_occurrences,
                'exact_phrase_density': round(exact_density, 2),
                'word_density': round(word_density, 2),
                'optimization_status': self._get_density_status(exact_density)
            }
        
        return keyword_analysis

    def _get_density_status(self, density: float) -> str:
        """Get optimization status based on keyword density"""
        if density == 0:
            return "Missing - add keyword naturally"
        elif density < 0.5:
            return "Low - consider adding more mentions"
        elif 0.5 <= density <= 2.0:
            return "Optimal - good keyword usage"
        elif 2.0 < density <= 3.0:
            return "High - monitor for over-optimization"
        else:
            return "Excessive - reduce keyword usage"

    def _get_bullet_recommendations(self, validated_bullets: List[Dict]) -> List[str]:
        """Generate recommendations for bullet point improvement"""
        recommendations = []
        
        # Check average length
        avg_length = sum(b['character_count'] for b in validated_bullets) / len(validated_bullets)
        if avg_length < 100:
            recommendations.append("Consider adding more detail to bullet points for better information value")
        elif avg_length > 800:
            recommendations.append("Consider shortening bullet points for better readability")
        
        # Check compliance scores
        low_score_count = len([b for b in validated_bullets if b['compliance_score'] < 80])
        if low_score_count > 0:
            recommendations.append(f"{low_score_count} bullet(s) need compliance improvements")
        
        # Check for benefit focus
        benefit_keywords = ['superior', 'advanced', 'premium', 'enhanced', 'professional']
        bullets_with_benefits = sum(1 for b in validated_bullets 
                                  if any(keyword in b['bullet'].lower() for keyword in benefit_keywords))
        
        if bullets_with_benefits < 3:
            recommendations.append("Consider leading more bullets with clear benefit statements")
        
        return recommendations

# Global instance
ai_listing_builder = AmazonListingBuilder()