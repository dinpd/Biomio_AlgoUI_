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


def get_all_files(path, joined=False):
    res = []
    fnames = get_files(path)
    for file_name in fnames:
        if joined:
            res.append(os.path.join(path, file_name))
        else:
            res.append((path, file_name))
    dnames = get_dirs(path)
    for dir_name in dnames:
        nfiles = get_all_files(os.path.join(path, dir_name), joined)
        for nfile in nfiles:
            res.append(nfile)
    return res
