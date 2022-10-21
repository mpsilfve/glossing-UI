import sys
import csv

assert(len(sys.argv) > 2)
desiredModelIdentifier = sys.argv[1]
md5Actual = sys.argv[2]
md5Expected = -1

# Find the desired MD5 value
with open("md5_model_info.csv", mode='r') as file:
     md5_dict = csv.DictReader(file)
     for row in md5_dict:
          if row["Model"] == desiredModelIdentifier:
               md5Expected = (row["MD5"])
               break

# Compare the actual MD5 value to the expected one
if md5Actual == md5Expected:
     print(f"\nMD5 check for {desiredModelIdentifier} model succeeded.\n")
else:
     # The MD5 check failed, but we will try to find out why to provide a more informative error message
     print(f"\nError: MD5 check for {desiredModelIdentifier} model failed:")

     # Check if we failed to read the expected MD5 value altogether
     if md5Expected == -1 or md5Expected == "":
          print("Error reading expected MD5 value from CSV file.")
     else:

          # Check if the actual MD5 matches the expected MD5 for *another* model/version combo
          matchedModel = ""
          matchedVersion = ""
          with open("md5_model_info.csv", mode='r') as file:
               md5_dict = csv.DictReader(file)
               for row in md5_dict:
                    if row["MD5"] == md5Actual:
                         matchedModel = row["Model"]
                         matchedVersion = row["Version Number"]
                         break
          if matchedModel != "":
               print(f"Actual MD5 value did not match expected MD5 value, but it did match the MD5 value for model {matchedModel}, version {matchedVersion}.")
          
          # We're not sure what caused the MD5 mismatch
          else:
               print("Actual MD5 value did not match expected MD5 value.")

     sys.exit(1)