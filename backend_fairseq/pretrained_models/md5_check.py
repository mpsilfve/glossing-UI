import sys
import csv

desiredModelIdentifier = sys.argv[1]
glossActual = sys.argv[2]
glossExpected = -1

# Find the desired MD5 value
with open("md5_model_info.csv", mode='r') as file:
     md5_dict = csv.DictReader(file)
     for row in md5_dict:
          if row["Model"] == desiredModelIdentifier:
               glossExpected = (row["MD5"])
               # May want to quit the loop early here....?

# Compare the actual MD5 value to the expected one
if glossActual == glossExpected:
     print(f"\nMD5 check for {desiredModelIdentifier} model succeeded.\n")
else:
     print(f"\nError: MD5 check for {desiredModelIdentifier} model failed:")
     if glossExpected == -1 or glossExpected == "":
          print("Error reading expected MD5 value from CSV file.")
     else:
          print("Actual MD5 value did not match expected MD5 value.")
     sys.exit(1)