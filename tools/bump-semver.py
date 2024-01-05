import sys
import semver

def bump_minor_version(version):
    # Bump the minor version using the semver library
    updated_version = semver.bump_minor(version)

    return updated_version

# Get the semver string from the command-line arguments
input_version = sys.argv[1]

has_prefix_v = False
# If the semver string starts with a "v", remove it
if input_version[0] == "v":
    input_version = input_version[1:]
    has_prefix_v = True

# Bump the minor version
updated_version = bump_minor_version(input_version)

# If the original semver string started with a "v", add it back
if has_prefix_v:
    updated_version = f"v{updated_version}"

# Print the new version
print(f'{updated_version}')