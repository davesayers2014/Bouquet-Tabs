# Bouquet-Tabs

Add an optional widget to `EPGSelectionGrid` screen that shows a horizontal
strip of bouquet names — current bouquet bracketed, followed by the
bouquets that come after it — so users can see what's available to
switch to without opening the separate bouquet-list popup. This has
been running as a third-party plugin (no core files modified) across
several skins for a few weeks with no issues using OpenVIX and OpenATV.

The widget is entirely optional at the skin level: skins that don't
define a `guidebouquetlist` widget see no change in behaviour at all.


## What to add to the default skin (optional, for skins that want it)

A widget definition inside the `EPGSelectionGrid` screen block, e.g.:

```xml
<widget name="guidebouquetlist" position="X,Y" size="W,H"
	font="Regular;30" foregroundColor="..." backgroundColor="..."
	valign="center" halign="left" noWrap="1" transparent="1"/>


<img width="1301" height="115" alt="OnyxTabs" src="https://github.com/user-attachments/assets/95955af6-d006-4344-8b30-3694f96b4db6" />
