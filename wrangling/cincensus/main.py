from lxml import etree
from datetime import datetime
import pandas as pd
import glob
import re
import os


def main(input_folder, config):
    '''Runs the degradation, cleaning and flat file steps'''
    
    # Find CIN files in the input folder
    cin_files = glob.glob(os.path.join(input_folder, "*.xml"))
    print("Found {} CIN files in folder {}".format(len(cin_files), input_folder))
    
    # Go through each CIN file
    clean_tree_list = []
    for i, file in enumerate(cin_files):
        filename = file.split('\\')[-1]
        print("File {} out of {}".format(i+1, len(cin_files)))
        
        # Degrade and clean
        print("--- Degrade file {}".format(i+1))
        degraded_tree = degradefile(file)
        print("--- Clean file {}".format(i+1))
        cleaned_tree = cleanfile(degraded_tree, config)
        
        # Save
        clean_tree_list.append(cleaned_tree)
    
    # Create CIN flatfile
    print("--- Create CIN flatfile")
    flatfile = build_cinrecord(clean_tree_list)
    
    return flatfile
    
    

# --- Degrade step ---

def degradefile(file):
    '''
    Degrades fields in the CIN Census. We are only degrading the birthdate here. We can adapt this function to degrade more fields.
    '''

    # Upload file and set root
    tree = etree.parse(file)
    root = tree.getroot()
    NS = get_namespace(root)

    # Set counter to 0
    birthdates_degraded = 0

    # Find all birthdates
    dates = root.findall('.//PersonBirthDate', NS)
    for date in dates:
        if len(date.text) > 4: #if birthdate not degraded
            birthdate = date.text
            birthdate = birthdate.replace('/', '-')
            year = re.search(r'\d{4}', birthdate).group(0)
            # Only keep year of birth
            date.text = year
            # Create new variable school year
            if birthdate > '{}-08-31'.format(year):
                school_year = year
            else:
                school_year = int(year) - 1
            parent = date.getparent()
            etree.SubElement(parent, 'PersonSchoolYear').text = str(school_year)
            # Count changes done
            birthdates_degraded += 1              
                
        
    changes = "{} PersonBirthDate events were found, of which {} were degraded to year of birth and school year".format(len(dates), birthdates_degraded)
    print(changes)
    
    return tree


# Function to identify namespace

def get_namespace(root):
    regex = r'{(.*)}.*' # pattern to pick up namespace
    namespace = re.findall(regex, root.tag)
    if len(namespace)>0:
        namespace = namespace[0]
    else:
        namespace = None
    NS = {None: namespace}
    return NS


# --- Clean step ---

# Main cleaner function

def cleanfile(tree, config):
    ''' Takes tree from degradefile step'''
    
    # Upload files and set root
    root = tree.getroot()
    NS = get_namespace(root)
    children = root.find('Children', NS)
    for child in children:
        child = cleanchild(child, config)
        
    return tree


# Cleaner functions depending on XML tag for each file

def cleanchild(value, config):
    for group in value:
        if group.tag.endswith('ChildIdentifiers'):
            group = childidentifiers(group, config['ChildIdentifiers'])
        elif group.tag.endswith('ChildCharacteristics'):
            group = childcharacteristics(group, config['ChildCharacteristics'])
        elif group.tag.endswith('CINdetails'):
            group = cindetails(group, config['CINdetails'])
    return value

# Child Identifiers functions
def childidentifiers(value, config):
    for group in value:
        if group.tag.endswith('LAchildID'):
            group = lachildid(group)
        if group.tag.endswith('UPN'):
            group = upn(group)
        if group.tag.endswith('FormerUPN'):
            group = formerupn(group)
        if group.tag.endswith('UPNunknown'):
            group = upnunknown(group, config['UPNunknown'])
        if group.tag.endswith('PersonBirthDate'):
            group = personbirthdate(group, config['PersonBirthDate'])
        if group.tag.endswith('ExpectedPersonBirthDate'):
            group = expectedpersonbirthdate(group, config['ExpectedPersonBirthDate'])
        if group.tag.endswith('GenderCurrent'):
            group = gendercurrent(group, config['GenderCurrent'])
        if group.tag.endswith('PersonDeathDate'):
            group = persondeathdate(group, config['PersonDeathDate'])
    return value

