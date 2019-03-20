# duplicate_tools
Tools for finding and moving file duplicates

NAME
    duplicates.py - Lists file duplicates and optionally moves duplicates to a separate folder
SYNOPSIS
    python3 duplicates.py -s input_dir -o output_dir [-t {n|s|h}] [-x]

DESCRIPTION
    Basic script that searches for file duplicates in a directory tree. By default files are compared by hash (sha1) but 
    files can also be compared by filename or size. 
    With the flag -x duplicates are moved to a separate folder where the path of a duplicate relative to the source 
    folder is preserved.
    
    -s input_dir
        The folder that is searched for duplicates. If a duplicate is found of a file, the first occurence is considered
        the original file and subsequent occurences are considered duplicates.
        
    -o output_dir
        The base folder where duplicates are moved to if the -x flag is used. The path relative to the input_dir 
        of a duplicate is preserved
        
    -t type
        Sets the method of file comparison, options are n,s and h. 'h' is the default.
        
        n   compares files by name (case sensitive)
        s   compares files by size 
        h   this is the default. Files are compared by their sha1 hash.
        
        
 EXAMPLES
 
 Searches for files in the /data/src folder that have equal size
 # duplicates.py -i /data/src -o /tmp -t s
 
 Searches for files in the /data/src folder that have the same filename and moves the duplicates to the /tmp folder
 # duplicates.py -i /data/src -o /tmp -t n -x
 
 Searches for files in the /data/src folder with the same hash and moves the duplicates to the /tmp folder
 # duplicates.py -i /data/src -o /tmp -x
 
 
 
 
 
 
        
    
    
    
