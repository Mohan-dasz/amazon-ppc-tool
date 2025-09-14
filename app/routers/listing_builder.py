from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from services.ai_listing_builder import ai_listing_builder

router = APIRouter(prefix="/listing-builder", tags=["AI Listing Builder"])

class ProductInfo(BaseModel):
    brand: str = Field(..., description="Product brand name", min_length=1, max_length=50)
    product_type: str = Field(..., description="Type of product (e.g., 'Wireless Headphones')", min_length=1, max_length=100)
    key_features: List[str] = Field(..., description="Key product features", min_items=1, max_items=10)
    benefits: List[str] = Field(..., description="Product benefits", min_items=1, max_items=8)
    target_keywords: List[str] = Field(..., description="Target keywords for SEO", min_items=1, max_items=10)
    specifications: Optional[Dict[str, str]] = Field(default={}, description="Technical specifications")
    features: Optional[List[str]] = Field(default=[], description="Additional features")
    use_cases: Optional[List[str]] = Field(default=[], description="Primary use cases")
    color: Optional[str] = Field(default="", description="Product color")
    size: Optional[str] = Field(default="", description="Product size")
    warranty: Optional[str] = Field(default="", description="Warranty information")

class TitleResponse(BaseModel):
    title: str
    character_count: int
    compliance_score: float
    compliance_issues: List[str]
    suggestions: List[str]
    amazon_policy_compliant: bool

class BulletResponse(BaseModel):
    bullet: str
    bullet_number: int
    character_count: int
    compliance_score: float
    issues: List[str]
    is_compliant: bool

class BulletsResponse(BaseModel):
    bullets: List[BulletResponse]
    total_bullets: int
    overall_compliance_score: float
    all_bullets_compliant: bool
    recommendations: List[str]

class DescriptionResponse(BaseModel):
    description: str
    character_count: int
    word_count: int
    compliance_score: float
    compliance_issues: List[str]
    keyword_analysis: Dict
    html_validation: Dict
    is_compliant: bool

class CompleteListingResponse(BaseModel):
    title: TitleResponse
    bullets: BulletsResponse
    description: DescriptionResponse
    overall_compliance_score: float
    amazon_policy_grade: str
    ready_for_amazon: bool

@router.post("/generate-title", response_model=TitleResponse)
async def generate_product_title(product_info: ProductInfo):
    """
    Generate Amazon-compliant product title with compliance checking
    
    Creates optimized titles following Amazon's guidelines:
    - Maximum 200 characters
    - No promotional language
    - Proper keyword integration
    - Indian market optimization
    """
    
    try:
        title_data = await ai_listing_builder.generate_compliant_title(product_info.dict())
        
        return TitleResponse(
            title=title_data['title'],
            character_count=title_data['character_count'],
            compliance_score=title_data['compliance_score'],
            compliance_issues=title_data['compliance_issues'],
            suggestions=title_data['suggestions'],
            amazon_policy_compliant=title_data['amazon_policy_compliant']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating title: {str(e)}"
        )

@router.post("/generate-bullets", response_model=BulletsResponse)
async def generate_bullet_points(product_info: ProductInfo):
    """
    Generate 5 Amazon-compliant bullet points with benefit focus
    
    Creates bullet points that:
    - Focus on customer benefits
    - Follow Amazon's content guidelines
    - Optimize for search keywords
    - Meet character limits
    """
    
    try:
        bullets_data = await ai_listing_builder.generate_compliant_bullets(product_info.dict())
        
        bullet_responses = []
        for bullet_info in bullets_data['bullets']:
            bullet_responses.append(BulletResponse(
                bullet=bullet_info['bullet'],
                bullet_number=bullet_info['bullet_number'],
                character_count=bullet_info['character_count'],
                compliance_score=bullet_info['compliance_score'],
                issues=bullet_info['issues'],
                is_compliant=bullet_info['is_compliant']
            ))
        
        return BulletsResponse(
            bullets=bullet_responses,
            total_bullets=bullets_data['total_bullets'],
            overall_compliance_score=bullets_data['overall_compliance_score'],
            all_bullets_compliant=bullets_data['all_bullets_compliant'],
            recommendations=bullets_data['recommendations']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating bullets: {str(e)}"
        )

