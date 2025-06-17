# Copyright (c) 2025, shreshtadev and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import frappe.utils
import frappe.utils.logger

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("sbms_survey.member_details", allow_site=True, file_count=1)

class MemberDetails(Document):
    def __handle_when_clear_parent_ref(self, old_family_ref: str) -> None:
         old_parent_doc = frappe.get_doc("Family Details", old_family_ref)
         family_members = old_parent_doc.get('family_members', default=[])
         to_remove = [d for d in family_members if d.full_name.lower() == str(self.get_value('full_name')).lower()]
         for row in to_remove:
            old_parent_doc.remove(row)
         if len(to_remove) > 0:
             old_parent_doc.save()

    def __handle_when_update_parent_ref(self, family_ref: str) -> None:
         fd = frappe.get_doc("Family Details", family_ref)
         if fd is not None:
            # Check if the family member already exists
            family_members = fd.get('family_members', default=[])
            existing_member = next((d for d in family_members if d.full_name.lower() == str(self.get_value('full_name')).lower()), None)
            if not existing_member:
                fd.append('family_members', {
                    'full_name': str(self.get_value('full_name')).upper() if self.get_value('full_name') else 'NA',
                    'related_as': self.get_value('related_as'),
                    'marital_status': self.get_value('marital_status'),
                    'phone_number': self.get_value('phone_number'),
                    'email_address': self.get_value('email_address'),
                    'education_or_occupation': self.get_value('education_profession'),
                    'age': self.get_value('age')
                })
            fd.save()

    def before_save(self):
            old_doc = self.get_doc_before_save()
            family_detail_id = self.get_value('family_ref')
            old_doc_family_ref = old_doc.get_value('family_ref')
            if family_detail_id == old_doc_family_ref:
                logger.info(f"No changes in parent reference for {self.get_value('full_name')}, skipping update.")
            elif not family_detail_id and old_doc_family_ref:
                logger.info(f"Clearing parent reference for {self.get_value('full_name')} as family_ref is None")
                self.__handle_when_clear_parent_ref(old_family_ref=str(old_doc_family_ref))
            elif family_detail_id and not old_doc_family_ref:
                logger.info(f"Updating parent reference for {self.get_value('full_name')} to family_ref {family_detail_id}")
                self.__handle_when_update_parent_ref(family_ref=str(family_detail_id))
            elif family_detail_id and old_doc_family_ref and family_detail_id != old_doc_family_ref:
                logger.info(f"Updating parent reference for {self.get_value('full_name')} from {old_doc_family_ref} to {family_detail_id}")
                self.__handle_when_clear_parent_ref(old_family_ref=str(old_doc_family_ref))
                self.__handle_when_update_parent_ref(family_ref=str(family_detail_id))
