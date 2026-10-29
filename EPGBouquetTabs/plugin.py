# -*- coding: utf-8 -*-
#
# EPG Bouquet Tabs
# ------------------------------------------------------------------
# Shows a horizontal strip of bouquet names in Grid EPG, current
# bouquet bracketed first, e.g. "[ Entertainment ]   |   Sports   |
# Movies". Left/Right (or TV +/-) switch bouquets immediately, same
# as stock behaviour -- this plugin only adds the strip, it does not
# change how bouquet switching works.
#
# Works on OpenViX and on TWO different generations of OpenATV from one
# file. Which branch runs is decided automatically at import time:
#
#   1. OpenViX: Screens/EpgSelectionGrid.py exists as its own module.
#   2. Newer OpenATV (2026+): no separate EpgSelectionGrid module, but
#      Screens.EpgSelection.EPGSelectionGrid exists as a dedicated
#      class, built via a module-level createEPGSelection() factory.
#      The old EPGSelection() compat wrapper no longer constructs the
#      grid screen directly -- its __new__ redirects straight to
#      createEPGSelection(), bypassing any patch applied to
#      EPGSelection itself. createEPGSelection() looks up the name
#      "EPGSelectionGrid" in Screens.EpgSelection's own module globals
#      *at call time*, so overwriting that module attribute is enough
#      to redirect it to our subclass -- no need to touch EPGSelection
#      or its __new__ at all.
#   3. Older OpenATV: Screens.EpgSelection has no EPGSelectionGrid at
#      all -- there's just the one flat EPGSelection class, opened
#      with an EPGtype="graph" argument for the grid view. This is the
#      architecture the plugin originally targeted; patching
#      EPGSelection itself still works here, because the old image
#      has no factory redirecting around it.
#
# Case 2 and case 3 need different code because EPGSelection on an
# older image is never the problem (a plain `except ImportError` can't
# tell them apart -- the Screens.EpgSelection module import always
# succeeds on both; only the EPGSelectionGrid *attribute* differs), so
# detection checks hasattr(epgmod, "EPGSelectionGrid") rather than
# relying on import failure a second time.
#
# Do NOT reintroduce any execEnd()/execBegin() suppression of shared
# stock ActionMaps (okactions / bouquetokactions) to try to add a
# "highlight then OK to commit" browsing mode -- that was tried once,
# caused a real crash (AttributeError in Screens/UserDefinedButtons.py)
# and a screen the user could not exit without a reboot. Left/Right
# switch bouquets immediately, on purpose.

from Components.Label import Label


class GuideBouquetList(Label):
	"""Current bouquet bracketed first, followed by the rest in order."""

	def __init__(self):
		Label.__init__(self, "")
		self.tabNames = []

	def setBouquets(self, names, currentIndex):
		self.tabNames = names
		self._render(currentIndex)

	def setOpenIndex(self, index):
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


try:
	# ---------------------------------------------------------------
	# OpenViX: Screens/EpgSelectionGrid.py is its own module, with
	# EPGSelectionGrid.__init__(self, session, startBouquet, startRef,
	# bouquets, *args, **kwargs) and self.skinName as a list.
	# ---------------------------------------------------------------
	from Screens.EpgSelectionGrid import EPGSelectionGrid

	class EPGSelectionGridTabs(EPGSelectionGrid):

		def __init__(self, session, startBouquet, startRef, bouquets, *args, **kwargs):
			EPGSelectionGrid.__init__(self, session, startBouquet, startRef, bouquets, *args, **kwargs)
			# Extend, don't replace -- a skin without our widget still
			# falls back to its own stock screen name correctly.
			self.skinName = ["EPGBouquetTabsGrid"] + self.skinName
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
				self["guidebouquetlist"].setOpenIndex(self.selectedBouquetIndex)

	def _patch_infobar():
		import Screens.InfoBarGenerics as ibg
		ibg.EPGSelectionGrid = EPGSelectionGridTabs

	_IMAGE = "openvix"

