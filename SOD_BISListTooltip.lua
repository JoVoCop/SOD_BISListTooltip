
-- New Example
BISListTooltip = CreateFrame("Frame")

BISListTooltip.classIcons = {
    ["Warrior"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:0:64:0:64|t",
    ["Mage"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:64:128:0:64|t",
    ["Rogue"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:128:196:0:64|t",
    ["Druid"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:196:256:0:64|t",
    ["Hunter"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:0:64:64:128|t",
    ["Shaman"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:64:128:64:128|t",
    ["Priest"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:128:196:64:128|t",
    ["Warlock"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:196:256:64:128|t",
    ["Paladin"] = "|TInterface\\WorldStateFrame\\ICONS-CLASSES:0:0:0:0:256:256:0:64:128:196|t",
}

BISListTooltip.AddonName = "SOD_BISListTooltip" -- Don't change this. It's used for AddonLoaded event
BISListTooltip.FriendlyAddonName = "SOD BIS List Tooltip"

BISListTooltip.classNames = {
    "WARRIOR",
    "MAGE",
    "ROGUE",
    "DRUID",
    "HUNTER",
    "SHAMAN",
    "PRIEST",
    "WARLOCK",
    "PALADIN"
}

function BISListTooltip:OnEvent(event, ...)
	self[event](self, event, ...)
end
BISListTooltip:SetScript("OnEvent", BISListTooltip.OnEvent)
BISListTooltip:RegisterEvent("ADDON_LOADED")


function BISListTooltip:ADDON_LOADED(event, addOnName)
	if addOnName == BISListTooltip.AddonName then
		BisListTooltipDB = BisListTooltipDB or {}
		self.db = BisListTooltipDB
		for k, v in pairs(self.defaults) do
			if self.db[k] == nil then
				self.db[k] = v
			end
		end
        
        -- Default: only show current class
        if self.db.classOptionsSet == false then
            local _, classFilename = UnitClass("player")

            -- Set current class to true, all others to false
            for index, value in next, BISListTooltip.classNames do
                if value == classFilename then
                    self.db.displayClass[value] = true
                else
                    self.db.displayClass[value] = false
                end
            end
            self.db.classOptionsSet = true
        end

		self.db.sessions = self.db.sessions + 1
        
        -- Debugging. Can change to a single 'loaded successfully' message later
		-- print("### " .. BISListTooltip.AddonName .. " - You loaded this addon "..self.db.sessions.." times")

		self:InitializeOptions()
		self:UnregisterEvent(event)

        
        -- Add hooks
        GameTooltip:HookScript("OnTooltipSetItem", injectTooltip)
        ItemRefTooltip:HookScript("OnTooltipSetItem", injectTooltip)
        ShoppingTooltip1:HookScript("OnTooltipSetItem", injectTooltip)
        ShoppingTooltip2:HookScript("OnTooltipSetItem", injectTooltip)
	end
end


-- ############################################################################################################
-- # Tooltip Injection
-- ############################################################################################################

-- Mapping of suffixid to suffixkey
-- Suffix key is an internal key used to map a range of suffixids to a single suffix
-- For example, suffixID 6 (of Strength) maps to the internal key of "P".
-- This allows us to map multiple suffixIDs in game to a single suffix in the loot table.
-- It's a known issue that this may result in non-optimal suffixes getting shown as BIS but we're only able to use the information 
-- we have from the BIS source which doesn't reliably indicate teh specific suffix combination that's ideal. Users need to be aware that 
-- suffixes can vary and that they should use their own judgement when selecting the suffix.
function getSuffixKeyforSuffixId(suffixid)
    for index, value in next, suffixMapping do
        if value["suffixid"] == suffixid then
            return value["suffixkey"]
        end
    end
end

-- Extracts a value from the loot table based on a provided key for a given itemLink and itemName
-- param: itemLink (string): format defined here: https://wowwiki-archive.fandom.com/wiki/API_GameTooltip_GetItem
-- param: itemName (string): name of the item
-- param: key (string): "prio" or "note"
-- return: value (string)
function getValue(itemLink, itemName, key, lootTable)    
    -- Extract the itemid and itemsuffixid from the itemLink
    -- See https://wowwiki-archive.fandom.com/wiki/ItemString
    item_id = itemLink:match("item:(%d+):")
    item_suffix_id = itemLink:match("item:%d+:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:(%d*):") -- there has got to be a nicer way to do this
    if item_suffix_id ~= nil and item_suffix_id ~= "" then
        suffix_key = getSuffixKeyforSuffixId(item_suffix_id)
    end
    
    for index, value in next, lootTable do
        -- We used to match on itemid alone however that resulted in random enchants (suffixes) not being matched. This resulted in some classes showing BIS for an item even if it had the wrong suffix
        --     Example: Warlock DPS wants "Elder's Cloak of the Owl" but Priest healers want "Elder's Cloak of Intellect".
        --     The suffixes are different but the itemid is the same which means that the item (regarless of suffix) will show as BIS for both classes
        -- To fix this specific issue, we have a mapping of suffixid to an intenral "suffixkey". This allows us to map multiple suffixIDs in game to a single suffix in the loot table regardless of localisation
        -- How it works:
        --     If item_suffix_id is not nil, then we need to check if getSuffixKeyforSuffixId returns a value
        --     If it does, then we need to check if the suffixkey matches the suffixkey in the loot table for the given itemid
        --     If there is no item_suffix_id, then we just check the itemid
        --
        -- Reference: https://wowwiki-archive.fandom.com/wiki/SuffixId
        --
        -- It's a known issue that this may result in non-optimal suffixes getting shown as BIS but we're only able to use the information we have from the BIS source which doesn't reliably indicate the
        -- specific suffix combination that's ideal (example: +4 Agility/+3 Stamina is better than +3 Agility/+4 Stamina).
        -- Users need to be aware that suffixes can vary and that they should use their own judgement when selecting the suffix.
        

        if item_suffix_id ~= nil and item_suffix_id ~= "" then
            if suffix_key then
                -- We have a suffix key, so check the itemid and suffix key
                if value["itemid"] == item_id and value["itemsuffixkey"] == suffix_key then

                    -- Check if we have a BIS suffix id and if the setting is enabled
                    if value["itembissuffixid"] ~= "" and BisListTooltipDB.filterBISSuffixes then
                        -- We have a BIS suffix id, so check if it matches the item_suffix_id
                        if value["itembissuffixid"] == item_suffix_id then
                            return value[key]
                        end
                    else
                        -- No BIS suffix id, so just return the value
                        return value[key]
                    end
                end
            end
        else
            -- No suffix id, so just check the itemid
            if value["itemid"] == item_id then
                return value[key]
            end
        end
    end
end

-- Handles OnTooltipSetItem
-- param: tooltip
-- More info: https://wowwiki-archive.fandom.com/wiki/UIHANDLER_OnTooltipSetItem
function injectTooltip(tooltip)
    -- https://wowwiki-archive.fandom.com/wiki/API_GameTooltip_GetItem
    -- Formatted item link (e.g. "|cff9d9d9d|Hitem:7073:0:0:0:0:0:0:0|h[Broken Fang]|h|r").
    local itemName, itemLink = tooltip:GetItem()

    if itemLink then
        wowheadSections = getValue(itemLink, itemName, "sections", wowheadLootTable) -- Use wowheadLootTable for now, extend to other sources later

        if BisListTooltipDB.datasouceWowhead == true and wowheadSections then
            -- We have at least one line to add
            tooltip:AddLine(" ")
            tooltip:AddLine(string.format("|c000af5a2SOD BIS List [Wowhead]"), 1, 1, 1, false)


            -- Iterate over the wowheadSections and add them to the tooltip
            for index, value in next, wowheadSections do
                -- Extract the values
                local class = value["class"]
                local spec = value["spec"]
                local rank = value["rank"]
                local phase = value["phase"]
                local priority_text = value["priority_text"]

                -- Get the class color and icon
                local color = RAID_CLASS_COLORS[class:upper()]
                local icon = BISListTooltip.classIcons[class]

                -- Confirm the phase and class are enabled
                if BisListTooltipDB.displayClass[class:upper()] == false then
                    -- Nothing
                elseif phase == "1" and BisListTooltipDB.phase1 == false then
                    -- Nothing
                else
                    -- Add the line 
                    -- https://wowpedia.fandom.com/wiki/API_GameTooltip_AddDoubleLine
                    tooltip:AddDoubleLine(string.format("%s %s %s", icon, class, spec), string.format("%s - %s", rank, priority_text), color.r, color.g, color.b, color.r, color.g, color.b)
                end
            end
        end
    end
end


