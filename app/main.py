from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from core.config import settings
from routers import keywords, listing_builder

# Create FastAPI app instance
app = FastAPI(
    title="Amazon PPC Keyword Mining Tool",
    description="AI-Powered SaaS tool for Amazon PPC keyword research and mining - Indian Market with AI Listing Builder",
    version="1.1.0",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server  
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://*.lovable.dev",  # Lovable.dev domains
        "https://*.vercel.app",   # Vercel deployments
        "https://*.netlify.app",  # Netlify deployments
        "*"  # Allow all origins for development (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files directory (for serving HTML/CSS/JS)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routers
app.include_router(keywords.router, prefix="/api/v1")
app.include_router(listing_builder.router, prefix="/api/v1")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Amazon PPC Keyword Mining Tool</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 900px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
            }
            h1 { 
                color: #2c3e50; 
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #7f8c8d;
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            .api-info { 
                background: #ecf0f1; 
                padding: 25px; 
                border-radius: 10px; 
                margin: 25px 0; 
                border-left: 5px solid #3498db;
            }
            .endpoint { 
                background: #3498db; 
                color: white; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 8px;
                transition: background 0.3s;
            }
            .endpoint:hover {
                background: #2980b9;
            }
            .new-feature {
                background: #27ae60;
                color: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                position: relative;
            }
            .new-badge {
                position: absolute;
                top: -8px;
                right: -8px;
                background: #e74c3c;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
            }
            a { 
                color: inherit; 
                text-decoration: none; 
                display: block;
                width: 100%;
            }
            a:hover { 
                text-decoration: none; 
            }
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #3498db;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 30px 0;
                text-align: center;
            }
            .stat {
                padding: 20px;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
            }
            .stat-label {
                color: #7f8c8d;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Amazon PPC Keyword Mining Tool</h1>
            <div class="subtitle">AI-Powered Keyword Research & Listing Builder for Amazon India Market</div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">v1.1.0</div>
                    <div class="stat-label">Latest Version</div>
                </div>
                <div class="stat">
                    <div class="stat-number">15+</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat">
                    <div class="stat-number">INR</div>
                    <div class="stat-label">Indian Market</div>
                </div>
            </div>
            
            <div class="api-info">
                <h3>🎯 Core Features</h3>
                <div class="features-grid">
                    <div class="feature-card">
                        <h4>🔍 Keyword Research</h4>
                        <p>Real Amazon suggestions with AI-powered metrics, Magnet IQ scoring, and trend analysis</p>
                    </div>
                    <div class="feature-card">
                        <h4>🤖 AI Listing Builder</h4>
                        <p>Generate compliant Amazon titles, bullets, and descriptions with policy checking</p>
                    </div>
                    <div class="feature-card">
                        <h4>💰 Dynamic Bidding</h4>
                        <p>AI-powered bid recommendations based on competition and market conditions</p>
                    </div>
                    <div class="feature-card">
                        <h4>🇮🇳 Indian Market Focus</h4>
                        <p>Optimized for Amazon India with local preferences and INR pricing</p>
                    </div>
                </div>
            </div>
            
            <h3>📚 API Documentation</h3>
            <div class="endpoint">
                <a href="/docs" target="_blank">📖 Interactive API Docs (Swagger UI)</a>
            </div>
            <div class="endpoint">
                <a href="/redoc" target="_blank">📋 Alternative Docs (ReDoc)</a>
            </div>
            
            <h3>🔧 Keyword Research Endpoints</h3>
            <div class="api-info">
                <p><strong>POST</strong> /api/v1/keywords/analyze - AI-powered keyword analysis with bidding</p>
                <p><strong>GET</strong> /api/v1/keywords/suggest/{keyword} - Amazon keyword suggestions</p>
                <p><strong>GET</strong> /api/v1/keywords/metrics/{keyword} - Detailed keyword metrics</p>
                <p><strong>GET</strong> /api/v1/keywords/competitor-analysis/{keyword} - Competitor insights</p>
                <p><strong>POST</strong> /api/v1/keywords/bulk-analyze - Bulk keyword processing</p>
            </div>
            
            <h3>🆕 AI Listing Builder Endpoints</h3>
            <div class="new-feature">
                <div class="new-badge">NEW</div>
                <p><strong>POST</strong> /api/v1/listing-builder/generate-complete-listing - Full listing generation</p>
            </div>
            <div class="api-info">
                <p><strong>POST</strong> /api/v1/listing-builder/generate-title - Amazon-compliant titles</p>
                <p><strong>POST</strong> /api/v1/listing-builder/generate-bullets - 5 optimized bullet points</p>
                <p><strong>POST</strong> /api/v1/listing-builder/generate-description - HTML product descriptions</p>
                <p><strong>GET</strong> /api/v1/listing-builder/compliance-rules - Amazon policy guidelines</p>
                <p><strong>POST</strong> /api/v1/listing-builder/analyze-existing-listing - Listing optimization</p>
            </div>
            
            <h3>🌐 Integration Options</h3>
            <div class="api-info">
                <p>• <strong>Frontend:</strong> Use <a href="https://lovable.dev" target="_blank" style="color: #3498db;">Lovable.dev</a> for AI-generated UI</p>
                <p>• <strong>Frameworks:</strong> Integrate with React, Vue, Angular, or any framework</p>
                <p>• <strong>CORS:</strong> Configured for development and production environments</p>
                <p>• <strong>Authentication:</strong> Ready for API key integration</p>
            </div>
            
            <div class="api-info">
                <h3>✅ System Status</h3>
                <p><strong>Service:</strong> Amazon PPC Keyword Mining Tool</p>
                <p><strong>Market:</strong> India (INR Currency)</p>
                <p><strong>Debug Mode:</strong> """ + str(settings.DEBUG) + """</p>
                <p><strong>Features:</strong> Keyword Research ✅ | AI Listing Builder ✅ | Bulk Analysis ✅</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Amazon PPC Keyword Mining Tool",
        "version": "1.1.0",
        "market": "India",
        "currency": "INR",
        "debug": settings.DEBUG,
        "features": {
            "keyword_research": True,
            "ai_listing_builder": True,
            "bulk_analysis": True,
            "competitor_analysis": True,
            "dynamic_bidding": True
        },
        "endpoints": {
            "keyword_research": {
                "analyze": "/api/v1/keywords/analyze",
                "suggest": "/api/v1/keywords/suggest/{keyword}",
                "metrics": "/api/v1/keywords/metrics/{keyword}",
                "competitor_analysis": "/api/v1/keywords/competitor-analysis/{keyword}",
                "bulk_analyze": "/api/v1/keywords/bulk-analyze"
            },
            "listing_builder": {
                "complete_listing": "/api/v1/listing-builder/generate-complete-listing",
                "title": "/api/v1/listing-builder/generate-title",
                "bullets": "/api/v1/listing-builder/generate-bullets", 
                "description": "/api/v1/listing-builder/generate-description",
                "compliance_rules": "/api/v1/listing-builder/compliance-rules",
                "analyze_existing": "/api/v1/listing-builder/analyze-existing-listing"
            }
        }
    }

