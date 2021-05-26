# -*- coding: utf-8 -*-
r"""
Finite filtered complexes

AUTHORS:

- Guillaume Rousseau (2021-05)

This module implements the basic structures of finite filtered complexes.
A filtered complex is a simplicial complex, where each simplex is given
a weight, or "filtration value", such that the weight of a simplex is
greater than the weight of each of its faces.

.. NOTE::

    This module should behave close to the sage.homology.simplicial_complex
    module, and have similar notations and methods.

.. EXAMPLES::

    sage: FilteredComplex([([0], 0), ([1], 0), ([0,1], 1)])
    Filtered complex with vertex set (0, 1) and with simplices ((0,) : 0), ((1,) : 0), ((0, 1) : 1)

Sage can compute persistent homology of simplicial complexes::

    sage: X = FilteredComplex([([0], 0), ([1], 0), ([0,1], 1)])
    sage: X.compute_homology()
    sage: X.persistence_intervals(0)
    [(0, 1), (0, +Infinity)]

FilteredComplex objects are mutable::

    sage: X = FilteredComplex() # returns an empty complex
    sage: X.insert([0,2],0) # recursively adds faces
    sage: X.insert([0,1],0)
    sage: X.insert([1,2],0)
    sage: X.insert([0,1,2],1) # closes the circle
    sage: X.compute_homology()
    sage: X.persistence_intervals(1)
    [(0, 1)]

Filtration values can be accessed with function and list syntaxes.
A simplex not in the complex will have filtration value -1

    sage: X = FilteredComplex([([0], 0), ([1], 0), ([0,1], 1)])
    sage: s_1 = Simplex([0])
    sage: X[s_1]
    0
    sage: X(Simplex([0,1]))
    1


"""

from sage.structure.sage_object import SageObject
from sage.homology.simplicial_complex import Simplex
from sage.modules.free_module import FreeModule
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.infinity import infinity




