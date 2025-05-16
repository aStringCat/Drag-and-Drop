# Drag and Drop and Judge

本项目为方便测评机而开发的跨设备文件传输工具

### 使用说明

!请确保你的设备中有 node 环境，并且能够支持项目依赖
node 下载链接：[node.js](https://nodejs.org/en)

第一次使用时，务必输入 npm install 自动下载依赖

开启一个终端，进入项目的目录，输入`node server.js`。

再开启一个终端，进入项目的目录，输入`npm run dev`

修改文件保存位置可以通过修改 server.js 中的 UPLOADS_DIR 的值实现

目前文件无大小限制，但你可以通过修改 server.js 中的 upload 函数添加文件限制

测评机样例可见 judge.py

> [!TIP]
>
> 当然，你可以仅仅用来传输文件文件文件 🥹
