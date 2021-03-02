from lxml import etree
import re
import os 


def degradefiles(cin_files, output_folder):
    '''
    Degrades fields in the CIN Census. We are only degrading the birthdate here. We adapt this function to degrade more fields.
    '''
    birthdates_degraded = 0
    
    # Create borough folder
    borough = cin_files[0].split('\\')[-2]
    borough_folder = os.path.join(output_folder, borough)
    if not os.path.exists(borough_folder):
        os.makedirs(borough_folder)
    
    # Create text file to keep track of degradation
    f = open(os.path.join(borough_folder, '{}-degradation.txt'.format(borough)), "w")   
    
    # Go through each CIN file
    for i, file in enumerate(cin_files):
        filename = file.split('\\')[-1]
        print("File {} out of {}".format(i+1, len(cin_files)))

        # Upload file and set root
        tree = etree.parse(file)
        root = tree.getroot()
        NS = get_namespace(root)
        
        # Find all birthdates
        dates = root.findall('.//PersonBirthDate', NS)
        for date in dates:
            if len(date.text) > 4:
                year = re.search(r'\d{4}', date.text).group(0)
                date.text = year
                birthdates_degraded += 1
        
        changes = "{} PersonBirthDate events were found, of which {} were degraded to year of birth".format(len(dates), birthdates_degraded)
        f.write(filename + ": " + changes + "\n")    
        print(changes)

        # Save output in borough folder
        print('Re-writing')
        tree.write(os.path.join(borough_folder, "{}".format(filename)))

    f.close()
    print('Done')
    
    return


# Function to dentify namespace

def get_namespace(root):
    regex = r'{(.*)}.*' # pattern to pick up namespace
    namespace = re.findall(regex, root.tag)
    if len(namespace)>0:
        namespace = namespace[0]
    else:
        namespace = None
    NS = {None: namespace}
    return NS