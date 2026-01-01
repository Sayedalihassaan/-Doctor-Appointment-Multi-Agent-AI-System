from datetime import datetime, timedelta
import re

def parse_relative_date(text: str) -> str:
    """
    Parse relative date expressions from text and return formatted date DD-MM-YYYY.
    Handles: tomorrow, today, next week, etc.
    Always assumes current year is 2024 for consistency with agent instructions.
    """
    text_lower = text.lower()
    
    # Use 2024 as base year per agent instructions
    base_date = datetime(2024, 1, 1)
    
    # Check if text contains relative date keywords
    if 'tomorrow' in text_lower:
        target_date = base_date + timedelta(days=1)
    elif 'today' in text_lower:
        target_date = base_date
    elif 'next week' in text_lower:
        target_date = base_date + timedelta(weeks=1)
    elif 'day after tomorrow' in text_lower:
        target_date = base_date + timedelta(days=2)
    else:
        # Try to extract explicit date
        # Look for patterns like DD-MM-YYYY or DD/MM/YYYY
        date_pattern = r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})'
        match = re.search(date_pattern, text)
        if match:
            day, month, year = match.groups()
            return f"{int(day):02d}-{int(month):02d}-{year}"
        
        # Default to tomorrow if no date found
        target_date = base_date + timedelta(days=1)
    
    return target_date.strftime("%d-%m-%Y")


def extract_specialization_keyword(text: str) -> str:
    """
    Extract specialization from user query.
    Maps common terms to official specialization names.
    """
    text_lower = text.lower()
    
    # Mapping of common terms to specialization literals
    specialization_map = {
        'dentist': 'general_dentist',
        'general dentist': 'general_dentist',
        'cosmetic dentist': 'cosmetic_dentist',
        'prosthodontist': 'prosthodontist',
        'pediatric dentist': 'pediatric_dentist',
        'emergency dentist': 'emergency_dentist',
        'oral surgeon': 'oral_surgeon',
        'orthodontist': 'orthodontist',
    }
    
    for keyword, specialization in specialization_map.items():
        if keyword in text_lower:
            return specialization
    
    return None


def extract_doctor_name(text: str) -> str:
    """
    Extract doctor name from user query.
    Returns None if no doctor name found.
    """
    text_lower = text.lower()
    
    doctor_names = [
        'kevin anderson', 'robert martinez', 'susan davis',
        'daniel miller', 'sarah wilson', 'michael green',
        'lisa brown', 'jane smith', 'emily johnson', 'john doe'
    ]
    
    for name in doctor_names:
        if name in text_lower:
            return name
    
    return None
