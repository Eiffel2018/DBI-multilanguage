DBI 912 unofficial translation v7.7 — 默认简体中文

补齐编辑器“有尚未保存的更改”第一行，并翻译安装选项“修补元数据版本”。六种语言同步更新。NRO与v7.6完全相同；从v7.6升级只需替换translation.bin并重启DBI，更旧版本请同时替换两个文件。用户已确认v7.6可还原备份；新增文字通过本机原生绘制测试，仍待Switch界面确认。

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
