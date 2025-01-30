from database import Users, User
from util import text_formatter, getName
import os

async def get_name(fetchName, uid):
  try:
    users = Users()
    userX = users.get(uid)
    if userX:
      if userX != 'Facebook User':
        return userX.get('name')
    else:
      nameX = getName(uid)
      if nameX != 'Facebook User':
        users.add(uid, nameX)
        return nameX
      fetch = await fetchName(uid)
      tao = fetch.get(uid)
      name = tao.name
      users.add(uid, name)
      return name
  except Exception as e:
    print(e)
    return "Facebook User"

class MessageData:
  def __init__(self, **data):
    self.bot = data.get('client')
    
    self.cmd = data.get('cmd')
    self.args = data.get('args')
    
    self.mid = data.get('mid')
    self.author_id = data.get('author_id')
    self.author_name = data.get('author_name')
    self.message = data.get('message')
    self.message_object = data.get('message_object')
    self.thread_id = data.get('thread_id')
    self.thread_type = data.get('thread_type')
    self.reply = None
    
    self.line = "━━━━━━━━━━━━━━"
    self.font = text_formatter
    
    if self.message_object.replied_to:
      self.reply = self.message_object.replied_to
  async def getName(self, uid):
    name = await get_name(self.bot.fetchUserInfo, uid)
    return name
  async def sendReply(self, message, auto_font=False, mentions=None):
    text = self.font(message) if auto_font else message
    return await self.bot.sendMessage(text, self.thread_id, self.thread_type, reply_to_id=self.mid, mentions=mentions)

async def handleMessage(bot, **kwargs):
  try:
    thread_id = kwargs.get('thread_id')
    thread_type = kwargs.get('thread_type')
    message = kwargs.get('message')
    author_id = kwargs.get('author_id')
    
    _split = message.split(' ',1) if message else ['']
    cmd, args = _split if len(_split) != 1 else [_split[0],'']
    cnp = cmd if bot.prefix == "" or not cmd.startswith(bot.prefix) else cmd[1:];cnp = cnp.lower()
    if cnp in bot.commands:
      function = bot.commands[cnp]
      is_need_prefix = function.get('usePrefix', True)
      is_admin_only = function.get('adminOnly', False)
      if bot.prefix != '' and is_need_prefix and not cmd.startswith(bot.prefix):
        return await bot.sendMessage(text_formatter(":mono[This command require to use prefix]"), thread_id, thread_type)
      elif is_admin_only and str(author_id) not in bot.admin:
        return await bot.sendMessage(text_formatter(":mono[You dont have permission to use this command.]"), thread_id, thread_type)
      else:
        sender = await get_name(bot.fetchUserInfo, author_id)
        message_data = MessageData(
          cmd = cnp,
          args = args,
          client = bot,
          author_name = sender,
          **kwargs
        )
        mtg = f"[blue]Sender   : [/blue] {sender}\n"
        mtg += f"[blue]UID      : [/blue] {author_id}\n"
        mtg += f"[blue]Command  : [/blue] [yellow]{cnp}[/yellow]"
        bot.logInfo(mtg, title=f"{thread_id}")
        bot.weblog({
          "type": 'user',
          "name": sender,
          "uid": author_id,
          "threadId": thread_id,
          "command": cnp
        })
        return await function['def'](bot, message_data)
    else:
      if bot.prefix != "" and message.startswith(bot.prefix):
        await bot.sendMessage(f"Command '{cnp}' does not exist, type '{bot.prefix}help' to view commands", thread_id, thread_type, reply_to_id=kwargs['mid'])
  except bot.FBchatFacebookError as err:
    bot.weblog(f"{err}", 'FBchatFacebookError', 'red')
    bot.error(f"{err}", 'FBchatFacebookError')
  except bot.FBchatException as err:
    bot.weblog(f"{err}", 'FBchatException', 'red')
    bot.error(f"{err}", 'FBchatException')
  except Exception as err:
    bot.weblog(f"{err}", 'Exception', 'red')
    bot.error(f"{err}", 'Exception')