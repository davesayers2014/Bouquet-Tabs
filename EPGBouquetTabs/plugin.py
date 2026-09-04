# -*- coding: utf-8 -*-
#
# EPG Bouquet Tabs — unified plugin, works on both OpenViX and OpenATV
# ------------------------------------------------------------------
# This merges the two previously-separate versions of this plugin into
# one file. At load time it detects which image it's running on by
# trying to import OpenViX's EPGSelectionGrid class first; if that
# import fails (because it doesn't exist on this image), it falls back
# to OpenATV's EPGSelection class instead. Only ONE code path actually
# runs on a given box — this file is just a single copy you can install
# on either image without needing to know in advance which one it is.

from Components.Label import Label


class GuideBouquetList(Label):
	"""Shows ALL bouquets in a single line, with the current one
	bracketed at the start — e.g. '[ Entertainment ]   |   Plus 1   |
	Movies   |   ...'. This replaces the earlier two-widget approach
	(a separate 'Title' widget for the current bouquet, plus this list
	for the rest) with one self-contained widget, so the skin's own
	'Title' widget for current-bouquet display is no longer needed."""

	def __init__(self):
		Label.__init__(self, "")
		self.tabNames = []

	def setBouquets(self, names, currentIndex):
		self.tabNames = names
		self._render(currentIndex)

	def setSelected(self, index):
		self._render(index)

	def _render(self, currentIndex):
		if not self.tabNames:
			self.setText("")
			return
		ordered = self.tabNames[currentIndex:] + self.tabNames[:currentIndex]
		parts = []
		for i, name in enumerate(ordered):
			parts.append("[ %s ]" % name if i == 0 else name)
		self.setText("   |   ".join(parts))


# ---------------------------------------------------------------------------
# Try OpenViX first (EPGSelectionGrid, a dedicated class per EPG screen type).
# ---------------------------------------------------------------------------
try:
	from Screens.EpgSelectionGrid import EPGSelectionGrid

	class EPGSelectionGridTabs(EPGSelectionGrid):

		def __init__(self, session, startBouquet, startRef, bouquets, *args, **kwargs):
			EPGSelectionGrid.__init__(self, session, startBouquet, startRef, bouquets, *args, **kwargs)
			# Extends the base class's own skinName list rather than
			# replacing it outright, so other skins aren't broken if this
			# plugin is active while a different skin is selected.
			self.skinName = ["EPGBouquetTabsGrid", "GraphicalEPGPIG"] + self.skinName
			self["guidebouquetlist"] = GuideBouquetList()
			self.onLayoutFinish.append(self._refreshTabs)

		def _refreshTabs(self):
			if not self.bouquets:
				return
			names = [b[0] for b in self.bouquets]
			if "guidebouquetlist" in self:
				self["guidebouquetlist"].setBouquets(names, self.selectedBouquetIndex)

		def bouquetChanged(self):
			EPGSelectionGrid.bouquetChanged(self)
			if "guidebouquetlist" in self:
				self["guidebouquetlist"].setSelected(self.selectedBouquetIndex)

	def _patch_infobar():
		import Screens.InfoBarGenerics as ibg
		ibg.EPGSelectionGrid = EPGSelectionGridTabs

	_IMAGE = "openvix"

# ---------------------------------------------------------------------------
# Fall back to OpenATV (single EPGSelection class, EPGtype="graph" for grid).
# ---------------------------------------------------------------------------
except ImportError:
	from Screens.EpgSelection import EPGSelection

	class EPGSelectionTabs(EPGSelection):

		def __init__(self, session, service=None, zapFunc=None, eventid=None,
				bouquetChangeCB=None, serviceChangeCB=None, EPGtype=None,
				StartBouquet=None, StartRef=None, bouquets=None):
			EPGSelection.__init__(self, session, service, zapFunc, eventid,
				bouquetChangeCB, serviceChangeCB, EPGtype, StartBouquet, StartRef, bouquets)

			# Only add the tab strip for grid-style EPG.
			self._isGridType = (EPGtype == "graph")
			if self._isGridType:
				self.skinName = ["EPGBouquetTabsGrid", "GraphicalEPGPIG"] + (self.skinName if isinstance(self.skinName, list) else [self.skinName])
				self["guidebouquetlist"] = GuideBouquetList()

				# Use the bouquets list handed to us directly as a
				# constructor argument, since OpenATV's EPGSelection
				# delegates bouquet switching to an external callback
				# rather than keeping a persistent internal list.
				self._tabBouquets = bouquets or []
				self._tabIndex = self._findStartIndex(StartBouquet, self._tabBouquets)
				self.onLayoutFinish.append(self._refreshTabs)

		def _findStartIndex(self, startBouquet, bouquets):
			if not startBouquet or not bouquets:
				return 0
			try:
				startStr = startBouquet.toString() if hasattr(startBouquet, "toString") else str(startBouquet)
				for i, b in enumerate(bouquets):
					ref = b[1] if len(b) > 1 else None
					refStr = ref.toString() if hasattr(ref, "toString") else str(ref)
					if refStr == startStr:
						return i
			except Exception:
				pass
			return 0

		def _refreshTabs(self):
			if not self._isGridType or "guidebouquetlist" not in self or not self._tabBouquets:
				return
			try:
				names = [b[0] for b in self._tabBouquets]
				self["guidebouquetlist"].setBouquets(names, self._tabIndex)
			except Exception:
				pass

		# Tracks bouquet position ourselves rather than relying on
		# OpenATV's internal state, since the same screen instance stays
		# open across a bouquet switch (confirmed via testing) and
		# nextBouquet()/prevBouquet() are the confirmed methods triggered
		# by left/right on the remote.
		def nextBouquet(self):
			EPGSelection.nextBouquet(self)
			if self._isGridType and self._tabBouquets:
				self._tabIndex = (self._tabIndex + 1) % len(self._tabBouquets)
				self._refreshTabs()

		def prevBouquet(self):
			EPGSelection.prevBouquet(self)
			if self._isGridType and self._tabBouquets:
				self._tabIndex = (self._tabIndex - 1) % len(self._tabBouquets)
				self._refreshTabs()

	def _patch_infobar():
		import Screens.EpgSelection as epgmod
		import Screens.InfoBarGenerics as ibg
		epgmod.EPGSelection = EPGSelectionTabs
		ibg.EPGSelection = EPGSelectionTabs

	_IMAGE = "openatv"


def Plugins(**kwargs):
	_patch_infobar()
	return []
