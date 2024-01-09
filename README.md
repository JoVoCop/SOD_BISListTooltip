## SOD BIS List Tooltip

Adds Season of Discovery BIS information in a tooltip

Currently sources BIS information from Wowhead. Additional sources to be added in the future

### Features
* BIS information for all classes and phases displayed in a tooltip. No more alt-tabbing to compare items.
* Customizable class, phase, and source display. Only care about your class? No problem.
* Auto-updating. BIS lists are updated nightly.
* Meaningful changelogs. Changelogs indicate additions, removals, and changes.
* Tooltip text matches the upstream source. For example, if your BIS list says something like 'Optional: Shadow', that will be displayed in the tooltip.


## Automation

The following GitHub Actions are used...
1. `parse-bis-lists.yaml` - Nightly job to detect changes to the BIS lists. If there's a change, a new changelog will be created and submmitted to a new PR.
2. `auto-tag.yaml` - If the PR is merged, a new tag will be created and pushed to GitHub
    * NOTE: if you're doing a bug fix PR that isn't adding a new feature, this should be tracked as a patch. To get a patch to go through, run 'S'quash and Merge' in the PR and add `#patch` to the end of the commit title.
3. `auto-release.yaml` - Ran manually for now. Should be automated after `auto-tag` soon. Run against the tag and it will add a new GH release. Currently the zip needs to be added to curseforge manually. TODO: Add automation to auto-publish to Curseforge


## Running parse-bis-lists manunally

Assuming WSL2 for now...

1. Create virtual env: `virtualenv venv`
2. Activate the venv: `source ./venv/bin/activate`
3. CD to `tools/`
3. Run `./install-chrome.sh`
4. Run `pip install -r requirements.txt`
5. Run `python parse-wowhead.py`
6. If needed, you can generate the changelog and open a PR but it's HIGHLY recommended to leave this to the nightly GH Action
