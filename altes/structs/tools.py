import os

###################################################################################################
# Python Filesystem Extras - Directory Searching
# import os
def get_dirs(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
###################################################################################################


###################################################################################################
# Python Filesystem Extras - File Searching
# import os
def get_files(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
###################################################################################################
