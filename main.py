from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_keke_xiaoyu_setup", "keke_xiaoyu", "小羽ASTRBOT部署帮助插件", "1.1.0")
class KekeXiaoyuSetupPlugin(Star):
    """小羽ASTRBOT部署帮助插件
    
    一个智能的AstrBot和NapCat部署辅助工具，能够自动识别相关问题并提供解决方案。
    
    核心功能：
    - 智能监听：自动识别并回复AstrBot或NapCat相关问题
    - 命令触发：通过 /astr 命令快速获取部署帮助
    - 记忆学习：记录历史问题和答案，不断积累知识
    - 智能清理：自动管理记忆存储，保持系统高效运行
    """
    def __init__(self, context: Context):
        """初始化插件
        
        Args:
            context: 插件上下文对象
        """
        super().__init__(context)
        # 记忆存储的键名
        self.memory_key = "keke_xiaoyu_memory"
        # 记忆清理阈值设置
        self.memory_max_count = 1000  # 最大记忆数量
        self.memory_max_days = 7  # 最大记忆天数

    async def initialize(self):
        """初始化插件"""
        logger.info("小羽ASTRBOT部署帮助插件初始化完成")

    # 尝试添加自动监听功能，如果filter.message不存在则跳过
    @property
    def has_auto_listen(self):
        """检查是否支持自动监听功能
        
        Returns:
            bool: 是否支持自动监听
        """
        return hasattr(filter, 'message')

    # 自动监听方法（仅当filter.message存在时才会被使用）
    if hasattr(filter, 'message'):
        @filter.message
        async def on_message(self, event: AstrMessageEvent):
            """自动识别并回复AstrBot或NapCat相关问题
            
            Args:
                event: 消息事件对象
                
            Returns:
                None
            """
            try:
                message_str = event.message_str.strip()
                if not message_str:
                    return

                # 优化关键词检测，分为核心关键词和辅助关键词
                core_keywords = ["astrbot", "napcat"]
                helper_keywords = ["部署", "安装", "配置", "搭建", "启动", "运行", "错误", "问题", "无法", "怎么", "如何", "help", "install", "setup", "config", "deploy"]
                
                # 检测消息是否包含核心关键词或多个辅助关键词
                message_lower = message_str.lower()
                contains_core = any(k in message_lower for k in core_keywords)
                contains_helper = sum(1 for k in helper_keywords if k in message_lower)
                
                # 触发条件：包含核心关键词，或包含2个以上辅助关键词
                if contains_core or contains_helper >= 2:
                    logger.info(f"检测到相关问题: {message_str}")
                    # 使用异步任务处理，避免阻塞消息处理
                    import asyncio
                    asyncio.create_task(self._process_message(event, message_str))
            except Exception as e:
                logger.error(f"自动监听处理错误: {str(e)}")
    
    async def _process_message(self, event: AstrMessageEvent, message_str: str):
        """处理消息的异步方法
        
        Args:
            event: 消息事件对象
            message_str: 消息内容
            
        Returns:
            None
        """
        try:
            async for result in self.search_and_reply(event, message_str):
                pass
        except Exception as e:
            logger.error(f"处理消息时发生错误: {str(e)}")

    # 命令触发的处理
    @filter.command("astr")
    async def astr_command(self, event: AstrMessageEvent, args=None):
        """部署帮助命令"""

        if not args:
            yield event.plain_result("请输入部署问题，例如：/astr 如何安装 AstrBot")
            return
        
        # 确保args是一个列表
        if not isinstance(args, list):
            args = [args]
        
        query = " ".join(args)
        async for result in self.search_and_reply(event, query):
            yield result

    async def get_memory(self):
        """获取记忆存储
        
        Returns:
            dict: 包含记忆项的字典
        """
        return await self.get_kv_data(self.memory_key, {"items": []})

    async def add_memory(self, user_name, question, answer):
        """添加记忆
        
        Args:
            user_name: 用户名
            question: 问题
            answer: 答案
            
        Returns:
            None
        """
        import time
        memory = await self.get_memory()
        memory_item = {
            "user_name": user_name,
            "question": question,
            "answer": answer,
            "timestamp": int(time.time())
        }
        memory["items"].append(memory_item)
        await self.put_kv_data(self.memory_key, memory)
        await self.clean_memory()

    async def clean_memory(self):
        """智能清理记忆
        
        清理过期记忆和超出数量限制的记忆，保留更重要的记忆项
        
        Returns:
            None
        """
        import time
        memory = await self.get_memory()
        current_time = int(time.time())
        max_age = self.memory_max_days * 24 * 3600
        
        # 清理过期记忆
        memory["items"] = [item for item in memory["items"] if current_time - item["timestamp"] < max_age]
        
        # 如果仍然超出数量限制，进行智能清理
        if len(memory["items"]) > self.memory_max_count:
            # 按时间戳排序，保留最新的记忆项
            memory["items"].sort(key=lambda x: x["timestamp"], reverse=True)
            # 保留前memory_max_count个记忆项
            memory["items"] = memory["items"][:self.memory_max_count]
        
        await self.put_kv_data(self.memory_key, memory)
        logger.info(f"记忆清理完成，当前记忆数量: {len(memory['items'])}")

    async def search_memory(self, query):
        """搜索相关记忆
        
        Args:
            query: 搜索查询
            
        Returns:
            list: 相关记忆列表，最多返回3条
        """
        memory = await self.get_memory()
        relevant = []
        query_words = query.lower().split()
        
        # 计算每个记忆项与查询的相关性得分
        for item in memory["items"]:
            item_question = item["question"].lower()
            # 计算匹配的关键词数量
            match_count = sum(1 for word in query_words if word in item_question)
            # 计算匹配的关键词比例
            if item_question:
                match_ratio = match_count / len(query_words)
            else:
                match_ratio = 0
            
            # 只添加匹配度大于0的记忆项
            if match_ratio > 0:
                relevant.append((item, match_ratio))
        
        # 按相关性得分排序，然后按时间戳排序
        relevant.sort(key=lambda x: (x[1], x[0]["timestamp"]), reverse=True)
        
        # 提取排序后的记忆项
        sorted_memory = [item[0] for item in relevant]
        
        # 返回前3条最相关的记忆
        return sorted_memory[:3]

    async def search_and_reply(self, event: AstrMessageEvent, query: str):
        """处理并回复问题
        
        基于记忆功能回答用户的问题，学习并记录历史问题和答案
        
        Args:
            event: 消息事件对象
            query: 搜索查询
            
        Yields:
            MessageEventResult: 回复结果
        """
        try:
            # 搜索相关记忆
            relevant_memory = await self.search_memory(query)
            
            # 构建回复内容
            if relevant_memory:
                reply = f"根据您的问题，为您找到以下解决方案：\n\n"
                for i, item in enumerate(relevant_memory, 1):
                    reply += f"{i}. {item['user_name']} 曾经问：{item['question']}\n"
                    reply += f"   解决方案：{item['answer']}\n\n"
                reply += "如果这些信息不能解决您的问题，请尝试更详细地描述具体情况。"
            else:
                reply = "抱歉，我暂时没有相关问题的解决方案。请尝试更详细地描述您的问题，或者查看官方文档获取帮助。"
            
            # 添加当前问题到记忆（如果有相关记忆）
            if relevant_memory:
                try:
                    user_name = event.get_sender_name()
                except Exception:
                    user_name = "未知用户"
                # 使用第一个相关记忆的答案作为当前问题的答案
                answer = relevant_memory[0]['answer']
                await self.add_memory(user_name, query, answer)
            
            yield event.plain_result(reply)
            
        except Exception as e:
            logger.error(f"处理问题时发生错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            yield event.plain_result(f"处理问题时发生错误: {str(e)}")

    async def terminate(self):
        """停止插件
        
        插件销毁时调用的方法
        
        Returns:
            None
        """
        logger.info("小羽ASTRBOT部署帮助插件已停止")
