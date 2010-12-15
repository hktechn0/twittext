#-*- coding: utf-8 -*-

import threading

class BaseTimelineThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
    
    def run(self): pass
    
    def set_event(self, func):
        self._on_update_main = func
    
    def _on_update_before(self, statuses): pass
    def _on_update_main(self, statuses): pass
    def _on_update_after(self, statuses): pass
    
    def _on_update(self, statuses):
        self._on_update_before(statuses)
        self._on_update_main(statuses)
        self._on_update_after(statuses)

class StreamingTimelineThread(BaseTimelineThread):
    def set_stream(self, stream):
        self._stream = stream
    
    def run(self):
        self._stream.start()
        
        while True:
            statuses = self._stream.pop()
            self._on_update(statuses)
            self._stream.event.wait()
