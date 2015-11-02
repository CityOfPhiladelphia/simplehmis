# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

HUD_CLIENT_DOESNT_KNOW = 8
HUD_CLIENT_REFUSED = 9
HUD_DATA_NOT_COLLECTED = 99
HUD_BLANK = None

HUD_DEFAULT_DATA_QUALITY = [
    (HUD_CLIENT_DOESNT_KNOW, _('Client doesn’t know')),
    (HUD_CLIENT_REFUSED,     _('Client refused')),
    (HUD_DATA_NOT_COLLECTED, _('Data not collected')),
    (HUD_BLANK, _('(Please choose an option)')),
]

def with_data_quality(d):
    return d + HUD_DEFAULT_DATA_QUALITY

YES_NO = [
    (0, _('No')),
    (1, _('Yes')),
]

HUD_YES_NO = with_data_quality(YES_NO)

HUD_CLIENT_NAME_QUALITY = with_data_quality([
    (1, _('Full name reported')),
    (2, _('Partial, street name, or code name reported')),
])

HUD_CLIENT_SSN_QUALITY = with_data_quality([
    (1, _('Full SSN reported')),
    (2, _('Approximate or partial SSN reported')),
])

HUD_CLIENT_DOB_QUALITY = with_data_quality([
    (1, _('Full DOB reported')),
    (2, _('Approximate or partial DOB reported')),
])

HUD_CLIENT_RACE = with_data_quality([
    (1, _('American Indian or Alaska Native')),
    (2, _('Asian')),
    (3, _('Black or African American')),
    (4, _('Native Hawaiian or Other Pacific Islander')),
    (5, _('White')),
])

HUD_CLIENT_ETHNICITY = with_data_quality([
    (0, _('Non-Hispanic/Non-Latino')),
    (1, _('Hispanic/Latino')),
])

HUD_CLIENT_GENDER = with_data_quality([
    (0, _('Female')),
    (1, _('Male')),
    (2, _('Transgender male to female')),
    (3, _('Transgender female to male')),
    (4, _('Other')),
])

HUD_CLIENT_HOH_RELATIONSHIP = [
    (None, _('(Please select a relationship to the head of household)')),
    (1, _('Self (head of household)')),
    (2, _('Head of household’s child')),
    (3, _('Head of household’s spouse or partner')),
    (4, _('Head of household’s other relation member (other relation to head of household)')),
    (5, _('Other: non-relation member')),
]

HUD_CLIENT_SUBSTANCE_ABUSE = with_data_quality([
    (0, _('No')),
    (1, _('Alcohol abuse')),
    (2, _('Drug abuse')),
    (3, _('Both alcohol and drug abuse')),
])

HUD_CLIENT_UNINSURED_REASON = with_data_quality([
    (1, _('Applied; decision pending')),
    (2, _('Applied; client not eligible')),
    (3, _('Client did not apply')),
    (4, _('Insurance type N/A for this client')),
])

HUD_CLIENT_EXIT_DESTINATION = with_data_quality([
    (24, _('Deceased')),
    (1, _('Emergency shelter, including hotel or motel paid for with emergency shelter voucher')),
    (15, _('Foster care home or foster care group home')),
    (6, _('Hospital or other residential non-psychiatric medical facility')),
    (14, _('Hotel or motel paid for without emergency shelter voucher')),
    (7, _('Jail, prison or juvenile detention facility')),
    (25, _('Long-term care facility or nursing home')),
    (26, _('Moved from one HOPWA funded project to HOPWA PH')),
    (27, _('Moved from one HOPWA funded project to HOPWA TH')),
    (11, _('Owned by client, no ongoing housing subsidy')),
    (21, _('Owned by client, with ongoing housing subsidy')),
    (3, _('Permanent housing for formerly homeless persons (such as: CoC project; or HUD legacy programs; or HOPWA PH)')),
    (16, _('Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)')),
    (4, _('Psychiatric hospital or other psychiatric facility')),
    (10, _('Rental by client, no ongoing housing subsidy')),
    (19, _('Rental by client, with VASH housing subsidy')),
    (28, _('Rental by client, with GPD TIP housing subsidy')),
    (20, _('Rental by client, with other ongoing housing subsidy')),
    (29, _('Residential project or halfway house with no homeless criteria')),
    (18, _('Safe Haven')),
    (22, _('Staying or living with family, permanent tenure')),
    (12, _('Staying or living with family, temporary tenure (e.g., room, apartment or house)')),
    (23, _('Staying or living with friends, permanent tenure')),
    (13, _('Staying or living with friends, temporary tenure (e.g., room apartment or house)')),
    (5, _('Substance abuse treatment facility or detox center')),
    (2, _('Transitional housing for homeless persons (including homeless youth)')),
    (17, _('Other')),
    (30, _('No exit interview completed')),
])

