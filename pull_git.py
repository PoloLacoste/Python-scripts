import argparse, os, glob, logging, animation
from multiprocessing import Pool
from subprocess import Popen, PIPE, STDOUT

logging.basicConfig(format='%(message)s\n', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="Directory to search for git repository", default=".")
parser.add_argument("-r", "--recursive", 
	help="Search through all directories recursively, stop when a .git directory is found",
	action="store_true", default=False)

args = parser.parse_args()

def pull(dir):
	p = Popen(["git", "pull", "--progress", "-v"], cwd=dir, stdout=PIPE, stderr=STDOUT)
	p.wait()
	out = p.stdout.read().strip().decode("utf-8")
	logging.info(out)

@animation.simple_wait
def getGitDirs():
	dirs = glob.glob("%s/**/" % args.directory)
	gitDirs = []

	while len(dirs) > 0:
		dir = dirs[0]

		if os.path.exists("%s/.git/" % dir):
			gitDirs.append(dir)
		else:
			if args.recursive:
				dirs.extend(glob.glob("%s/**/" % dir))
		dirs.pop(0)
	return gitDirs
		

if __name__ == '__main__':
	if os.path.exists(args.directory):
		gitDirs = getGitDirs()
		with Pool(8) as p:
			p.map(pull, gitDirs)