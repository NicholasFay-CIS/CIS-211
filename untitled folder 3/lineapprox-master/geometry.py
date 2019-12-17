"""
Geometry:  Points and polylines, including
approximation using the Ramer-Douglas-Peucker
algorithm.   

This is a 'model' component and should not directly 
contain any graphics code. All coordinates are in the 
model coordinate system.  The unit of the coordinate 
system can be any metric (cm, meters, whatever), but 
it must be the same unit in the x and y dimension 
so that the the usual distance formula holds.  Note that 
this IS true of UTM coordinates but it is NOT true of 
latitude and longitude. 

Class PolyLine is the representation of a sequence of 
points.  Includes hooks for a view component. 

Events generated (for view components): 
   "trial_approx" with options = { "p1": (x,y), "p2": (x,y) }
   "final_approx_seg" with options = { "p1": (x,y), "p2": (x,y) }

A trial approximation (event "trial_approx") is a segment that may 
be further subdivided.  A final approximation (event "final_approx_seg")
is a segment that will be incorporated in the line approximation with 
no further refinement.  

Author: Nicholas Fay 951566471
Problems attempted for extra credit:
problem
"""
import math

from typing import List, Tuple, Any
from numbers import Number

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Point(object):
    """Integer Cartesian coordinates. Immutable.
    x and y coordinates are public, read-only.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    def move(self, dx, dy):
        return Point(self.x+dx, self.y + dy)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False


class PolyLine(object):
    """A polyline is a sequence of points.
    All fields are private.
    """
    # Part 1:
    #   by calling corresponding methods in the _points field
    def __init__(self):
        self._points = []
        self._listeners = []
        self.tolerance = 0

    def __repr__(self):
        return "Polyline({})".format(self._points)

    def __eq__(self, other):
        if self._points == other._points:
            return True
        return False

    def __iter__(self):
        return self._points.__iter__()

    def __len__(self):
        return len(self._points)

    def __getitem__(self, index):
        return self._points.__getitem__(index)

    def append(self, pt):
        self._points.append(pt)


    # ----- List protocol emulation --------
    # We want the PolyLine object to act like other Python
    # sequence objects (lists, tuples, etc).  These methods
    # should act exactly like their counterpoints in class
    # 'list'.
    #
    # ---- End of list protocol emulation ---------
    # ---- Connection to graphics in Model-View-Controller (MVC) style;
    #      We will talk about this in week 2.  Don't change this section
    #

    def add_listener(self, listener: Any):
        self._listeners.append(listener)

    # Note: There is a way to declare a useful type for the 'listener' parameter,
    # but it involves inheritance, which will be introduced in the
    # next project. For now I've just labeled it an Any, meaning anything.

    def notify_all(self, event_name: str, options={}):
        for listener in self._listeners:
            listener.notify(event_name, options=options)

    # ------ end of MVC ---------


    def approximate(self, tolerance: int) -> "PolyLine":
        """Returns a new PolyLine with a subset of the
        Points in this polyline, deviating from this polyline
        by no more than tolerance units.
        """
        approx = PolyLine()
        self._dp_simplify(approx, tolerance, 0, len(self._points) - 1)
        approx.append(self._points[-1])
        return approx

    def _dp_simplify(self, approx: "PolyLine", tolerance: int, from_index: int, to_index: int):
        """Recursively build up simplified path, working left to
        right to add the resulting points to the simplified list.
        """
        Beg = self._points[from_index]  # variable for the first point (eliminates amount of times self. needs to be added)
        finish = self._points[to_index]  # variable for the last point (eliminates amount of times self. needs to be added)
        log.debug("dp {}-{} {}-{}".format(from_index, to_index, Beg, finish))
        self.notify_all("trial_approx", options={"p1": Beg, "p2": finish})  # creates gray lines where further divisions can be made
        Maxindex = from_index  # This is the variable that keeps track of the index in the middle
        Maxdeviation = 0  # This variable keeps track of the largest deviating value given
        for i in range(from_index + 1, to_index):  # goes through each one of the given points, adds one to from_index in order to do so
            NEWDev = deviation(Beg, finish, self._points[i])  # This checks the deviation of a point
            if NEWDev > Maxdeviation:  # Compares the next deviation of a point to the max it can be
                Maxdeviation = NEWDev
                Maxindex = i
        # A recursive algorithm that allows for the Ramer-Douglas-Peucker to be implimented the needed amount of times.
        if to_index - from_index < 2:
            '''
            This is the first Base Case:
            This if statement determines if the distance between the 
            last point and the first point and if it is greater than 2.
            Doesnt return a value.
            '''
            approx.append(Beg)
            self.notify_all("final_approx_seg", options={"p1": self._points[from_index], "p2": self._points[to_index]})
        elif Maxdeviation > tolerance:
            """
            Second Base Case:
            Refers to the deviation definition in order to run through this elif statement.
            If the distance is greater than the tolerance, then starting at the 
            right it will approximate the line then transistions to the left using recursion (which is where is calls _dp_simplify)
            Doesnt return a value.
            """
            # notice that there is a split at the middle or (Maxindex)
            self._dp_simplify(approx, tolerance, from_index, Maxindex)
            self._dp_simplify(approx, tolerance, Maxindex, to_index)
        else:
            """
            Inductive Case: Deviation is greater than the tolerance with more than two points
            Doesnt return a value.
            """
            approx.append(Beg)  # appends the approx value
            self.notify_all("final_approx_seg", options={"p1": self._points[from_index],"p2": self._points[to_index]})  # initiates the new red line
            log.debug('The simplified value = {}'.format(approx))

        
def deviation(p1: Point, p2: Point, p: Point) -> float:
    """Shortest distance from point p to a line through p1,p2"""
    intercept = normal_intercept(p1, p2, p)
    # Standard distance formula, sqrt((x2-x1)^2 +(y2-y1)^2)
    log.debug("Computing distance from {} to {}"
                  .format(p, (intercept.x,intercept.y)))
    dx = intercept.x - p.x
    dy = intercept.y - p.y
    return math.sqrt(dx*dx + dy*dy)


def normal_intercept(p1: Point, p2: Point, p: Point) -> Point:
    """
    The point at which a line through p1 and p2 
    intersects a normal dropped from p.  See normals.md
    for an illustration. 
    """
    log.debug("Normal intercept {}-{} from {}".format(p1, p2, p))

    # Special cases: slope or normal slope is undefined
    # for vertical or horizontal lines, but the intersections
    # are trivial for those cases
    if p2.x == p1.x:
        log.debug("Intercept at {}".format((p1.x,p.y)))
        return Point(p1.x, p.y)
    elif p2.y == p1.y:
        log.debug("Intercept at {}".format((p.x, p1.y)))
        return Point(p.x, p1.y)

    # The slope of the segment, and of a normal ray
    seg_slope = (p2.y - p1.y)/(p2.x - p1.x)
    normal_slope = 0 - (1.0 / seg_slope)

    # For y=mx+b form, we need to solve for b (y intercept)
    seg_b = p1.y - seg_slope * p1.x
    normal_b = p.y - normal_slope * p.x

    # Combining and subtracting the two line equations to solve for
    x_intersect = (seg_b - normal_b) / (normal_slope - seg_slope)
    y_intersect = seg_slope * x_intersect + seg_b
    # Colinear points are ok!

    log.debug("Intercept at {}".format(x_intersect, y_intersect))
    return Point(x_intersect, y_intersect)


    
    
