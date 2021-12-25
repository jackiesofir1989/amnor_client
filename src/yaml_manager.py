import yaml


class Yaml:
    def __init__(self, path):
        self.path = path

    def load_yaml(self):
        with open(self.path) as _f:
            sys_dict_tree = yaml.load(_f, Loader=yaml.FullLoader)
        return sys_dict_tree

    def save_yaml(self, _dict):
        with open(self.path, 'w') as outfile:
            yaml.safe_dump(_dict, outfile, default_flow_style=False)