def lachildid(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
    # If time, add config and test that len<=10 and type = alphanumeric
    return value

def upn(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
    # If time, add config and test that len==13 and regex follows pattern
    return value

def formerupn(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
    # If time, add config and test that len==13 and regex follows pattern
    return value

def upnunknown(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def personbirthdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        #value.text = to_date(value.text, config['date']) This is disabled because we are degrading date of birth into year of birth
    return value

def expectedpersonbirthdate(value, config):
    if value.text is None:
        node = value.getparent()
        try:
            node.remove(value)
        except:
            pass
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value
# If time, add logical test to check there is just one birth date

def gendercurrent(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_category(value.text, config['category'])
    return value

def persondeathdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

# Child Characteristics functions
def childcharacteristics(value, config):
    for group in value:
        if group.tag.endswith('Ethnicity'):
            group = ethnicity(group, config['Ethnicity'])
        if group.tag.endswith('Disabilities'):
            group = disabilities(group, config['Disabilities'])
    return value

def ethnicity(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def disabilities(value, config):
    for group in value:
        if group.tag.endswith('Disability'):
            group = disability(group, config['Disability'])
        else:
            pass #Here add a flag if we are getting something else
    return value

def disability(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

# CIN Details functions
def cindetails(value, config):
    for group in value:
        if group.tag.endswith('CINreferralDate'):
            group = cinreferraldate(group, config['CINreferralDate'])
        if group.tag.endswith('ReferralSource'):
            group = referralsource(group, config['ReferralSource'])
        if group.tag.endswith('PrimaryNeedCode'):
            group = primaryneedcode(group, config['PrimaryNeedCode'])
        if group.tag.endswith('CINclosureDate'):
            group = cinclosuredate(group, config['CINclosureDate'])
        if group.tag.endswith('ReasonForClosure'):
            group = reasonforclosure(group, config['ReasonForClosure'])
        if group.tag.endswith('ReferralNFA'):
            group = referralnfa(group, config['ReferralNFA'])
        if group.tag.endswith('DateOfInitialCPC'):
            group = dateofinitialcpc(group, config['DateOfInitialCPC'])
        if group.tag.endswith('Assessments'):
            group = assessments(group, config['Assessments'])
        if group.tag.endswith('Section47'):
            group = section47(group, config['Section47'])
        if group.tag.endswith('ChildProtectionPlans'):
            group = childprotectionplans(group, config['ChildProtectionPlans'])
    return value

def cinreferraldate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def referralsource(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def primaryneedcode(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category']) 
    return value

def cinclosuredate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def reasonforclosure(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def referralnfa(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().capitalize()
        value.text = to_category(value.text, config['category'])
    return value

def dateofinitialcpc(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def assessments(value, config):
    for group in value:
        if group.tag.endswith('AssessmentActualStartDate'):
            group = assessmentactualstartdate(group, config['AssessmentActualStartDate'])
        if group.tag.endswith('AssessmentInternalReviewDate'):
            group = assessmentinternalreviewdate(group, config['AssessmentInternalReviewDate'])
        if group.tag.endswith('AssessmentAuthorisationDate'):
            group = assessmentauthorisationdate(group, config['AssessmentAuthorisationDate'])
        if group.tag.endswith('FactorsIdentifiedAtAssessment'):
            group = factorsidentifiedatassessment(group, config['FactorsIdentifiedAtAssessment'])
    return value

def assessmentactualstartdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def assessmentinternalreviewdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def assessmentauthorisationdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def factorsidentifiedatassessment(value, config):
    regex = r"(20|21|\d+[A-Z])"
    factors_list = []
    assessmentfactors_list = value.findall("AssessmentFactors")
    for assessmentfactor in assessmentfactors_list:
        factors_list.append(assessmentfactor.text.strip())
        value.remove(assessmentfactor)
    factors_list = ','.join(factors_list)
    # Use regex to get list of proper factors
    factors = re.findall(regex, factors_list)
    # Re-write AssessmentFactors in proper format in the xml - this is because several factors are on one line
    for factor in factors:
        add_factor = etree.SubElement(value, "AssessmentFactors")
        add_factor.text = factor
    return value     

def section47(value, config):
    for group in value:
        if group.tag.endswith('S47ActualStartDate'):
            group = s47actualstartdate(group, config['S47ActualStartDate'])
        if group.tag.endswith('InitialCPCtarget'):
            group = initialcpctarget(group, config['InitialCPCtarget'])
        if group.tag.endswith('DateOfInitialCPC'):
            group = dateofinitialcpc(group, config['DateOfInitialCPC'])
        if group.tag.endswith('ICPCnotRequired'):
            group = icpcnotrequired(group, config['ICPCnotRequired'])
    return value

def s47actualstartdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def initialcpctarget(value, config):
    if value.text is not None: #if time, automate the reading of 'canbeblank'
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def dateofinitialcpc(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def icpcnotrequired(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().capitalize()
        value.text = to_category(value.text, config['category'])
    return value

def childprotectionplans(value, config):
    for group in value:
        if group.tag.endswith('CPPstartDate'):
            group = cppstartdate(group, config['CPPstartDate'])
        if group.tag.endswith('InitialCategoryOfAbuse'):
            group = initialcategoryofabuse(group, config['InitialCategoryOfAbuse'])
        if group.tag.endswith('LatestCategoryOfAbuse'):
            group = latestcategoryofabuse(group, config['LatestCategoryOfAbuse'])
        if group.tag.endswith('NumberOfPreviousCPP'):
            group = numberofpreviouscpp(group)
        if group.tag.endswith('CPPendDate'):
            group = cppenddate(group, config['CPPendDate'])
        if group.tag.endswith('Reviews'):
            group = reviews(group, config['Reviews'])
    return value

def cppstartdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def initialcategoryofabuse(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def latestcategoryofabuse(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def numberofpreviouscpp(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_integer(value.text)
    return value

def cppenddate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value) 
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def reviews(value, config):
    for group in value:
        if group.tag.endswith('CPPreviewDate'):
            group = cppreviewdate(group, config['CPPreviewDate'])
        else:
            pass # if time, flag whatever else we find here
    return value

def cppreviewdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value


# Generic cleaner functions

def to_category(string, categories):
    for code in categories:
        if str(string).lower() == str(code['code']).lower():
            return code['code']
        elif 'name' in code:
            if str(code['name']).lower() in str(string).lower():
                return code['code']
    return 'Not in proper format: {}'.format(string)
    # If time, add here the matching report

def to_date(string, dateformat):
    string = string.replace('/', '-')
    try:
        datetime.strptime(string, dateformat) # Check this is possible
    except:
        string = 'Not in proper format: {}'.format(string)
    return string
    # If time, add here the matching report
    
def to_integer(string):
    try:
        int(string) # Check this is possible
    except:
        string = 'Not in proper format: {}'.format(string)
        # If time, add here the matching report

        
# --- Flatfile step ---

# Function to pull all the files data into a unique dataframe
# We recommend including all of the events into the cin log: it is the default list included below in build_cinrecord
# You can edit if you only need certain events

def build_cinrecord(trees, tag_list=['CINreferralDate', 'CINclosureDate', 'DateOfInitialCPC',
                                                        'AssessmentActualStartDate', 'AssessmentAuthorisationDate', 'S47ActualStartDate', 
                                                        'CPPstartDate', 'CPPendDate']):
    data_list = []
    for i, tree in enumerate(trees):
        # Upload trees and set root
        root = tree.getroot()
        NS = get_namespace(root)
        children = root.find('Children', NS)
        # Get data
        print('Extracting data from file {} out of {} from CIN Census'.format(i+1, len(trees)))
        file_data = buildchildren(children, tag_list, NS)
        data_list.append(file_data)
    cinrecord = pd.concat(data_list, sort=False)

    # Remove duplicates of LAchildID, Date and Type - we keep the one with the least null values
    cinrecord['null_values'] = cinrecord.isnull().sum(axis=1)
    cinrecord = cinrecord.sort_values('null_values')
    cinrecord.drop_duplicates(subset=['LAchildID', 'Date', 'Type'], keep='first', inplace=True)
    cinrecord.drop(labels='null_values', axis=1, inplace=True)

    # Re-arrange columns
    firstcols = ['LAchildID', 'Date', 'Type']
    newcols = firstcols + [col for col in list(cinrecord.columns) if col not in firstcols]
    cinrecord = cinrecord[newcols]

    print('Done!')
    
    return cinrecord



# Functions to build dataframes containing information of the child within each file

def buildchildren(children, tag_list, NS):
    df_list = []
    for child in children:
        data = buildchild(child, tag_list, NS)
        df_list.append(data)
    children_data = pd.concat(df_list, sort=False)    
    return children_data


def buildchild(child, tag_list, NS):
    '''
    Creates a dataframe storing all the events (specified in tag_list) that happened to the child
    Pass if no ChildIdentifiers, ChildCharacteristics and CINdetails
    '''
    df_list = []
    if 'ChildIdentifiers' in get_childrentags(child) and \
    'ChildCharacteristics' in get_childrentags(child) and \
    'CINdetails' in get_childrentags(child):
        for group in child:
            if group.tag.endswith('ChildIdentifiers'):
                childidentifiers = get_ChildIdentifiers(group)
            if group.tag.endswith('ChildCharacteristics'):
                childcharacteristics = get_ChildCharacteristics(group, NS)
            if group.tag.endswith('CINdetails'):
                for tag in tag_list:
                    event_list = group.findall('.//{}'.format(tag), NS)
                    for event in event_list:
                        event_group = get_group(event, NS)
                        df = pd.DataFrame(event_group)
                        df_list.append(df)        
        child_data = pd.concat(df_list, sort=False)
        for key, value in childidentifiers.items() :
            child_data[key] = value
        for key, value in childcharacteristics.items() :
            child_data[key] = value
        # Fill forward the referral source, to make sure all events can be linked to the original referral partner
        if 'ReferralSource' in child_data.columns:
            child_data['ReferralSource'].fillna(method='ffill', inplace=True)
        return(child_data)
    
    return None


# Functions to store the information at child level

def get_ChildIdentifiers(element, NS=None):
    childidentifiers = {}
    for group in element:
        column = etree.QName(group).localname
        value = group.text
        childidentifiers[column] = value
    return childidentifiers


def get_ChildCharacteristics(element, NS):
    childcharacteristics = {}
    for group in element:
        if group.tag.endswith('Ethnicity'):
            column = etree.QName(group).localname
            value = group.text
        elif group.tag.endswith('Disabilities'):
            column = etree.QName(group).localname
            value = get_list(group, 'Disability', NS)
        childcharacteristics[column] = value
    return childcharacteristics


# Functions to get information at element level

def get_list(element, tag, NS):
    '''
    Starting from the 'element', makes a list of the contents of 'tag' nieces (siblings' children sharing the same tag)
    and returns a string
    '''
    value_list = []
    values = element.getparent().findall('.//{}'.format(tag), NS)
    for value in values:
        value_list.append(value.text.strip())
    value_list = (',').join(value_list)
    value_list = value_list.replace(' ', '')
    return value_list


def get_group(element, NS):
    group = {}
    # Load our reference element
    group['Date'] = element.text
    group['Type'] = etree.QName(element).localname
    # Get the other elements on the same level (siblings)
    siblings = element.getparent().getchildren()
    for sibling in siblings:
        if len(sibling.getchildren())==0: # if siblings don't have children, just get their value
            column = etree.QName(sibling).localname
            value = sibling.text
            group[column] = [value]
    # If we're in the Assessment or ChildProtectionPlans modules, we need to get down one level
    # to collect all AssessmentFactors and CPPreviewDate
    if element.getparent().tag.endswith('Assessments'):
        group['Factors'] = get_list(element, 'AssessmentFactors', NS)
    if element.getparent().tag.endswith('ChildProtectionPlans'):
        group['CPPreview'] = get_list(element, 'CPPreviewDate', NS)
    return group


def get_childrentags(element):
    '''
    Returns the list of tags of the element's children
    '''
    children = element.getchildren()
    tags = []
    for child in children:
        tags.append(etree.QName(child).localname)
    return tags