HUD_CLIENT_PRIOR_RESIDENCE = with_data_quality([
    (1, _('Emergency shelter, including hotel or motel paid for with emergency shelter voucher')),
    (15, _('Foster care home or foster care group home')),
    (6, _('Hospital or other residential non-psychiatric medical facility')),
    (14, _('Hotel or motel paid for without emergency shelter voucher')),
    (7, _('Jail, prison or juvenile detention facility')),
    (24, _('Long-term care facility or nursing home')),
    (23, _('Owned by client, no ongoing housing subsidy')),
    (21, _('Owned by client, with ongoing housing subsidy')),
    (3, _('Permanent housing for formerly homeless persons (such as: a CoC project; HUD legacy programs; or HOPWA PH)')),
    (16, _('Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)')),
    (4, _('Psychiatric hospital or other psychiatric facility')),
    (22, _('Rental by client, no ongoing housing subsidy')),
    (19, _('Rental by client, with VASH subsidy')),
    (25, _('Rental by client, with GPD TIP subsidy')),
    (20, _('Rental by client, with other ongoing housing subsidy')),
    (26, _('Residential project or halfway house with no homeless criteria')),
    (18, _('Safe Haven')),
    (12, _('Staying or living in a family member’s room, apartment or house')),
    (13, _('Staying or living in a friend’s room, apartment or house')),
    (5, _('Substance abuse treatment facility or detox center')),
    (2, _('Transitional housing for homeless persons (including homeless youth)')),
    (17, _('Other')),
])

HUD_CLIENT_LENGTH_AT_PRIOR_RESIDENCE = with_data_quality([
    (10, _('One day or less')),
    (11, _('Two days to one week')),
    (2, _('More than one week, but less than one month')),
    (3, _('One to three months')),
    (4, _('More than three months, but less than one year')),
    (5, _('One year or longer')),
])

HUD_CLIENT_DESTINATION = with_data_quality([
    (24, _('Deceased')),
    (1, _('Emergency shelter, including hotel or motel paid for with emergency shelter voucher')),
    (15, _('Foster care home or foster care group home')),
    (6, _('Hospital or other residential non-psychiatric medical facility')),
    (14, _('Hotel or motel paid for without emergency shelter voucher')),
    (7, _('Jail, prison or juvenile detention facility')),
    (25, _('Long-term care facility or nursing home')),
    (26, _('Moved from one HOPWA funded project to HOPWA PH')),
    (27, _('Moved from one HOPWA funded project to HOPWA TH')),
    (11, _('Owned by client, no ongoing housing subsidy')),
    (21, _('Owned by client, with ongoing housing subsidy')),
    (3, _('Permanent housing for formerly homeless persons (such as: CoC project; or HUD legacy programs; or HOPWA PH)')),
    (16, _('Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)')),
    (4, _('Psychiatric hospital or other psychiatric facility')),
    (10, _('Rental by client, no ongoing housing subsidy')),
    (19, _('Rental by client, with VASH housing subsidy')),
    (28, _('Rental by client, with GPD TIP housing subsidy')),
    (20, _('Rental by client, with other ongoing housing subsidy')),
    (29, _('Residential project or halfway house with no homeless criteria')),
    (18, _('Safe Haven')),
    (22, _('Staying or living with family, permanent tenure')),
    (12, _('Staying or living with family, temporary tenure (e.g., room, apartment or house)')),
    (23, _('Staying or living with friends, permanent tenure')),
    (13, _('Staying or living with friends, temporary tenure (e.g., room apartment or house)')),
    (5, _('Substance abuse treatment facility or detox center')),
    (2, _('Transitional housing for homeless persons (including homeless youth)')),
    (17, _('Other')),
    (30, _('No exit interview completed')),
])

HUD_CLIENT_HOMELESS_COUNT = with_data_quality([
    (0, _('Never in 3 years')),
    (1, _('One time')),
    (2, _('Two times')),
    (3, _('Three times')),
    (4, _('Four or more times')),
])

