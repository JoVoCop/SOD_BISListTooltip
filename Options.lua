BISListTooltip.defaults = {
	sessions = 0,

    -- Phases
    phase1 = true,

    -- Data Sources
    datasouceWowhead = true,

    -- Class Display
    classOptionsSet = true, -- Set to false to populate only the user's class on first load
    -- displayClass = {}, -- Set to {} if classOptionsSet is false
    displayClass = {
        ["WARRIOR"] = true,
        ["MAGE"] = true,
        ["ROGUE"] = true,
        ["DRUID"] = true,
        ["HUNTER"] = true,
        ["SHAMAN"] = true,
        ["PRIEST"] = true,
        ["WARLOCK"] = true,
        ["PALADIN"] = true
    },

    -- Show only BIS Suffixes
    filterBISSuffixes = true
}

-- Options set by the initalization function if classOptionsSet is false
-- displayClass["WARRIOR"] (bool)
-- displayClass["MAGE"] (bool)
-- displayClass["ROGUE"] (bool)
-- displayClass["DRUID"] (bool)
-- displayClass["HUNTER"] (bool)
-- displayClass["SHAMAN"] (bool)
-- displayClass["PRIEST"] (bool)
-- displayClass["WARLOCK"] (bool)
-- displayClass["PALADIN"] (bool)

function BISListTooltip:CreateCheckbox(option, label, parent, updateFunc)
	local cb = CreateFrame("CheckButton", nil, parent, "InterfaceOptionsCheckButtonTemplate")
	cb.Text:SetText(label)
	local function UpdateOption(value)
		self.db[option] = value
		cb:SetChecked(value)
		if updateFunc then
			updateFunc(value)
		end
	end
	UpdateOption(self.db[option])
	-- there already is an existing OnClick script that plays a sound, hook it
	cb:HookScript("OnClick", function(_, btn, down)
		UpdateOption(cb:GetChecked())
	end)
	return cb
end


function BISListTooltip:CreateCheckboxDisplayClass(className, label, parent, color, updateFunc)
	local cb = CreateFrame("CheckButton", nil, parent, "InterfaceOptionsCheckButtonTemplate")
	cb.Text:SetText(label)
    cb.Text:SetTextColor( color.r, color.g, color.b )
	local function UpdateOption(value)
		self.db.displayClass[className] = value
		cb:SetChecked(value)
		if updateFunc then
			updateFunc(value)
		end
	end


	UpdateOption(self.db.displayClass[className])
	-- there already is an existing OnClick script that plays a sound, hook it
	cb:HookScript("OnClick", function(_, btn, down)
		UpdateOption(cb:GetChecked())
	end)
	return cb
end

