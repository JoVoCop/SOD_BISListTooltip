
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
        ShoppingTooltip:HookScript("OnTooltipSetItem", injectTooltip)
	end
end


-- ############################################################################################################
-- # Tooltip Injection
-- ############################################################################################################

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
    for index, value in next, lootTable do
        -- Use itemid match only. I originally used itemid AND itemsuffixid, but this was causing issues with items that have random enchants
        -- Issues:
        --  * Wowhead lists sometimes contain the rand (suffixid) and sometimes don't
        --  * The suffixid is not always the same as the one linked in wowhead. For example, https://www.wowhead.com/classic/item=6617/sages-mantle?rand=767 has the rand id of 767 but in game, these can range between 754 and 838
        -- Reference: https://wowwiki-archive.fandom.com/wiki/SuffixId
        -- May save a mapping of possible values in the future but for now, just use itemid as that still only solves #1. #2 would need to be solved by parsing the text of the cell in wowhead
        if value["itemid"] == item_id then
            return value[key]
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
        print("1")
        wowheadSections = getValue(itemLink, itemName, "sections", wowheadLootTable) -- Use wowheadLootTable for now, extend to other sources later
        print("2")

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


