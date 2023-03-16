import numpy as np

class Primitive:
    def __init__(self):
        pass

    def get_primitive(self, primitive):
        if primitive == 0:
            return self.get_triangle()
        elif primitive == 1:
            return self.get_rectangle()
        elif primitive == 2:
            return self.get_box()
        else :
            return None, None

    # vertices, indices setting
    def get_triangle(self):
        vertices = [  # positions        # texture coords
                    -0.5, -0.5,  0.0,   0.0, 0.0,
                     0.5, -0.5,  0.0,   1.0, 0.0,
                     0.0,  0.5,  0.0,   0.5, 1.0
                   ]
        vertices = np.array(vertices, dtype=np.float32)

        return vertices, None

    def get_rectangle(self):
        vertices = [  # positions        # texture coords
                     0.5,  0.5,  0.0,   1.0, 1.0,   # top right
                     0.5, -0.5,  0.0,   1.0, 0.0,   # bottom right
                    -0.5, -0.5,  0.0,   0.0, 0.0,   # bottom left
                    -0.5,  0.5,  0.0,   0.0, 1.0    # top left
                   ]
        vertices = np.array(vertices, dtype=np.float32)

        indices = [ 0, 1, 3,
                    1, 2, 3 ]
        indices = np.array(indices, dtype=np.uint32)

        return vertices, indices

    def get_box(self):
        vertices = [  # positions       # texture coords
                    -0.5, -0.5, -0.5,  0.0, 0.0,
                     0.5, -0.5, -0.5,  1.0, 0.0,
                     0.5,  0.5, -0.5,  1.0, 1.0,
                     0.5,  0.5, -0.5,  1.0, 1.0,
                    -0.5,  0.5, -0.5,  0.0, 1.0,
                    -0.5, -0.5, -0.5,  0.0, 0.0,

                    -0.5, -0.5,  0.5,  0.0, 0.0,
                     0.5, -0.5,  0.5,  1.0, 0.0,
                     0.5,  0.5,  0.5,  1.0, 1.0,
                     0.5,  0.5,  0.5,  1.0, 1.0,
                    -0.5,  0.5,  0.5,  0.0, 1.0,
                    -0.5, -0.5,  0.5,  0.0, 0.0,

                    -0.5,  0.5,  0.5,  1.0, 0.0,
                    -0.5,  0.5, -0.5,  1.0, 1.0,
                    -0.5, -0.5, -0.5,  0.0, 1.0,
                    -0.5, -0.5, -0.5,  0.0, 1.0,
                    -0.5, -0.5,  0.5,  0.0, 0.0,
                    -0.5,  0.5,  0.5,  1.0, 0.0,

                     0.5,  0.5,  0.5,  1.0, 0.0,
                     0.5,  0.5, -0.5,  1.0, 1.0,
                     0.5, -0.5, -0.5,  0.0, 1.0,
                     0.5, -0.5, -0.5,  0.0, 1.0,
                     0.5, -0.5,  0.5,  0.0, 0.0,
                     0.5,  0.5,  0.5,  1.0, 0.0,

                    -0.5, -0.5, -0.5,  0.0, 1.0,
                     0.5, -0.5, -0.5,  1.0, 1.0,
                     0.5, -0.5,  0.5,  1.0, 0.0,
                     0.5, -0.5,  0.5,  1.0, 0.0,
                    -0.5, -0.5,  0.5,  0.0, 0.0,
                    -0.5, -0.5, -0.5,  0.0, 1.0,

                    -0.5,  0.5, -0.5,  0.0, 1.0,
                     0.5,  0.5, -0.5,  1.0, 1.0,
                     0.5,  0.5,  0.5,  1.0, 0.0,
                     0.5,  0.5,  0.5,  1.0, 0.0,
                    -0.5,  0.5,  0.5,  0.0, 0.0,
                    -0.5,  0.5, -0.5,  0.0, 1.0
                    ]

        vertices = np.array(vertices, dtype=np.float32)

        return vertices, None