function BISListTooltip:InitializeOptions()
	-- main panel
	self.panel_main = CreateFrame("Frame")
	self.panel_main.name = BISListTooltip.FriendlyAddonName

    -- Info Header
    local info_header = self.panel_main:CreateFontString( "InfoHeader", "OVERLAY", "GameTooltipText" )
    info_header:SetPoint( "TOPLEFT", 20, -20 )
    info_header:SetText( "These options control what data is shown in the tooltip" )

    -- Class Display Section
    local class_x_offset = 0
    local class_y_offset = -20

    local classes_label = self.panel_main:CreateFontString( "ClassesLabel", "OVERLAY", "GameTooltipText" )
	classes_label:SetPoint( "TOPLEFT", info_header, class_x_offset, -30 )
	classes_label:SetTextColor( 1, 0.85, 0.15 )
	classes_label:SetText( "Display Classes" )

    local cb_display_warrior = self:CreateCheckboxDisplayClass("WARRIOR", string.format("%s %s", BISListTooltip.classIcons["Warrior"], "Warrior"), self.panel_main, RAID_CLASS_COLORS["WARRIOR"])
    cb_display_warrior:SetPoint("TOPLEFT", classes_label, class_x_offset, class_y_offset)
    local cb_display_mage = self:CreateCheckboxDisplayClass("MAGE", string.format("%s %s", BISListTooltip.classIcons["Mage"], "Mage"), self.panel_main, RAID_CLASS_COLORS["MAGE"])
    cb_display_mage:SetPoint("TOPLEFT", cb_display_warrior, class_x_offset, class_y_offset)
    local cb_display_rogue = self:CreateCheckboxDisplayClass("ROGUE", string.format("%s %s", BISListTooltip.classIcons["Rogue"], "Rogue"), self.panel_main, RAID_CLASS_COLORS["ROGUE"])
    cb_display_rogue:SetPoint("TOPLEFT", cb_display_mage, class_x_offset, class_y_offset)
    local cb_display_druid = self:CreateCheckboxDisplayClass("DRUID", string.format("%s %s", BISListTooltip.classIcons["Druid"], "Druid"), self.panel_main, RAID_CLASS_COLORS["DRUID"])
    cb_display_druid:SetPoint("TOPLEFT", cb_display_rogue, class_x_offset, class_y_offset)
    local cb_display_hunter = self:CreateCheckboxDisplayClass("HUNTER", string.format("%s %s", BISListTooltip.classIcons["Hunter"], "Hunter"), self.panel_main, RAID_CLASS_COLORS["HUNTER"])
    cb_display_hunter:SetPoint("TOPLEFT", cb_display_druid, class_x_offset, class_y_offset)
    local cb_display_shaman = self:CreateCheckboxDisplayClass("SHAMAN", string.format("%s %s", BISListTooltip.classIcons["Shaman"], "Shaman"), self.panel_main, RAID_CLASS_COLORS["SHAMAN"])
    cb_display_shaman:SetPoint("TOPLEFT", cb_display_hunter, class_x_offset, class_y_offset)
    local cb_display_priest = self:CreateCheckboxDisplayClass("PRIEST", string.format("%s %s", BISListTooltip.classIcons["Priest"], "Priest"), self.panel_main, RAID_CLASS_COLORS["PRIEST"])
    cb_display_priest:SetPoint("TOPLEFT", cb_display_shaman, class_x_offset, class_y_offset)
    local cb_display_warlock = self:CreateCheckboxDisplayClass("WARLOCK", string.format("%s %s", BISListTooltip.classIcons["Warlock"], "Warlock"), self.panel_main, RAID_CLASS_COLORS["WARLOCK"])
    cb_display_warlock:SetPoint("TOPLEFT", cb_display_priest, class_x_offset, class_y_offset)
    local cb_display_paladin = self:CreateCheckboxDisplayClass("PALADIN", string.format("%s %s", BISListTooltip.classIcons["Paladin"], "Paladin"), self.panel_main, RAID_CLASS_COLORS["PALADIN"])
    cb_display_paladin:SetPoint("TOPLEFT", cb_display_warlock, class_x_offset, class_y_offset)

    -- Data Source Display Section
    local data_source_x_offset = 200
    local data_source_y_offset = -20

    local data_source_label = self.panel_main:CreateFontString( "DataSourceLabel", "OVERLAY", "GameTooltipText" )
    data_source_label:SetPoint( "TOPLEFT", classes_label, data_source_x_offset, 0 )
    data_source_label:SetTextColor( 1, 0.85, 0.15 )
    data_source_label:SetText( "Data Sources" )

    local cb_datasource_wowhead = self:CreateCheckbox("datasouceWowhead", "Wowhead", self.panel_main)
    cb_datasource_wowhead:SetPoint("TOPLEFT", data_source_label, 0, data_source_y_offset)

    -- Phase Display Section
    local phase_x_offset = 200
    local phase_y_offset = -20

    local phase_label = self.panel_main:CreateFontString( "PhaseLabel", "OVERLAY", "GameTooltipText" )
    phase_label:SetPoint( "TOPLEFT", data_source_label, phase_x_offset, 0 )
    phase_label:SetTextColor( 1, 0.85, 0.15 )
    phase_label:SetText( "Phases" )

    local cb_phase_1 = self:CreateCheckbox("phase1", "Phase 1", self.panel_main)
    cb_phase_1:SetPoint("TOPLEFT", phase_label, 0, phase_y_offset)

    -- BIS Suffix Filter Section - below the paladin checkbox
    local bis_suffix_x_offset = 0
    local bis_suffix_y_offset_header = -40
    local bis_suffix_y_offset = -20

    local bis_suffix_label = self.panel_main:CreateFontString( "BISSuffixLabel", "OVERLAY", "GameTooltipText" )
    bis_suffix_label:SetPoint( "TOPLEFT", cb_display_paladin, bis_suffix_x_offset, bis_suffix_y_offset_header )
    bis_suffix_label:SetTextColor( 1, 0.85, 0.15 )
    bis_suffix_label:SetText( "Show only BIS suffixes" )

    -- Info Header
    local bis_suffix_info_header = self.panel_main:CreateFontString( "BISSuffixInfoHeader", "OVERLAY", "GameTooltipText" )
    bis_suffix_info_header:SetPoint( "TOPLEFT", bis_suffix_label, 0, bis_suffix_y_offset )
    bis_suffix_info_header:SetText( "Display only the best possible suffix rolls (random enchants)" )

    local cb_bis_suffix_filter = self:CreateCheckbox("filterBISSuffixes", "Show only BIS suffixes", self.panel_main)
    cb_bis_suffix_filter:SetPoint("TOPLEFT", bis_suffix_info_header, 0, bis_suffix_y_offset)


    

    -- Add to interface panel
	InterfaceOptions_AddCategory(BISListTooltip.panel_main)
end

-- a bit more efficient to register/unregister the event when it fires a lot
function BISListTooltip:UpdateEvent(value, event)
	if value then
		self:RegisterEvent(event)
	else
		self:UnregisterEvent(event)
	end
end