HUD_CLIENT_HOMELESS_MONTHS = [
    (101, _('One Month'))] + [
    (100 + m, str(m)) for m in range(2, 13)] + with_data_quality([
    (113, _('More than 12 months')),
])

HUD_CLIENT_HOUSING_STATUS = with_data_quality([
    (1, _('Category 1 - Homeless')),
    (2, _('Category 2 - At imminent risk of losing housing')),
    (5, _('Category 3 - Homeless only under other federal statutes')),
    (6, _('Category 4 - Fleeing domestic violence')),
    (3, _('At-risk of homelessness ')),
    (4, _('Stably Housed')),
])

HUD_CLIENT_DOMESTIC_VIOLENCE = with_data_quality([
    (1, _('Within the past three months')),
    (2, _('Three to six months ago (excluding six months exactly)')),
    (3, _('Six months to one year ago (excluding one year exactly)')),
    (4, _('One year ago or more')),
])

HUD_PROJECT_TYPE_CHOICES = (
    (1, _('Emergency Shelter')),
    (2, _('Transitional Housing')),
    (3, _('PH - Permanent Supportive Housing (disability required for entry)')),
    (4, _('Street Outreach')),
    (5, _('RETIRED')),
    (6, _('Services Only')),
    (7, _('Other')),
    (8, _('Safe Haven')),
    (9, _('PH – Housing Only')),
    (10, _('PH – Housing with Services (no disability required for entry)')),
    (11, _('Day Shelter')),
    (12, _('Homelessness Prevention')),
    (13, _('PH - Rapid Re-Housing')),
    (14, _('Coordinated Assessment')),
)

HUD_PROJECT_TRACKING_METHOD_CHOICES = (
    (0, _('Entry/Exit Date')),
    (3, _('Night-by-Night')),
)

HUD_FUNDING_PROGRAM_CHOICES = (
    (1, _('HUD:CoC – Homelessness Prevention (High Performing Comm. Only)')),
    (2, _('HUD:CoC – Permanent Supportive Housing ')),
    (3, _('HUD:CoC – Rapid Re-Housing')),
    (4, _('HUD:CoC – Supportive Services Only')),
    (5, _('HUD:CoC – Transitional Housing')),
    (6, _('HUD:CoC – Safe Haven')),
    (7, _('HUD:CoC – Single Room Occupancy (SRO)')),
    (8, _('HUD:ESG – Emergency Shelter (operating and/or essential services)')),
    (9, _('HUD:ESG – Homelessness Prevention ')),
    (10, _('HUD:ESG – Rapid Rehousing')),
    (11, _('HUD:ESG – Street Outreach')),
    (12, _('HUD:Rural Housing Stability Assistance Program ')),
    (13, _('HUD:HOPWA – Hotel/Motel Vouchers')),
    (14, _('HUD:HOPWA – Housing Information')),
    (15, _('HUD:HOPWA – Permanent Housing (facility based or TBRA)')),
    (16, _('HUD:HOPWA – Permanent Housing Placement ')),
    (17, _('HUD:HOPWA – Short-Term Rent, Mortgage, Utility assistance')),
    (18, _('HUD:HOPWA – Short-Term Supportive Facility')),
    (19, _('HUD:HOPWA – Transitional Housing (facility based or TBRA)')),
    (20, _('HUD:HUD/VASH')),
    (21, _('HHS:PATH – Street Outreach & Supportive Services Only')),
    (22, _('HHS:RHY – Basic Center Program (prevention and shelter)')),
    (23, _('HHS:RHY – Maternity Group Home for Pregnant and Parenting Youth')),
    (24, _('HHS:RHY – Transitional Living Program')),
    (25, _('HHS:RHY – Street Outreach Project')),
    (26, _('HHS:RHY – Demonstration Project**')),
    (27, _('VA: Community Contract Emergency Housing')),
    (28, _('VA: Community Contract Residential Treatment Program***')),
    (29, _('VA:Domiciliary Care***')),
    (30, _('VA:Community Contract Safe Haven Program***')),
    (31, _('VA:Grant and Per Diem Program')),
    (32, _('VA:Compensated Work Therapy Transitional Residence***')),
    (33, _('VA:Supportive Services for Veteran Families')),
    (34, _('N/A')),
)

