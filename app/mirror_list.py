""" manage iterating through mirrors and return appropriate one based by region """


class Mirror():

    def __init__(self, mirror_list):
        self.mirror_list = dict()
        self._list_position = dict()
        self._list_max = dict()
        self.mirror_list['default'] = list(
            mirror_list['NA'] + mirror_list['EU'])
        self.mirror_list = mirror_list
        for region in list(mirror_list.keys()):
            self._list_position[region] = 0
            self._list_max[region] = len(mirror_list[region]) - 1

    def increment(self, region='default'):
        """ move to next element regions mirror list and return list position"""
        if self._list_position[region] == self._list_max[region]:
            self._list_position[region] = 0
        else:
            self._list_position[region] = self._list_position[region] + 1

    def next(self, region='default'):
        """ return next mirror in rotation """
        self.increment(region)
        return self.mirror_list[region][self._list_position[region]]

    def all_mirrors(self):
        """ return all mirrrors configured """
        self.mirror_list

    def all_regions(self):
        """ return list of regions configured """
        return list(self.mirror_list.keys())
