import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
from rx.subjects import Subject
from rx import Observable
from Types import SliceOrientation, EventType

class PanesSyncEventManager(Subject):
	def __init__(self, panes, sync=True):
		super().__init__()
		self.sync = sync
		
		# SliceWillChange -> SyncSliceToPane
		Observable.merge([ pane for uid, (pane, viewport) in panes.items() ]) \
			.filter(lambda x: x[0] == EventType.SliceWillChange and self.sync) \
			.subscribe(lambda x: self.on_next((EventType.SyncSliceToPane, self, x[1])))