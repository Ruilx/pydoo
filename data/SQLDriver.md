# MySQL Conf

```python
MySQLConf = {
    'host': "49.232.253.114",
    'user': "root",
    'password': "uGdWbrCap5x8rqVQw4h5",
    'database': "knowledge",
    'port': 3307,
    'cursorclass': pymysql.cursors.DictCursor,
}
```

# PyMySQL

`````python
import pymysql

conn = pymysql.connect(**MySQLConf)
# <class 'pymysql.connections.Connection'>

cursor = conn.cursor()
# <class 'pymysql.cursors.DictCursor'>

conn.begin() -> None
conn.commit() -> None
conn.rollback() -> None

cursor.execute(query: str, args=None) -> int<"number of affected rows">
cursor.executemany(query: str, args) -> int|None
cursor.mogrify(query: str, args=None) -> str<"SQL">

cursor.fetchone() -> result
cursor.fetchmany(size: int) -> list[result]
cursor.fetchall() -> list[result]
cursor.scroll(value: int, mode: str<"relative"|...>)

cursor.description -> tuple<...>
cursor.rownumber
cursor.rowcount

cursor.close()
`````

