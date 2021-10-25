import os
import glob
import pandas as pd

def concat(flatfile_folder):
    df_list = []
    
    # Identify relevant flatfiles
    all_flatfiles = glob.glob(os.path.join(flatfile_folder, "*.csv"))
    target_flatfiles = [f for f in all_flatfiles if f not in os.path.join(flatfile_folder, 'main_flatcin.csv')]
    
    # Run through each file to concatenate
    print("Processing {} flatfiles".format(len(target_flatfiles)))
    for file in target_flatfiles:
        prefix = file.split('\\')[-1][:3].upper() # Get first 3 letters of borough name
        df = pd.read_csv(file)
        df['LAchildID'] = prefix + df['LAchildID'].astype(str) # Add prefix to Child ID to differentiate across LAs
        df_list.append(df)
    data = pd.concat(df_list)
    # Save
    data.to_csv(os.path.join(flatfile_folder, "main_flatcin.csv"), index=False)
    print("Done!")
    
    return 