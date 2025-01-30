import os
import importlib
from rich.console import Console
from rich.panel import Panel

events = []

def loadEvents(isReload=False, log=None):
  global events
  if events:
    if isReload:
      events = []
    else:
      return events
  
  def Log(message, isError=False):
    if log:
      log({
        "message": message,
        "label": {
          "text": "EVENTS",
          "color": "#0A5EB0" if not isError else "red"
        }
      })
  console = Console()
  files = list(filter(lambda file: file.endswith('.py') and
  file!='__init__.py',os.listdir('./events')))
  message = ""
  #log("---------------------------------------------"*2)
  for file in files:
    filepath = f"events.{os.path.splitext(file)[0]}"
    module = importlib.import_module(filepath)
    importlib.reload(module)
    config = getattr(module, 'config', None)
    if config:
      config['fileName'] = file
      event_type = config.get('event')
      function = config.get('def')
      if not event_type:
        Log(f"{file} - Missing event type", True)
        message += f"[bold red]ERROR[/bold red] [red]{file} [white]- Missing event type\n"
      elif not function:
        Log(f"{file} - Missing event function", True)
        message += f"[bold red]ERROR[/bold red] [red]{file} [white]- Missing event function\n"
      else:
        if not event_type.startswith('type:'):
          Log(f"{file} - Invalid event type", True)
          message += f"[bold red]ERROR[/bold red] [red]{file} [white]- Invalid event type\n"
        else:
          config["event"] = config["event"].lower()
          events.append(config)
          Log(f"Loaded <span style='color:#FEEE91'>{file}</span>")
          message += f"[blue]EVENT[/blue] Loaded [yellow]{file}[/yellow]\n"
  panel = Panel(message[:-1], title="EVENTS", border_style="royal_blue1")
  console.print(panel)
  return events