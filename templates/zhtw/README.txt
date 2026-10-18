v7.5補上SaltyNX排除清單及修補選單漏譯。NRO與v7.4相同，translation.bin已更新。若由較舊版本升級，請同時覆蓋兩個檔案。已通過本機測試，尚待實機確認。

﻿DBI 912 非官方翻譯 v7.4 — 預設繁體中文

修正實際的 MTP 多行訊息：[儲存空間名稱]\nСоздание объекта: 路徑。原生呼叫追蹤重現 v7.3 實機遇到的漏譯；v7.4 通過本地原生、多行及截圖檢查。v7.4 未在 Switch 實機測試。英文 v7.2 實機確認僅作歷史參考；此版不保證所有俄文訊息均已翻譯。
v7.4 的 NRO 與 v7.3 不同，安裝或更新時請同時替換/switch/DBI/DBI.nro 與 translation.bin；可保留 dbi.config。


安裝：完全退出DBI，將switch資料夾複製至SD卡根目錄，
同時替換/switch/DBI/DBI.nro與translation.bin，再重新啟動DBI。
已有自訂設定時，可保留自己的dbi.config。

包含存檔與活動紀錄分頁、統計欄名、安裝及清理訊息、更新提示、
MiB/s速度單位修正，保留中文空格修正與「DBI記錄」名稱。
六種語言共用同一個NRO。英文v7.2已由使用者確認Switch實機可用；
六種語言的翻譯表均通過本地檢查，仍可能有未涵蓋的俄文訊息。

合併包預設英文：將translations內所需語言檔複製至/switch/DBI/，
改名為translation.bin，完全退出DBI後重新啟動。
en英文；zhtw繁中；zhcn簡中；jp日文；fr法文；es西班牙文。

內建官方更新可能覆蓋修補版NRO，更新後請重新覆蓋本包NRO與BIN。
來源與授權聲明見licenses資料夾。
