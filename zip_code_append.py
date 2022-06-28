from uszipcode import SearchEngine, SimpleZipcode, ComprehensiveZipcode
import pandas as pd
import os

def main():
    # read input file
    df = pd.read_csv(r"C:\Users\email\OneDrive\Documents\Python\zip_codes\cluster_data_pregrouping.csv")
    # rename column containing zip code to ZipCode if necessary
    se = SearchEngine()
    zip_df = []
    for i in df["ZipCode"].dropna().unique():
        row = [i]
        x = se.by_zipcode(i) # x is a SimpleZipCode object
        # appending zip code information:
        # geography:
        row.append(x.lat)
        row.append(x.lng)
        row.append(x.bounds_north)
        row.append(x.bounds_south)
        row.append(x.bounds_east)
        row.append(x.bounds_west)
        row.append(x.radius_in_miles)
        row.append(x.land_area_in_sqmi)
        row.append(x.water_area_in_sqmi)
        # population:
        row.append(x.population)
        row.append(x.population_density)
        # housing:
        row.append(x.housing_units)
        row.append(x.occupied_housing_units)
        row.append(x.median_home_value)
        row.append(x.median_household_income)
        zip_df.append(row)
    # converting data into a dataframe:
    zipped = pd.DataFrame(zip_df, columns=[
        "ZipCode",      "Latitude",             "Longitude",       "BoundNorth",
        "BoundSouth",   "BoundEast",            "BoundWest",       "RadiusInMiles", 
        "LandArea",     "WaterArea",            "Population",      "PopulationDensity", 
        "HousingUnits", "OccupiedHousingUnits", "MedianHomeValue", "MedianHouseholdIncome" 
        ])
    # merging with our original data, df
    output = pd.merge(left = df, right = zipped, how =  'left', on = 'ZipCode')
    # adding leading 0 to 5 digit CCNs
    new_output = []
    for i in output["CCN"]:
        i = str(i)
        while(len(i) < 6):
            i = "0" + i
        new_output.append(i)
    output['CCN'] = new_output
    # Adding extra features from web scraped data, joining using CCN
    provider_directory_1 = pd.read_csv(r"C:\Users\email\OneDrive\Documents\Python\zip_codes\CMS_provider_directory_all.csv", dtype='string')
    provider_directory_2 = pd.read_csv(r"C:\Users\email\OneDrive\Documents\Python\zip_codes\CMS_directory_every_provider.csv", dtype='string')
    # Combining both batches of scraped data into 1 data frame, dropping index column
    provider_directory = pd.concat([provider_directory_1, provider_directory_2]).drop(columns = ['Unnamed: 0'])
    # renaming variables to avoid confusion, dropping duplicates
    provider_directory = provider_directory.rename({'ProviderID' : 'CCN'}, axis = 'columns').drop_duplicates()
    # dropping all columns with duplicate CCN's EDA revealed they are not 
    # treated as duplicates due to a different data type for some columns
    provider_directory = provider_directory[~provider_directory['CCN'].duplicated(keep='first')]
    output_final = pd.merge(left = output, right = provider_directory, how = "left", on = 'CCN' )
    # export final file
    output_final.to_csv("zip_codes\\final_result.csv")

if __name__ == '__main__':
    main()