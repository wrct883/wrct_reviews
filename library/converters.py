class TableConverter:
    regex = "(review|album|artist|label|genre|user|subgenre)"

    def to_python(self, value):
        return value.capitalize()

    def to_url(self, value):
        return value
