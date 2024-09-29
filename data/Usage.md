# 普通用法

```sql
Select colA, colB, colC 
From tableA 
Where colA = 1 And colB = "ValueB" 
Order By colC Desc 
Limit 10 Offset 20
```

```python
doo.table("tableA")
# -----------------------------------------------
   .where("colA", 1)
   .where("colB", "ValueB")
# -----------------------------------------------
   .where({
       "colA": 1,
       "colB": "ValueB",
   })
# -----------------------------------------------
   .fields(["colA", "colB", "colC"])
# -----------------------------------------------
   .order_by("colC", pydoo.Desc)
# -----------------------------------------------
   .order_by("colC", "desc")
# -----------------------------------------------
   .limit(20, 10)
# -----------------------------------------------
   .limit(10)
   .offset(20)
# -----------------------------------------------
   .select()
```

# 原生查询

```python
doo.query(sql: str, args: list | dict) -> Result
```

```python
doo.execute(sql: str, args: list | dict) -> int
```

# Table启动查询

```python
doo.table(table_name: str) -> Statement
```
```python
doo.table(table_name: str, alias: str | None = None) -> Statement
```

# Statement 设定

```python
state: Statement
```

## 设置Table别名

```python
state.alias(name: str) -> Statement
```

## 设置Select的字段

```python
state.field(fields: list[str]) -> Statement
```

```python
state.field(fields: list[Field]) -> Statement
```

```python
state.field(field: str) -> Statement
```

```python
state.field('*') -> Statement
```

```python
state.field(Select.All) -> Statement
```

### 设置distinct

```python
state.distinct(enable: bool) -> Statement
```

```python
@deleted
state.distinct(field: str) -> Statement
```

## 设置Where条件

```python
state.where(cond: WherePart) -> Statement
```

```python
state.where(condstr: str) -> Statement
```

```python
state.where(name: str, op: str, value: ValueType) -> Statement
```

```python
state.where(name: str, value: ValueType) -> Statement
```

```python
state.where(cond: dict[str, ValueType | Closure<cond> | Statement]) -> Statement # cond: where builder
```

```python
state.where(cond: list[tuple[str, str | Op, ValueType]]) -> Statement
```

### 设置WhereOr

```
state.where(or_cond: WhereOr) -> Statement
```

### Where builder

operators:

* `,eq` `=` equal
* `,lt` `<` less than
* `,gt` `>` greater than
* x 1from clickhouse_driver.dbapi import connection, cursor2​3conn = connection.Connection(**DBConf)4​5cursor = conn.cursor()6​7​8​9cursor.close()10conn.close()python
* `,ge` `>=` greater than or equal
* `,ne` `!=` not equal
* `,in` `:` in set
  * `{'col:', [1, 2, 3]}` `Where col in (1, 2, 3)`
  * `{'col:', Statement<Select>}` `Where col in (Select ...)`
* `,like` `?` like '%string%'
  * `,like prefix` `?^` like 'string%'
  * `,like suffix` `?$` like '%string'
* `,not like` `!?` not like '%string%'
* `,between` `~` between A and B
* `,not between` `!~` not between A and B
* NULL operator:
  * `{'col': None}` `Where col Is None`
  * `{'col!': None}` `Where col Is Not None` different from `in` operator
