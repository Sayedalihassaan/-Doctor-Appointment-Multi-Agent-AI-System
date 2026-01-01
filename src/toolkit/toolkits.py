import pandas as pd
from typing import  Literal
from langchain_core.tools import tool
from src.data_models.models import *


@tool
def check_availability_by_doctor(desired_date: str, doctor_name: Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe']):
    """
    Check availability for a SPECIFIC DOCTOR by name.
    Use this tool when the user mentions a specific doctor's name.
    Example: "Is Dr. John Doe available?", "Check Kevin Anderson's schedule"
    
    Parameters:
    - desired_date: Date in DD-MM-YYYY format (e.g., "02-01-2024")
    - doctor_name: Exact doctor name from the list (lowercase)
    """
    try:
        # Validate date format
        import re
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', desired_date):
            return f"Invalid date format. Please use DD-MM-YYYY format (e.g., 02-01-2024)"
        
        df = pd.read_csv(r"data/doctor_availability.csv")
        
        df['date_slot_time'] = df['date_slot'].apply(lambda input: input.split(' ')[-1])
        
        rows = list(df[(df['date_slot'].apply(lambda input: input.split(' ')[0]) == desired_date)&(df['doctor_name'] == doctor_name)&(df['is_available'] == True)]['date_slot_time'])
    
        if len(rows) == 0:
            output = f"No availability for {doctor_name} on {desired_date}"
        else:
            output = f'Availability for {doctor_name} on {desired_date}:\n'
            output += "Available slots: " + ', '.join(rows)
    
        return output
    except Exception as e:
        return f"Error checking doctor availability: {str(e)}"
@tool
def check_availability_by_specialization(desired_date: str, specialization: Literal["general_dentist", "cosmetic_dentist", "prosthodontist", "pediatric_dentist","emergency_dentist","oral_surgeon","orthodontist"]):
    """
    Check availability by SPECIALIZATION (e.g., dentist type).
    Use this tool when the user asks about a type/specialization without mentioning a specific doctor.
    Example: "Is a dentist available?", "Find me a general dentist", "Any orthodontist available?"
    
    Parameters:
    - desired_date: Date in DD-MM-YYYY format as a string (e.g., "02-01-2024")
    - specialization: One of the specialization types (use 'general_dentist' for just 'dentist')
    
    Specializations:
    - general_dentist: general dental care (use this for "dentist")
    - cosmetic_dentist: cosmetic procedures
    - orthodontist: braces and alignment
    - pediatric_dentist: children's dentistry
    - oral_surgeon: surgical procedures
    - prosthodontist: prosthetics and implants
    - emergency_dentist: emergency care
    """
    try:
        # Validate date format
        import re
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', desired_date):
            return f"Invalid date format. Please use DD-MM-YYYY format (e.g., 02-01-2024)"
        
        df = pd.read_csv(r"data/doctor_availability.csv")
        df['date_slot_time'] = df['date_slot'].apply(lambda input: input.split(' ')[-1])
        rows = df[(df['date_slot'].apply(lambda input: input.split(' ')[0]) == desired_date) & (df['specialization'] == specialization) & (df['is_available'] == True)].groupby(['specialization', 'doctor_name'])['date_slot_time'].apply(list).reset_index(name='available_slots')
    
        if len(rows) == 0:
            output = f"No {specialization.replace('_', ' ')} available on {desired_date}"
        else:
            def convert_to_am_pm(time_str):
                time_str = str(time_str)
                hours, minutes = map(int, time_str.split(":"))
                period = "AM" if hours < 12 else "PM"
                hours = hours % 12 or 12
                return f"{hours}:{minutes:02d} {period}"
            
            output = f'Available {specialization.replace("_", " ")}s on {desired_date}:\n\n'
            for row in rows.values:
                output += f"Dr. {row[1].title()}:\n"
                output += '  ' + ', '.join([convert_to_am_pm(value) for value in row[2]]) + '\n\n'
    
        return output
    except Exception as e:
        return f"Error checking specialization availability: {str(e)}"
@tool
def set_appointment(desired_date:DateTimeModel, id_number:IdentificationNumberModel, doctor_name:Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe']):
    """
    Set appointment or slot with the doctor.
    The parameters MUST be mentioned by the user in the query.
    """
    df = pd.read_csv(r"doctor_availability.csv")
   
    from datetime import datetime
    def convert_datetime_format(dt_str):
        # Parse the input datetime string
        #dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        dt = datetime.strptime(dt_str, "%d-%m-%Y %H:%M")
        
        # Format the output as 'DD-MM-YYYY H.M' (removing leading zero from hour only)
        return dt.strftime("%d-%m-%Y %#H.%M")
    
    case = df[(df['date_slot'] == convert_datetime_format(desired_date.date))&(df['doctor_name'] == doctor_name)&(df['is_available'] == True)]
    if len(case) == 0:
        return "No available appointments for that particular case"
    else:
        df.loc[(df['date_slot'] == convert_datetime_format(desired_date.date))&(df['doctor_name'] == doctor_name) & (df['is_available'] == True), ['is_available','patient_to_attend']] = [False, id_number.id]
        df.to_csv(f'availability.csv', index = False)

        return "Successfully done"
@tool
def cancel_appointment(date:DateTimeModel, id_number:IdentificationNumberModel, doctor_name:Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe']):
    """
    Canceling an appointment.
    The parameters MUST be mentioned by the user in the query.
    """
    df = pd.read_csv(r"doctor_availability.csv")
    case_to_remove = df[(df['date_slot'] == date.date)&(df['patient_to_attend'] == id_number.id)&(df['doctor_name'] == doctor_name)]
    if len(case_to_remove) == 0:
        return "You don´t have any appointment with that specifications"
    else:
        df.loc[(df['date_slot'] == date.date) & (df['patient_to_attend'] == id_number.id) & (df['doctor_name'] == doctor_name), ['is_available', 'patient_to_attend']] = [True, None]
        df.to_csv(f'availability.csv', index = False)

        return "Successfully cancelled"
@tool
def reschedule_appointment(old_date:DateTimeModel, new_date:DateTimeModel, id_number:IdentificationNumberModel, doctor_name:Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe']):
    """
    Rescheduling an appointment.
    The parameters MUST be mentioned by the user in the query.
    """
    #Dummy data
    df = pd.read_csv(r"doctor_availability.csv")
    available_for_desired_date = df[(df['date_slot'] == new_date.date)&(df['is_available'] == True)&(df['doctor_name'] == doctor_name)]
    if len(available_for_desired_date) == 0:
        return "Not available slots in the desired period"
    else:
        cancel_appointment.invoke({'date':old_date, 'id_number':id_number, 'doctor_name':doctor_name})
        set_appointment.invoke({'desired_date':new_date, 'id_number': id_number, 'doctor_name': doctor_name})
        return "Successfully rescheduled for the desired time"