@router.post("/generate-description", response_model=DescriptionResponse)
async def generate_product_description(product_info: ProductInfo):
    """
    Generate Amazon-compliant product description with HTML formatting
    
    Creates descriptions that:
    - Use proper HTML structure
    - Follow Amazon's content policies
    - Optimize keyword density
    - Include all required sections
    """
    
    try:
        desc_data = await ai_listing_builder.generate_compliant_description(product_info.dict())
        
        return DescriptionResponse(
            description=desc_data['description'],
            character_count=desc_data['character_count'],
            word_count=desc_data['word_count'],
            compliance_score=desc_data['compliance_score'],
            compliance_issues=desc_data['compliance_issues'],
            keyword_analysis=desc_data['keyword_analysis'],
            html_validation=desc_data['html_validation'],
            is_compliant=desc_data['is_compliant']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating description: {str(e)}"
        )

@router.post("/generate-complete-listing", response_model=CompleteListingResponse)
async def generate_complete_listing(product_info: ProductInfo):
    """
    Generate complete Amazon listing (title + bullets + description) with full compliance analysis
    
    This is the main endpoint that creates a complete, Amazon-ready product listing
    with comprehensive compliance checking and optimization recommendations.
    """
    
    try:
        # Generate all components
        title_data = await ai_listing_builder.generate_compliant_title(product_info.dict())
        bullets_data = await ai_listing_builder.generate_compliant_bullets(product_info.dict())
        description_data = await ai_listing_builder.generate_compliant_description(product_info.dict())
        
        # Calculate overall compliance
        overall_score = (
            title_data['compliance_score'] + 
            bullets_data['overall_compliance_score'] + 
            description_data['compliance_score']
        ) / 3
        
        # Determine grade and readiness
        if overall_score >= 95:
            grade = "A+"
            ready = True
        elif overall_score >= 90:
            grade = "A"
            ready = True
        elif overall_score >= 85:
            grade = "B+"
            ready = True
        elif overall_score >= 80:
            grade = "B"
            ready = True
        elif overall_score >= 70:
            grade = "C"
            ready = False
        else:
            grade = "D"
            ready = False
        
        # Prepare response data
        title_response = TitleResponse(
            title=title_data['title'],
            character_count=title_data['character_count'],
            compliance_score=title_data['compliance_score'],
            compliance_issues=title_data['compliance_issues'],
            suggestions=title_data['suggestions'],
            amazon_policy_compliant=title_data['amazon_policy_compliant']
        )
        
        bullet_responses = []
        for bullet_info in bullets_data['bullets']:
            bullet_responses.append(BulletResponse(
                bullet=bullet_info['bullet'],
                bullet_number=bullet_info['bullet_number'],
                character_count=bullet_info['character_count'],
                compliance_score=bullet_info['compliance_score'],
                issues=bullet_info['issues'],
                is_compliant=bullet_info['is_compliant']
            ))
        
        bullets_response = BulletsResponse(
            bullets=bullet_responses,
            total_bullets=bullets_data['total_bullets'],
            overall_compliance_score=bullets_data['overall_compliance_score'],
            all_bullets_compliant=bullets_data['all_bullets_compliant'],
            recommendations=bullets_data['recommendations']
        )
        
        description_response = DescriptionResponse(
            description=description_data['description'],
            character_count=description_data['character_count'],
            word_count=description_data['word_count'],
            compliance_score=description_data['compliance_score'],
            compliance_issues=description_data['compliance_issues'],
            keyword_analysis=description_data['keyword_analysis'],
            html_validation=description_data['html_validation'],
            is_compliant=description_data['is_compliant']
        )
        
        return CompleteListingResponse(
            title=title_response,
            bullets=bullets_response,
            description=description_response,
            overall_compliance_score=round(overall_score, 1),
            amazon_policy_grade=grade,
            ready_for_amazon=ready
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating complete listing: {str(e)}"
        )