* `,regexp` `,\` regex expression 
* `{string}` literal string, eg: `count(distinct colA)`  
* `'#or': {...}` or condition, `'#or': {'id': 1, 'name': 'Alice'}` `Where id = 1 Or name = 'Alice'`
* `'#and': {...}` and condition, `'#and': {'id': 1, 'name': 'Alice'}` `Where id = 1 And name = 'Alice'`
* `'#exist': Statement<Select>` data exists in subquery
* `'#not exists': Statement<Select>` data not exists in subquery
* `'/<func>'`: use functions
  * `col/STR_TO_DATE(*, '%Y-%m-%d')` `STR_TO_DATE(col, '%Y-%m-%d')`
  * `col/FROM_UNIXTIME/DATE` `DATE(FROM_UNIXTIME(col))`
* `->{TYPE}` cast datatype
  * `col->Integer` `CAST(col AS Integer)`
* `colA|colB` multiple columns with same condition
  * `'colA|colB?': 'Alice'` `colA like '%Alice%' Or colB like '%Alice%'`

```python
{
    'id': 1,
    'name': "name"
}
# Where id = 1 And name = 'name'
```

```python
{
    'id>': 1,       # =, >, <, >=, <=, !=
    'name?': "name" # ?(like), :(in)
}
# Where id > 1 And name like '%name%'
```

```python
{
	('id', '<=', 1000),
	('name', 'in', ['name1', 'name2'])
}
# Where id <= 1000 And name in ('name1', 'name2')
```

```python
{
	'id:': [1, 2]
}
# Where id in (1, 2)
```

```python
{
	'id~': (1, 10)
}
# Where id Between 1 And 10
{
    'id!~': (1, 10)
}
# Where id Not Between 1 And 10
```

```python
{
	'#or': {
		'id': 1,
		'name': 'Alice'
	}
}
# Where id = 1 Or name = 'Alice'
{
    '#or': {
        'id' : 1,
        'name': 'Alice'
    },
    'age': 20
}
# Where (id = 1 Or name = 'Alice') And age = 20
```

```
where_builder(cond: list[dict[str, ValueType | Closure<cond> | Statement]])
```



## 设置Join

```
.inner_join(...)
.left_join(...)
.right_join(...)
.cross_join(...)
```

```python
state.inner_join(table_name: str, alias: str, on_statement: str) -> Statement
```

### 设置子表

```python
state.inner_join(sub_query: Statement<Select>, alias: str, on_statement: str) -> Statement
```

## 设置Group By

```python
state.group_by(field: str) -> Statement
```

```
state.group_by(fields: list[str]) -> Statement
```

## 设置Order By

``` python
state.order_by(field: str, ordering: str | Ordering = "asc")
```

## 设置Having

```python
state.having(cond: str)
```

## 设置Limit

```python
state.limit(rows: int) -> Statement
```

```
state.limit(offset: int, rows: int) -> Statement
```

``` python
state.offset(offset: int) -> Statement
```

### 设置Page

```
state.page(page_index: int, page_size: int)
```

## 设置For Update

```python
state.lock(lock: bool) -> Statement
```

```
state.lock(lock_str: str) -> Statement
```

# 开始执行

## 查询

```python
# 获取所有结果
state.select() -> Result
```

```python
# 获得一行结果
state.find() -> Result
```

### 聚合查询 

聚合查询因为需要重新配置fields, 所以在前面不能设置fields和distinct, 否则会报异常

```python
state.count() -> int
state.count(field: str | list[str]) -> Result
state.sum() -> int
state.sum(field: str | list[str]) -> Result
state.max(field: str | list[str]) -> Result
state.min(field: str | list[str]) -> Result
state.avg(field: str | list[str]) -> Result
```

## 修改

### Insert

Insert语句只和table有关, 其他选项例如fields和where等不能设置, 否则会报异常

```python
state.insert(data: dict[str, ValueType]) -> int
```

### Update

update语句和table和where有关, 其他选项例如fields, group_by等不能设置, 否则会报异常

```python
state.update(data: dict[str, ValueType | Statement<Select/Aggregated>]) -> int
```

update参数`key` aka. `fields`支持:

* `col` 直接写field名称, `state.update({'id', 10})` `SET id = 10`
* `col+=` 给指定field做加法, `state.update({'id+=', 10})` `SET id = id + 10`
  * `col+=`, `col-=`, `col*=`, `col/=`, `col%=`
* `col=` 将后面`ValueType<string>`视为字面量, 直接传递至SQL
  * `{'col=': 'colA + colB'}` `SET col = colA + colB`

### Delete

delete语句和table和where有关, 其他选项如fields, group_by等不能设置, 否则会报异常

`WherePart`与前面Where格式相同

`soft`字段确定是否为软删除(使用update而并非delete语句), 如果是`None`则会以pydoo的初始设定为准

```python
# 更改pydoo soft_delete初始设置
pydoo.soft_delete_field = 'deleted' # 留空则不设置软删除字段
pydoo.soft_delete_type = 'tinyint' # 'tinyint', 'datetime', 'date', 'mask={int}'
# tinyint:
#    设置该字段为1视为已删除, 0视为未删除
# datetime:
#    设置该字段为CURRENT_DATETIME视为已删除, '0000-01-01 00:00:00'视为未删除
# date:
#    设置该字段为CURRENT_DATE视为已删除, '0000-01-01'视为未删除
# mask={int}:
#    mask=后加一个数字, 表示该字段从右往左第{int}位设置为1则视为删除, 否则视为未删除
```

```python
state.delete(cond: WherePart, soft: bool | None = None) -> int
```

强制使用软删除(避免全局设置污染)

```python
state.soft_delete(cond: WherePart, delete_field: str, delete_type: str = 'tinyint')
```

# Cache设定
