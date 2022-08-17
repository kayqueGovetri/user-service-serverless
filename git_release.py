#!/usr/bin/env python3

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request


class version_number:

    major = 0
    minor = 0
    release = 0
    release_suffix = ""

    def __init__(self, version="0.0.0"):

        (self.major, self.minor, release) = version.split(".", 2)

        # extract release suffix like 0.1.2-alpha1234
        res = re.search(r"[^0-9]", release)
        if res:
            s = res.start()
            self.release = release[:s]
            self.release_suffix = release[s:]
        else:
            self.release = release

        (self.major, self.minor, self.release) = map(
            int, (self.major, self.minor, self.release)
        )

    def __add__(self, other):
        self.release_suffix = ""
        self.major += other.major
        self.minor += other.minor
        self.release += other.release
        return self

    def incr(self, what="release"):
        self.release_suffix = ""
        if what == "release":
            self.release += 1
        if what == "minor":
            self.minor += 1
            self.release = 0
        if what == "major":
            self.major += 1
            self.minor = 0
            self.release = 0

        return self

    def __str__(self):
        s = ".".join(map(str, (self.major, self.minor, self.release)))
        return "%s%s" % (s, self.release_suffix)


def shell(cmd, check=True):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, check=check)
    return result.stdout.decode("utf-8").strip()


def get_file_data(
    plugin_file, headers={"Plugin Name": "Plugin Name", "Version": "Version"}
):
    f = open(plugin_file, "r")
    contents = f.read()
    f.close()
    contents.replace("\r", "\n")
    ret = {}
    for field, regex in headers.items():
        res = re.compile("^[ \t*#@]*%s:(?P<value>.*)$" % (regex), re.I | re.M).search(
            contents
        )
        ret[field] = res.group("value").strip()
        #
        # contents.match()
    return ret


def update_plugin_version(new_version):
    for plugin_file in glob.glob("*.php"):
        fdata = get_file_data(plugin_file)
        if "Version" in fdata:
            # read
            f = open(plugin_file, "r")
            contents = f.read()
            f.close()
            reg = re.compile("^([ \t*#@]*)Version:[\s\t]*(.*)$", re.I | re.M)
            repl = r"\1Version: %s" % (new_version)
            contents = reg.sub(repl, contents)

            f = open(plugin_file, "w")
            contents = f.write(contents)
            f.close()
            # add commit push
            shell("git add .")
            try:
                shell(
                    'git commit -q -m "Release version %s"' % (new_version), check=True
                )
                shell("git push", check=True)
                return True
            except subprocess.CalledProcessError:
                return False

        return False


# check env config
try:
    access_token = shell(
        "security find-generic-password -a ${USER} -s GithubAccessToken -w"
    )
except KeyError:
    print("Missing env var `GITHUB_ACCESS_TOKEN`")
    sys.exit(1)


# check if git repo
repo_remote = shell("git config --get remote.origin.url")

if not repo_remote:
    print("Not a git repository")
    sys.exit(1)

repo_name = re.sub(r"\.git$", "", os.path.basename(repo_remote))
repo_owner = shell("git config --get user.name")

repo_current_branch = shell("git rev-parse --abbrev-ref HEAD")

# Parse cli args
parser = argparse.ArgumentParser()
parser.add_argument(
    "-r",
    "--release",
    default="release",
    const="release",
    help="Type of Release. 'release' (default) will increment the last version number, 'minor' the middle one and 'major' the first one.",
    type=str,
    choices=["release", "minor", "major"],
    nargs="?",
)
parser.add_argument(
    "-v",
    "--version",
    help="Version number. Must be in format `<major>.<minor>.<release>`. You may append something like `1.2.3-beta-RC3` also. For automatic versioning use -r.",
    type=str,
)
parser.add_argument("-m", "--message", help="Release Message")
parser.add_argument("-p", "--pre", type=bool, help="Prerelease", default=False)
parser.add_argument("-d", "--draft", type=bool, help="Draft", default=False)
parser.add_argument(
    "-b", "--branch", type=str, help="Branch", default=repo_current_branch
)
args = parser.parse_args()


# get version string
if args.version:
    new_version = version_number(args.version)

elif args.release:
    #
    new_version = False

    for plugin_file in glob.glob("*.php"):
        fdata = get_file_data(plugin_file)
        if "Version" in fdata:
            new_version = version_number(fdata["Version"])
            break
        else:
            print("Nope...", plugin_file)

    new_version.incr(args.release)

print("Building Release %s from branch %s now." % (new_version, args.branch))

# get message
if args.message:
    body = args.message
else:
    body = "Release of version %s from branch %s" % (new_version, args.branch)

readme_data = get_file_data(
    "readme.txt",
    headers={
        "Requires at least": "Requires at least",
        "Tested up to": "Tested up to",
        "Requires PHP": "Requires PHP",
    },
)

body = """%s
Requires at least: %s
Tested up to: %s
Requires PHP: %s
""" % (
    body,
    readme_data["Requires at least"],
    readme_data["Tested up to"],
    readme_data["Requires PHP"],
)

# Update plugin header, commit, push
if not update_plugin_version(new_version):
    print("Could not push changes")
    sys.exit(1)

# create tag via api
request_data = {
    "tag_name": "v%s" % (new_version),
    "target_commitish": args.branch,
    "name": "v%s" % (new_version),
    "body": body,
    "draft": bool(args.draft),
    "prerelease": bool(args.pre),
}
request_url = "https://api.github.com/repos/%s/%s/releases?access_token=%s" % (
    repo_owner,
    repo_name,
    access_token,
)

# send api request
print("Create tag...")
with urllib.request.urlopen(
    request_url, data=json.dumps(request_data).encode("utf-8")
) as f:
    # parse response
    api_response = json.loads(f.read().decode("utf-8"))

# create installable zip
# git archive --format=zip -v --output=../<reponame>.zip --worktree-attributes HEAD


# mk zip
zip_path = "../%s.zip" % (repo_name)
print("Create installable ZIP...")
shell(
    "git archive --format=zip --prefix=%s/ --output=%s --worktree-attributes HEAD"
    % (repo_name, zip_path)
)

# upload zip to tag
print("Upload ZIP...")
upload_url = "%s?name=%s.zip" % (
    re.sub(r"{\?.*}$", "", api_response["upload_url"]),
    repo_name,
)
hdl = open("../%s.zip" % (repo_name), "rb")

# post file
upload_req = urllib.request.Request(
    upload_url,
    data=hdl.read(),
    headers={
        "Authorization": "token %s" % (access_token),
        "Content-Type": "application/zip",
    },
)
with urllib.request.urlopen(upload_req) as f:
    # parse response
    upload_response = json.loads(f.read().decode("utf-8"))


print("Cleanup...")
shell("rm %s" % (zip_path))


print("All done.")
