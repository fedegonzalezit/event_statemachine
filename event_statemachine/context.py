class Context:
    def __init__(self):
        self._data = {}

    def __getattr__(self, key):
        if key in self._data:
            return self._data[key]
        raise AttributeError(f"Key '{key}' does not exist.")

    def __setattr__(self, key, value):
        if key == "_data":
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def to_dict(self):
        return self._data

    def from_dict(self, data):
        self._data.update(data)

    def __eq__(self, __value: object) -> bool:
        return self._data == __value._data
