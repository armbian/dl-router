#!/usr/bin/env python
class Mirror():
    def __init__(self, mirror_list=None):
        self.mirror_list = mirror_list
        self._list_position = 0
        self._list_max = len(mirror_list) - 1

    def increment(self):
        if self._list_position == self._list_max:
            self._list_position = 0
        else:
            self._list_position = self._list_position + 1

    def next(self):
        self.increment()
        return self.mirror_list[self._list_position]
