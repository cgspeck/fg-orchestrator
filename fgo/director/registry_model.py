from PyQt5.QtCore import QAbstractTableModel, Qt, QTimer

from fgo.director.registry import Registry

# largely from https://gist.github.com/345161974/dd5003ed9b706adc557ee12e6a344c6e#file-qtableview_demo-py-L130
class RegistryModel(QAbstractTableModel):

    def __init__(self, parent, registry: Registry, *args):
        super(RegistryModel, self).__init__(parent, *args)
        self._registry = registry
        self._header = ['Host', 'online', 'uuid', '0conf']
        self._nodes = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateModel)
        self.timer.start(10000)

    def updateModel(self):
        agents = self._registry.get_agents()
        memo = []

        for agent in agents:
            memo.append([
                agent.host,
                agent.online,
                agent.uuid,
                bool(agent.zeroconf_name)
            ])

        self._nodes = memo

        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(
                self.rowCount(0),
                self.columnCount(0)
            )
        )
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self._nodes)

    def columnCount(self, parent):
        return len(self._header)

    def data(self, index, role):
        if not index.isValid():
            return None

        # special handling if the first col is some sort of object, e.g.
        #    QtGui.QCheckBox("关")
        #
        # if (index.column() == 0):
        #     value = self._nodes[index.row()][index.column()].text()
        value = self._nodes[index.row()][index.column()]

        if role == Qt.EditRole:
            return value
        elif role == Qt.DisplayRole:
            return value
        #   special handling if col 0 is some sort of object as above
        # elif role == QtCore.Qt.CheckStateRole:
        #     if index.column() == 0:
        #         # print(">>> data() row,col = %d, %d" % (index.row(), index.column()))
        #         if self.mylist[index.row()][index.column()].isChecked():
        #             return QtCore.Qt.Checked
        #         else:
        #             return QtCore.Qt.Unchecked

    def flags(self, index):
        if not index.isValid():
            return None

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[col]

        return None
