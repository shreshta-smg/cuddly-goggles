
import os
import frappe
import phonenumbers
import polars as pl
import frappe.utils

def read_csvs(file_path):
    """
    Reads a CSV file using polars and returns a DataFrame.
    Allows access to columns by header column name.
    Args:
        file_path: The path to the CSV file.
    Returns:
        pl.DataFrame: Polars DataFrame with CSV data.
    """
    try:
        df = pl.read_csv(file_path)
        return df
    except Exception as e:
        print(f"An error occurred while reading CSV with polars: {e}")
        return None

# read csv files from a given directory with frappe
def get_csv_files_from_directory(directory='../data'):
     """Get all CSV files from a directory using frappe helper methods."""
     files = dict()
     family_file_names = ['fdss', 'veenadataentry_fdss', 'vipradetails1_fdss', 'vipradetails2_fdss']
     member_file_names = ['mdss', 'veenadataentry_mdss', 'vipradetails1_mdss', 'vipradetails2_mdss']
     directory_path = frappe.get_app_path("sbms_survey", directory)
     for ff in family_file_names:
         files[ff] = os.path.join(directory_path, f"{ff}.csv")
     for mf in member_file_names:
         files[mf] = os.path.join(directory_path, f"{mf}.csv")
     return files

def format_phone_number(raw_number, country_code="IN"):
    if not raw_number:
        return None  # Return None or a default value if empty
    if raw_number is None:
        return None
    if type(raw_number) is not str:
        raw_number = str(raw_number)
    try:
        number = phonenumbers.parse(raw_number, country_code)
        if phonenumbers.is_valid_number(number):
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164).replace('+91', '+91-')
        else:
            return None  # Invalid number
    except phonenumbers.NumberParseException:
        return None  # Handle parsing errors

def validated_email(list_of_emails: list[str]):
    """Validate a list of emails and return the first valid one."""
    for email in list_of_emails:
        if not email or email.strip() == "":
            return None
        email_valid = frappe.utils.validate_email_address(email.strip().lower().replace(' ', ''))
        if email_valid:
            return email_valid
    return None  # Return None if no valid email found


def save_family_details(survey_data: list[pl.DataFrame | None]):
     """Batch insert data from files"""
     family_details: pl.DataFrame | None = survey_data[0]
     family_member_details: pl.DataFrame | None = survey_data[1]

     if family_details is None:
         print("No Family Data Found")
         return
     if family_member_details is None:
         print("No Family Member Data Found")
         return

     if not family_details.is_empty():
         for row in family_details.to_dicts():  # Skip header row
            doc = frappe.new_doc("Family Details")
            sl_no = row['id']
            doc.set('full_name', row['full_name'].upper() if row['full_name'] is not None else 'NA')
            doc.set('address_line_1', row['address_line_1'])
            doc.set('email_address', validated_email([row['email_address']]))
            doc.set('veda' , row['veda'])
            doc.set('taluk', row['taluk'])
            doc.set('gotra', row['gothra'])
            doc.set('sub_category', row['sub_category'])
            doc.set('phone_number', format_phone_number(row['phone_number']))
            doc.set('category', row['category'])
            doc.set('area', row['area'])
            doc.set('profession', row['profession'])
            for member in family_member_details.filter((pl.col('family_detail_id') is not None and pl.col('family_detail_id') == sl_no)).to_dicts():
                doc.append('family_members', {
                    'full_name': member['full_name'].upper() if member['full_name'] else 'NA',
                    'related_as': member['related_as'],
                    'marital_status': member['is_married'],
                    'phone_number': format_phone_number(member['phone_number']),
                    'email_address': validated_email([member['email_address']]),
                    'education_or_occupation': member['education_profession'],
                    'age': member['age']
                })
            doc.save()
         print("Completed Family Details")


def execute():
     all_files = get_csv_files_from_directory()
     fd1 = read_csvs(all_files['fdss'])
     md1 = read_csvs(all_files['mdss'])
     fd2 = read_csvs(all_files['veenadataentry_fdss'])
     md2 = read_csvs(all_files['veenadataentry_mdss'])
     fd3 = read_csvs(all_files['vipradetails1_fdss'])
     md3 = read_csvs(all_files['vipradetails1_mdss'])
     fd4 = read_csvs(all_files['vipradetails2_fdss'])
     md4 = read_csvs(all_files['vipradetails2_mdss'])
     save_family_details([fd1, md1])
     save_family_details([fd2, md2])
     save_family_details([fd3, md3])
     save_family_details([fd4, md4])
# This function is called by Frappe to execute the patch
