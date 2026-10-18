v7.5补上SaltyNX排除列表及补丁菜单漏译。NRO与v7.4相同，translation.bin已更新。若从更旧版本升级，请同时覆盖两个文件。已通过本机测试，尚待实机确认。

﻿DBI 912 非官方翻译 v7.4 — 默认简体中文

修复实际的 MTP 多行消息：[存储名称]\nСоздание объекта: 路径。原生调用追踪重现 v7.3 实机遇到的漏译；v7.4 通过本地原生、多行和截图检查。v7.4 未在 Switch 实机测试。英文 v7.2 实机确认仅作历史参考；此版不保证所有俄文消息均已翻译。
v7.4 的 NRO 与 v7.3 不同，安装或更新时请同时替换/switch/DBI/DBI.nro 和 translation.bin；可保留 dbi.config。


安装：完全退出DBI，将switch文件夹复制到SD卡根目录，
同时替换/switch/DBI/DBI.nro和translation.bin，再重新启动DBI。
已有自定义设置时，可以保留自己的dbi.config。

包含存档和活动记录分页、统计栏名、安装及清理信息、更新提示、
MiB/s速度单位修正，保留中文空格修正和「DBI记录」名称。
六种语言使用同一个NRO。英文v7.2已由用户确认Switch实机可用；
六种语言的翻译表均通过本地检查，仍可能有未覆盖的俄文信息。

合并包默认英文：将translations中所需语言文件复制到/switch/DBI/，
重命名为translation.bin，完全退出DBI后重新启动。
en英文；zhtw繁中；zhcn简中；jp日文；fr法文；es西班牙文。

内置官方更新可能覆盖修补版NRO，更新后请重新覆盖本包NRO和BIN。
来源及授权声明见licenses文件夹。
