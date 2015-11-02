import os
from django.core.management.base import BaseCommand
from django.db import transaction
from simplehmis import consts
from simplehmis.models import (Client, HouseholdMember, ClientEntryAssessment,
                               ClientAnnualAssessment, ClientExitAssessment)
from simplehmis.management.dumper_utils import DumpHelper


class Command(BaseCommand):
    help = ('Loads clients from a CSV file.')

    def add_arguments(self, parser):
        parser.add_argument('dirname', nargs=1, type=str)

    def handle(self, *args, **options):
        dirname = options['dirname'][0]

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with transaction.atomic():
            print('dumping clients')
            Client.objects.dump_to_csv_file(os.path.join(dirname, 'clients.csv'))
            print('enrollments')
            HouseholdMember.objects.filter(present_at_enrollment=True)\
                .dump_to_csv_file(os.path.join(dirname, 'enrollments.csv'))

            print('dumping entry assessments')
            DumpHelper().dump_to_csv_file(
                ClientEntryAssessment.objects.filter(member__present_at_enrollment=True),
                os.path.join(dirname, 'entry_assessments.csv'),
                all_fields=(
                    'enrollment_id',
                    'health_insurance', 'health_insurance_medicaid', 'health_insurance_medicare', 'health_insurance_chip', 'health_insurance_va', 'health_insurance_employer', 'health_insurance_cobra', 'health_insurance_private', 'health_insurance_state', 'health_insurance_none_reason',
                    'physical_disability', 'physical_disability_impairing', 'developmental_disability', 'developmental_disability_impairing', 'chronic_health', 'chronic_health_impairing', 'hiv_aids', 'hiv_aids_impairing', 'mental_health', 'mental_health_impairing', 'substance_abuse', 'substance_abuse_impairing',
                    'housing_status', 'entering_from_streets', 'homeless_start_date', 'homeless_in_three_years', 'homeless_months_in_three_years', 'status_documented', 'prior_residence', 'prior_residence_other', 'length_at_prior_residence',
                    'domestic_violence', 'domestic_violence_occurred',
                    'income_status', 'income_notes',
                ),
                hud_code_fields={
                    'health_insurance': dict(consts.HUD_YES_NO), 'health_insurance_medicaid': dict(consts.HUD_YES_NO), 'health_insurance_medicare': dict(consts.HUD_YES_NO), 'health_insurance_chip': dict(consts.HUD_YES_NO), 'health_insurance_va': dict(consts.HUD_YES_NO), 'health_insurance_employer': dict(consts.HUD_YES_NO), 'health_insurance_cobra': dict(consts.HUD_YES_NO), 'health_insurance_private': dict(consts.HUD_YES_NO), 'health_insurance_state': dict(consts.HUD_YES_NO), 'health_insurance_none_reason': dict(consts.HUD_CLIENT_UNINSURED_REASON),
                    'physical_disability': dict(consts.HUD_YES_NO), 'physical_disability_impairing': dict(consts.HUD_YES_NO), 'developmental_disability': dict(consts.HUD_YES_NO), 'developmental_disability_impairing': dict(consts.HUD_YES_NO), 'chronic_health': dict(consts.HUD_YES_NO), 'chronic_health_impairing': dict(consts.HUD_YES_NO), 'hiv_aids': dict(consts.HUD_YES_NO), 'hiv_aids_impairing': dict(consts.HUD_YES_NO), 'mental_health': dict(consts.HUD_YES_NO), 'mental_health_impairing': dict(consts.HUD_YES_NO), 'substance_abuse': dict(consts.HUD_CLIENT_SUBSTANCE_ABUSE), 'substance_abuse_impairing': dict(consts.HUD_YES_NO),
                    'housing_status': dict(consts.HUD_CLIENT_HOUSING_STATUS), 'entering_from_streets': dict(consts.HUD_YES_NO), 'homeless_in_three_years': dict(consts.HUD_CLIENT_HOMELESS_COUNT), 'homeless_months_in_three_years': dict(consts.HUD_CLIENT_HOMELESS_MONTHS), 'status_documented': dict(consts.HUD_YES_NO), 'prior_residence': dict(consts.HUD_CLIENT_PRIOR_RESIDENCE), 'length_at_prior_residence': dict(consts.HUD_CLIENT_LENGTH_AT_PRIOR_RESIDENCE),
                    'domestic_violence': dict(consts.HUD_YES_NO), 'domestic_violence_occurred': dict(consts.HUD_CLIENT_DOMESTIC_VIOLENCE),
                    'income_status': dict(consts.HUD_YES_NO),
                },
                multi_hud_code_fields=set(),
                renamed_fields={
                    'enrollment_id': 'member_id'
                },)

            print('dumping annual assessments')
            DumpHelper().dump_to_csv_file(
                ClientAnnualAssessment.objects.filter(member__present_at_enrollment=True),
                os.path.join(dirname, 'annual_assessments.csv'),
                all_fields=(
                    'enrollment_id',
                    'health_insurance', 'health_insurance_medicaid', 'health_insurance_medicare', 'health_insurance_chip', 'health_insurance_va', 'health_insurance_employer', 'health_insurance_cobra', 'health_insurance_private', 'health_insurance_state', 'health_insurance_none_reason',
                    'physical_disability', 'physical_disability_impairing', 'developmental_disability', 'developmental_disability_impairing', 'chronic_health', 'chronic_health_impairing', 'hiv_aids', 'hiv_aids_impairing', 'mental_health', 'mental_health_impairing', 'substance_abuse', 'substance_abuse_impairing',
                    'domestic_violence', 'domestic_violence_occurred',
                    'income_status', 'income_notes',
                ),
                hud_code_fields={
                    'health_insurance': dict(consts.HUD_YES_NO), 'health_insurance_medicaid': dict(consts.HUD_YES_NO), 'health_insurance_medicare': dict(consts.HUD_YES_NO), 'health_insurance_chip': dict(consts.HUD_YES_NO), 'health_insurance_va': dict(consts.HUD_YES_NO), 'health_insurance_employer': dict(consts.HUD_YES_NO), 'health_insurance_cobra': dict(consts.HUD_YES_NO), 'health_insurance_private': dict(consts.HUD_YES_NO), 'health_insurance_state': dict(consts.HUD_YES_NO), 'health_insurance_none_reason': dict(consts.HUD_CLIENT_UNINSURED_REASON),
                    'physical_disability': dict(consts.HUD_YES_NO), 'physical_disability_impairing': dict(consts.HUD_YES_NO), 'developmental_disability': dict(consts.HUD_YES_NO), 'developmental_disability_impairing': dict(consts.HUD_YES_NO), 'chronic_health': dict(consts.HUD_YES_NO), 'chronic_health_impairing': dict(consts.HUD_YES_NO), 'hiv_aids': dict(consts.HUD_YES_NO), 'hiv_aids_impairing': dict(consts.HUD_YES_NO), 'mental_health': dict(consts.HUD_YES_NO), 'mental_health_impairing': dict(consts.HUD_YES_NO), 'substance_abuse': dict(consts.HUD_CLIENT_SUBSTANCE_ABUSE), 'substance_abuse_impairing': dict(consts.HUD_YES_NO),
                    'domestic_violence': dict(consts.HUD_YES_NO), 'domestic_violence_occurred': dict(consts.HUD_CLIENT_DOMESTIC_VIOLENCE),
                    'income_status': dict(consts.HUD_YES_NO),
                },
                multi_hud_code_fields=set(),
                renamed_fields={
                    'enrollment_id': 'member_id'
                },)

            print('dumping exit assessments')
            DumpHelper().dump_to_csv_file(
                ClientExitAssessment.objects.filter(member__present_at_enrollment=True),
                os.path.join(dirname, 'exit_assessments.csv'),
                all_fields=(
                    'enrollment_id',
                    'health_insurance', 'health_insurance_medicaid', 'health_insurance_medicare', 'health_insurance_chip', 'health_insurance_va', 'health_insurance_employer', 'health_insurance_cobra', 'health_insurance_private', 'health_insurance_state', 'health_insurance_none_reason',
                    'physical_disability', 'physical_disability_impairing', 'developmental_disability', 'developmental_disability_impairing', 'chronic_health', 'chronic_health_impairing', 'hiv_aids', 'hiv_aids_impairing', 'mental_health', 'mental_health_impairing', 'substance_abuse', 'substance_abuse_impairing',
                    'domestic_violence', 'domestic_violence_occurred',
                    'income_status', 'income_notes',
                    'destination',
                    'destination_other',
                ),
                hud_code_fields={
                    'health_insurance': dict(consts.HUD_YES_NO), 'health_insurance_medicaid': dict(consts.HUD_YES_NO), 'health_insurance_medicare': dict(consts.HUD_YES_NO), 'health_insurance_chip': dict(consts.HUD_YES_NO), 'health_insurance_va': dict(consts.HUD_YES_NO), 'health_insurance_employer': dict(consts.HUD_YES_NO), 'health_insurance_cobra': dict(consts.HUD_YES_NO), 'health_insurance_private': dict(consts.HUD_YES_NO), 'health_insurance_state': dict(consts.HUD_YES_NO), 'health_insurance_none_reason': dict(consts.HUD_CLIENT_UNINSURED_REASON),
                    'physical_disability': dict(consts.HUD_YES_NO), 'physical_disability_impairing': dict(consts.HUD_YES_NO), 'developmental_disability': dict(consts.HUD_YES_NO), 'developmental_disability_impairing': dict(consts.HUD_YES_NO), 'chronic_health': dict(consts.HUD_YES_NO), 'chronic_health_impairing': dict(consts.HUD_YES_NO), 'hiv_aids': dict(consts.HUD_YES_NO), 'hiv_aids_impairing': dict(consts.HUD_YES_NO), 'mental_health': dict(consts.HUD_YES_NO), 'mental_health_impairing': dict(consts.HUD_YES_NO), 'substance_abuse': dict(consts.HUD_CLIENT_SUBSTANCE_ABUSE), 'substance_abuse_impairing': dict(consts.HUD_YES_NO),
                    'domestic_violence': dict(consts.HUD_YES_NO), 'domestic_violence_occurred': dict(consts.HUD_CLIENT_DOMESTIC_VIOLENCE),
                    'income_status': dict(consts.HUD_YES_NO),
                    'destination': dict(consts.HUD_CLIENT_DESTINATION),
                },
                multi_hud_code_fields=set(),
                renamed_fields={
                    'enrollment_id': 'member_id'
                },)
