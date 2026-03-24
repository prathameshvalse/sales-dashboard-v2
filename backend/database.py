import pandas as pd
from datetime import datetime
import os
import shutil

DATA_FILE = "../OATEY - Sales Dashboard.xlsx"
BACKUP_DIR = "./backups"

def create_empty_dataframe() -> pd.DataFrame:
    columns = [
        'lead_id', 'lead_name', 'poc_name', 'contact_no', 'email',
        'category', 'status', 'salesperson', 'po_value_expected',
        'comments', 'last_updated', 'ai_pitch', 'created_date',
        'follow_up_date', 'priority', 'source'
    ]
    return pd.DataFrame(columns=columns)

def load_data() -> pd.DataFrame:
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_excel(DATA_FILE)
            if 'po_value_expected' in df.columns:
                df['po_value_expected'] = pd.to_numeric(df['po_value_expected'], errors='coerce').fillna(0)
            return df
        return create_empty_dataframe()
    except Exception as e:
        print(f"Error loading data: {e}")
        return create_empty_dataframe()

def save_data(df: pd.DataFrame) -> bool:
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        if os.path.exists(DATA_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(BACKUP_DIR, f"sales_data_backup_{timestamp}.xlsx")
            shutil.copy2(DATA_FILE, backup_path)
            
            # Keep only last 5 backups
            backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("sales_data_backup_")])
            for old_backup in backups[:-5]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))

        df.to_excel(DATA_FILE, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def add_lead(lead_data: dict) -> dict:
    df = load_data()
    
    # Generate new lead_id
    if df.empty:
        new_id = "OATEY-1000"
    else:
        # Simple ID generation logic based on max ID
        # Assumes IDs are like 'OATEY-1XXX'
        ids = df['lead_id'].dropna().astype(str)
        if len(ids) > 0:
            last_id_num = int(ids.iloc[-1].split('-')[1]) if '-' in ids.iloc[-1] else 1000
            new_id = f"OATEY-{last_id_num + 1:04d}"
        else:
            new_id = "OATEY-1000"
            
    lead_data['lead_id'] = new_id
    lead_data['created_date'] = datetime.now().strftime("%Y-%m-%d")
    lead_data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lead_data['ai_pitch'] = ""
    
    new_row = pd.DataFrame([lead_data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    success = save_data(df)
    return lead_data if success else None

def update_lead(lead_id: str, update_data: dict) -> bool:
    df = load_data()
    mask = df['lead_id'] == lead_id
    if not mask.any():
        return False
        
    for key, value in update_data.items():
        if value is not None:
            df.loc[mask, key] = value
            
    df.loc[mask, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return save_data(df)
