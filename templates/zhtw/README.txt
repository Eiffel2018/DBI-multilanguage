DBI 912 unofficial translation v7.6 — 預設繁體中文

修正翻譯導致存檔備份無法還原的問題，並補上文字編輯器「未儲存變更」確認視窗。內部INI資料保留原文，畫面標籤維持翻譯。請同時替換DBI.nro與translation.bin，完全退出後重新啟動。已通過本機原生測試，實際還原及確認視窗仍待Switch實機確認。

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