@router.get("/compliance-rules")
async def get_amazon_compliance_rules():
    """
    Get Amazon listing compliance rules and guidelines
    
    Returns the current ruleset used for compliance checking
    to help users understand what makes a listing compliant.
    """
    
    return {
        "title_rules": {
            "max_length": 200,
            "banned_words_examples": ["best", "cheapest", "#1", "sale", "deal"],
            "required_elements": ["brand", "product_type", "key_feature"],
            "forbidden_symbols": ["!", "?", "®", "™", "©", "*"],
            "guidelines": [
                "Use title case (not ALL CAPS)",
                "Include brand name at the beginning",
                "Specify product type clearly",
                "Add key differentiating features",
                "Avoid promotional language"
            ]
        },
        "bullet_rules": {
            "max_length": 1000,
            "max_bullets": 5,
            "min_length": 50,
            "focus": "Benefits over features",
            "banned_phrases_examples": ["money back guarantee", "best price"],
            "guidelines": [
                "Start with clear benefit statements",
                "Use proper capitalization",
                "Focus on customer value",
                "Avoid promotional language",
                "Keep within character limits"
            ]
        },
        "description_rules": {
            "max_length": 2000,
            "min_length": 200,
            "allowed_html": ["<p>", "<br>", "<b>", "<strong>", "<i>", "<em>", "<ul>", "<li>"],
            "banned_content": ["contact info", "external links", "pricing"],
            "required_sections": ["product_overview", "key_benefits"],
            "guidelines": [
                "Use proper HTML formatting",
                "Include structured sections",
                "Optimize keyword density (0.5-2%)",
                "Avoid banned content types",
                "Focus on product value proposition"
            ]
        },
        "indian_market_tips": [
            "Consider local preferences and terminology",
            "Mention suitability for Indian conditions",
            "Use value-focused language",
            "Consider family-friendly positioning",
            "Highlight durability and quality"
        ]
    }

@router.post("/analyze-existing-listing")
async def analyze_existing_listing(
    title: str = Query(..., description="Existing product title"),
    bullets: List[str] = Query(..., description="Existing bullet points"),
    description: str = Query(..., description="Existing product description")
):
    """
    Analyze an existing Amazon listing for compliance and optimization opportunities
    
    Useful for optimizing current listings or analyzing competitor products.
    """
    
    try:
        # Analyze each component
        title_validation = ai_listing_builder._validate_title_compliance(title)
        
        bullet_analyses = []
        for i, bullet in enumerate(bullets):
            bullet_validation = ai_listing_builder._validate_bullet_compliance(bullet)
            bullet_analyses.append({
                "bullet_number": i + 1,
                "bullet": bullet,
                "compliance_score": bullet_validation['score'],
                "issues": bullet_validation['issues'],
                "character_count": len(bullet)
            })
        
        desc_validation = ai_listing_builder._validate_description_compliance(description)
        html_validation = ai_listing_builder._validate_html_tags(description)
        
        # Calculate overall score
        bullet_avg_score = sum(b['compliance_score'] for b in bullet_analyses) / len(bullet_analyses) if bullet_analyses else 0
        overall_score = (title_validation['score'] + bullet_avg_score + desc_validation['score']) / 3
        
        return {
            "overall_analysis": {
                "compliance_score": round(overall_score, 1),
                "grade": "A" if overall_score >= 90 else "B" if overall_score >= 80 else "C" if overall_score >= 70 else "D",
                "amazon_ready": overall_score >= 80
            },
            "title_analysis": {
                "title": title,
                "character_count": len(title),
                "compliance_score": title_validation['score'],
                "issues": title_validation['issues'],
                "suggestions": title_validation['suggestions']
            },
            "bullets_analysis": bullet_analyses,
            "description_analysis": {
                "character_count": len(description),
                "compliance_score": desc_validation['score'],
                "issues": desc_validation['issues'],
                "html_validation": html_validation
            },
            "improvement_recommendations": [
                "Focus on highest-impact compliance issues first",
                "Ensure all components meet minimum score of 80",
                "Optimize keyword usage without over-stuffing",
                "Test different variations for better performance"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing existing listing: {str(e)}"
        )