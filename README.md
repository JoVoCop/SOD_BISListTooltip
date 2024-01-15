## SOD BIS List Tooltip

Adds Season of Discovery BIS information in a tooltip

Currently sources BIS information from Wowhead. Additional sources to be added in the future

### Features
* BIS information for all classes and phases displayed in a tooltip. No more alt-tabbing to compare items.
* Customizable class, phase, and source display. Only care about your class? No problem.
* Auto-updating. BIS lists are updated nightly.
* Meaningful changelogs. Changelogs indicate additions, removals, and changes.
* Tooltip text matches the upstream source. For example, if your BIS list says something like 'Optional: Shadow', that will be displayed in the tooltip.
* Suffix matching. For example: "Sage's Mantle of the Owl" is a BIS option for Priest Healers is only shown as BIS in P1 for Priest Healers. Classes that want other suffixes like "Sage's Mantle of Shadow Wrath" and "Sage's Mantle of Intellect" won't show in the tooltip
* Optional interpretation of the ideal suffix (see note below).

### Option: Show only BIS suffixes

My philosophy with this addon is to strictly use the data available in the BIS list. That being said, random enchants (aka suffixes) are a bit unique. BIS lists often note the ideal suffix for an item however that suffix can vary slightly and, only one combination is usually "BIS". An optional (enabled by default) setting "Show only BIS suffixes" is available to have the addon interpret the 'ideal' suffix (the higest possible random enchant roll). 

For example, the Rogue BIS list in phase 1 identifies "Cutthroat's Cape of the Monkey" but this can have the following rolls: "+(3 - 4) Agility , +(3 - 4) Stamina". When the "Show only BIS suffixes" toggle is enabled, the addon will interpret this as "+4 Agility, +4 Stamina" and will only show this combination as BIS in the tooltip. If you disable this setting, the addon will show all possible combinations of the suffix "of the Monkey" as BIS in the tooltip.

There are some exceptions for this logic:
* When the suffix (ex: "of Power") is not found as a known possible suffix for an item but the BIS list indicates it is BIS. In this case, the addon will show all versions of 'of Power' as BIS in the tooltip as we cannot determine the specific rolls available.


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
