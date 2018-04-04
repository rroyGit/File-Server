import os

class Snapshot:

    def __init__(self, file_path):
        self.last_modified = os.path.getmtime(file_path)
        self.file_name = file_path

    def update(self, file_path=""):
        pass

    def __str__(self):
        return '{"file_name": "' +  self.file_name + '", "last_modified": ' + str(self.last_modified) + '}'

class FileSnapshot(Snapshot):

    def __init__(self, file_name):
        Snapshot.__init__(self, file_name)

    def update(self, file_path=""):
        Snapshot.update(self)

    def __str__(self):
        return Snapshot.__str__(self)

class DirectorySnapshot(Snapshot):

    def __init__(self, directory):
        Snapshot.__init__(self, directory)
        self.snapshots = {};
        self.add_path(directory)
        print(str(self))

    def add_path(self, path):
        for file in os.listdir(path):
            file_path = self.file_name + "/" + file

            cls = FileSnapshot

            if os.path.isdir(file_path):
                print("Added dir" + file_path)
                cls = DirectorySnapshot
            else:
                print("Added file" + file_path)

            self.snapshots[file] = cls(file_path)

    def update(self, file_path=""):
        Snapshot.update(self)

        allparts = []
        while 1:
            parts = os.path.split(file_path)
            if parts[0] == file_path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                file_path = parts[0]
                allparts.insert(0, parts[1])

        if allparts[0] in self.snapshots.keys():
            self.snapshots[allparts[0]].update(file_path)

    def to_json(self, recursive=True):
        string = '{"file_name": "' +  self.file_name + '", "last_modified": ' + str(self.last_modified) + ', "snapshots": ['

        if not recursive:
            wanted_snapshots = list()
            for index, key in enumerate(self.snapshots.keys()):
                snapshot = self.snapshots[key]
                if not isinstance(snapshot, DirectorySnapshot):
                    wanted_snapshots.append(snapshot)
        else:
            wanted_snapshots = self.snapshots.values()

        for index, value in enumerate(wanted_snapshots):
            string += str(value)
            if index != len(wanted_snapshots) - 1:
                string +=  ","
        string += "]}"
        return string

    def __str__(self):
        return self.to_json()