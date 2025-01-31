import asyncio
import json
import threading
import datos
import os
from rich.console import Console
from rich.panel import Panel
from app import startapp
from fbchat_muqit import (
  Client,
  Message,
  ThreadType, ThreadLocation,
  State,
  FBchatException, FBchatFacebookError
)
from handler import (
  loadConfig,
  loadEvents,
  loadCommands,
  handleMessage,
  handleEvent
)

config = json.load(open('config.json', 'r'))
bot_running = False

class Greeg(Client):
  def BOT(self, data):
    self.commands = loadCommands(data['prefix'], log=self.weblog) # dict
    self.events = loadEvents(log=self.weblog) # list
    self.prefix = data['prefix']
    self.name = data['botName']
    self.owner = data['owner']
    self.admin = data['admin']
    # exception
    self.FBchatException = FBchatException
    self.FBchatFacebookError = FBchatFacebookError
    # models
    self.ThreadType = ThreadType
    self.ThreadLocation = ThreadLocation
    # console
    self.console = Console()
    self.panel = Panel
    # clayent sayd
    self.colorPanel = {
      "error": {"#8E1616", "#D84040"},
      "success": {"#21BF73", "#4AA96C"}
    }
  async def onListening(self):
    print("\033[32m[BOT] \033[0mListening...")
    await self._botEvent('type:listening', isOnline=True)
    self.logMessage("Listening...", "BOT", "green")
    print()
  
  """CUSTOM METHOD"""
  def error(self, message, title="ERROR"):
    error = Panel(message, title=title, border_style='red')
    Console().print(error)
  
  def logInfo(self, message, title="INFO", border="blue"):
    info = Panel(message, title=title, border_style=border)
    Console().print(info)
  
  async def _botEvent(self, event, **data):
    asyncio.create_task(handleEvent(self, event.lower(), **data))
  
  async def _messaging(self,event, **kwargs):
    if kwargs['author_id'] != self.uid:
      await self._botEvent(event, **kwargs)
      asyncio.create_task(handleMessage(self, **kwargs))
  
  def reload_modules(self):
    self.logInfo("Reloading modules...", title="Modules", border="yellow")
    self.commands = loadCommands(self.prefix, isReload=True)
    self.events = loadEvents(isReload=True)
    self.logInfo("Modules has been reloaded", title="Modules", border="yellow")
  
  def weblog(self, _data):
    datos.logs.append(_data)
    datos.socket.emit('log',_data)
  def logMessage(self, message, label=None, color="#4477CE"):
    self.weblog({
      "message": str(message),
      "label": {"text":label,"color": color}
    })
  def weblog_error(self, message, lable="ERROR"):
    self.weblog({
      "type": "info",
      "body": str(message),
      "border": self.colors['error'][1],
      "label": {
        "text": str(label),
        "color": self.colors['error'][0],
        "icon": "fa-solid fa-circle-exclamation"
      }
    })
  
  """MESSAGE EVENTS"""
  async def onReply(self, **kwargs):
    await self._messaging("type:reply",**kwargs)
  async def onMessage(self, **kwargs):
    await self._messaging("type:message", **kwargs)
  
  """OTHER EVENTS"""
  async def onPeopleAdded(self, **data):
    await self._botEvent("type:peopleAdded",thread_type=ThreadType.GROUP, **data)
  async def onPersonRemoved(self, **data):
    # somebody removes a person from a group thread.
    await self._botEvent("type:personRemoved",thread_type=ThreadType.GROUP, **data)
  async def onPendingMessage(self, **data):
    # somebody that isn’t connected with you on either Facebook or Messenger sends a message. After that, you need to use fetchThreadList to actually read the message.
    await self._botEvent("type:pendingMessage", **data)
  async def onColorChange(self, **data):
    # somebody changes a thread’s color.
    await self._botEvent("type:colorChange", **data)
  async def onEmojiChange(self, **data):
    # somebody changes a thread’s emoji.
    await self._botEvent("type:emojiChange", **data)
  async def onTitleChange(self, **data):
    # and somebody changes a thread’s title.
    await self._botEvent("type:titleChange", **data)
  async def onImageChange(self, **data):
    # somebody changes a thread’s image.
    await self._botEvent("type:imageChange", **data)
  async def onNicknameChange(self, **data):
    # somebody changes a nickname.
    await self._botEvent("type:nicknameChange", **data)
  async def onAdminAdded(self, **data):
    # somebody adds an admin to a group.
    await self._botEvent("type:adminAdded", **data)
  async def onAdminRemoved(self, **data):
    # somebody is removed as an admin in a group.
    await self._botEvent("type:adminRemoved", **data)
  async def onMessageUnsent(self, **data):
    # someone unsends (deletes for everyone) a message.
    await self._botEvent("type:messageUnsent", **data)
  

async def main():
  global bot_data
  cookies_path = "fbstate.json"
  bot = await Greeg.startSession(cookies_path)
  if await bot.isLoggedIn():
    fetch_bot = await bot.fetchUserInfo(bot.uid)
    bot_info = fetch_bot[bot.uid]
    kol = await loadConfig(bot_info.name)
    bot.BOT(kol)
    datos.BOT = {
      "uid": bot.uid,
      "name": bot.name,
      "prefix": bot.prefix or 'No prefix',
      "owner": bot.owner,
      "admins": ', '.join(bot.admin),
      "events": len(bot.events),
      "commands": len(bot.commands)
    }
    print(f"\033[32m[BOT] \033[0m{bot_info.name} is now logged in")
    bot.logMessage(f"{bot_info.name} is now logged in", "BOT", "green")
  try:
    await bot.listen()
  except FBchatException as g:
    stopbot() # <--
    bot.logMessage(f"{g}", "ERROR", "red")
    bot.error("{}".format(g), title="FBchatException")
  except FBchatFacebookError as g:
    stopbot() # <--
    bot.logMessage(f"{g}", "ERROR", "red")
    bot.error("{}".format(g), title="FBchatFacebookError")
  except Exception as e:
    stopbot() # <--
    bot.error(f"An error occured while trying to login, please check your bot account or get a new fbstate.\n\n{e}", title="Exception")
    bot.logMessage(f"An error occured while trying to login, please check your bot account or get a new fbstate.\n\n{e}", "BOT", "red")

def stopbot():
  global bot_running
  datos.BOT = {}
  if bot_running:
    bot_running = False
def restartbot():
  stopbot()
  th = threading.Thread(target=startbot)
  th.start()
def startbot():
  global bot_running
  bot_running = True
  asyncio.run(main())

if __name__ == '__main__':
  socket, app = startapp(restartbot)
  PORT = os.getenv('PORT', 5000)
  
  threading.Thread(target=startbot).start()
  
  socket.run(
    app,
    host='0.0.0.0',
    port=PORT,
    debug=False,
    allow_unsafe_werkzeug=True
  )
  #app.run(debug=True, host='0.0.0.0', port=PORT)