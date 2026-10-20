# import python modules
import os

# directory name from which we are
# going to extract our files with its size
path = "nba_sim/data/raw"

# get the path p, sub_directory sub_dir,
# and filename files from the given path
walk_method = os.walk(path)

# using exception handling to remove
# the stop iteration from generator object 
# which we get the output from os.walk()  method.
while True:
    try:
        p, sub_dir, files = next(walk_method)
        break
    except:
        break  
        
# Create a list of files in directory along with the size
size_of_file = [
    (f,os.stat(os.path.join(path, f)).st_size)
    for f in files
]
 
# get the size of the sub_dir of the given path
for sub in sub_dir:
    i = os.path.join(path,sub)
    size = 0
    for k in os.listdir(i):
        size += os.stat(os.path.join(i,k)).st_size
    size_of_file.append((sub,size))
    
# Iterate over list of files along with size 
# and print them one by one.
# now we have print the result by
# sorting the size of the file
# so, we have call sorted function
# to sort according to the size of the file

# in this case we have use its file paths.
for f,s in sorted(size_of_file,key = lambda x : x[1]):
    print("{} : {}MB".format(os.path.join(path,f),round(s/(1024*1024),3)))

total_rows = 0

for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Subtract 1 if you want to exclude the header row
                    row_count = sum(1 for line in f) 
                total_rows += row_count
                #print(f"{file_path}: {row_count} rows")
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

print(f"With total rows of: {total_rows}")