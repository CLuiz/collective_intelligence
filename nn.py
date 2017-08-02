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
                    """INSERT INTO %s (fromid, toid, strength)
                       VALUES (%d, %d, %f)
                    """ % (table, fromid, toid, strength))
        else:
            rowid = res[0]
            self.con.execute(
                    """UPDATE %s SET strength=%f
                       WHERE rowid=%d
                    """ % (table, strength, rowid))

    def generate_hidden_node(self, wordids, urls):
        if len(wordids) > 3:
            return None
        # Check if node was already created for this word
        create_key = '_'.join(sorted([str(wordid) for wordid in wordids]))
        res = self.con.execute(
                    """SELECT rowid
                       FROM hiddennode
                       WHERE create_key='%s'
                       """ % create_key).fetchone()

        # Create node
        if res is None:
            cur = self.con.execute(
                        """INSERT INTO hiddennode (create_key)
                           VALUES ('%s')""" % create_key)
            hiddenid = cur.lastrowid
            # Put in default weights
            for wordid in wordids:
                self.set_strength(wordid, hiddenid, 0, 1.0 / len(wordids))
            for urlid in urls:
                self.set_strength(hiddenid, urlid, 1, 0.1)
            self.con.commit()
            
