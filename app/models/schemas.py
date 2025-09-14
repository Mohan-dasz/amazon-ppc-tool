from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class CompetitionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TrendDirection(str, Enum):
    UP = "up"
    STABLE = "stable"
    DOWN = "down"

class KeywordData(BaseModel):
    keyword: str = Field(..., description="The keyword phrase")
    search_volume: int = Field(..., description="Estimated monthly search volume")
    cpc: float = Field(..., description="Estimated cost per click in INR")
    rank: int = Field(..., description="Rank position in results")
    competition: CompetitionLevel = Field(..., description="Competition level")
    suggested_bid: float = Field(..., description="AI-recommended optimal bid in INR")
    intent_score: int = Field(..., ge=1, le=10, description="Purchase intent score (1-10)")
    
    # Enhanced AI Fields
    ai_category: Optional[str] = Field(None, description="AI-detected product category")
    ai_insights: Optional[str] = Field(None, description="AI reasoning and insights")
    magnet_iq_score: Optional[int] = Field(None, ge=1, le=100, description="Opportunity score (1-100)")
    
    # Trend Analysis
    trend_percentage: Optional[float] = Field(None, description="Search volume trend percentage")
    trend_direction: Optional[TrendDirection] = Field(None, description="Trend direction")
    seasonal_factor: Optional[float] = Field(None, description="Seasonal influence factor")
    
    # Competition Analysis  
    organic_competitors: Optional[int] = Field(None, description="Number of organic competitors")
    sponsored_competitors: Optional[int] = Field(None, description="Number of sponsored competitors")
    competition_score: Optional[float] = Field(None, ge=0, le=1, description="Competition intensity (0-1)")
    
    # ABA-Style Data
    aba_click_share: Optional[float] = Field(None, description="Estimated click share percentage")
    aba_conversion_share: Optional[float] = Field(None, description="Estimated conversion share percentage")
    sponsored_rank: Optional[int] = Field(None, description="Average sponsored ad rank")
    
    # Bidding Strategy
    conservative_bid: Optional[float] = Field(None, description="Conservative bid recommendation")
    aggressive_bid: Optional[float] = Field(None, description="Aggressive bid recommendation")
    bid_confidence: Optional[float] = Field(None, ge=0, le=1, description="Bid prediction confidence")
    
    # Market Data
    currency: str = Field(default="INR", description="Currency code")
    market: str = Field(default="India", description="Target market")
    data_source: Optional[str] = Field(None, description="Data source identifier")

class KeywordSuggestionResponse(BaseModel):
    seed_keyword: str = Field(..., description="Original seed keyword")
    suggestions: list[str] = Field(..., description="List of keyword suggestions")
    total_found: int = Field(..., description="Total number of suggestions found")
    market: str = Field(default="India", description="Target market")
    source: str = Field(default="Amazon India + AI Expansion", description="Data source")

class KeywordMetricsResponse(BaseModel):
    keyword: str = Field(..., description="The analyzed keyword")
    metrics: Dict[str, Any] = Field(..., description="Comprehensive keyword metrics")
    analysis_timestamp: Optional[float] = Field(None, description="Analysis timestamp")

class CompetitorAnalysisResponse(BaseModel):
    primary_keyword: str = Field(..., description="Primary seed keyword")
    competitor_keywords: list[KeywordData] = Field(..., description="Related competitor keywords")
    total_found: int = Field(..., description="Total keywords found")
    analysis_summary: Dict[str, Any] = Field(..., description="Summary statistics")
    market: str = Field(default="India", description="Target market")
    currency: str = Field(default="INR", description="Currency code")
    timestamp: Optional[float] = Field(None, description="Analysis timestamp")

class BulkAnalysisRequest(BaseModel):
    keywords: list[str] = Field(..., min_items=1, max_items=100, description="List of keywords to analyze")
    include_competitor_analysis: bool = Field(default=False, description="Include competitor analysis")

class BulkAnalysisResponse(BaseModel):
    total_keywords: int = Field(..., description="Total keywords analyzed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    failed_analyses: int = Field(..., description="Number of failed analyses")
    results: list[KeywordData] = Field(..., description="Analysis results")
    analysis_summary: Dict[str, Any] = Field(..., description="Overall summary statistics")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")

class APIHealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    market: str = Field(..., description="Target market")
    currency: str = Field(..., description="Default currency")
    debug: bool = Field(..., description="Debug mode status")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints")
    features: Dict[str, bool] = Field(..., description="Available features")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Detailed error information")
    timestamp: Optional[float] = Field(None, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")

# Validation models for request/response
class HTTPValidationError(BaseModel):
    detail: list[Dict[str, Any]] = Field(..., description="Validation error details")

class ValidationError(BaseModel):
    loc: list[str] = Field(..., description="Error location")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")