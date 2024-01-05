## SOD BIS List Tooltip

Adds Season of Discovery BIS information in a tooltip

Currently sources BIS information from Wowhead. Additional sources to be added in the future

### Features
* BIS information for all classes and phases displayed in a tooltip. No more alt-tabbing to compare items.
* Customizable class, phase, and source display. Only care about your class? No problem.
* Auto-updating. BIS lists are updated nightly.
* Meaningful changelogs. Changelogs indicate additions, removals, and changes.
* Tooltip text matches the upstream source. For example, if your BIS list says something like 'Optional: Shadow', that will be displayed in the tooltip.

NOTE: Some Wowhead BIS lists don't link to the proper enchant suffix (ex: "...of the Owl"). In these cases, the tooltip will not show correct information.

## Running

Assuming WSL2 for now...

1. Create virtual env: `virtualenv venv`
2. Activate the venv: `source ./venv/bin/activate`
3. CD to `tools/`
3. Run `./install-chrome.sh`
4. Run `pip install -r requirements.txt`
5. Run `python parse-wowhead.py`
