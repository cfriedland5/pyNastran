"""
Defines the GUI IO file for Tetegen.
"""
from __future__ import print_function
import os

from pyNastran.converters.tetgen.tetgen import Tetgen
from pyNastran.gui.gui_objects.gui_result import GuiResult
from pyNastran.gui.gui_utils.vtk_utils import (
    create_vtk_cells_of_constant_element_type, numpy_to_vtk_points)


class TetgenIO(object):
    def __init__(self):
        pass

    def get_tetgen_wildcard_geometry_results_functions(self):
        data = ('Tetgen',
                'Tetgen (*.smesh)', self.load_tetgen_geometry,
                None, None)
        return data

    def load_tetgen_geometry(self, smesh_filename, name='main', plot=True):
        #print("load_tetgen_geometry...")
        skip_reading = self._remove_old_geometry(smesh_filename)
        if skip_reading:
            return

        model = Tetgen(log=self.log, debug=False)

        base_filename, ext = os.path.splitext(smesh_filename)
        ext = ext.lower()
        node_filename = base_filename + '.node'
        ele_filename = base_filename + '.ele'
        if ext == '.smesh':
            dimension_flag = 2
        elif ext == '.ele':
            dimension_flag = 3
        else:
            raise RuntimeError('unsupported extension.  Use "smesh" or "ele".')
        model.read_tetgen(node_filename, smesh_filename, ele_filename, dimension_flag)
        nodes = model.nodes
        tris = model.tris
        tets = model.tets

        self.nnodes = nodes.shape[0]
        ntris = 0
        ntets = 0
        if dimension_flag == 2:
            ntris = tris.shape[0]
        elif dimension_flag == 3:
            ntets = tets.shape[0]
        else:
            raise RuntimeError()
        self.nelements = ntris + ntets

        #print("nnodes = ",self.nnodes)
        #print("nelements = ", self.nelements)

        grid = self.grid
        grid.Allocate(self.nelements, 1000)
        #self.gridResult.SetNumberOfComponents(self.nelements)

        assert nodes is not None
        points = numpy_to_vtk_points(nodes)
        self.nid_map = {}

        #elements -= 1
        if dimension_flag == 2:
            etype = 5  # vtkTriangle().GetCellType()
            create_vtk_cells_of_constant_element_type(grid, tris, etype)
        elif dimension_flag == 3:
            etype = 10  # vtkTetra().GetCellType()
            create_vtk_cells_of_constant_element_type(grid, tets, etype)
        else:
            raise RuntimeError('dimension_flag=%r; expected=[2, 3]' % dimension_flag)

        grid.SetPoints(points)
        grid.Modified()
        if hasattr(grid, 'Update'):
            grid.Update()

        # loadTetgenResults - regions/loads
        self.scalarBar.VisibilityOff()
        self.scalarBar.Modified()

        cases = {}
        ID = 1

        #cases = self._fill_tetgen_case(cases, ID, elements)
        self._finish_results_io(cases)

    def _fill_tetgen_case(self, cases, ID, elements):
        return cases

