import google.generativeai as genai
import os

def configure_api():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def generate_sales_pitch(lead_name: str, category: str, comments: str, po_value: float = 0) -> str:
    if not configure_api():
        return "🔒 AI Assistant is currently unavailable. Please check API configuration."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = f"""
        You are OATEY's elite B2B sales strategist, specialized in plant-based dairy alternatives.
        
        **OATEY PRODUCT PORTFOLIO:**
        🥛 **Core B2B Products**: Premium Oat Milk & Millet Milk (Bulk for cafes, hotels, restaurants)
        🍫 **RTD Collection**: 200ml Tetra Paks - Chocolate, Coffee (10g protein), Kesar Badam
        
        **COMPETITIVE ADVANTAGES:**
        - 100% Plant-based, sustainable alternative to dairy
        - Indian-made, supporting local economy
        - Health-conscious formulations with added nutrition
        - Scalable B2B solutions with flexible packaging
        - Cost-effective compared to imported alternatives
        
        **LEAD ANALYSIS:**
        - **Company**: {lead_name}
        - **Category**: {category}
        - **Expected Value**: ₹{po_value:,.0f}
        - **Current Status**: {comments}
        
        **TASK**: Create a comprehensive, actionable sales strategy using this structure:
        
        ### 🎯 Lead Assessment & Opportunity Analysis
        ### 💡 Tailored Value Proposition
        ### 📋 Specific Action Plan & Timeline
        ### 🔥 Key Talking Points & Objection Handling
        
        Make it specific, actionable, and ready for immediate implementation.
        """
        
        response = model.generate_content(prompt)
        return response.text if response and response.text else "⚠️ AI Assistant returned an empty response."
        
    except Exception as e:
        return f"⚠️ Error generating AI insight: {str(e)}"