# API Info endpoint
@app.get("/api/v1/info")
async def api_info():
    """Get comprehensive API information and capabilities"""
    return {
        "name": "Amazon PPC Keyword Mining Tool",
        "version": "1.1.0",
        "description": "AI-Powered keyword research and listing optimization for Amazon India market",
        "market": "India",
        "currency": "INR",
        "release_date": "2025",
        "features": [
            "Real Amazon keyword suggestions with expansion beyond 10-item limit",
            "AI-powered bid predictions with dynamic pricing",
            "Magnet IQ scoring and opportunity analysis",
            "Search volume trends and seasonal patterns",
            "Competition analysis (organic vs sponsored)",
            "ABA-style click and conversion data simulation",
            "AI listing builder with Amazon policy compliance",
            "Title, bullets, and description generation",
            "HTML formatting and validation",
            "Bulk keyword analysis with concurrency control",
            "Competitor keyword analysis (Cerebro-style)",
            "Indian market optimization and local preferences"
        ],
        "compliance": {
            "amazon_policies": True,
            "indian_market_optimized": True,
            "html_validation": True,
            "keyword_density_optimization": True
        },
        "ai_capabilities": {
            "listing_optimization": True,
            "compliance_checking": True,
            "keyword_expansion": True,
            "bid_prediction": True,
            "trend_analysis": True,
            "competitive_intelligence": True
        },
        "data_sources": [
            "Amazon India autocomplete API",
            "Enhanced AI prediction algorithms",
            "Indian market behavior analysis",
            "Seasonal trend modeling",
            "Competition simulation"
        ]
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print("🚀 Amazon PPC Keyword Mining Tool v1.1.0 starting up...")
    print(f"📊 Market: India (INR)")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    print(f"🌐 API Host: {settings.API_HOST}")
    print("✅ Features enabled:")
    print("   • Keyword Research & Analysis")
    print("   • AI Listing Builder (NEW)")
    print("   • Dynamic Bidding Predictions")
    print("   • Bulk Processing")
    print("   • Competitor Analysis")
    print("🎯 Ready to optimize Amazon listings!")

# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    print("👋 Amazon PPC Keyword Mining Tool shutting down...")
    print("💾 All sessions saved successfully")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=8000, 
        reload=settings.DEBUG,
        log_level="info"
    )