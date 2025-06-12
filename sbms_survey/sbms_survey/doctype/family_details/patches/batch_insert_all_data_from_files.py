
import os
import frappe
import phonenumbers
import csv

import frappe.utils

def read_csv_file(file_path):
    """Reads a CSV file and prints each row.
    Args:
      file_path: The path to the CSV file.
    """
    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            rows = []
            for row in csv_reader:
                rows.append(row)
            return rows
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# read csv files from a given directory with frappe
def get_csv_files_from_directory(directory='../data'):
    """Get all CSV files from a directory using frappe helper methods."""
    files = dict()
    directory_path = frappe.get_app_path("sbms_survey", directory)
    files['family_details'] = os.path.join(directory_path, "family_details.csv")
    files['family_member_details'] = os.path.join(directory_path, "family_members_details.csv")
    return files

def format_phone_number(raw_number, country_code="IN"):
    if not raw_number or raw_number.strip() == "":
        return None  # Return None or a default value if empty

    try:
        number = phonenumbers.parse(raw_number, country_code)
        if phonenumbers.is_valid_number(number):
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164).replace('+91', '+91-')
        else:
            return None  # Invalid number
    except phonenumbers.NumberParseException:
        return None  # Handle parsing errors


def save_family_details():
     """Batch insert data from files"""
     all_files = get_csv_files_from_directory()
     family_details = read_csv_file(all_files['family_details'])
     family_member_details = read_csv_file(all_files['family_member_details'])

     if family_details and family_member_details:
         print(f"Found {len(family_details) - 1} rows in family_details.csv")
         for row in family_details[1:]:  # Skip header row
            doc = frappe.new_doc("Family Details")
            familyID = row[6]
            sl_no = row[3]
            doc.set('full_name', row[8] if row[8] else 'NA')
            doc.set('address_line_1', row[0])
            doc.set('email_address', row[1].lower().replace(' ', '') if row[1] else None)
            doc.set('veda' , row[2])
            doc.set('taluk', row[4])
            doc.set('gotra', row[5])
            doc.set('sub_category', row[9])
            doc.set('phone_number', format_phone_number(row[10]))
            doc.set('category', row[11])
            doc.set('area', row[12])
            doc.set('profession', row[14])
            family_members = [family_member for family_member in family_member_details if (familyID and family_member[3] == familyID) or (sl_no and family_member[4] == sl_no)]
            for member in family_members:
                doc.append('family_members', {
                    'full_name': member[9] if member[9] else 'NA',
                    'related_as': member[1],
                    'marital_status': member[8],
                    'phone_number': format_phone_number(member[6]),
                    'email_address': member[5].lower().replace(' ', '') if member[5] else None,
                    'education_or_occupation': member[7],
                    'age': member[2]
                })
            doc.save()
         print("Completed Family Details")


def execute():
     save_family_details()
# This function is called by Frappe to execute the patch
