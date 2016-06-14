
import pyxhook, pyautogui, sys, subprocess, json

class Pahk:
	def __init__(self, commandsFile="./default_commands.json", configFile="./default_configs.json"):
		self.setConfigs(configFile)
		self.setCommands(commandsFile)
		self.stopEventListener = False
		self.keysPressed = ""
		self.keywordObject = {
				"hotStrings" : self.hotStrings,
				"hotKeys" : self.hotKeys
			}
		self.initHook()

	def OnKeyPress(self, event):
		print(event)
		print(self.stopEventListener)
		if self.isLocked():
			return
		if self.modifiers.has_key(event.Key):
			self.modifiers[event.Key]['active'] = 1
			return
		self.updateKeysPressed(event, {})
		self.handleHotStrings()
		self.handleHotKeys(event)
		if event.Key == 'Escape':
			self.hook.cancel()
			sys.exit("Exited safely")

	def OnKeyRelease(self, event):
		if self.isLocked():
			return
		if self.modifiers.has_key(event.Key):
			self.modifiers[event.Key]['active'] = 0

	def executeCommand(self, options):
		p = subprocess.Popen(options.get('cmd'), stdout=subprocess.PIPE)
		for line in iter(p.stdout.readline, b''):
			#print(line.rstrip())
			pass

	def updateKeysPressed(self, event, options):
		# If on keyword begins with the received letter
		foundMatchAtFirstChar = False
		# If on keyword has a char that corresponds with the received letter at the length of the keysPressed
		foundMatchAtCurrentChar = False
		# If a matching hotkey is found
		foundMatchingHotKey = False
		for keywordObject in self.keywordObject:
			for keywords in self.keywordObject[keywordObject]:
				if keywordObject == "hotStrings": 
					if len(keywords) > len(self.keysPressed):
						if len(keywords) > 0 and keywords[0] == chr(event.Ascii):
							foundMatchAtFirstChar = True
						if keywords[len(self.keysPressed)] == chr(event.Ascii):
							foundMatchAtCurrentChar = True
				if keywordObject == "hotKeys":
					if keywords == event.Key:
						foundMatchingHotKey = True
		if foundMatchAtCurrentChar:
			self.keysPressed += chr(event.Ascii)
		else:
			self.resetKeysPressed()
			if foundMatchAtFirstChar:
				self.keysPressed += chr(event.Ascii)
		return {
			"foundMatchAtFirstChar" : foundMatchAtFirstChar,
			"foundMatchAtCurrentChar" : foundMatchAtCurrentChar,
			"foundMatchingHotKey" : foundMatchingHotKey
		}

	def handleHotStrings(self):
		print("\n - " + self.keysPressed + " - ")
		hotString = self.hotStrings.get(self.keysPressed)
		if hotString:
			self.lock()
			self.resetKeysPressed("", True)
			self.handleActions(hotString["actions"])
			self.unlock()

	def handleHotKeys(self, event):
		hotKey = self.hotKeys.get(event.Key)
		if hotKey:
			self.lock()
			self.handleActions(hotKey["actions"])
			self.unlock()

	def handleActions(self, actions):
		for action in actions : 
			if action["type"] == "cmd":
				self.executeCommand({
					'cmd' : action["args"]
				})
			elif action["type"] == "pyautogui":
				getattr(pyautogui, action["function"])(*action["params"])

	def resetKeysPressed(self, keysPressed="", cancelKeyStrokes=False):
		if cancelKeyStrokes:
			backspaces = []
			for x in range(0, len(self.keysPressed)):
				backspaces.append("backspace")
			pyautogui.typewrite(backspaces)
		self.keysPressed = keysPressed

	def lock(self):
		self.stopEventListener = True

	def unlock(self):
		self.stopEventListener = False

	def isLocked(self):
		return self.stopEventListener

	def initHook(self):
		self.hook = pyxhook.HookManager()
		self.hook.KeyDown = self.OnKeyPress
		self.hook.KeyUp = self.OnKeyRelease
		self.hook.HookKeyboard()
		self.hook.start()

	def setConfigs(self, jsonFile):
		with open(jsonFile) as file:
			configs = json.load(file)
			self.modifiers = configs.get('modifiers')
			self.forceExitKeys = configs.get('forceExitKeys')

	def setCommands(self, jsonFile):
		with open(jsonFile) as file:
			commands = json.load(file)
			self.hotKeys = commands.get('hotKeys')
			self.hotStrings = commands.get('hotStrings')

def main():
	subprocess.call(["xhost", "+"])
	if len(sys.argv) == 2:
		print("Using '" + sys.argv[1] + "' command file.")
		pahk = Pahk(sys.argv[1]);
	elif len(sys.argv) == 3:
		print("Using '" + sys.argv[1] + "' as command file.")
		print("Using '" + sys.argv[2] + "' as config file.")
		pahk = Pahk(sys.argv[1], sys.argv[2]);
	else:
		print("Using './default_commands.json' as command file.")
		print("Using './default_configs.json' as config file.")
		pahk = Pahk();

if __name__ == "__main__":
	main()

