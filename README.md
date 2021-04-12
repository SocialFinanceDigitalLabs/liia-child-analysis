# LIIA child-level analysis

Welcome to the LIIA child-level analysis ingest code! This code was developed as part of a project to collect CIN Census data from multiple local authorities, clean it and combine it in a spreadsheet ready for visualisation (most of it done on PowerBI).

The code goes through 3 main steps:
- Step 1: Transform the CIN Census from each local authority and bring them together into a unique CSV. It is possible to stop here, and do further analysis with PowerBI.
- Step 2: Create a specific table for assessments and factors identified.
- Step 3: Create specific tables for journeys: 1) What happens at S47? 2) What happens at the Front Door?

## Step 1: Transform the CIN Census from each local authority and bring them together into a unique CSV

Notebooks 10, 11 and 12 need to be run for each local authority.

#### 10-degrade-cincensus
- Input: Standard XML CIN Census (what is sent to DfE).
- Action: The code degrades the information contained in 'Date of Birth' to protect the identify of children. It transforms it into 1) Year of birth, and 2) School year (see definition further down).
- Output: XML CIN Census with only year data in the tag <PersonBirthDate>, and a new tag <PersonSchoolYear> with the child's school year.

#### 11-clean-cincensus
- Input: CIN Census from notebook 10 above.
- Action: The code runs through the CIN Census to check for obvious errors, such as invalid formats for dates or empty tags. This is light touch validation work, much simpler than the validation done by DfE.
- Output: XML CIN Census with light-touch cleaning.

#### 12-create-flat-file
- Input: CIN Census from notebook 11 above.
- Action: The code extracts the hierarchical information to turn it into a flat table. Each row of the new table is a Date associated with an event (Assessment Start, CIN Referral, CPP close, etc.) with additional information in the columns. The flat format enables more easy access to information, compared to XML.
- Output: CSV of all dates and events recorded in the CIN Census.

#### 13-concat
- Input: CSVs from notebook 12 above, for all LAs included in the analysis.
- Action: Concatenate all the CSVs from each LA into a single one. For precaution, we are re-generating LA child IDs in case several LAs have the same: we add the 3 first letters of the LA as a prefix to the ID.
- Output: A unique CSV of all LA events.

## Step 2: Create a specific table for assessments and factors identified

#### 20-assessment-factors
- Input: CSV from notebook 13.
- Action: Extract assessments information and create flags for each factor (one column per factor) to facilitate further analysis.
- Output: CSV with factor information.

## Step 3: Create specific tables for journeys

#### 30-s47-journeys
- Input: CSV from notebook 13.
- Action: Link S47, ICPC and CPP events experienced by each child to understand their trajectory. Shape the resulting table into a format that can feed into a Sankey Chart, with "Source" and "Destination". E.g.: if 10 children went from S47 to ICPC, but only 8 of those to CPP start, it will show as:

| Source      | Destination | Count       |
| ----------- | ----------- | ----------- |
| S47         | ICPC        | 10          |
| ICPC        | CPP start   | 8           | 
(This is a simplified view - we also include info on age, gender, ethnicity and disability for further analysis)
- Output: CSV with the format highlighted in the example above.

#### Other journeys - TBD


## Definitions
School year: refers to the school year (1st September - 31st August) the child was born into. For example:
- A child born on 24/03/1996 has a school year of 1995.
- A child born on 01/09/2000 has a school year of 2000.
- A child born on 31/08/2009 has a school year of 2008.
