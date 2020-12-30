""" manage iterating through mirrors and return appropriate one based by region """

from ruamel.yaml import YAML

class Mirror():

    def __init__(self):
        self.load_mirrors()
        self._list_position = dict()
        self._list_max = dict()
        self.continents = [region for region in self.mirror_list.keys() ]
        self.regions = self.continents + [ 'default' ]
        self.mirror_list['default'] = list(
            self.mirror_list['NA'] + self.mirror_list['EU'])
        for region in self.regions:
            self._list_position[region] = 0
            self._list_max[region] = len(self.mirror_list[region]) - 1

    def load_mirrors(self):
        """ open mirrors file and return contents """
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.preserve_quotes = True

        with open('mirrors.yaml', 'r') as f:
            config = yaml.load(f)
        self.mode = config['mode']
        print("using mode: {}".format(self.mode))
        self.mirror_list = config.get('mirrors', {})
        return self.mirror_list

    # set defaults to None in param list, then actually set inside
    # body to avoid scope change
    def increment(self, region=None):
        """ move to next element regions mirror list and return list position"""
        if region is None or region not in self.all_regions():
            region = 'default'
        if self._list_position[region] == self._list_max[region]:
            self._list_position[region] = 0
        else:
            self._list_position[region] = self._list_position[region] + 1

    def next(self, region=None):
        """ return next mirror in rotation """
        if region is None:
            region = 'default'
        self.increment(region)
        return self.mirror_list.get(region, self.mirror_list.get('default'))[self._list_position[region]]

    def all_mirrors(self):
        """ return all mirrrors configured """
        return self.mirror_list

    def all_regions(self):
        """ return list of regions configured """
        return self.regions
