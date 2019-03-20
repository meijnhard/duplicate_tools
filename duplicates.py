from os import walk, path, rename
from os import path, stat
from os import path, makedirs
from errno import EEXIST
import getopt
import sys
import datetime
import hashlib

arguments = '-s input_dir -o output_dir [-t {n|s|h}]'
synopsis = './duplicates.py ' + arguments

def create_dir(directory):
    if not path.exists(directory):
        try:
            makedirs(directory)
        except OSError as exc:
            if exc.errno != EEXIST:
                raise

class File:
    def __init__(self, r, d, f):
        self.r = r
        self.d = d
        self.f = f
        self.digest = self.create_digest()
        self.size = path.getsize(self.get_path())

    def get_path(self):
        return self.r + "/" + self.f

    def get_size(self):
        return self.size

    def get_size_str(self):
        return str(self.get_size())

    def get_stats(self):
        file_stats = stat(self.get_path())
        return file_stats

    def get_modified_time(self):
        file_stats = self.get_stats()
        return datetime.datetime.fromtimestamp(file_stats.st_mtime)

    def year_modified(self):
        return self.get_modified_time().strftime("%Y")

    def month_modified(self):
        return self.get_modified_time().strftime("%m")

    def qrt_modified(self):
        month = self.get_modified_time().month
        if month <= 3:
            return 1
        if month <= 6:
            return 2
        if month <= 9:
            return 3
        return 4

    def contains(self, fi):
        return fi == self.f  # and fi.get_size() == self.get_size()

    def contains_by_name(self, fi):
        return fi == self.f

    def contains_by_size(self, fi_size):
        return fi_size == self.get_size()

    def contains_by_hash(self, fi_hash):
        return fi_hash == self.digest

    def create_digest(self):
        BLOCKSIZE = 65536

        hasher = hashlib.sha1()
        with open(self.get_path(), 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def to_string(self):
        return f'File={self.get_path()} size={self.get_size_str()}'




class Duplicate(File):
    def __init__(self, r, d, f):
        File.__init__(self, r, d, f)

    def to_string(self):
        return f"dup{self.get_path()} size={self.get_size_str()}"

    def move_path(self, base, new_base):
        offset_path = self.r[len(base):]
        new_path = new_base + offset_path
        return new_path


class FileDuplicates(File):
    def __init__(self, r, d, f):
        File.__init__(self, r, d, f)
        self.duplicates = []

    def print_file(self):
        # print(f"\nFile={self.get_path()}, file_size={self.get_size_str()}")
        for dup in self.duplicates:
           print(dup.to_string())

    def print_duplicates(self):
        if len(self.duplicates) > 0:
            self.print_file()

    def print_duplicates_new_path(self, base, new_base):
        if len(self.duplicates) > 0:
            #print("\norg:" + self.get_path() + " size=" + self.get_size_str())
            #self.print_file()
            print(f'\n{super(FileDuplicates, self).to_string()}')
            for dup in self.duplicates:
                print(f"  duplicate {dup.to_string()} --> new path={dup.move_path(base, new_base)}")

    

    def add_duplicate(self, r, d, f):
        self.duplicates.append(Duplicate(r, d, f))


files = []

def find_file_in_db(fi, compareBy, files_db=files):
    if len(files) == 0:
        return None
    else:
        for f in files_db:
            if compareBy == 'h' and f.contains_by_hash(fi.digest):
                return f
            if compareBy == 's' and f.contains_by_size(fi.get_size()):
                return f
            if compareBy == 'n' and f.contains_by_name(fi.f):
                return f
        return None


def init_files(file, compareBy, db=files):
    r = find_file_in_db(file, compareBy)
    if r is not None:
        r.add_duplicate(file.r, file.d, file.f)
    else:
        db.append(FileDuplicates(file.r, file.d, file.f))


def move_duplicates(sdir, ddir, db=files):
    for f in db:
        for dup in f.duplicates:
            newdir = dup.move_path(sdir, ddir)
            if path.isfile(dup.get_path()):
                create_dir(newdir)
                rename(dup.get_path(), newdir + "/" + dup.f)


def count_duplicates(sdir, ddir, db=files):
    total_duplicates = 0
    for f in db:
        f.print_duplicates_new_path(sdir, ddir)
        total_duplicates = total_duplicates + len(f.duplicates)

    print(f"\ntotal files={len(db)}")
    print(f"total duplicates ={total_duplicates}")


def run(sdir, ddir, execute, compareBy, db=files):
    for r, d, f in walk(sdir):
        for f2 in f:
            fil = File(r, d, f2)
            # print(f2)
            init_files(fil, compareBy, db)
    count_duplicates(sdir, ddir)
    if (execute):
        move_duplicates(sdir, ddir)

# run()

def main(argv):
    ddir = ''
    sdir = '.'
    execute = False
    compareBy = 's'
    try:
        opts, args = getopt.getopt(argv, "hs:o:t:x", ["source=", "dest="])
    except getopt.GetoptError:
        print('error' + synopsis)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(synopsis)
            sys.exit()
        elif opt in ("-s", "--source"):
            sdir = arg
        elif opt in ("-o", "--dest"):
            ddir = arg
        elif opt in ("-t"):
            if arg in ('s', 'n', 'h'):
                compareBy = arg
            else:
                print('allowed values for argument -t: s,n,h')
                sys.exit(2)
        elif opt == '-x':
            execute = True

    print(f"sdir={sdir}, odir={ddir}, compare={compareBy}, execute={execute}")
    if len(sdir) == 0 or len(ddir) == 0:
        print(f"arguments required: {arguments}")
        sys.exit()
    run(sdir, ddir, execute, compareBy)


if __name__ == "__main__":
    main(sys.argv[1:])
