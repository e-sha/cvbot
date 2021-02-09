class Command:
    def __init__(self, description, processor):
        self._description = description
        self._processor = processor

    def __call__(self, *args, **kwargs):
        return self._processor(*args, **kwargs)

    def __str__(self):
        return self._description
