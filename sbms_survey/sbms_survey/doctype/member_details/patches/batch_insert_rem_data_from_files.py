import frappe
import polars as pl
from sbms_survey.sbms_survey.doctype.family_details.patches.batch_insert_all_data_from_files import format_phone_number, get_csv_files_from_directory, read_csvs, validated_email

def family_members_unassigned(member_data: pl.DataFrame):
    """
    Process member data to find unassigned family members.
    Args:
        member_data (pl.DataFrame): DataFrame containing member details.
    Returns:
        list: List of unassigned family members.
    """
    if member_data is None or member_data.is_empty():
        return None

    unassigned_members = member_data.filter(pl.col('family_detail_id').is_null()).to_dicts()
    return unassigned_members

def execute():
     all_files = get_csv_files_from_directory()
     md1 = read_csvs(all_files['mdss'])
     if md1 is not None:
         md1 = family_members_unassigned(md1)
         if md1 is not None:
             for row in md1:
                 mdmr = frappe.new_doc('Member Details')
                 mdmr.set('full_name', row['full_name'] if row['full_name'] is not None else 'NA')
                 mdmr.set('related_as', row['related_as'])
                 mdmr.set('marital_status', row['is_married'])
                 mdmr.set('phone_number', format_phone_number(row['phone_number']))
                 mdmr.set('email_address', validated_email([row['email_address']]))
                 mdmr.set('education_profession', row['education_profession'])
                 mdmr.set('age', row['age'])
                 mdmr.save()
         print('Complete Adding Remaining Details')


# This function is called by Frappe to execute the patch
