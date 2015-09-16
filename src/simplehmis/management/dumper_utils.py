import csv

from simplehmis.models import (
    ClientRace, Household, HouseholdMember, Project, ClientEntryAssessment,
    ClientExitAssessment)

import logging
logger = logging.getLogger(__name__)


class DumpHelper:
    """
    A helper class for a `Manager` to dump data to a CSV file.

    """
    def dump_to_csv_file(self, manager, filename,
                         all_fields=tuple(), hud_code_fields=dict(),
                         multi_hud_code_fields=set(),
                         renamed_fields=dict()):
        logger.debug('Opening the CSV file {}'.format(filename))

        all_fields = list(all_fields)

        for field in hud_code_fields.keys() | multi_hud_code_fields:
            i = all_fields.index(field)
            all_fields.insert(i + 1, field + ' display value')

        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, all_fields)

            writer.writeheader()

            for obj in manager.all():
                data = self.build_row(obj, all_fields, hud_code_fields,
                                      multi_hud_code_fields, renamed_fields)
                writer.writerow(data)

    def build_row(self, obj, all_fields, hud_code_fields,
                  multi_hud_code_fields, renamed_fields, data=None):
        if data is None:
            data = {}

        for field in all_fields:
            if field in data:
                continue

            if field in hud_code_fields:
                display = hud_code_fields[field]
                code = getattr(obj, field)
                data[field] = code
                try:
                    data[field + ' display value'] = display[code]
                except KeyError:
                    raise KeyError('Hud code {} for field {} not found in {}'.format(code, field, display))
            elif field in multi_hud_code_fields:
                codes = getattr(obj, field).all()
                data[field] = ';'.join(str(code.hud_value) for code in codes)
                data[field + ' display value'] = ';'.join(code.label for code in codes)
            elif field in renamed_fields:
                orig_field = renamed_fields[field]
                data[field] = getattr(obj, orig_field)
            else:
                data[field] = getattr(obj, field)
        return data


class HouseholdMemberDumpHelper (DumpHelper):
    def build_row(self, obj, all_fields, hud_code_fields,
                  multi_hud_code_fields, renamed_fields, data=None):
        if data is None:
            data = {}

        data['project_id'] = obj.household.project.id
        data['project_name'] = obj.household.project.name

        return super().build_row(obj, all_fields, hud_code_fields,
                                 multi_hud_code_fields, renamed_fields,
                                 data=data)
