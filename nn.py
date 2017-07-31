from math import tanh
from pysqlite2 import dbapi2 as sqlite


class search_net(object):
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close

    def make_table(self):
        self.con.execute("""CREATE table hiddennode(create key)""")
        self.con.execute("""CREATE table wordhidden(fromid, toid, strenght)""")
        self.con.execute("""Create table hiddenurl(fromid, toid, strength)""")
        self.con.commit()

    def get_strength(self, fromid, toid, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        res = self.con.execute(
                    """SELECT strength
                       FROM %s
                       WHERE fromid=%d
                       AND toid=%d
                    """ % (table, fromid, toid)).fetchone()
        if res is None:
            if layer == 0:
                return -0.2
            if layer == 1:
                return 0
        return res[0]

    def set_strength(self, fromid, toid, layer, strength):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        res = self.con.execute(
                    """SELECT rowid
                       FROM %s
                       WHERE fromid=%d
                       AND toid=%d
                    """ % (table, fromid, toid)).fetchone()
        if res is None:
            self.con.execute(
                    """SELECT
                    """)