class FilteredComplex(SageObject):

    def __init__(self,simplex_degree_list = [], warnings = False):
        r"""
        Define a filtered complex.

        :param simplex_degree_list: list of simplices and filtration values
        :param warnings: set to True for more info on each insertion

        ``simplex_degree_list`` should be a list of tuples ``(l,v)`` where
        ``l`` is a list of vertices and ``v`` is the corresponding filtration
        value.

        .. EXAMPLES::

            sage: FilteredComplex([([0], 0), ([1], 0), ([2], 1), ([0,1],2.27)])
            Filtered complex with vertex set (0, 1, 2) and with simplices ((0,) : 0), ((1,) : 0), ((2,) : 1), ((0, 1) : 2.27000000000000)

        """
        self._vertices = set()
        self._simplices = [] # list of simplices
        self._degrees_dict = {} # contains the degrees. keys are simplices
        self._numSimplices = 0
        self._dimension = 0
        self._warnings = warnings
        self._maxDeg = 0
        for l,v in simplex_degree_list:
            self.insert(l,v)


    def get_value(self,s):
        r"""
        Return the filtration value of a simplex in the complex.

        :param s: simplex
        TODO
        """
        if s in self._degrees_dict:
            return self._degrees_dict[s]
        else:
            return -1


    def _insert(self,simplex,d):
        r"""
        Add a simplex to the complex.

        All faces of the simplex are added recursively if they are
        not already present, with the same degree.

        If the simplex is already present, and the new degree is lower
        than its current degree in the complex, the value gets updated,
        otherwise it does not change. This propagates recursively to faces.

        :param simplex: simplex to be inserted
        :type simplex: Simplex
        :param d: degree of the simplex

        .. EXAMPLES::

            sage: X = FilteredComplex()
            sage: X._insert(Simplex([0]),3)
            sage: X
            Filtered complex with vertex set (0,) and with simplices ((0,) : 3)




        """
        # Keep track of whether the simplex is already in the complex
        # and if it should be updated or not
        update = False
        value = self[simplex]
        if value >= 0:
            if self._warnings:
                print("Face {} is already in the complex.".format(simplex))
            if value > d:
                if self._warnings:
                    print("However its degree is {}: updating it to {}".format(self.get_value(simplex),d))
                update = True
                self._degrees_dict.pop(simplex)
            else:
                if self._warnings:
                    print("Its degree is {} which is lower than {}: keeping it that way".format(self._degrees_dict[simplex],d))
                return

        # check that all faces are in the complex already. If not, warn the user and add faces (recursively)
        faces = simplex.faces()
        if simplex.dimension()>0:
            for f in faces:

                if self._warnings:
                    print("Also inserting face {} with value {}".format(f,d))
                self._insert(f,d)

        if not update:
            self._numSimplices += 1
            self._simplices.append(simplex)

        self._degrees_dict[simplex] = d
        self._dimension = max(self._dimension,simplex.dimension())
        self._maxDeg = max(self._maxDeg,d)
        self._vertices.update(simplex.set())

    def insert(self,vertex_list,filtration_value):
        r"""
        Add a simplex to the complex.

        This method calls self._insert, turning the list of vertices
        into a simplex.

        :param vertex_list: list of vertices
        :param filtration_value: desired degree of the simplex to be
        added.

        .. EXAMPLES::

            sage: X = FilteredComplex()
            sage: X.insert(Simplex([0]),3)
            sage: X
            Filtered complex with vertex set (0,) and with simplices ((0,) : 3)

        If the warning parameter was set to true, this method will print
        some info.

            sage: X = FilteredComplex(warnings = True)
            sage: X.insert(Simplex([0,1]),2)
            Also inserting face (1,) with value 2
            Also inserting face (0,) with value 2
            sage: X.insert(Simplex([0]),1)
            Face (0,) is already in the complex.
            However its degree is 2: updating it to 1
            sage: X.insert(Simplex([0]),77)
            Face (0,) is already in the complex.
            Its degree is 1 which is lower than 77: keeping it that way
        """
        self._insert(Simplex(vertex_list),filtration_value)



    def compute_homology(self,field = 2, strict = True, verbose = False):
        """
        Compute the homology intervals of the complex.

        :param field: prime number modulo which homology is computed
        :param strict: if set to False, takes into account intervals
        of persistence 0. Default value: True
        :param verbose: if set to True, prints progress of computation.
        Default value: False.

        .. ALGORITHM::
        TODO


        .. EXAMPLES::
        TODO

        .. REFERENCES::
        TODO
        """


        # first, order the simplices in lexico order on dimension, degree and then arbitrary order
        def key(s):
            d = self.get_value(s)
            return (s.dimension(),d,s)
        self._simplices.sort(key = key)

        # remember the index of each simplex
        self._indexBySimplex = {}
        for i in range(self._numSimplices):
            self._indexBySimplex[self._simplices[i]] = i

        self._fieldPrime = field
        self._field = GF(field)
        self._chaingroup = FreeModule(self._field,rank_or_basis_keys=self._simplices)

        self.marked = [False for i in range(self._numSimplices)]
        self.T = [None for i in range(self._numSimplices)] # contains couples (index,chain)
        self.intervals = [[] for i in range(self._dimension+1)] # contains homology intervals once the algo has finished
        self.pairs = []

        self._strict = strict
        self._verbose = verbose

        if self._verbose:
            print("Beginning first pass")
        for j in range(self._numSimplices):
            if j%1000 == 0 and self._verbose:
                print('{}/{}'.format(j,self._numSimplices))
            s = self._simplices[j]
            #if self._verbose:
                #print("Examining {}. Removing pivot rows...".format(s))
            d = self.__remove_pivot_rows(s)
            #if self._verbose:
                #print("Done removing pivot rows")
            if d == 0:
                #if self._verbose:
                    #print("Boundary is empty when pivots are removed: marking {}".format(s))
                self.marked[j] = True
            else:

                maxInd = self.__max_index(d)
                t = self._simplices[maxInd]
                self.T[maxInd] = (s,d)
                self.__add_interval(t,s)
                #if self._verbose:
                    #print("Boundary non-reducible: T{} is set to:".format(t))
                    #print(str(d))

        if self._verbose:
            print("First pass over, beginning second pass")
        for j in range(self._numSimplices):
            if j%1000 == 0 and self._verbose:
                print('{}/{}'.format(j,self._numSimplices))
            s = self._simplices[j]
            if self.marked[j] and not self.T[j]:

                #if self._verbose:
                    #print("Infinite interval found for {}.".format(s))
                self.__add_interval(s,None)
        if self._verbose:
            print("Second pass over")

    def __add_interval(self,s,t):
        r"""
        Add a new interval (i.e. homology element).
        This method should not be called by users, it is used in
        the ``compute_persistence`` method.
        """
        k = s.dimension()
        i = self._degrees_dict[s]
        if not t:
            j = infinity
        else:
            j = self._degrees_dict[t]

        if i != j or (not self._strict):
            #if self._verbose:
                #print("Adding {}-interval ({},{})".format(k,i,j))
            self.intervals[k].append((i,j))
            self.pairs.append((s,t))
            #if i == 10:
            #    print(k,t,s)

    def __remove_pivot_rows(self,s):
        r"""
        This method should not be called by users, it is used in
        the ``compute_persistence`` method.
        """
        d = self._chaingroup()
        if s.dimension() == 0:
            return d
        for (i,f) in enumerate(s.faces()):
            d += ((-1)**i) * self._chaingroup(f)
        for (s,x_s) in d:
            j = self._indexBySimplex[s]
            if not self.marked[j]:
                d = d - x_s*self._chaingroup(s)

        while d != 0:
            maxInd = self.__max_index(d)
            t = self._simplices[maxInd]

            if not self.T[maxInd]:
                break

            c = self.T[maxInd][1]
            q = c[t]

            d = d - (q**(-1)*c)

        return d


    def __max_index(self,d):
        r"""
        Return the maximal index of all simplices with nonzero
        coefficient in ``d``.

        This method is called in ``__remove_pivot_rows`` and ``compute_persistence``
        """
        currmax = -1
        for (s,x_s) in d:
            j = self._indexBySimplex[s]
            if j>currmax:
                currmax = j
        return currmax



    def persistence_intervals(self,d):
        """
        Returns the list of d-dimensional homology elements.
        Should only be run after compute_homology has been run.
        TODO

        """
        return self.intervals[d][:]

    def betti_number(self,k,l,p):
        r"""
        TODO
        """
        res = 0
        for (i,j) in self.intervals[k]:
            if (i <= l and l + p < j ) and p>=0:
                    res+=1
        return res

    def __call__(self,s):
        return self.get_value(s)

    def __getitem__(self,s):
        return self.get_value(s)

    def _repr_(self):
        """
        Print representation.

        If there are too many simplices or vertices, only prints the
        count for each.


        EXAMPLES::

            TODO
        """

        vert_count = len(self._vertices)
        simp_count = self._numSimplices
        if simp_count > 10 or vert_count>20:
            return "Filtered Complex on {} vertices with {} simplices.".format(vert_count,simp_count)

        vertex_string = "with vertex set {}".format(tuple(self._vertices))
        simplex_string = "with simplices " + ", ".join(["({} : {})".format(s,self._degrees_dict[s]) for s in self._simplices])


        return "Filtered complex " + vertex_string + " and " + simplex_string