1. 查看mysql打开表
```
mysql> show status like '%open%';
+--------------------------+----------+
| Variable_name            | Value    |
+--------------------------+----------+
| Com_ha_open              | 0        |
| Com_show_open_tables     | 6        |
| Open_files               | 982      |
| Open_streams             | 0        |
| Open_table_definitions   | 329      |
| Open_tables              | 716      |
| Opened_files             | 40932494 |
| Opened_table_definitions | 4        |
| Opened_tables            | 8        |
| Slave_open_temp_tables   | 0        |
+--------------------------+----------+
show open tables from DB;
```
- load data infile
```
show variables like 'local_infile';
set global local_infile = 'ON'; 或设置local-infle = 1
```
- show processlist
```
select * from information_schema.processlist
```