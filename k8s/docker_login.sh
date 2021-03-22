#!/bin/expect
set timeout 30 # 设置超时时间为30s
spawn docker login 192.168.163.114:5000 # spawn是expect的语句，执行命令前都要加这句
expect "Username:" # 交互获取返回Username:时，发送jack
send "jack\r"
expect "Password:"
send "123456\r"
expect eof # 表示结束expect
interact # 执行完命令后，控制权交互控制台，此时再有交互，expect将不会进行交互,如果没有这句，在需要交互的ssh命令执行完毕后将会退出远程，而不是继续保持在远程