# Bouquet-Tabs

Shows a horizontal strip of bouquet names in the Grid EPG, with the current bouquet in brackets followed by the others in order:

`[ Entertainment ]   |   Sports   |   Movies   |   News`

You can see which bouquets are available without opening the bouquet-list popup. Left/Right (or your usual bouquet buttons) switch bouquets immediately, exactly as before. The plugin only adds the strip and changes no core files.

<img width="1301" height="115" alt="OnyxTabs" src="https://github.com/user-attachments/assets/176af322-24e4-4aa6-a167-484c606bb679" />

## Supported images

One plugin file covers all of these and detects which one it is running on automatically:

- OpenViX
- OpenATV (current builds)
- OpenATV (older builds)

## Install

1. Download `ipk/enigma2-plugin-extensions-epgbouquettabs_005_all.ipk` and copy it to your box (for example into `/tmp`).
2. Install it:
   ```
   opkg install /tmp/enigma2-plugin-extensions-epgbouquettabs_005_all.ipk
   ```
   If the same version is already installed, run `opkg remove enigma2-plugin-extensions-epgbouquettabs` first, or add `--force-reinstall`.
3. Restart the GUI (`init 4 && init 3`) or reboot.

Manual install: copy `usr/lib/enigma2/python/Plugins/Extensions/EPGBouquetTabs/` to `/usr/lib/enigma2/python/Plugins/Extensions/EPGBouquetTabs/` on the box and restart the GUI.

## Skin setup (required)

The plugin only draws the strip if the active skin defines a widget named `guidebouquetlist`. A skin without it behaves exactly as it does today, so installing the plugin is always safe, but you will see no tabs until the skin has the widget.

Add this inside the Grid EPG screen of your skin:

```xml
<widget name="guidebouquetlist" position="X,Y" size="W,H"
	font="Regular;30" foregroundColor="white" backgroundColor="#000000"
	valign="center" halign="left" noWrap="1" transparent="1" zPosition="2"/>
```

Adjust `position`, `size`, font and colours to suit your skin.

**Which screen?** It depends on the skin and on whether picture-in-graphics is on. Common names are `GraphicalEPG`, `GraphicalEPGPIG`, `GraphicalEPGPIG1` and `GraphicalEPGPIG2`. If you are unsure, check the skin's EPG XML file for the screen that holds the `list` and `timeline_text` widgets.

**Don't edit the skin directly.** Put your change in an override file named after the skin's folder, so skin updates don't wipe it:

```
/etc/enigma2/skin_user_<skin-folder-name>.xml
```

Notes:

- The skin folder name is case-sensitive.
- Any `<screen>` tag you write in an override file must have explicit `position` and `size` (for example `position="0,0" size="1920,1080"`). Without them the GUI can crash.
- Don't write a literal `-->` inside an XML comment, because it ends the comment early.
- Restart the GUI after changing skin files.

The plugin also tries a custom screen name, `EPGBouquetTabsGrid`, before the stock one. This lets you define a dedicated tabs layout without touching the skin's own screen.

### Alternative: show the tabs in the screen title (v005 and later)

Some skins already show the bouquet name in a header title on the Grid EPG screen, and are generated or hard to copy screens from (for example Umbra). For those, skip the widget and add one parameter to the skin's `skin_user` file instead:

```xml
<skin>
	<parameters>
		<parameter name="EPGBouquetTabsTitle" value="1"/>
	</parameters>
</skin>
```

Save it as `/etc/enigma2/skin_user_<skin folder name>.xml` (for Umbra: `/etc/enigma2/skin_user_Umbra.xml`) and restart the GUI. The plugin then sets the screen title to the tab strip (current bouquet in brackets), so the skin's existing title shows it and the bouquet name is not repeated.

Limits: the skin must show the screen title on the Grid EPG, and the strip is cut off if it is wider than the skin's title widget. The skin's own font and colour apply to the whole strip. Skins without a usable title still need the `guidebouquetlist` widget described above.

## Uninstall

```
opkg remove enigma2-plugin-extensions-epgbouquettabs
```

This also deletes the plugin folder. Any `skin_user_*.xml` you created stays in place, so remove it yourself if you no longer want it.

## Troubleshooting

- **No tabs showing:** the skin has no `guidebouquetlist` widget on the screen your box is using. Check the screen name and make sure the skin file change was saved and the GUI restarted.
- **"Plugin not available" warning:** read the message. It names the missing attribute and means the image's EPG code differs from what the plugin expects. Open an issue with your image name and version.
- **Grid EPG broken or crashing:** remove the plugin (and any `skin_user_*.xml` you added) and reboot. Then check the crash log in `/home/root/logs/` (or your image's log folder) and open an issue with it.

## How it works

The plugin subclasses the Grid EPG screen and swaps it in at runtime, in memory. On OpenViX it patches `EPGSelectionGrid`. On current OpenATV it replaces `Screens.EpgSelection.EPGSelectionGrid`, which the image's `createEPGSelection()` factory uses. On older OpenATV it patches the flat `EPGSelection` class. It then adds the `guidebouquetlist` label and refreshes it whenever the bouquet changes.

## Repo layout

```
usr/lib/enigma2/python/Plugins/Extensions/EPGBouquetTabs/   plugin files (install path)
CONTROL/                                                      ipk control file and postrm
ipk/                                                          built package
```
