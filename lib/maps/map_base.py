import logging
import math

import numpy as np

from lib.DB.DBSingleton import DBSingleton


class MapBase:

    def __init__(self):

        self._length = None
        self._width = None
        self._height = None
        self._logger = logging.getLogger(__name__)

    def init(self, length, width, height):

        self._length = length
        self._width = width
        self._height = height

        #グリッドを作成しDBに
        self.__create_grid()

    @property
    def length(self):
        return self._length

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def logger(self):
        return self._logger

    #グリッドを作成しDBに格納
    def __create_grid(self):

        #古いグリッドを削除
        db = DBSingleton()
        if not db.delete(table="hex_grid", where=""):
            self.logger.critical("error happened when deleting old hex_grid")
            raise Exception("map_base.__create_grid : failed")

        x_offset = self.length
        y_offset = self.length * math.sin(1 / 3 * math.pi)
        delta_x = 3 / 2 * self.length
        delta_y = y_offset;

        #アフィン変換行列
        matGridToNorm = np.matrix([[   delta_x,           0, x_offset],
                               [-(delta_y), 2 * delta_y, y_offset],
                               [         0,           0,        1]])

        matNormToGrid = np.linalg.inv(matGridToNorm)

        #グリッド生成
        x = x_offset
        col = 0
        serial = 0

        while x + delta_x + (self.length / 2) < self.width:

            y = y_offset
            if col % 2 == 1:
                y += delta_y

            while (y + delta_y * 3) < self.height:

                #グリッド空間の座標に変換
                n_vec = np.matrix([[x], [y], [1]])
                g_vec = matNormToGrid * n_vec
                g_col = int(np.round(g_vec[0])[0])
                g_row = int(np.round(g_vec[1])[0])

                #DBに格納
                db.insert("hex_grid", col=g_col, row=g_row, serial=serial)
                serial += 1

                y += delta_y * 2

            x += delta_x
            col += 1


