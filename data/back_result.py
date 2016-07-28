#! encoding:utf-8
import sqlite3


class DBResult(object):
    """
    这里放回测的结果数据
    """
    _db_path = '/Users/wgx/workspace/data/result_db.db'
    table_relative_strength_zero = 'relative_strength_zero'

    line_id = 'id'
    line_denominator = 'denominator'
    line_malength = 'malength'
    line_temlength = 'temlength'
    line_reweightperiod = 'reweightperiod'
    line_winpercent = 'winpercent'
    line_needups01 = 'needups01'
    line_sellafterreweight = 'sellafterreweight'
    line_losepercent = 'losepercent'
    line_rankposition = 'rankposition'
    line_rankpercent = 'rankpercent'

    line_maxdd = 'maxdd'
    line_returns = 'returns'

    relative_strenth_zero_columns = (
        line_denominator,
        line_malength,
        line_temlength,
        line_reweightperiod,
        line_winpercent,
        line_needups01,
        line_sellafterreweight,
        line_losepercent,
        line_rankposition,
        line_rankpercent,
        line_maxdd,
        line_returns,
    )

    def __init__(self):
        super(DBResult, self).__init__()
        self.connection = None
        """:type:sqlite3.Connection"""
        self.cursor = None
        """:type:sqlite3.Cursor"""

    def open(self):
        self.connection = sqlite3.connect(self._db_path)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def create_relative_strength_zero(self):
        self.open()
        db_columns = (
            self.line_id + ' integer primary key',
            self.line_denominator + ' double',
            self.line_malength + ' integer',
            self.line_temlength + ' integer',
            self.line_reweightperiod + ' integer',
            self.line_winpercent + ' double',
            self.line_needups01 + ' integer',
            self.line_sellafterreweight + ' integer',
            self.line_losepercent + ' double',
            self.line_rankposition + ' integer',
            self.line_rankpercent + ' double',
            self.line_maxdd + ' double',
            self.line_returns + ' double',
        )
        sql_str = 'create table %s (%s)' % (self.table_relative_strength_zero, ','.join(db_columns))
        self.cursor.execute(sql_str)
        self.close()

if __name__ == '__main__':
    DBResult().create_relative_strength_zero()