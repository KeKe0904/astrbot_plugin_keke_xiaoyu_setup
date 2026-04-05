# 小羽AstrBot部署帮助插件

## 插件简介

小羽AstrBot部署帮助插件是一个智能的AstrBot和NapCat部署辅助插件，具备智能监听、命令触发、记忆学习和智能清理功能。

### 制作人

落梦陳

### 核心功能

- **全平台支持**：支持所有 AstrBot 兼容的平台
- **智能监听**：自动识别并回复AstrBot或NapCat相关问题
- **命令触发**：支持使用 `/astr` 命令手动触发搜索
- **记忆学习**：记录历史问题和答案，不断积累知识
- **智能清理**：自动管理记忆存储，保持系统高效运行

## 安装方法

1. 将插件文件夹 `astrbot_plugin_keke_xiaoyu_setup` 复制到 AstrBot 的 `data/plugins` 目录
2. 重启 AstrBot 或在 WebUI 中重载插件

## 使用方法

### 方法一：自动触发
当您在聊天中提及AstrBot或NapCat相关关键词时，插件会自动识别并回复相关解决方案。

### 方法二：手动触发
使用 `/astr` 命令后跟您的问题，例如：
```
/astr 如何安装 AstrBot
/astr 部署时出现错误怎么办
/astr 如何配置 NapCat
```

## 支持的平台

- aiocqhttp
- qq_official
- telegram
- wecom
- lark
- dingtalk
- discord
- slack
- kook
- vocechat
- satori
- misskey
- line

## 版本历史

详细版本更新记录请查看 [CHANGELOG.md](CHANGELOG.md)

## 相关链接

- [AstrBot 官方仓库](https://github.com/AstrBotDevs/AstrBot)
- [AstrBot 官方文档](https://docs.astrbot.app/)
- [NapCatQQ 官方文档](https://napcat.napneko.icu/)

