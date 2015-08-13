# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0003_auto_update_destination_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='ethnicity',
            field=models.PositiveIntegerField(choices=[(0, 'Non-Hispanic/Non-Latino'), (1, 'Hispanic/Latino'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='Ethnicity'),
        ),
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=models.PositiveIntegerField(choices=[(0, 'Female'), (1, 'Male'), (2, 'Transgender male to female'), (3, 'Transgender female to male'), (4, 'Other'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='client',
            name='race',
            field=models.PositiveIntegerField(choices=[(1, 'American Indian or Alaska Native'), (2, 'Asian'), (3, 'Black or African American'), (4, 'Native Hawaiian or Other Pacific Islander'), (5, 'White'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='Race'),
        ),
        migrations.AlterField(
            model_name='client',
            name='veteran_status',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], help_text='Only collect veteran status if client is over 18.', verbose_name='Veteran status (adults only)', blank=True, null=True, default=None),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='chronic_health',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a chronic health condition?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='chronic_health_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the chronic health condition expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='developmental_disability',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a developmental disability?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='developmental_disability_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the developmental disability expected to substantially impair ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='domestic_violence',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Client is a victim/survivor of domestic violence'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='domestic_violence_occurred',
            field=models.PositiveIntegerField(choices=[(1, 'Within the past three months'), (2, 'Three to six months ago (excluding six months exactly)'), (3, 'Six months to one year ago (excluding one year exactly)'), (4, 'One year ago or more'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If Client has experience domestic violence, when?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='health_insurance',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Client has health insurance'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='health_insurance_none_reason',
            field=models.PositiveIntegerField(choices=[(1, 'Applied; decision pending'), (2, 'Applied; client not eligible'), (3, 'Client did not apply'), (4, 'Insurance type N/A for this client'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If none of the above, give reason'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='hiv_aids',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have HIV/AIDS?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='hiv_aids_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is HIV/AIDS expected to substantially impair ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='income_status',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Income from any source?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='mental_health',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a mental health problem?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='mental_health_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the mental health problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='physical_disability',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a physical disability?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='physical_disability_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the physical disability expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='substance_abuse',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Alcohol abuse'), (2, 'Drug abuse'), (3, 'Both alcohol and drug abuse'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a substance abuse problem?'),
        ),
        migrations.AlterField(
            model_name='clientannualassessment',
            name='substance_abuse_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes for alcohol abuse, drug abuse, or both, is the substance abuse problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='chronic_health',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a chronic health condition?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='chronic_health_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the chronic health condition expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='developmental_disability',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a developmental disability?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='developmental_disability_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the developmental disability expected to substantially impair ability to live independently'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='domestic_violence',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Client is a victim/survivor of domestic violence'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='domestic_violence_occurred',
            field=models.PositiveIntegerField(choices=[(1, 'Within the past three months'), (2, 'Three to six months ago (excluding six months exactly)'), (3, 'Six months to one year ago (excluding one year exactly)'), (4, 'One year ago or more'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If Client has experience domestic violence, when?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='health_insurance',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Client has health insurance'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='health_insurance_none_reason',
            field=models.PositiveIntegerField(choices=[(1, 'Applied; decision pending'), (2, 'Applied; client not eligible'), (3, 'Client did not apply'), (4, 'Insurance type N/A for this client'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If none of the above, give reason'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='hiv_aids',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have HIV/AIDS?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='hiv_aids_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is HIV/AIDS expected to substantially impair ability to live independently'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='homeless_at_least_one_year',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Continuously homeless for at least one year'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='homeless_in_three_years',
            field=models.PositiveIntegerField(choices=[(0, '0 (not homeless - Prevention only)'), (1, '1 (homeless only this time)'), (2, '2'), (3, '3'), (4, '4 or more'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Number of times the client has been homeless in the past three years'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='homeless_months_in_three_years',
            field=models.PositiveIntegerField(choices=[(100, '0'), (101, '1'), (102, '2'), (103, '3'), (104, '4'), (105, '5'), (106, '6'), (107, '7'), (108, '8'), (109, '9'), (110, '10'), (111, '11'), (112, '12'), (7, 'More than 12 months'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If client has been homeless 4 or more times, how many total months homeless in the past three years'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='housing_status',
            field=models.PositiveIntegerField(choices=[(1, 'Category 1 - Homeless'), (2, 'Category 2 - At imminent risk of losing housing'), (5, 'Category 3 - Homeless only under other federal statutes'), (6, 'Category 4 - Fleeing domestic violence'), (3, 'At-risk of homelessness '), (4, 'Stably Housed'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Housing status'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='income_status',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Income from any source?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='length_at_prior_residence',
            field=models.PositiveIntegerField(choices=[(10, 'One day or less'), (11, 'Two days to one week'), (2, 'More than one week, but less than one month'), (3, 'One to three months'), (4, 'More than three months, but less than one year'), (5, 'One year or longer'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Length of time at prior residence'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='mental_health',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a mental health problem?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='mental_health_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the mental health problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='physical_disability',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a physical disability?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='physical_disability_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the physical disability expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='prior_residence',
            field=models.PositiveIntegerField(choices=[(1, 'Emergency shelter, including hotel or motel paid for with emergency shelter voucher'), (15, 'Foster care home or foster care group home'), (6, 'Hospital or other residential non-psychiatric medical facility'), (14, 'Hotel or motel paid for without emergency shelter voucher'), (7, 'Jail, prison or juvenile detention facility'), (24, 'Long-term care facility or nursing home'), (23, 'Owned by client, no ongoing housing subsidy'), (21, 'Owned by client, with ongoing housing subsidy'), (3, 'Permanent housing for formerly homeless persons (such as: a CoC project; HUD legacy programs; or HOPWA PH)'), (16, 'Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)'), (4, 'Psychiatric hospital or other psychiatric facility'), (22, 'Rental by client, no ongoing housing subsidy'), (19, 'Rental by client, with VASH subsidy'), (25, 'Rental by client, with GPD TIP subsidy'), (20, 'Rental by client, with other ongoing housing subsidy'), (26, 'Residential project or halfway house with no homeless criteria'), (18, 'Safe Haven'), (12, 'Staying or living in a family member’s room, apartment or house'), (13, 'Staying or living in a friend’s room, apartment or house'), (5, 'Substance abuse treatment facility or detox center'), (2, 'Transitional housing for homeless persons (including homeless youth)'), (17, 'Other'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Type of residence prior to project entry'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='substance_abuse',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Alcohol abuse'), (2, 'Drug abuse'), (3, 'Both alcohol and drug abuse'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a substance abuse problem?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='substance_abuse_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes for alcohol abuse, drug abuse, or both, is the substance abuse problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='chronic_health',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a chronic health condition?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='chronic_health_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the chronic health condition expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='destination',
            field=models.PositiveIntegerField(choices=[(24, 'Deceased'), (1, 'Emergency shelter, including hotel or motel paid for with emergency shelter voucher'), (15, 'Foster care home or foster care group home'), (6, 'Hospital or other residential non-psychiatric medical facility'), (14, 'Hotel or motel paid for without emergency shelter voucher'), (7, 'Jail, prison or juvenile detention facility'), (25, 'Long-term care facility or nursing home'), (26, 'Moved from one HOPWA funded project to HOPWA PH'), (27, 'Moved from one HOPWA funded project to HOPWA TH'), (11, 'Owned by client, no ongoing housing subsidy'), (21, 'Owned by client, with ongoing housing subsidy'), (3, 'Permanent housing for formerly homeless persons (such as: CoC project; or HUD legacy programs; or HOPWA PH)'), (16, 'Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)'), (4, 'Psychiatric hospital or other psychiatric facility'), (10, 'Rental by client, no ongoing housing subsidy'), (19, 'Rental by client, with VASH housing subsidy'), (28, 'Rental by client, with GPD TIP housing subsidy'), (20, 'Rental by client, with other ongoing housing subsidy'), (29, 'Residential project or halfway house with no homeless criteria'), (18, 'Safe Haven'), (22, 'Staying or living with family, permanent tenure'), (12, 'Staying or living with family, temporary tenure (e.g., room, apartment or house)'), (23, 'Staying or living with friends, permanent tenure'), (13, 'Staying or living with friends, temporary tenure (e.g., room apartment or house)'), (5, 'Substance abuse treatment facility or detox center'), (2, 'Transitional housing for homeless persons (including homeless youth)'), (17, 'Other'), (30, 'No exit interview completed'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], null=True),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='developmental_disability',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a developmental disability?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='developmental_disability_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the developmental disability expected to substantially impair ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='domestic_violence',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Client is a victim/survivor of domestic violence'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='domestic_violence_occurred',
            field=models.PositiveIntegerField(choices=[(1, 'Within the past three months'), (2, 'Three to six months ago (excluding six months exactly)'), (3, 'Six months to one year ago (excluding one year exactly)'), (4, 'One year ago or more'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If Client has experience domestic violence, when?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='health_insurance',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Client has health insurance'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='health_insurance_none_reason',
            field=models.PositiveIntegerField(choices=[(1, 'Applied; decision pending'), (2, 'Applied; client not eligible'), (3, 'Client did not apply'), (4, 'Insurance type N/A for this client'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If none of the above, give reason'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='hiv_aids',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have HIV/AIDS?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='hiv_aids_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is HIV/AIDS expected to substantially impair ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='income_status',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Income from any source?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='mental_health',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a mental health problem?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='mental_health_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the mental health problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='physical_disability',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a physical disability?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='physical_disability_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes, is the physical disability expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='substance_abuse',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Alcohol abuse'), (2, 'Drug abuse'), (3, 'Both alcohol and drug abuse'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], default=None, null=True, verbose_name='Does the client have a substance abuse problem?'),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='substance_abuse_impairing',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], blank=True, default=None, null=True, verbose_name='If yes for alcohol abuse, drug abuse, or both, is the substance abuse problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'),
        ),
    ]
