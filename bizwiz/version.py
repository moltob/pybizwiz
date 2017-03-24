class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return '{s.major}.{s.minor}.{s.patch}'.format(s=self)


BIZWIZ_VERSION = Version(4, 2, 0)

if __name__ == '__main__':
    print(BIZWIZ_VERSION)
