"""
References:
-----------
https://wiki.python.org/moin/PyQt/Distinguishing%20between%20click%20and%20double%20click
http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttablemodel/
http://stackoverflow.com/questions/12152060/how-does-the-keypressevent-method-work-in-this-program
"""
from __future__ import print_function
from six import iteritems
from PyQt4 import QtCore, QtGui
#from pyNastran.gui.qt_files.menu_utils import eval_float_from_string
from pyNastran.gui.qt_files.alt_geometry_storage import AltGeometry

class CustomQTableView(QtGui.QTableView):
    def __init__(self, *args, **kwargs):
        self.parent2 = args[0]
        #super(CustomQTableView, self).__init__()
        QtGui.QTableView.__init__(self, *args, **kwargs) #Use QTableView constructor

    def mouseDoubleClickEvent(self, event):
        #self.last = "Double Click"
        index = self.currentIndex()
        self.parent2.update_active_key(index)

    #def performSingleClickAction(self):
        #if self.last == "Click":
            #self.message = "Click"
            #self.update()

    #def keyPressEvent(self, event): #Reimplement the event here, in your case, do nothing
        #if event.key() == QtCore.Qt.Key_Escape:
            #self.close()
        #return

class Model(QtCore.QAbstractTableModel):

    def __init__(self, items, header_labels, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.items = items
        self.header_labels = header_labels

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        row = index.row()
        if row < len(self.items):
            return QtCore.QVariant(self.items[row])
        else:
            return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable #| QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

class EditGroupProperties(QtGui.QDialog):
    def __init__(self, data, win_parent=None):
        """
        +------------------+
        | Edit Actor Props |
        +------------------+------+
        |  Name1                  |
        |  Name2                  |
        |  Name3                  |
        |  Name4                  |
        |                         |
        |  Active_Name    main    |
        |  Color          box     |
        |  Line_Width     2       |
        |  Opacity        0.5     |
        |                         |
        |    Apply   OK   Cancel  |
        +-------------------------+
        """
        QtGui.QDialog.__init__(self, win_parent)
        self.setWindowTitle('Edit Group Properties')

        #default
        self.win_parent = win_parent
        self.out_data = data

        self.keys = sorted(data.keys())
        keys = self.keys
        nrows = len(keys)
        self.active_key = keys[0]

        self._use_old_table = False
        items = keys
        header_labels = ['Groups']
        table_model = Model(items, header_labels, self)
        view = CustomQTableView(self) #Call your custom QTableView here
        view.setModel(table_model)
        view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.table = view

        actor_obj = data[self.active_key]
        name = actor_obj.name
        line_width = actor_obj.line_width
        opacity = actor_obj.opacity
        color = actor_obj.color

        table = self.table
        #headers = [QtCore.QString('Groups')]

        header = table.horizontalHeader()
        header.setStretchLastSection(True)

        self._default_is_apply = False
        self.name = QtGui.QLabel("Name:")
        self.name_edit = QtGui.QLineEdit(str(name))
        self.name_edit.setDisabled(True)

        self.color = QtGui.QLabel("Color:")
        self.color_edit = QtGui.QPushButton()
        #self.color_edit.setFlat(True)

        color = self.out_data[self.active_key].color
        qcolor = QtGui.QColor()
        qcolor.setRgb(*color)
        print('color =%s' % str(color))
        palette = QtGui.QPalette(self.color_edit.palette()) # make a copy of the palette
        #palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, \
                         #qcolor)
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor('blue'))  # ButtonText
        self.color_edit.setPalette(palette)

        self.color_edit.setStyleSheet("QPushButton {"
                                      "background-color: rgb(%s, %s, %s);" % tuple(color) +
                                      #"border:1px solid rgb(255, 170, 255); "
                                      "}")


        self.opacity = QtGui.QLabel("Opacity:")
        self.opacity_edit = QtGui.QDoubleSpinBox(self)
        self.opacity_edit.setRange(0.1, 1.0)
        self.opacity_edit.setDecimals(1)
        self.opacity_edit.setSingleStep(0.1)
        self.opacity_edit.setValue(opacity)

        self.line_width = QtGui.QLabel("Line Width:")
        self.line_width_edit = QtGui.QSpinBox(self)
        self.line_width_edit.setRange(0, 10)
        self.line_width_edit.setSingleStep(1)
        self.line_width_edit.setValue(line_width)

        # closing
        self.apply_button = QtGui.QPushButton("Apply")
        #if self._default_is_apply:
            #self.apply_button.setDisabled(True)

        self.ok_button = QtGui.QPushButton("OK")
        self.cancel_button = QtGui.QPushButton("Cancel")

        self.create_layout()
        self.set_connections()

    def update_active_key(self, index):
        old_obj = self.out_data[self.active_key]
        old_obj.line_width = self.line_width_edit.value()
        old_obj.opacity = self.opacity_edit.value()

        name = str(index.data().toString())
        #i = self.keys.index(self.active_key)

        self.active_key = name
        self.name_edit.setText(name)
        obj = self.out_data[name]
        line_width = obj.line_width
        opacity = obj.opacity
        self.color_edit.setStyleSheet("QPushButton {"
                                      "background-color: rgb(%s, %s, %s);" % tuple(obj.color) +
                                      #"border:1px solid rgb(255, 170, 255); "
                                      "}")
        self.line_width_edit.setValue(line_width)
        self.opacity_edit.setValue(opacity)

    #def on_name_select(self):
        #print('on_name_select')
        #return

    def create_layout(self):
        ok_cancel_box = QtGui.QHBoxLayout()
        ok_cancel_box.addWidget(self.apply_button)
        ok_cancel_box.addWidget(self.ok_button)
        ok_cancel_box.addWidget(self.cancel_button)

        grid = QtGui.QGridLayout()

        irow = 0
        grid.addWidget(self.name, irow, 0)
        grid.addWidget(self.name_edit, irow, 1)
        irow += 1

        grid.addWidget(self.color, irow, 0)
        grid.addWidget(self.color_edit, irow, 1)
        irow += 1

        grid.addWidget(self.opacity, irow, 0)
        grid.addWidget(self.opacity_edit, irow, 1)
        irow += 1

        grid.addWidget(self.line_width, irow, 0)
        grid.addWidget(self.line_width_edit, irow, 1)
        irow += 1

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addLayout(grid)
        vbox.addStretch()
        #vbox.addWidget(self.check_apply)
        vbox.addLayout(ok_cancel_box)
        self.setLayout(vbox)

    def set_connections(self):
        self.connect(self.opacity_edit, QtCore.SIGNAL('clicked()'), self.on_opacity)
        self.connect(self.line_width, QtCore.SIGNAL('clicked()'), self.on_line_width)
        self.connect(self.color_edit, QtCore.SIGNAL('clicked()'), self.on_color)
        #self.connect(self.check_apply, QtCore.SIGNAL('clicked()'), self.on_check_apply)

        self.connect(self.apply_button, QtCore.SIGNAL('clicked()'), self.on_apply)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), self.on_ok)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'), self.on_cancel)

    def on_color(self):
        name = self.active_key
        obj = self.out_data[name]
        rgb_color_ints = obj.color

        msg = name
        col = QtGui.QColorDialog.getColor(QtGui.QColor(*rgb_color_ints), self, "Choose a %s color" % msg)
        if col.isValid():
            color = col.getRgbF()[:3]
            obj.color = color
            #print('new_color =', color)
            self.color_edit.setStyleSheet("QPushButton {"
                                          "background-color: rgb(%s, %s, %s);" % tuple(obj.color) +
                                          #"border:1px solid rgb(255, 170, 255); "
                                          "}")

    def on_line_width(self):
        name = self.active_key
        line_width = self.line_width_edit.value()
        self.out_data[name].line_width = line_width

    def on_opacity(self):
        name = self.active_key
        opacity = self.opacity_edit.value()
        self.out_data[name].opacity = opacity

    #def on_axis(self, text):
        ##print(self.combo_axis.itemText())
        #self._axis = str(text)
        #self.plane.setText('Point on %s? Plane:' % self._axis)
        #self.point_a.setText('Point on %s Axis:' % self._axis)
        #self.point_b.setText('Point on %s%s Plane:' % (self._axis, self._plane))

    #def on_plane(self, text):
        #self._plane = str(text)
        #self.point_b.setText('Point on %s%s Plane:' % (self._axis, self._plane))

    def on_check_apply(self):
        is_checked = self.check_apply.isChecked()
        self.apply_button.setDisabled(is_checked)

    def _on_float(self, field):
        try:
            eval_float_from_string(field.text())
            field.setStyleSheet("QLineEdit{background: white;}")
        except ValueError:
            field.setStyleSheet("QLineEdit{background: red;}")

    def closeEvent(self, event):
        event.accept()

    #def on_default_name(self):
        #self.name_edit.setText(str(self._default_name))
        #self.name_edit.setStyleSheet("QLineEdit{background: white;}")

    #def check_float(self, cell):
        #text = cell.text()
        #try:
            #value = eval_float_from_string(text)
            #cell.setStyleSheet("QLineEdit{background: white;}")
            #return value, True
        #except ValueError:
            #cell.setStyleSheet("QLineEdit{background: red;}")
            #return None, False

    #def check_name(self, cell):
        #text = str(cell.text()).strip()
        #if len(text):
            #cell.setStyleSheet("QLineEdit{background: white;}")
            #return text, True
        #else:
            #cell.setStyleSheet("QLineEdit{background: red;}")
            #return None, False

    def on_validate(self):
        self.out_data['clicked_ok'] = True
        self.out_data['clicked_cancel'] = False

        old_obj = self.out_data[self.active_key]
        old_obj.line_width = self.line_width_edit.value()
        old_obj.opacity = self.opacity_edit.value()
        return True
        #name_value, flag0 = self.check_name(self.name_edit)
        #ox_value, flag1 = self.check_float(self.transparency_edit)
        #if flag0 and flag1:
            #self.out_data['clicked_ok'] = True
            #return True
        #return False

    def on_apply(self):
        passed = self.on_validate()
        if passed:
            self.win_parent.on_update_geometry_properties(self.out_data)
        return passed

    def on_ok(self):
        passed = self.on_apply()
        if passed:
            self.close()
            #self.destroy()

    def on_cancel(self):
        self.out_data['clicked_ok'] = False
        self.out_data['clicked_cancel'] = True
        self.close()


def main():
    # kills the program when you hit Cntl+C from the command line
    # doesn't save the current state as presumably there's been an error
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


    import sys
    # Someone is launching this directly
    # Create the QApplication
    app = QtGui.QApplication(sys.argv)
    #The Main window
    #g = GeometryHandle()
    #g.add('main', color=(0, 0, 0), line_thickness=0.0)
    #g.get_grid('name')
    #g.set_color('name')
    #g.set_grid('name')
    #g.set_grid('name')
    parent = app
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    purple = (255, 0, 255)
    d = {
        'caero1' : AltGeometry(parent, 'caero', color=green, line_width=3, transparency=0.2),
        'caero2' : AltGeometry(parent, 'caero', color=purple, line_width=4, transparency=0.3),
        'caero' : AltGeometry(parent, 'caero', color=blue, line_width=2, transparency=0.1),
        'main' : AltGeometry(parent, 'main', color=red, line_width=1, transparency=0.0),
    }
    main_window = EditGroupProperties(d, win_parent=None)
    main_window.show()
    # Enter the main loop
    app.exec_()

if __name__ == "__main__":
    main()