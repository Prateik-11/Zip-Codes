from uszipcode import SearchEngine
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np

def main():
    # read input file, rename column containing zip code to ZipCode if necessary
    df = pd.read_csv(r"C:\Users\email\OneDrive\Documents\Python\zip_codes\cluster_data_pregrouping.csv")

    se = SearchEngine()
    zip_df = []
    bad_zip = []
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
        skip = False
        for j in row:
            if j is None:
                # add ZIPs with missing info to this list to impute them
                bad_zip.append(row)
                skip = True
                break
        if not skip: 
            zip_df.append(row)

    # converting data into a dataframe:
    zipped = pd.DataFrame(zip_df, columns=[
        "ZipCode",      "Latitude",             "Longitude",       "BoundNorth",
        "BoundSouth",   "BoundEast",            "BoundWest",       "RadiusInMiles", 
        "LandArea",     "WaterArea",            "Population",      "PopulationDensity", 
        "HousingUnits", "OccupiedHousingUnits", "MedianHomeValue", "MedianHouseholdIncome" 
        ])
    
    # for bad zips, give them values of their closest neighbor

    # enter coordinates into model
    train = pd.read_csv(r"C:\Users\email\OneDrive\Documents\Python\zip_codes\zip_reference.csv", header=None).iloc[1:,1:] 
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(train.iloc[:,1:3])
    for i in range(len(bad_zip)):
        # search for closest coordinates
        distances, indices = nbrs.kneighbors(np.reshape(bad_zip[i][1:3], (1, -1)))
        # give bad zip value of closest coordinate
        bad_zip[i][3:] = train.iloc[indices[0,0],3:] 

    imputed_zips = pd.DataFrame(bad_zip, columns=[
        "ZipCode",      "Latitude",             "Longitude",       "BoundNorth",
        "BoundSouth",   "BoundEast",            "BoundWest",       "RadiusInMiles", 
        "LandArea",     "WaterArea",            "Population",      "PopulationDensity", 
        "HousingUnits", "OccupiedHousingUnits", "MedianHomeValue", "MedianHouseholdIncome" 
        ])

    all_zip = pd.concat([zipped, imputed_zips])

    # merging with our original data, df
    output = pd.merge(left = df, right = all_zip, how =  'left', on = 'ZipCode')

    # export final file
    output.to_csv("zip_codes\\final_result_2.csv")

if __name__ == '__main__':
    main()