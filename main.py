import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import base64
import json

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Utility Functions (Moved for correct dependency order) ---
def hash_password(password: str) -> str:
    """
    Hashes a password using SHA256 for secure storage and comparison.
    NOTE: A salt should be used in a high-security production environment.
    """
    return hashlib.sha256(password.encode()).hexdigest()

# --- Enhanced Configuration ---
class Config:
    """Centralized configuration management with validation."""
    
    # File paths
    DATA_FILE = 'sales_data.xlsx'
    SOURCE_FILE = 'OATEY - Sales Dashboard.xlsx'
    LOGO_FILE = 'Logo PNG Brown.png'
    BACKUP_DIR = 'backups'
    
    # Data validation
    REQUIRED_COLUMNS = ['lead_name', 'category', 'status', 'salesperson']
    STATUS_OPTIONS = ['Yet to approach', 'Ongoing', 'Closed (Success)', 'Closed (Unsuccessful)']
    
    SHEET_MAPPING = {
        'B2B_HORECA': 'B2B HORECA',
        'B2B_Corporate': 'B2B Corporate', 
        'Collaborations': 'Collaborations'
    }
    
    # Performance settings
    MAX_BACKUP_FILES = 10
    DATA_CACHE_TTL = 300  # 5 minutes
    
    @staticmethod
    def ensure_directories() -> None:
        """Ensure required directories exist."""
        Path(Config.BACKUP_DIR).mkdir(exist_ok=True)
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if file exists with enhanced logging."""
        path = Path(filepath)
        exists = path.exists()
        if not exists:
            logger.warning(f"File not found: {filepath}")
        else:
            file_size = path.stat().st_size
            logger.info(f"File found: {filepath} ({file_size} bytes)")
        return exists
    
    @staticmethod
    def get_user_credentials() -> Dict[str, str]:
        """
        Enhanced credential management.
        IMPORTANT: For production, passwords in secrets or env vars MUST be pre-hashed with SHA256.
        """
        try:
            # Primary: Streamlit secrets
            if hasattr(st, 'secrets') and 'user_credentials' in st.secrets:
                creds = dict(st.secrets['user_credentials'])
                logger.info(f"Loaded {len(creds)} user credentials from Streamlit secrets")
                return creds
            
            # Secondary: Environment variables
            creds = {}
            for key, value in os.environ.items():
                if key.startswith('USER_') and not key.endswith('_PASSWORD'):
                    password_key = f"{key}_PASSWORD"
                    if password_key in os.environ:
                        username = key.replace('USER_', '')
                        creds[username] = os.environ[password_key] # Assumes pre-hashed password
            
            if creds:
                logger.info(f"Loaded {len(creds)} user credentials from environment")
                return creds
                
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
    
        # Fallback (development only) with HASHED passwords
        logger.warning("Using fallback credentials - NOT for production!")
        return {
            "Leadership": hash_password("leadpass123"),
            "Ichcha Lizmi": hash_password("ichchapass"), 
            "Avadhut K": hash_password("avadhutpass"),
            "Abhijit": hash_password("abhijitpass")
        }

# --- Enhanced CSS with Modern Design ---
def load_custom_css():
    """Load enhanced CSS with modern design patterns."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* CSS Variables for better maintainability */
    :root {
        --primary-color: #8B4513;
        --primary-light: #CD853F;
        --primary-dark: #654321;
        --secondary-color: #D2B48C;
        --accent-color: #F4A460;
        --success-color: #22c55e;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --info-color: #3b82f6;
        --light-bg: #f8fafc;
        --dark-text: #1e293b;
        --border-radius: 12px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-md: 0 4px 15px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.15);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global Styles */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Enhanced Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 50%, var(--accent-color) 100%);
        padding: 2rem;
        border-radius: var(--border-radius);
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    
    .main-header h1 {
        margin: 0;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .main-header .subtitle {
        opacity: 0.95;
        margin-top: 0.5rem;
        font-size: 1.2rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .kpi-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.75rem;
        box-shadow: var(--shadow-md);
        border: 1px solid #e2e8f0;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--primary-color);
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-light);
    }
    
    .kpi-value {
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--primary-color);
        margin: 0 0 0.5rem 0;
        line-height: 1;
    }
    
    .kpi-label {
        font-size: 0.95rem;
        color: var(--dark-text);
        opacity: 0.8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Login Page Enhancements */
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .login-card {
        background: white;
        padding: 3rem;
        border-radius: 16px;
        box-shadow: var(--shadow-lg);
        border: 1px solid #e2e8f0;
        max-width: 400px;
        width: 100%;
    }
    
    .brand-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.5rem 0;
        text-align: center;
        letter-spacing: -0.025em;
    }
    
    .brand-subtitle {
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Enhanced Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* AI Insight Enhancement */
    .ai-insight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    
    .ai-insight::before {
        content: '🤖';
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    .ai-insight h3 {
        color: white;
        margin-top: 0;
        font-weight: 600;
    }
    
    /* Form Enhancements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(139, 69, 19, 0.1);
    }
    
    /* Data Table Enhancements */
    .dataframe {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        width: 100%;
        border-collapse: collapse;
    }
    .dataframe th, .dataframe td {
        padding: 12px 15px;
        border: 1px solid #e2e8f0;
        text-align: left;
    }
    .dataframe th {
        background-color: var(--light-bg);
        font-weight: 600;
        color: var(--dark-text);
    }
    .dataframe tr:nth-child(even) {
        background-color: #f8fafc;
    }
    
    /* Status Badge Styles */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }
    
    .status-success { background: #dcfce7; color: #166534; }
    .status-ongoing { background: #dbeafe; color: #1d4ed8; }
    .status-pending { background: #fef3c7; color: #92400e; }
    .status-unsuccessful { background: #fee2e2; color: #991b1b; }
    
    /* Sidebar Enhancements */
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid #e2e8f0;
    }
    
    /* Loading States */
    .loading-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: var(--light-bg);
        border-radius: var(--border-radius);
        margin: 1rem 0;
    }
    
    /* Error States */
    .error-container {
        background: #fee2e2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
    }
    
    /* Success States */
    .success-container {
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .kpi-container {
            grid-template-columns: 1fr;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* Animation Classes */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Enhanced Utility Functions ---
def get_base64_of_bin_file(bin_file: str) -> str:
    """Convert binary file to base64 with error handling."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        logger.warning(f"Error encoding file {bin_file}: {e}")
        return ""

def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) if email else True

def validate_phone(phone: str) -> bool:
    """Basic phone number validation."""
    import re
    if not phone:
        return True
    # Remove spaces and special characters for validation
    clean_phone = re.sub(r'[^\d+]', '', phone)
    return len(clean_phone) >= 10

# --- Enhanced API Configuration ---
def configure_api() -> bool:
    """Enhanced API configuration with health checks."""
    try:
        import google.generativeai as genai
        
        api_key = None
        
        # Try multiple sources for API key
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            api_key = st.secrets['GEMINI_API_KEY']
        elif 'GEMINI_API_KEY' in os.environ:
            api_key = os.environ['GEMINI_API_KEY']
        
        if api_key and len(api_key) > 20:  # Basic validation
            genai.configure(api_key=api_key)
            
            # Test API with a simple call
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                test_response = model.generate_content("Test")
                logger.info("Gemini API health check passed")
                return True
            except Exception as e:
                logger.warning(f"Gemini API health check failed: {e}")
                return False
        else:
            logger.warning("Invalid or missing Gemini API key")
            return False
            
    except ImportError:
        logger.warning("google.generativeai package not available")
        return False
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        return False

# --- Enhanced Data Management ---
@st.cache_data(ttl=Config.DATA_CACHE_TTL)
def load_cached_data(file_path: str, file_hash: str) -> pd.DataFrame:
    """Cache data loading for better performance."""
    return pd.read_excel(file_path)

def get_file_hash(file_path: str) -> str:
    """Get file hash for cache invalidation."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def create_empty_dataframe() -> pd.DataFrame:
    """Create standardized empty DataFrame."""
    columns = [
        'lead_id', 'lead_name', 'poc_name', 'contact_no', 'email', 
        'category', 'status', 'salesperson', 'po_value_expected', 
        'comments', 'last_updated', 'ai_pitch', 'created_date',
        'follow_up_date', 'priority', 'source'
    ]
    return pd.DataFrame(columns=columns)

def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate DataFrame structure and data quality."""
    errors = []
    
    # Check required columns
    missing_cols = [col for col in Config.REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    
    # Check data types and ranges
    if 'po_value_expected' in df.columns:
        invalid_po_values = df['po_value_expected'].apply(
            lambda x: pd.isna(x) or (pd.notna(x) and (x < 0 or x > 1e10))
        ).sum()
        if invalid_po_values > 0:
            errors.append(f"Invalid PO values found: {invalid_po_values} records")
    
    # Check for duplicates
    if 'lead_id' in df.columns:
        duplicate_ids = df['lead_id'].duplicated().sum()
        if duplicate_ids > 0:
            errors.append(f"Duplicate lead IDs found: {duplicate_ids}")
    
    return len(errors) == 0, errors

def clean_and_prepare_df(df: pd.DataFrame, category_name: str) -> pd.DataFrame:
    """Enhanced DataFrame cleaning with validation."""
    try:
        if df.empty:
            logger.warning(f"Empty DataFrame for category: {category_name}")
            return create_empty_dataframe()
        
        # Store original state
        original_shape = df.shape
        logger.info(f"Processing {category_name}: {original_shape[0]} rows, {original_shape[1]} columns")
        
        # Enhanced column normalization
        df.columns = (df.columns
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .str.replace(r"['\"\s]+", "_", regex=True)
                        .str.replace(r"[^\w]", "_", regex=True)
                        .str.replace(r"_+", "_", regex=True)
                        .str.strip("_"))
        
        # Comprehensive column mapping
        column_mappings = {
            'pocs_name': 'poc_name',
            'poc_s_name': 'poc_name',
            'pocs_number': 'contact_no',
            'contact_number': 'contact_no',
            'pocs_email': 'email',
            'email_id': 'email',
            'po_expected': 'po_value_expected',
            'expected_po_value': 'po_value_expected',
            'po_value': 'po_value_expected',
            'sales_person': 'salesperson',
            'sales_rep': 'salesperson',
        }
        
        df = df.rename(columns=column_mappings)
        
        # Add metadata
        df['category'] = category_name
        df['created_date'] = df.get('created_date', datetime.now().strftime("%Y-%m-%d"))
        df['last_updated'] = df.get('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        df['ai_pitch'] = df.get('ai_pitch', '')
        df['priority'] = df.get('priority', 'Medium')
        df['source'] = df.get('source', 'Excel Import')
        
        # Data cleaning and validation
        if 'po_value_expected' in df.columns:
            df['po_value_expected'] = pd.to_numeric(df['po_value_expected'], errors='coerce').fillna(0)
            df.loc[df['po_value_expected'] < 0, 'po_value_expected'] = 0
        
        # Clean text fields
        text_columns = ['lead_name', 'poc_name', 'comments', 'salesperson']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df.loc[df[col].isin(['nan', 'None', '']), col] = 'Unknown'
        
        # Remove invalid rows
        initial_count = len(df)
        df = df.dropna(subset=['lead_name'])
        df = df[df['lead_name'].str.len() > 0]
        final_count = len(df)
        
        if initial_count != final_count:
            logger.info(f"Cleaned {initial_count - final_count} invalid rows from {category_name}")
        
        # Validate final DataFrame
        is_valid, validation_errors = validate_dataframe(df)
        if not is_valid:
            logger.warning(f"Validation issues in {category_name}: {validation_errors}")
        
        logger.info(f"Successfully processed {category_name}: {final_count} valid records")
        return df
        
    except Exception as e:
        logger.error(f"Error processing {category_name}: {e}")
        return create_empty_dataframe()

def initialize_from_source() -> pd.DataFrame:
    """Enhanced data initialization with better error recovery."""
    try:
        if not Config.file_exists(Config.SOURCE_FILE):
            logger.error(f"Source file not found: {Config.SOURCE_FILE}")
            return create_empty_dataframe()
        
        xls = pd.ExcelFile(Config.SOURCE_FILE)
        logger.info(f"Source file sheets: {xls.sheet_names}")
        
        all_dfs = []
        processing_summary = {}
        
        for sheet_name, category in Config.SHEET_MAPPING.items():
            try:
                if sheet_name in xls.sheet_names:
                    logger.info(f"Processing sheet: {sheet_name}")
                    df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=1)
                    df_cleaned = clean_and_prepare_df(df, category)
                    
                    if not df_cleaned.empty:
                        all_dfs.append(df_cleaned)
                        processing_summary[category] = len(df_cleaned)
                    else:
                        logger.warning(f"No valid data in sheet: {sheet_name}")
                        processing_summary[category] = 0
                else:
                    logger.warning(f"Sheet not found: {sheet_name}")
                    processing_summary[category] = 0
                    
            except Exception as e:
                logger.error(f"Error processing sheet {sheet_name}: {e}")
                processing_summary[category] = 0
                continue
        
        # Combine and process
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Enhanced deduplication
            combined_df = combined_df.drop_duplicates(
                subset=['lead_name', 'poc_name', 'category'], 
                keep='first'
            )
            
            # Generate proper lead IDs
            combined_df = combined_df.reset_index(drop=True)
            combined_df['lead_id'] = [f"OATEY-{i+1000:04d}" for i in range(len(combined_df))]
            
            # Final validation
            is_valid, errors = validate_dataframe(combined_df)
            if not is_valid:
                logger.warning(f"Data validation issues: {errors}")
            
            # Save with backup
            save_data_safely(combined_df)
            
            logger.info(f"Successfully initialized {len(combined_df)} records")
            logger.info(f"Processing summary: {processing_summary}")
            
            return combined_df
        else:
            logger.error("No valid data found in any sheets")
            return create_empty_dataframe()
            
    except Exception as e:
        logger.error(f"Critical error initializing data: {e}")
        return create_empty_dataframe()

def load_data_safely() -> pd.DataFrame:
    """Enhanced data loading with caching and validation."""
    try:
     # Try cached data first
        if Config.file_exists(Config.DATA_FILE):
            file_hash = get_file_hash(Config.DATA_FILE)
            df = load_cached_data(Config.DATA_FILE, file_hash)

            # --- START OF REPLACEMENT LOGIC ---

            # If loaded from the main data file, still perform a quick cleanup for safety.
            # This handles cases where the file might be manually edited or corrupted.
            if 'po_value_expected' in df.columns:
                # This line converts any invalid/null values to NaN, then fills NaN with 0.
                df['po_value_expected'] = pd.to_numeric(df['po_value_expected'], errors='coerce').fillna(0)

            # Re-validate the DataFrame after the quick cleanup
            is_valid, errors = validate_dataframe(df)
            if is_valid:
                logger.info(f"Loaded and cleaned {len(df)} records from data file")
                return df
            else:
                logger.warning(f"Data file validation failed even after cleaning: {errors}")

            # --- END OF REPLACEMENT LOGIC ---
        # Fallback to source initialization
        if Config.file_exists(Config.SOURCE_FILE):
            logger.info("Initializing from source file")
            return initialize_from_source()
        
        logger.warning("No data sources available")
        return create_empty_dataframe()
            
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return create_empty_dataframe()

def save_data_safely(df: pd.DataFrame) -> bool:
    """Enhanced data saving with rotation backup system."""
    try:
        Config.ensure_directories()
        
        # Validate before saving
        is_valid, errors = validate_dataframe(df)
        if not is_valid:
            logger.error(f"Cannot save invalid data: {errors}")
            return False
        
        # Create timestamped backup
        if Config.file_exists(Config.DATA_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(Config.BACKUP_DIR) / f"sales_data_backup_{timestamp}.xlsx"
            
            # Copy current file to backup
            import shutil
            shutil.copy2(Config.DATA_FILE, backup_path)
            logger.info(f"Created backup: {backup_path}")
            
            # Cleanup old backups
            cleanup_old_backups()
        
        # Save new data
        df.to_excel(Config.DATA_FILE, index=False, engine='openpyxl')
        
        # Clear cache to force reload
        load_cached_data.clear()
        
        logger.info(f"Successfully saved {len(df)} records")
        return True
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def cleanup_old_backups():
    """Remove old backup files to manage disk space."""
    try:
        backup_dir = Path(Config.BACKUP_DIR)
        if not backup_dir.exists():
            return
        
        backup_files = list(backup_dir.glob("sales_data_backup_*.xlsx"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep only the latest N backups
        files_to_remove = backup_files[Config.MAX_BACKUP_FILES:]
        for file_path in files_to_remove:
            file_path.unlink()
            logger.info(f"Removed old backup: {file_path}")
            
    except Exception as e:
        logger.warning(f"Error cleaning up backups: {e}")

# --- Enhanced AI Functions ---
def generate_sales_pitch_safely(lead_name: str, category: str, comments: str, po_value: float = 0) -> str:
    """Enhanced AI pitch generation with context awareness."""
    if not st.session_state.get('gemini_available', False):
        return "🔒 AI Assistant is currently unavailable. Please check API configuration."
    
    try:
        import google.generativeai as genai
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Enhanced prompt with more context
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
        
        if response and response.text:
            logger.info(f"Generated enhanced AI pitch for {lead_name}")
            return response.text
        else:
            return "⚠️ AI Assistant returned an empty response. Please try again."
            
    except ImportError:
        logger.error("Google Generative AI package not available")
        return "❌ AI package not available. Install: pip install google-generativeai"
        
    except Exception as e:
        logger.error(f"Error generating AI pitch: {e}")
        return f"⚠️ Error generating AI insight: {str(e)}"

def generate_team_insights(df: pd.DataFrame) -> str:
    """Generate team-level insights for leadership."""
    if not st.session_state.get('gemini_available', False):
        return None
    
    try:
        import google.generativeai as genai
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Prepare summary data
        summary_stats = {
            'total_leads': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'salespeople_performance': df.groupby('salesperson')['status'].value_counts().to_dict(),
            'pipeline_value': df['po_value_expected'].sum(),
            'avg_deal_size': df['po_value_expected'].mean()
        }
        
        prompt = f"""
        As OATEY's Business Intelligence Analyst, analyze this sales data and provide strategic insights:
        
        **CURRENT METRICS:**
        - Total Leads: {summary_stats['total_leads']}
        - Pipeline Value: ₹{summary_stats['pipeline_value']:,.0f}
        - Average Deal Size: ₹{summary_stats['avg_deal_size']:,.0f}
        
        **TEAM PERFORMANCE:**
        {json.dumps(summary_stats['salespeople_performance'], indent=2)}
        
        **CATEGORY DISTRIBUTION:**
        {json.dumps(summary_stats['categories'], indent=2)}
        
        Provide:
        ### 📊 Key Performance Insights
        ### 🚨 Areas of Concern & Opportunities
        ### 💡 Strategic Recommendations
        ### 🎯 Focus Areas for Next Quarter
        
        Keep insights data-driven, actionable, and business-focused.
        """
        
        response = model.generate_content(prompt)
        return response.text if response and response.text else None
        
    except Exception as e:
        logger.error(f"Error generating team insights: {e}")
        return None

# --- Enhanced UI Components ---
def render_main_header(title: str, subtitle: str = "") -> None:
    """Render enhanced main header with animations."""
    st.markdown(f"""
    <div class="main-header fade-in-up">
        <h1>{title}</h1>
        {f'<div class="subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_cards(metrics: Dict[str, any]) -> None:
    """Enhanced KPI cards with better formatting."""
    st.markdown(f"""
    <div class="kpi-container fade-in-up">
        <div class="kpi-card">
            <div class="kpi-value">{metrics['total_leads']}</div>
            <div class="kpi-label">📊 Total Leads</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{metrics['successful_deals']}</div>
            <div class="kpi-label">✅ Successful Deals</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{metrics['ongoing_deals']}</div>
            <div class="kpi-label">⏳ Ongoing Deals</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{metrics['success_rate']:.1f}%</div>
            <div class="kpi-label">📈 Success Rate</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">₹{metrics['total_po_value']:,.0f}</div>
            <div class="kpi-label">💰 Total PO Value</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_status_badge(status: str) -> str:
    """Render status badge with appropriate styling."""
    badge_classes = {
        'Closed (Success)': 'status-success',
        'Ongoing': 'status-ongoing',
        'Yet to approach': 'status-pending',
        'Closed (Unsuccessful)': 'status-unsuccessful'
    }
    
    class_name = badge_classes.get(status, 'status-pending')
    return f'<span class="status-badge {class_name}">{status}</span>'

def create_enhanced_charts(df: pd.DataFrame) -> None:
    """Enhanced charts with better interactivity and design."""
    if df.empty:
        st.info("📊 No data available for visualization.")
        return
    
    # Performance Overview
    st.subheader("📊 Performance Analytics")
    
    tab1, tab2, tab3 = st.tabs(["🔥 Team Performance", "📈 Pipeline Analysis", "🎯 Category Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Salesperson performance
            sales_perf = df.groupby(['salesperson', 'status']).size().reset_index(name='count')
            fig = px.bar(
                sales_perf, 
                x='salesperson', 
                y='count', 
                color='status',
                title="Lead Distribution by Salesperson",
                color_discrete_map={
                    'Closed (Success)': '#22c55e',
                    'Ongoing': '#3b82f6', 
                    'Yet to approach': '#f59e0b',
                    'Closed (Unsuccessful)': '#ef4444'
                },
                text='count'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                showlegend=True,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Success rate by salesperson
            success_rates = df.groupby('salesperson').apply(
                lambda x: (x['status'] == 'Closed (Success)').sum() / len(x) * 100
            ).reset_index(name='success_rate')
            
            fig = px.bar(
                success_rates,
                x='salesperson',
                y='success_rate',
                title="Success Rate by Salesperson (%)",
                color='success_rate',
                color_continuous_scale='RdYlGn',
                text='success_rate'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pipeline value by status
            pipeline_value = df.groupby('status')['po_value_expected'].sum().reset_index()
            fig = px.pie(
                pipeline_value,
                values='po_value_expected',
                names='status',
                title="Pipeline Value Distribution",
                hole=0.4,
                color_discrete_map={
                    'Closed (Success)': '#22c55e',
                    'Ongoing': '#3b82f6',
                    'Yet to approach': '#f59e0b', 
                    'Closed (Unsuccessful)': '#ef4444'
                }
            )
            fig.update_traces(texttemplate='₹%{value:,.0f}<br>%{percent}', textposition='inside')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Lead status overview
            status_counts = df['status'].value_counts()
            fig = go.Figure(data=[
                go.Bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    text=status_counts.values,
                    textposition='auto',
                    marker_color=['#22c55e', '#3b82f6', '#f59e0b', '#ef4444'][:len(status_counts)]
                )
            ])
            fig.update_layout(
                title="Lead Count by Status",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Category performance
        category_perf = df.groupby(['category', 'status']).size().reset_index(name='count')
        fig = px.sunburst(
            category_perf,
            path=['category', 'status'],
            values='count',
            title="Lead Distribution by Category & Status",
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter"
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Enhanced Page Functions ---
def login_page():
    """Enhanced login page with better UX and secure password handling."""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and branding
        if Config.file_exists(Config.LOGO_FILE):
            st.image(Config.LOGO_FILE, width=200)
        
        st.markdown("""
        <div class="fade-in-up">
            <h1 class="brand-title">OATEY Sales Platform</h1>
            <p class="brand-subtitle">Professional Sales Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with validation
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Username",
                placeholder="Enter your username",
                help="Contact administrator if you don't have credentials"
            )
            
            password = st.text_input(
                "🔒 Password", 
                type="password",
                placeholder="Enter your password"
            )
            
            col_login, col_forgot = st.columns([2, 1])
            
            with col_login:
                login_submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            with col_forgot:
                if st.form_submit_button("❓ Forgot?", use_container_width=True):
                    st.info("💡 Please contact your administrator for password reset.")
        
        # Enhanced login handling with password hashing
        if login_submitted:
            if not username or not password:
                st.error("❌ Please enter both username and password.")
            else:
                user_creds = st.session_state.get('user_credentials', {})
                
                # *** SECURITY FIX: Compare hashed password ***
                if username in user_creds and hash_password(password) == user_creds[username]:
                    st.session_state.logged_in = True
                    st.session_state.role = username
                    st.session_state.login_time = datetime.now()
                    
                    st.success("✅ Authentication successful! Welcome to OATEY Sales Platform!")
                    
                    # Show loading animation
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please check your username and password.")
                    time.sleep(1)
        
        # System status info
        st.markdown("---")
        st.markdown("### 🖥️ System Status")
        
        data_status = "🟢 Online" if not load_data_safely().empty else "🔴 No Data"
        ai_status = "🟢 Active" if configure_api() else "🔴 Offline"
        
        st.markdown(f"""
        - **Data System**: {data_status}
        - **AI Assistant**: {ai_status}
        - **Last Updated**: {datetime.now().strftime('%H:%M:%S')}
        """)

def leadership_dashboard():
    """Enhanced Leadership Dashboard with advanced analytics."""
    render_main_header(
        "👑 Executive Leadership Dashboard", 
        "Comprehensive sales analytics and strategic insights"
    )
    
    df = st.session_state.get('sales_df', create_empty_dataframe())
    
    if df.empty:
        st.error("⚠️ No sales data available. Please check data sources or contact administrator.")
        return
    
    # Enhanced Sidebar Filters
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("🎯 Advanced Filters")
        
        # Date range filter
        st.subheader("📅 Date Range")
        if 'last_updated' in df.columns:
            df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
            min_date = df['last_updated'].min().date() if df['last_updated'].notna().any() else datetime.now().date()
            max_date = df['last_updated'].max().date() if df['last_updated'].notna().any() else datetime.now().date()
            
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        # Sales team filters
        st.subheader("👥 Sales Team")
        salespeople = ['All'] + sorted(df['salesperson'].astype(str).unique())
        selected_salespeople = st.multiselect(
            "Team Members", 
            salespeople[1:],  # Exclude 'All' from multiselect
            default=salespeople[1:]
        )
        
        # Status filters
        st.subheader("📊 Lead Status")
        selected_statuses = st.multiselect(
            "Status", 
            Config.STATUS_OPTIONS,
            default=Config.STATUS_OPTIONS
        )
        
        # Category filters
        st.subheader("🏢 Business Segments")
        categories = sorted(df['category'].unique())
        selected_categories = st.multiselect(
            "Categories", 
            categories,
            default=categories
        )
        
        # Value range filter
        st.subheader("💰 Deal Value Range")
        min_value = int(df['po_value_expected'].min())
        max_value = int(df['po_value_expected'].max()) if df['po_value_expected'].max() > 0 else 100000
        value_range = st.slider(
            "Expected PO Value (₹)",
            min_value=min_value,
            max_value=max_value,
            value=(min_value, max_value),
            step=1000
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df[
        (df['salesperson'].astype(str).isin(selected_salespeople)) &
        (df['status'].isin(selected_statuses)) &
        (df['category'].isin(selected_categories)) &
        (df['po_value_expected'].between(value_range[0], value_range[1]))
    ]
    
    # Calculate enhanced metrics
    metrics = calculate_enhanced_metrics(filtered_df, df)
    
    # Render KPIs
    render_kpi_cards(metrics)
    
    # AI-Generated Team Insights
    if st.session_state.get('gemini_available', False):
        with st.expander("🤖 AI Team Performance Insights", expanded=False):
            if st.button("✨ Generate Team Analysis", key="team_insights"):
                with st.spinner("🧠 Analyzing team performance..."):
                    insights = generate_team_insights(filtered_df)
                    if insights:
                        st.markdown(insights)
                    else:
                        st.warning("Unable to generate insights at this time.")
    
    # Enhanced Charts
    st.markdown("---")
    create_enhanced_charts(filtered_df)
    
    # Detailed Analytics
    st.markdown("---")
    render_detailed_analytics(filtered_df)

def calculate_enhanced_metrics(filtered_df: pd.DataFrame, full_df: pd.DataFrame) -> Dict:
    """Calculate comprehensive metrics for leadership dashboard."""
    if filtered_df.empty:
        return {
            'total_leads': 0, 'successful_deals': 0, 'ongoing_deals': 0,
            'success_rate': 0, 'total_po_value': 0
        }
    
    total_leads = len(filtered_df)
    successful_deals = len(filtered_df[filtered_df['status'] == 'Closed (Success)'])
    ongoing_deals = len(filtered_df[filtered_df['status'] == 'Ongoing'])
    yet_to_approach = len(filtered_df[filtered_df['status'] == 'Yet to approach'])
    unsuccessful_deals = len(filtered_df[filtered_df['status'] == 'Closed (Unsuccessful)'])
    
    # Calculate rates
    success_rate = (successful_deals / total_leads * 100) if total_leads > 0 else 0
    conversion_rate = (successful_deals / (successful_deals + unsuccessful_deals) * 100) if (successful_deals + unsuccessful_deals) > 0 else 0
    
    # Financial metrics
    total_po_value = filtered_df['po_value_expected'].sum()
    successful_po_value = filtered_df[filtered_df['status'] == 'Closed (Success)']['po_value_expected'].sum()
    pipeline_value = filtered_df[filtered_df['status'].isin(['Ongoing', 'Yet to approach'])]['po_value_expected'].sum()
    
    return {
        'total_leads': total_leads,
        'successful_deals': successful_deals,
        'ongoing_deals': ongoing_deals,
        'yet_to_approach': yet_to_approach,
        'unsuccessful_deals': unsuccessful_deals,
        'success_rate': success_rate,
        'conversion_rate': conversion_rate,
        'total_po_value': total_po_value,
        'successful_po_value': successful_po_value,
        'pipeline_value': pipeline_value,
        'avg_deal_size': total_po_value / total_leads if total_leads > 0 else 0
    }

def render_detailed_analytics(df: pd.DataFrame) -> None:
    """Render detailed analytics section with custom status badges."""
    st.subheader("📋 Detailed Lead Analysis")
    
    if df.empty:
        st.info("📭 No leads match the current filters.")
        return
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        high_value_leads = len(df[df['po_value_expected'] > df['po_value_expected'].median()])
        st.metric("💎 High-Value Leads", high_value_leads, help="Above median PO value")
    
    with col2:
        recent_updates = len(df[pd.to_datetime(df['last_updated'], errors='coerce') > datetime.now() - timedelta(days=7)])
        st.metric("🔄 Recent Updates", recent_updates, help="Updated in last 7 days")
    
    with col3:
        avg_deal_size = df['po_value_expected'].mean()
        st.metric("📊 Avg Deal Size", f"₹{avg_deal_size:,.0f}")
    
    with col4:
        total_salespeople = df['salesperson'].nunique()
        st.metric("👥 Active Sales Team", total_salespeople)
    
    # Enhanced data table with formatting
    display_df = prepare_display_dataframe(df)
    
    # Add search functionality
    search_term = st.text_input("🔍 Search leads...", placeholder="Enter company name, POC, or keyword")
    
    if search_term:
        mask = (
            display_df['Lead Name'].str.contains(search_term, case=False, na=False) |
            display_df['POC'].str.contains(search_term, case=False, na=False) |
            display_df['Category'].str.contains(search_term, case=False, na=False)
        )
        display_df = display_df[mask]
    
    # *** UI FEATURE IMPLEMENTATION: Apply custom status badges ***
    if 'Status' in display_df.columns:
        # Create a copy to avoid SettingWithCopyWarning
        display_df = display_df.copy()
        display_df['Status'] = display_df['Status'].apply(render_status_badge)

    # Render dataframe as HTML to display the badges
    html = display_df.to_html(escape=False, index=False, classes='dataframe', justify='left')
    st.markdown(html, unsafe_allow_html=True)
    
    # Export functionality
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # The download button needs to be created, not just the button to trigger it.
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Data (CSV)",
            data=csv,
            file_name=f"oatey_sales_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # This button triggers the report download directly
        if st.button("📊 Generate Report", use_container_width=True):
             generate_executive_report(df)

    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.sales_df = load_data_safely()
            st.success("✅ Data refreshed successfully!")
            time.sleep(1)
            st.rerun()

def prepare_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for display with proper formatting."""
    display_cols = [
        'lead_name', 'category', 'poc_name', 'contact_no', 
        'status', 'po_value_expected', 'salesperson', 'last_updated'
    ]
    
    # Select available columns
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].copy()
    
    # Format currency
    if 'po_value_expected' in display_df.columns:
        display_df['po_value_expected'] = display_df['po_value_expected'].apply(
            lambda x: f"₹{x:,.0f}" if pd.notna(x) else "₹0"
        )
    
    # Format dates
    if 'last_updated' in display_df.columns:
        display_df['last_updated'] = pd.to_datetime(
            display_df['last_updated'], errors='coerce'
        ).dt.strftime('%Y-%m-%d %H:%M')
    
    # Rename columns for display
    column_renames = {
        'lead_name': 'Lead Name',
        'category': 'Category',
        'poc_name': 'POC',
        'contact_no': 'Contact',
        'status': 'Status',
        'po_value_expected': 'Expected Value',
        'salesperson': 'Salesperson',
        'last_updated': 'Last Updated'
    }
    
    display_df = display_df.rename(columns=column_renames)
    return display_df

def generate_executive_report(df: pd.DataFrame) -> None:
    """Generate and trigger download for an executive summary report."""
    if df.empty:
        st.warning("No data available for report generation.")
        return
    
    metrics = calculate_enhanced_metrics(df, df)
    
    # Generate the report string
    team_perf_str = df.groupby('salesperson').agg({
        'lead_id': 'count',
        'po_value_expected': 'sum'
    }).rename(columns={'lead_id': 'Total Leads', 'po_value_expected': 'Pipeline Value'}).to_markdown()

    category_breakdown_str = df.groupby('category')['status'].value_counts().to_markdown()
    
    report = f"""
# OATEY Sales Executive Report
**Generated on**: {datetime.now().strftime('%B %d, %Y at %H:%M')}

## 📊 Executive Summary
- **Total Active Leads**: {metrics['total_leads']}
- **Success Rate**: {metrics['success_rate']:.1f}%
- **Pipeline Value**: ₹{metrics['pipeline_value']:,.0f}
- **Closed Deals Value**: ₹{metrics['successful_po_value']:,.0f}

## 🎯 Key Performance Indicators
- **Successful Deals**: {metrics['successful_deals']}
- **Ongoing Opportunities**: {metrics['ongoing_deals']}
- **Pending Approaches**: {metrics['yet_to_approach']}
- **Average Deal Size**: ₹{metrics['avg_deal_size']:,.0f}

## 👥 Team Performance
{team_perf_str}

## 📈 Category Breakdown
{category_breakdown_str}
    """
    
    # Use session state to manage the download state and avoid complex button logic
    st.session_state.report_data = report
    st.session_state.show_download_button = True

def salesperson_dashboard():
    """Enhanced Salesperson Dashboard with productivity features."""
    salesperson_name = st.session_state.role
    
    render_main_header(
        f"👋 Welcome back, {salesperson_name}!", 
        "Your personal sales command center"
    )
    
    df = st.session_state.get('sales_df', create_empty_dataframe())
    my_leads = df[df['salesperson'] == salesperson_name].copy() if not df.empty else create_empty_dataframe()
    
    # Personal Performance Metrics
    if not my_leads.empty:
        personal_metrics = calculate_enhanced_metrics(my_leads, my_leads)
        render_kpi_cards(personal_metrics)
        
        # Personal insights
        render_personal_insights(my_leads)
    
    st.markdown("---")
    
    # Enhanced Lead Management
    render_lead_management_section(my_leads, df, salesperson_name)
    
    # Quick Actions Section
    render_quick_actions_section(my_leads, salesperson_name)

def render_personal_insights(my_leads: pd.DataFrame) -> None:
    """Render personal performance insights."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Your Focus Areas")
        
        # Urgent follow-ups
        urgent_leads = my_leads[
            (my_leads['status'] == 'Ongoing') & 
            (pd.to_datetime(my_leads['last_updated'], errors='coerce') < datetime.now() - timedelta(days=7))
        ]
        
        if not urgent_leads.empty:
            st.warning(f"⚠️ {len(urgent_leads)} leads need urgent follow-up")
        
        # High-value opportunities
        high_value = my_leads[my_leads['po_value_expected'] > my_leads['po_value_expected'].quantile(0.75)]
        if not high_value.empty and len(high_value) > 0:
            st.info(f"💎 {len(high_value)} high-value opportunities in your pipeline")
    
    with col2:
        st.markdown("### 📈 This Week's Progress")
        
        # Recent activity
        recent_updates = my_leads[
            pd.to_datetime(my_leads['last_updated'], errors='coerce') > datetime.now() - timedelta(days=7)
        ]
        
        if not recent_updates.empty:
            st.success(f"✅ You updated {len(recent_updates)} leads this week")
        else:
            st.info("💡 No recent updates - time to engage with your leads!")

def render_lead_management_section(my_leads: pd.DataFrame, df: pd.DataFrame, salesperson_name: str) -> None:
    """Enhanced lead management interface."""
    tab1, tab2 = st.tabs(["✏️ Manage Existing Leads", "➕ Add New Lead"])
    
    with tab1:
        if not my_leads.empty:
            # Lead selection with search
            st.subheader("🎯 Select Lead to Manage")
            
            lead_search = st.text_input(
                "🔍 Search your leads",
                placeholder="Type company name or POC...",
                key="lead_search"
            )
            
            # Filter leads based on search
            search_filtered_leads = my_leads
            if lead_search:
                mask = (
                    my_leads['lead_name'].str.contains(lead_search, case=False, na=False) |
                    my_leads['poc_name'].str.contains(lead_search, case=False, na=False)
                )
                search_filtered_leads = my_leads[mask]
            
            if not search_filtered_leads.empty:
                search_filtered_leads['display_label'] = (
                    search_filtered_leads['lead_name'].astype(str) + 
                    " - " + search_filtered_leads['status'].astype(str) +
                    " (" + search_filtered_leads['lead_id'].astype(str) + ")"
                )
                
                lead_to_edit_label = st.selectbox(
                    "🎯 Select Lead", 
                    options=search_filtered_leads['display_label'],
                    help="Choose a lead to update or get AI insights"
                )
                
                # Extract lead ID and get lead data
                lead_id = lead_to_edit_label.split('(')[-1].replace(')', '')
                lead_data = my_leads[my_leads['lead_id'] == lead_id].iloc[0]
                
                # Enhanced lead editing interface
                render_lead_editor(lead_data, df, lead_id)
            else:
                st.info("🔍 No leads found matching your search.")
        else:
            st.info("📭 You don't have any leads assigned yet. Add a new lead to get started!")
    
    with tab2:
        render_add_new_lead_form(df, salesperson_name)

def render_lead_editor(lead_data: pd.Series, df: pd.DataFrame, lead_id: str) -> None:
    """Enhanced lead editing interface."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📝 Editing: **{lead_data['lead_name']}**")
        
        with st.form(f"update_form_{lead_id}"):
            # Lead information display
            with st.container():
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.text_input("🏢 Company Name", value=lead_data['lead_name'], disabled=True)
                    st.text_input("🏷️ Category", value=lead_data['category'], disabled=True)
                    st.text_input("📞 Contact", value=str(lead_data.get('contact_no', '')), disabled=True)
                
                with info_col2:
                    st.text_input("👤 POC Name", value=str(lead_data.get('poc_name', '')), disabled=True)
                    st.text_input("📧 Email", value=str(lead_data.get('email', '')), disabled=True)
                    st.text_input("📅 Last Updated", value=str(lead_data.get('last_updated', '')), disabled=True)
            
            st.markdown("---")
            
            # Editable fields
            col_status, col_priority = st.columns(2)
            
            with col_status:
                current_status_index = (
                    Config.STATUS_OPTIONS.index(lead_data['status']) 
                    if lead_data['status'] in Config.STATUS_OPTIONS else 0
                )
                
                new_status = st.selectbox(
                    "📊 Lead Status", 
                    options=Config.STATUS_OPTIONS, 
                    index=current_status_index,
                    help="Update the current status of this lead"
                )
            
            with col_priority:
                priority_options = ['Low', 'Medium', 'High', 'Critical']
                current_priority = lead_data.get('priority', 'Medium')
                priority_index = priority_options.index(current_priority) if current_priority in priority_options else 1
                
                new_priority = st.selectbox(
                    "🔥 Priority Level",
                    options=priority_options,
                    index=priority_index,
                    help="Set priority level for this lead"
                )
            
            new_po_value = st.number_input(
                "💰 Expected PO Value (₹)", 
                value=float(lead_data['po_value_expected']), 
                min_value=0.0,
                step=1000.0,
                help="Expected purchase order value"
            )
            
            # Follow-up date
            current_follow_up = lead_data.get('follow_up_date')
            if pd.notna(current_follow_up):
                follow_up_default = pd.to_datetime(current_follow_up).date()
            else:
                follow_up_default = datetime.now().date() + timedelta(days=7)
            
            new_follow_up_date = st.date_input(
                "📅 Next Follow-up Date",
                value=follow_up_default,
                help="When should you follow up with this lead?"
            )
            
            new_comments = st.text_area(
                "💬 Update Notes & Comments", 
                value=lead_data.get('comments', ''),
                height=120,
                placeholder="Add your latest observations, meeting notes, or next steps...",
                help="Document all interactions and important details"
            )
            
            # Form submission
            col_update, col_ai = st.columns(2)
            
            with col_update:
                update_submitted = st.form_submit_button("💾 Update Lead", use_container_width=True)
            
            with col_ai:
                ai_submitted = st.form_submit_button("🤖 Update & Get AI Strategy", use_container_width=True)
            
            # Handle form submission
            if update_submitted or ai_submitted:
                success = update_lead_data(
                    df, lead_id, new_status, new_priority, new_po_value, 
                    new_follow_up_date, new_comments
                )
                
                if success:
                    st.success(f"✅ Successfully updated: {lead_data['lead_name']}")
                    
                    if ai_submitted:
                        with st.spinner("🧠 Generating AI strategy..."):
                            pitch = generate_sales_pitch_safely(
                                lead_data['lead_name'], 
                                lead_data['category'], 
                                new_comments, 
                                new_po_value
                            )
                            update_ai_pitch(df, lead_id, pitch)
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to update lead. Please try again.")
    
    with col2:
        render_ai_assistant_panel(lead_data, lead_id)

def update_lead_data(df: pd.DataFrame, lead_id: str, status: str, priority: str, 
                     po_value: float, follow_up_date, comments: str) -> bool:
    """Update lead data with validation."""
    try:
        idx = df.index[df['lead_id'] == lead_id].tolist()
        if not idx:
            logger.error(f"Lead ID not found: {lead_id}")
            return False
        
        idx = idx[0]
        
        # Update lead data
        df.loc[idx, [
            'status', 'priority', 'po_value_expected', 
            'follow_up_date', 'comments', 'last_updated'
        ]] = [
            status, priority, po_value, 
            follow_up_date.strftime("%Y-%m-%d"), 
            comments, 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        # Save data
        success = save_data_safely(df)
        if success:
            st.session_state.sales_df = load_data_safely()
        
        return success
        
    except Exception as e:
        logger.error(f"Error updating lead {lead_id}: {e}")
        return False

def update_ai_pitch(df: pd.DataFrame, lead_id: str, pitch: str) -> bool:
    """Update AI pitch for a lead."""
    try:
        idx = df.index[df['lead_id'] == lead_id].tolist()
        if idx:
            df.loc[idx[0], 'ai_pitch'] = pitch
            return save_data_safely(df)
        return False
    except Exception as e:
        logger.error(f"Error updating AI pitch: {e}")
        return False

def render_ai_assistant_panel(lead_data: pd.Series, lead_id: str) -> None:
    """Enhanced AI assistant panel."""
    st.markdown("""
    <div class="ai-insight">
        <h3>🤖 AI Sales Assistant</h3>
        <p>Get intelligent, data-driven strategies tailored to this specific lead and market context.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('gemini_available', False):
        if st.button(
            "✨ Generate Smart Strategy", 
            key=f"ai_{lead_id}", 
            use_container_width=True,
            help="AI will analyze this lead and provide tailored recommendations"
        ):
            with st.spinner("🧠 AI is analyzing lead context and generating strategy..."):
                pitch = generate_sales_pitch_safely(
                    lead_data['lead_name'], 
                    lead_data['category'], 
                    lead_data.get('comments', ''),
                    lead_data.get('po_value_expected', 0)
                )
                
                if pitch and not pitch.startswith('🔒') and not pitch.startswith('❌'):
                    update_ai_pitch(st.session_state.sales_df, lead_id, pitch)
                    st.rerun()
    else:
        st.warning("🔒 AI Assistant is offline. Please contact administrator.")
    
    # Display existing AI pitch
    ai_pitch = lead_data.get('ai_pitch', '')
    if ai_pitch and pd.notna(ai_pitch) and len(str(ai_pitch).strip()) > 10:
        with st.container():
            st.markdown("### 🎯 AI-Generated Strategy")
            st.markdown(ai_pitch)
            
            # Action buttons for AI content
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate Strategy", key=f"regen_{lead_id}"):
                    with st.spinner("🔄 Regenerating strategy..."):
                        new_pitch = generate_sales_pitch_safely(
                            lead_data['lead_name'], 
                            lead_data['category'], 
                            lead_data.get('comments', ''),
                            lead_data.get('po_value_expected', 0)
                        )
                        if new_pitch:
                            update_ai_pitch(st.session_state.sales_df, lead_id, new_pitch)
                            st.rerun()
            
            with col2:
                if st.button("📋 Copy Strategy", key=f"copy_{lead_id}"):
                    st.code(ai_pitch, language=None)
                    st.success("✅ Strategy copied to clipboard area above!")
    else:
        st.info("💡 Click 'Generate Smart Strategy' to get AI-powered sales insights for this lead.")

def render_add_new_lead_form(df: pd.DataFrame, salesperson_name: str) -> None:
    """Enhanced new lead addition form."""
    st.subheader("🆕 Add New Lead to Your Pipeline")
    
    with st.form("new_lead_form", clear_on_submit=True):
        # Lead basic information
        st.markdown("#### 📋 Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            lead_name = st.text_input(
                "🏢 Company/Lead Name*", 
                placeholder="e.g., Starbucks India",
                help="Enter the full company or organization name"
            )
            
            category = st.selectbox(
                "🏷️ Business Category*", 
                options=[""] + list(Config.SHEET_MAPPING.values()),
                help="Select the appropriate business category"
            )
            
            priority = st.selectbox(
                "🔥 Priority Level",
                options=['Medium', 'Low', 'High', 'Critical'],
                help="Set initial priority for this lead"
            )
        
        with col2:
            poc_name = st.text_input(
                "👤 Point of Contact", 
                placeholder="e.g., John Smith",
                help="Main contact person at the organization"
            )
            
            source = st.selectbox(
                "📍 Lead Source",
                options=['Cold Outreach', 'Referral', 'Website Inquiry', 'Trade Show', 'Social Media', 'Other'],
                help="How did you acquire this lead?"
            )
            
            initial_po_value = st.number_input(
                "💰 Expected PO Value (₹)", 
                min_value=0.0, 
                step=1000.0,
                help="Estimated purchase order value"
            )
        
        # Contact information
        st.markdown("#### 📞 Contact Details")
        col1, col2 = st.columns(2)
        
        with col1:
            contact_no = st.text_input(
                "📱 Contact Number", 
                placeholder="e.g., +91 9876543210",
                help="Primary contact number"
            )
        
        with col2:
            email = st.text_input(
                "📧 Email Address", 
                placeholder="e.g., john@company.com",
                help="Primary email contact"
            )
        
        # Follow-up planning
        st.markdown("#### 📅 Planning")
        col1, col2 = st.columns(2)
        
        with col1:
            first_follow_up = st.date_input(
                "📅 First Follow-up Date",
                value=datetime.now().date() + timedelta(days=3),
                help="When should you first contact this lead?"
            )
        
        with col2:
            initial_status = st.selectbox(
                "📊 Initial Status",
                options=['Yet to approach', 'Ongoing'],
                help="Current status of this lead"
            )
        
        initial_comments = st.text_area(
            "💬 Initial Notes & Context",
            placeholder="Add context about this lead: how you found them, key requirements, decision-makers, timeline, budget constraints, competition, etc.",
            height=120,
            help="Document all relevant information about this lead"
        )
        
        # Form submission with validation
        submitted = st.form_submit_button("🚀 Add New Lead", use_container_width=True)
        
        if submitted:
            # Validate required fields
            validation_errors = []
            
            if not lead_name.strip():
                validation_errors.append("Lead Name is required")
            if not category:
                validation_errors.append("Business Category is required")
            if email and not validate_email(email):
                validation_errors.append("Invalid email format")
            if contact_no and not validate_phone(contact_no):
                validation_errors.append("Invalid phone number format")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                success = add_new_lead(
                    df, lead_name, category, poc_name, contact_no, email,
                    initial_po_value, initial_comments, salesperson_name,
                    priority, source, initial_status, first_follow_up
                )
                
                if success:
                    st.success(f"✅ Successfully added new lead: **{lead_name}**")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Failed to add lead. Please try again.")

def add_new_lead(df: pd.DataFrame, lead_name: str, category: str, poc_name: str,
                 contact_no: str, email: str, po_value: float, comments: str,
                 salesperson: str, priority: str, source: str, status: str, follow_up_date) -> bool:
    """Add new lead with comprehensive validation."""
    try:
        # Generate unique lead ID
        if not df.empty and 'lead_id' in df.columns:
            existing_ids = pd.to_numeric(
                df['lead_id'].str.replace('OATEY-', ''), errors='coerce'
            ).dropna()
            max_id = existing_ids.max() if not existing_ids.empty else 999
        else:
            max_id = 999

        new_id_num = int(max_id) + 1
        new_lead_id = f"OATEY-{new_id_num:04d}"
        
        # Create new lead data
        new_lead_data = {
            'lead_id': new_lead_id,
            'lead_name': lead_name.strip(),
            'poc_name': poc_name.strip() if poc_name else '',
            'contact_no': contact_no.strip() if contact_no else '',
            'email': email.strip() if email else '',
            'category': category,
            'status': status,
            'salesperson': salesperson,
            'po_value_expected': po_value,
            'comments': comments.strip() if comments else 'New lead added.',
            'priority': priority,
            'source': source,
            'created_date': datetime.now().strftime("%Y-%m-%d"),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'follow_up_date': follow_up_date.strftime("%Y-%m-%d"),
            'ai_pitch': ''
        }
        
        # Add to dataframe
        new_df = pd.DataFrame([new_lead_data])
        updated_df = pd.concat([df, new_df], ignore_index=True)
        
        # Save and update session state
        success = save_data_safely(updated_df)
        if success:
            st.session_state.sales_df = load_data_safely()
        
        return success
        
    except Exception as e:
        logger.error(f"Error adding new lead: {e}")
        return False

def render_quick_actions_section(my_leads: pd.DataFrame, salesperson_name: str) -> None:
    """Enhanced quick actions with productivity features."""
    st.markdown("---")
    st.subheader("🚀 Quick Actions & Productivity Tools")
    
    if my_leads.empty:
        st.info("📭 Add some leads to access quick actions and productivity tools.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📞 Today's Follow-ups", use_container_width=True):
            today = datetime.now().strftime("%Y-%m-%d")
            todays_leads = my_leads[my_leads['follow_up_date'] == today]
            if not todays_leads.empty:
                st.info(f"📅 You have {len(todays_leads)} follow-ups scheduled for today!")
            else:
                st.success("✅ No follow-ups scheduled for today. Great job!")
    
    with col2:
        if st.button("💰 Pipeline Calculator", use_container_width=True):
            pipeline_leads = my_leads[
                my_leads['status'].isin(['Ongoing', 'Yet to approach'])
            ]
            
            if not pipeline_leads.empty:
                total_pipeline = pipeline_leads['po_value_expected'].sum()
                avg_close_rate = 0.3  # Assumed 30% close rate
                projected_revenue = total_pipeline * avg_close_rate
                
                st.info(f"""
                💰 **Your Pipeline Analysis:**
                - Active Pipeline: ₹{total_pipeline:,.0f}
                - Projected Revenue (30% close): ₹{projected_revenue:,.0f}
                - Number of Opportunities: {len(pipeline_leads)}
                """)
            else:
                st.warning("No active pipeline opportunities.")
    
    with col3:
        if st.button("🏆 Performance Summary", use_container_width=True):
            if not my_leads.empty:
                success_count = len(my_leads[my_leads['status'] == 'Closed (Success)'])
                total_count = len(my_leads)
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                
                total_revenue = my_leads[
                    my_leads['status'] == 'Closed (Success)'
                ]['po_value_expected'].sum()
                
                st.success(f"""
                🏆 **Your Performance:**
                - Success Rate: {success_rate:.1f}%
                - Total Revenue: ₹{total_revenue:,.0f}
                - Deals Closed: {success_count}/{total_count}
                """)
    
    with col4:
        csv = my_leads.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Export My Data",
            data=csv,
            file_name=f"{salesperson_name.replace(' ', '_')}_leads_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def render_sidebar():
    """Enhanced sidebar with better organization and status."""
    with st.sidebar:
        # Logo and user info
        if Config.file_exists(Config.LOGO_FILE):
            st.image(Config.LOGO_FILE, use_container_width=True)
        
        # User session info
        st.markdown(f"""
        <div class="sidebar-section">
            <div style="text-align: center; color: var(--primary-color);">
                <strong>🔐 Active Session</strong><br>
                <span style="font-size: 1.1em; font-weight: 600;">{st.session_state.role}</span><br>
                <small>Since: {st.session_state.get('login_time', datetime.now()).strftime('%H:%M')}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # System status dashboard
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🖥️ System Health")
        
        # Data status with details
        df = st.session_state.get('sales_df', create_empty_dataframe())
        if not df.empty:
            last_update = "Just now"
            if Config.file_exists(Config.DATA_FILE):
                last_modified = datetime.fromtimestamp(os.path.getmtime(Config.DATA_FILE))
                time_diff = datetime.now() - last_modified
                if time_diff.days > 0:
                    last_update = f"{time_diff.days}d ago"
                elif time_diff.seconds > 3600:
                    last_update = f"{time_diff.seconds//3600}h ago"
                elif time_diff.seconds > 60:
                    last_update = f"{time_diff.seconds//60}m ago"
                else:
                    last_update = "Just now"
            
            st.success(f"📊 **Data**: {len(df)} records ({last_update})")
        else:
            st.error("📊 **Data**: No data loaded")
        
        # AI status
        ai_status = st.session_state.get('gemini_available', False)
        if ai_status:
            st.success("🤖 **AI Assistant**: Active")
        else:
            st.error("🤖 **AI Assistant**: Offline")
        
        # Performance metrics
        if not df.empty:
            file_size = os.path.getsize(Config.DATA_FILE) / 1024 if Config.file_exists(Config.DATA_FILE) else 0
            st.info(f"💾 **File Size**: {file_size:.1f} KB")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation and tools
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🧭 Quick Tools")
        
        if st.button("🔄 Refresh Data", use_container_width=True, help="Reload data from source"):
            with st.spinner("Refreshing data..."):
                st.session_state.sales_df = load_data_safely()
                st.success("✅ Data refreshed!")
                time.sleep(1)
                st.rerun()
        
        if st.button("📊 System Stats", use_container_width=True):
            if not df.empty:
                stats = {
                    'Total Users': len(st.session_state.get('user_credentials', {})),
                    'Active Salespeople': df['salesperson'].nunique(),
                    'Data Quality': f"{((df['lead_name'].notna()).sum() / len(df) * 100):.1f}%",
                    'Last Backup': 'Available' if len(list(Path(Config.BACKUP_DIR).glob("*.xlsx"))) > 0 else 'None'
                }
                
                for key, value in stats.items():
                    st.write(f"**{key}**: {value}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Logout with confirmation
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.login_time = None
            st.success("👋 Logged out successfully!")
            time.sleep(1)
            st.rerun()
        
        # Help and documentation
        with st.expander("❓ Help & Support"):
            st.markdown("""
            **🚀 Quick Start Guide:**
            
            **For Leadership:**
            - View team performance metrics
            - Analyze pipeline and conversion rates
            - Generate AI-powered team insights
            - Export comprehensive reports
            
            **For Sales Team:**
            - Manage your assigned leads
            - Update lead status and notes
            - Get AI-generated sales strategies
            - Track your personal performance
            
            **🤖 AI Features:**
            - Personalized sales strategies
            - Lead-specific talking points
            - Objection handling guidance
            - Market context analysis
            
            **📞 Need Help?**
            Contact your system administrator for technical support or additional features.
            """)

def render_main_application():
    """Enhanced main application router."""
    # Initialize sidebar
    render_sidebar()
    
    # Route to appropriate dashboard
    if st.session_state.role == "Leadership":
        leadership_dashboard()
    else:
        salesperson_dashboard()

    # Add a download button for the executive report if it's been generated
    if st.session_state.get('show_download_button', False):
        st.download_button(
            label="📄 Download Executive Report",
            data=st.session_state.get('report_data', ''),
            file_name=f"oatey_executive_report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )
        st.session_state.show_download_button = False # Reset state
    
    # Add footer with session info
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 1rem;">
        OATEY Sales Management Platform | Session: {st.session_state.role} | 
        Data: {len(st.session_state.get('sales_df', create_empty_dataframe()))} records |
        Last Update: {datetime.now().strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

# --- Enhanced Session State Management ---
def initialize_session_state():
    """Enhanced session state initialization with health checks."""
    try:
        # Core session variables
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            
        if 'role' not in st.session_state:
            st.session_state.role = None
            
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        
        # Load user credentials
        if 'user_credentials' not in st.session_state:
            st.session_state.user_credentials = Config.get_user_credentials()
            logger.info(f"Loaded credentials for {len(st.session_state.user_credentials)} users")
        
        # Load sales data
        if 'sales_df' not in st.session_state:
            with st.spinner("🔄 Loading sales data..."):
                st.session_state.sales_df = load_data_safely()
                logger.info(f"Loaded {len(st.session_state.sales_df)} sales records")
        
        # Configure AI
        if 'gemini_available' not in st.session_state:
            st.session_state.gemini_available = configure_api()
            logger.info(f"AI Assistant: {'Available' if st.session_state.gemini_available else 'Unavailable'}")
        
        # Performance monitoring
        if 'app_start_time' not in st.session_state:
            st.session_state.app_start_time = datetime.now()
        
        # Data validation and health checks
        df = st.session_state.sales_df
        if not df.empty:
            is_valid, errors = validate_dataframe(df)
            if not is_valid:
                st.warning(f"⚠️ Data validation issues detected: {'; '.join(errors)}")
        else:
            st.warning("⚠️ No sales data available. System is running in limited mode.")
            
    except Exception as e:
        logger.error(f"Critical error initializing session state: {e}")
        st.error(f"""
        ❌ **Application Initialization Error**
        
        Error: {str(e)}
        
        Please try refreshing the page. If the problem persists, contact your administrator.
        """)

# --- Error Handling and Recovery ---
def handle_application_error(error: Exception, context: str = "Application") -> None:
    """Centralized error handling with user-friendly messages."""
    logger.error(f"{context} error: {str(error)}", exc_info=True)
    
    st.markdown(f"""
    <div class="error-container">
        <h4>⚠️ {context} Error</h4>
        <p>Something went wrong: <code>{str(error)}</code></p>
        <p><strong>Suggested Actions:</strong></p>
        <ul>
            <li>Refresh the page</li>
            <li>Check your internet connection</li>
            <li>Contact administrator if problem persists</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_app_info():
    """Display application information and health status."""
    with st.expander("ℹ️ Application Information"):
        session_duration = datetime.now() - st.session_state.get('app_start_time', datetime.now())
        st.markdown(f"""
        **🏢 OATEY Sales Management Platform**
        
        **Session Information:**
        - User: {st.session_state.get('role', 'Not logged in')}
        - Login Time: {st.session_state.get('login_time', 'N/A')}
        - Session Duration: {str(session_duration).split('.')[0]}
        
        **Data Status:**
        - Records Loaded: {len(st.session_state.get('sales_df', create_empty_dataframe()))}
        - AI Assistant: {'🟢 Active' if st.session_state.get('gemini_available') else '🔴 Offline'}
        - Data Source: {'Excel File' if Config.file_exists(Config.DATA_FILE) else 'None'}
        """) # *** SYNTAX FIX: Added closing delimiter for f-string ***

# --- Main Application Entry Point ---
def main():
    """Enhanced main application with comprehensive error handling and monitoring."""
    try:
        # Set optimal page configuration
        st.set_page_config(
            page_title="OATEY Sales Management Platform",
            page_icon="🥛",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://oatey.com/support',
                'Report a bug': 'mailto:admin@oatey.com',
                'About': 'OATEY Sales Management Platform v2.0'
            }
        )
        
        # Performance monitoring
        start_time = time.time()
        
        # Initialize application
        initialize_session_state()
        
        # Load enhanced styling
        load_custom_css()
        
        # Main application routing with error boundaries
        try:
            if not st.session_state.logged_in:
                login_page()
            else:
                render_main_application()
                
                # Show app info in development mode
                if st.session_state.get('role') == 'Leadership':
                    show_app_info()
                    
        except Exception as app_error:
            handle_application_error(app_error, "Dashboard")
            
            # Fallback recovery options
            st.markdown("### 🔧 Recovery Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Refresh Application"):
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear Cache"):
                    st.cache_data.clear()
                    st.success("Cache cleared! Please refresh.")
            
            with col3:
                if st.button("🚪 Logout & Reset"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
        
        # Performance logging
        end_time = time.time()
        load_time = end_time - start_time
        
        if load_time > 2.0:  # Log slow loads
            logger.warning(f"Slow page load detected: {load_time:.2f}s")
            
    except Exception as critical_error:
        # Critical error handling - last resort
        logger.critical(f"Critical application failure: {critical_error}", exc_info=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #fee2e2, #fecaca); border-radius: 12px; margin: 2rem;">
            <h2 style="color: #991b1b;">🚨 Critical System Error</h2>
            <p style="color: #7f1d1d; font-size: 1.1rem;">
                The application encountered a critical error and cannot continue safely.
            </p>
            <p style="color: #7f1d1d;">
                Please contact your system administrator with the following information:
            </p>
            <code style="background: white; padding: 0.5rem; border-radius: 4px; color: #991b1b;">
                Error: {}</code>
            <br><br>
            <button onclick="window.location.reload();" style="
                background: linear-gradient(135deg, #991b1b, #dc2626);
                color: white; border: none; padding: 0.75rem 1.5rem;
                border-radius: 8px; font-weight: 600; cursor: pointer;
            ">🔄 Reload Application</button>
        </div>
        """.format(str(critical_error)), unsafe_allow_html=True)

# --- Application Entry Point ---
if __name__ == "__main__":
    # Ensure required directories exist
    Config.ensure_directories()
    
    # Start the application
    main()
