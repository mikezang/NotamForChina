on run argv
    -- Optional tab number (default 1)
    if (count of argv) ≥ 1 then
        set tabNum to (item 1 of argv) as integer
    else
        set tabNum to 1
    end if

    tell application "Safari"
        activate
        tell window 1
            set current tab to tab tabNum
            set currentURL to URL of tab tabNum
        end tell
    end tell

    -- Verify the tab is My Maps editor
    if currentURL does not contain "google.com/maps/d/edit?" and currentURL does not contain "google.com/maps/d/u/1/edit?" then
        display dialog "The selected tab is not a Google My Maps editor page." buttons {"OK"}
        return
    end if

    delay 1 -- ensure Safari is frontmost

    tell application "Safari"
        -- Step 1: Click "Add layer"
        do JavaScript "
            document.getElementById('map-action-add-layer').click();
        " in current tab of window 1

        delay 1

        -- Step 2: Click "Import" for the selected layer
        do JavaScript "
            var imports = document.querySelectorAll('[id$=\"-layerview-import-link\"]');
            if (imports.length) {
                imports[imports.length - 1].click();
            } else {
                alert('Import button not found!');
            }
        " in current tab of window 1
    end tell

    -- At this point, the Finder file picker will appear
    -- display dialog "Please select your KML file in the file picker for the new layer." buttons {"OK"} default button 1
end run

