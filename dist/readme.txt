1.通过Windows托盘打开web页面，退出SimpleWSS；
2.Websocket客户端通过ws://<主机IP>:5787/<客户端ID>进行连接，例如ws://192.168.9.222:5787/bert-test；
3.客户端ID为客户端别名，用于SimpleWSS向指定客户端发送命令，可以为空，为空时使用客户端IP。