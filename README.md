# LIIA child-level analysis

Welcome to the LIIA child-level analysis ingest code! This code was developed as part of a project to collect CIN Census data from multiple local authorities, clean it and combine it in a set of spreadsheets ready for visualisation (done on PowerBI).

The code goes through 3 main steps:
- Step 1: Pull multiple CIN Census files into a unique event-based, flat CSV for each LA.
- Step 2: Concatenate the various LA flat files into a unique CSV.
- Step 3: Create specific tables for various analyses: assessment factors, referral journeys, S47 journeys.

## Step 0: Config
The file paths need to be defined in the config notebook. We recommend creating a folder for the project, with the following subfolders:
- 'CIN' folder: contains one folder per LA (e.g. "Wandsworth", "Islington", etc.) each containing the CIN Census XML files
- 'Flatfile' folder: empty for now, will contain the LA combined CSVs
- 'Output' folder: empty for now, will contain specific cuts for various analyses


## Step 1: Pull multiple CIN Census files into a unique event-based, flat CSV for each LA

#### 1-create-la-flatfile
- Input: Standard XML CIN Census (what is sent to DfE), stored in the 'CIN' folder and in each LA folder.
- Action: The code degrades the information contained in 'Date of Birth' to protect the identify of children. It transforms it into 1) Year of birth, and 2) School year (see definition further down). Then the code runs through the CIN Census to check for obvious errors, such as invalid formats for dates or empty tags. This is light touch validation work, much simpler than the validation done by DfE. Finally, the code extracts the hierarchical information to turn it into a flat table. Each row of the new table is a Date associated with an event (Assessment Start, CIN Referral, CPP close, etc.) with additional information in the columns. The flat format enables more easy access to information, compared to XML.
- Option to run this notebook only for LA data not processed already (`process_missing_only=True`) or for ALL LAs, regardless of those already processed (`process_missing_only=False`). This is in case a large number of LAs send data at multiple dates, to enable the processing of those received first and process the rest later.
- Output: CSVs of all dates and events recorded in the CIN Census, for each LA.


## Step 2: Concatenate the various LA flat files into a unique CSV

#### 2-concat
- Input: CSVs from notebook 1 above, stored in teh 'Flat file' folder.
- Action: Concatenate all the CSVs from each LA into a single one. For precaution, we are re-generating LA child IDs in case several LAs have the same: we add the 3 first letters of the LA as a prefix to the ID.
- Output: A unique CSV of all LA events.


## Step 3: Create specific tables for journeys

#### 3-assessment-factors
- Input: CSV from notebook 2.
- Action: Extract assessments information and create flags for each factor (one column per factor) to facilitate further analysis.
- Output: CSV with factor information.

#### 3-s47-journeys
- Input: CSV from notebook 2.
- Action: Link each S47 event to an ICPC and CPP events experienced by the child to understand their trajectory. To be able to feed it into a Sankey chart on PowerBI, it needs to be shaped in a particular way (see info in notebook).
- Output: CSV with S47 information matched to ICPC and CPP where relevant.

#### 3-referral-journeys
- Input: CSV from notebook 2.
- Action: Link each Referral event to an Assessment (either S17 or S47) experienced by the child. 
- Output: CSV with one row per Referral, with a column specifying what the outcome was (S17, S47, S17+S47 or No Further Action).


## Definitions
School year: refers to the school year (1st September - 31st August) the child was born into. For example:
- A child born on 24/03/1996 has a school year of 1995.
- A child born on 01/09/2000 has a school year of 2000.
- A child born on 31/08/2009 has a school year of 2008.

## Get in touch
If you have any questions about this code, get in touch with Elaine Merrins (Elaine.Merrins@walthamforest.gov.uk) and Celine Gross (celine.gross@socialfinance.org.uk).
