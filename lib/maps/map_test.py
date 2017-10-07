from lib.maps.map_base import MapBase
import logging

class MapTest(MapBase):

    def __init__(self):

        super(MapTest,self).__init__()
        self._logger = logging.getLogger(__name__)


    @property
    def logger(self):
        return self._logger

    def init(self):

        #ヘックスグリッド定義
        super(MapTest, self).init(50, 1500, 1500)

        #他パラメータ（ヘックスごとの資源など）あれば設定


