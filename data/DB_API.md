# DB API

DB_API规范需要满足:

* Conf配置至少有以下内容:
  * `host`: `string<IPv4|IPv6|Domain|...>` `必填`表示要连接的机器地址
  * `port`: `int<Port>` `必填` `默认 以数据库属性为准`表示要连接的端口
  * `user`: `string<Nameable>` `必填` `默认:root`表示鉴权的用户名
  * `password`: `string` `必填`表示鉴权的密码
  * `database`: `string<Nameable>` `可选` 表示默认要连接的数据库名
* 通过Conf或DSN得到Connection对象
* 通过Connection对象开启/提交/回滚事务(取决于数据库性质)
* 通过`Connection.cursor()`得到Cursor对象
* 通过`Cursor.execute{∅|many}()`执行SQL语句
* 通过`Cursor.fetch{one|all|many}()`按要求获取数据条目
* 通过`Cursor.close()`和`Connection.close()`关闭连接

# Database Conf

``` python
DBConf = {
    'host': "49.232.253.114",
    'user': "root",
    'password': "uGdWbrCap5x8rqVQw4h5",
    'database': "knowledge",
    'port': 3307,
}
```

# PyMySQL

``` python
import pymysql

conn = pymysql.connect(**DBConf)
# <class 'pymysql.connections.Connection'>

cursor = conn.cursor()
# <class 'pymysql.cursors.DictCursor'>

conn.begin() -> None
conn.commit() -> None
conn.rollback() -> None

cursor.execute(query: str, args=None) -> int["number of affected rows"]
cursor.executemany(query: str, args) -> int | None
cursor.mogrify(query: str, args=None) -> str["SQL"]

cursor.fetchone() -> result
cursor.fetchmany(size: int) -> list[result]
cursor.fetchall() -> list[result]
cursor.scroll(value: int, mode: str["relative" | ...])

cursor.description -> tuple<...>
cursor.rownumber
cursor.rowcount

cursor.close()
conn.close()
`````

# MySQLConnectionPool

``` python
from mysql_connector_pool import MySQLConnectionPool

pool = MySQLConnection(**DBConf, pool_name="POOL_NAME", pool_size=10)

conn = pool.get_connection()
# <class ...>

cursor = conn.cursor()
# <class ...>

cursor.execute(query: str)

cursor.close()
conn.close()
```

# PooledDB

``` python
import pymysql
from dbutils.pooled_db import PooledDB

pool = PooledDB(creator=pymysql, mincached=1, maxcached=20, **DBConf, autocommit=False)

conn = pool.connection()
# <class ...>

cursor = conn.cursor()
# <class ...>

cursor.execute(query: str)

cursor.close()
conn.close()
```

# PyMSSQL

``` python
import pymssql

DBConf['server'] = DBConf['host']
del DBConf['host']

conn = pymyssql.connect(**DBConf)
# <class ...>

cursor = conn.cursor()
# <class ...>

cursor.close()
conn.close()
```

# CX_Oracle

``` python
import cx_Oracle

dsn = ...

conn = cx_Oracle.connect(user=DBConf['user'], password=DBConf['password'], dsn=dsn)
# <class ...>

cursor = conn.cursor()
# <class ...>

cursor.close()
conn.close()
```

# Clickhouse Client

``` python
from clickhouse_driver.dbapi import connection, cursor

conn = connection.Connection(**DBConf)

cursor = conn.cursor()



cursor.close()
conn.close()
```