except ImportError:
	import Screens.EpgSelection as epgmod

	if hasattr(epgmod, "EPGSelectionGrid"):
		# -----------------------------------------------------------
		# Newer OpenATV: EPGSelectionGrid lives inside
		# Screens/EpgSelection.py itself. Its __init__ signature is
		#   (self, session, zapFunc=None, startBouquet=None, startRef=None,
		#    bouquets=None, graphic=False, epgType=EPG_TYPE_GRAPH)
		# and self.skinName is set as a plain STRING (not a list):
		#   "GraphicalInfoBarEPG" / "GraphicalEPGPIG" / "GraphicalEPG"
		#
		# The real screen is built by the module-level createEPGSelection()
		# function, which does:
		#   if epgType == EPG_TYPE_GRAPH:
		#       return EPGSelectionGrid(session, zapFunc, StartBouquet,
		#                                StartRef, bouquets, graphic_flag)
		# "EPGSelectionGrid" there is a free variable resolved against
		# Screens.EpgSelection's module globals *when createEPGSelection
		# runs*, not when it was defined -- so overwriting that module
		# attribute is enough to redirect it to our subclass, with no need
		# to touch EPGSelection, its __new__, or createEPGSelection itself.
		# -------------------------------------------------------------
		_BaseGrid = epgmod.EPGSelectionGrid
		_EPG_TYPE_GRAPH = getattr(epgmod, "EPG_TYPE_GRAPH", None)
		if _EPG_TYPE_GRAPH is None:
			from Components.EpgList import EPG_TYPE_GRAPH as _EPG_TYPE_GRAPH

		class EPGSelectionGridTabs(_BaseGrid):

			def __init__(self, session, zapFunc=None, startBouquet=None, startRef=None,
					bouquets=None, graphic=False, epgType=_EPG_TYPE_GRAPH):
				_BaseGrid.__init__(self, session, zapFunc, startBouquet, startRef,
					bouquets, graphic, epgType)
				# self.skinName is a plain string on this class -- wrap it in
				# a list rather than replacing it, exactly like the OpenViX
				# branch above, so the stock screen name is still tried as a
				# fallback on any skin that doesn't define our widget.
				base_name = self.skinName
				if isinstance(base_name, list):
					self.skinName = ["EPGBouquetTabsGrid"] + base_name
				else:
					self.skinName = ["EPGBouquetTabsGrid", base_name]
				self["guidebouquetlist"] = GuideBouquetList()
				self.onLayoutFinish.append(self._refreshTabs)

			def _refreshTabs(self):
				if not getattr(self, "bouquets", None):
					return
				names = [b[0] for b in self.bouquets]
				if "guidebouquetlist" in self:
					self["guidebouquetlist"].setBouquets(names, self.selectedBouquetIndex)

			def nextBouquet(self):
				_BaseGrid.nextBouquet(self)
				if "guidebouquetlist" in self:
					self["guidebouquetlist"].setOpenIndex(self.selectedBouquetIndex)

			def prevBouquet(self):
				_BaseGrid.prevBouquet(self)
				if "guidebouquetlist" in self:
					self["guidebouquetlist"].setOpenIndex(self.selectedBouquetIndex)

			def bouquetChanged(self):
				_BaseGrid.bouquetChanged(self)
				if "guidebouquetlist" in self:
					self["guidebouquetlist"].setOpenIndex(self.selectedBouquetIndex)

		def _patch_infobar():
			# This is the one that actually matters: createEPGSelection()
			# resolves "EPGSelectionGrid" against this module's globals at
			# call time, so this line alone redirects Grid EPG construction.
			epgmod.EPGSelectionGrid = EPGSelectionGridTabs
			# Belt-and-braces: if InfoBarGenerics (or anything else) imported
			# the original class by reference rather than calling through
			# EPGSelection/createEPGSelection, patch that copy too.
			try:
				import Screens.InfoBarGenerics as ibg
				if getattr(ibg, "EPGSelectionGrid", None) is _BaseGrid:
					ibg.EPGSelectionGrid = EPGSelectionGridTabs
			except Exception:
				pass

		_IMAGE = "openatv-new"

	else:
		# -------------------------------------------------------------
		# Older OpenATV: there's no EPGSelectionGrid split at all -- just
		# one flat EPGSelection class, opened with EPGtype="graph" for
		# the grid view. No factory sits in front of it on this image,
		# so patching EPGSelection directly (and the copy InfoBarGenerics
		# imported) is the correct, sufficient fix here.
		# -------------------------------------------------------------
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
					self.skinName = ["EPGBouquetTabsGrid"] + (self.skinName if isinstance(self.skinName, list) else [self.skinName])
					self["guidebouquetlist"] = GuideBouquetList()

					# Use the bouquets list handed to us directly as a
					# constructor argument, since this image's EPGSelection
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

			def nextBouquet(self):
				EPGSelection.nextBouquet(self)
				if self._isGridType and self._tabBouquets:
					self._tabIndex = (self._tabIndex + 1) % len(self._tabBouquets)
					if "guidebouquetlist" in self:
						self["guidebouquetlist"].setOpenIndex(self._tabIndex)

			def prevBouquet(self):
				EPGSelection.prevBouquet(self)
				if self._isGridType and self._tabBouquets:
					self._tabIndex = (self._tabIndex - 1) % len(self._tabBouquets)
					if "guidebouquetlist" in self:
						self["guidebouquetlist"].setOpenIndex(self._tabIndex)

		def _patch_infobar():
			import Screens.InfoBarGenerics as ibg
			epgmod.EPGSelection = EPGSelectionTabs
			ibg.EPGSelection = EPGSelectionTabs

		_IMAGE = "openatv-legacy"


def Plugins(**kwargs):
	_patch_infobar()
	return []
