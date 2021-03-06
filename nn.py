from math import tanh
from pysqlite2 import dbapi2 as sqlite


def dtanh(y):
    return 1.0 - (y * y)


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

    def get_all_hidden_ids(self, wordids, urlids):
        l1 = {}
        for wordid in wordids:
            cur = self.con.execute(
                        """SELECT toid
                           FROM wordhidden
                           WHERE fromid=%d""" % wordid)
            for row in cur:
                l1[row[0]] = 1
        for urlid in urlids:
            cur = self.con.execute(
                        """SELECT fromid
                           FROM hiddenurl
                           WHERE toid=%d""" % urlid)
            for row in cur:
                l1[row[0]] = 1
        return l1.keys()

    def set_up_network(self, wordids, urlids):
        # value lists
        self.word_ids = wordids
        self.hidden_ids = self.get_all_hidden_ids(wordids, urlids)
        self.url_ids = urlids

        # node outputs
        self.ai = float(len(self.word_ids))
        self.ah = float(len(self.hidden_ids))
        self.ao = float(len(self.url_ids))

        # create weights matrix
        self.wi = [[self.get_strength(word_id, hidden_id, 0)
                    for hidden_id in self.hidden_ids]
                   for word_id in self.word_ids]

        self.wo = [[self.get_strength(hidden_id, url_id, 1)
                    for url_id in self.url_ids]
                   for hidden_id in self.hidden_ids]

    def feed_forward(self):
        for i in range(len(self.word_ids)):
            self.ai[i] = 0
        # hidden activations
        for j in range(len(self.hidden_ids)):
            total = 0.0
            for i in range(len(self.word_ids)):
                total += (self.ai[i] * self.wi[i][j])
            self.ah[j] = tanh(total)
        # output activations
        for k in range(len(self.url_ids)):
            total = 0.0
            for j in range(len(self.hidden_ids)):
                total += (self.ah[j] * self.wo[j][k])
                self.ao[k] = tanh(total)
        return self.ao[:]

    def get_results(self, wordids, urlids):
        self.set_up_network(wordids, urlids)
        return self.feed_forward()

    def back_propagate(self, targets, N=0.5):
        # calculate errors for output
        output_deltas = [0.0] * len(self.url_ids)
        for k in range(len(self.url_ids)):
            error = targets[k] - self.ao[k]
            output_deltas[k] = dtanh(self.ao[k]) * error

        # calculate errors for hidden layer
        hidden_deltas = [0.0] * len(self.hidden_ids)
        for j in range(len(self.hidden_ids)):
            error = 0.0
            for k in range(len(self.url_ids)):
                error += output_deltas[k] * self.wo[j][k]
            hidden_deltas[j] = dtanh(self.ah[j]) * error

        # update input weights
        for i in range(len(self.wordids)):
            for j in range(len(self.hidden_ids)):
                change = hidden_deltas[j] * self.ai[i]
                self.wi[i][j] += N * change

    def train_query(self, wordids, urlids, selected_url):
        # Generate a hidden node if necessary
        self.generate_hidden_node(wordids, urlids)
        self.set_up_network(wordids, urlids)
        self.feed_forward()
        targets = [0.0] * len(urlids)
        targets[urlids.index(selected_url)] = 1.0
        error = self.back_propagate(targets)
        self.update_database()

    def update_database(self):
        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                self.set_strength(self.word_ids[i],
                                  self.hidden_ids[j],
                                  0,
                                  self.wi[i][j])
        for j in range(len(self.hidden_ids)):
            for k in range(len(self.url_ids)):
                self.set_strength(self.hidden_ids[j],
                                  self.url_ids[k],
                                  1,
                                  self.wo[j][k])
        self.con.commit()
