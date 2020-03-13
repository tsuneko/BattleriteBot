buttonsLookup = {
    "Left": "\U00002b05", #u"2b05",
    "Right":"\U000027A1", #"➡",
    "Up": "\U00002B06", #"⬆",
    "Down": "\U00002B07", #"⬇",
    "Confirm": "\U00002705", #"✅",
    "Decline": "\U0000274C", #"❌"
}
for i in range(26):
    buttonsLookup[chr(ord("A") + i)] = chr(int("0x0001" + str(hex(int("0xf1e6", 16) + i))[2:],16))
for i in range(10):
    buttonsLookup[chr(ord("0") + i)] = chr(ord("0") + i) + "\U000020E3"

emojiLookup = {}
for button in buttonsLookup:
    emojiLookup[buttonsLookup[button]] = button

class Message:
    def __init__(self, users = [], buttons = [], prefix = "```\n", suffix = "\n```"):
        self.users = users
        self.buttons = buttons
        self.prefix = prefix
        self.suffix = suffix
        self.pages = []
        self.page = 0
        self.alive = True
        self.status = ""
        self.refresh = True
    def to_emoji(self, button):
        return buttonsLookup[button]
    def to_button(self, emoji):
        return emojiLookup[emoji]
    def is_alive(self):
        return self.alive
    def get_status(self):
        return self.status
    def set_msg(self, msg):
        self.msg = msg
        self.id = self.msg.id
    def get_msg(self):
        return self.msg
    def get_id(self):
        return self.id
    def set_refresh(self):
        self.refresh = False
    def needs_refresh(self):
        return self.refresh
    def add_page(self, page):
        self.pages.append(self.prefix + page + self.suffix)
    def remove_page(self, page_index):
        if len(self.pages) > 1:
            self.pages.remove(page_index)
            if self.page > len(self.pages) - 1:
                self.page -= 1
    def set_page(self, page, page_index):
        if page_index == len(self.pages):
            self.pages.append(page)
        elif page_index >= 0 and page_index < len(self.pages):
            self.pages[page_index] = page
    def add_navigation(self):
        if len(self.pages) >= 5:
            self.buttons.append("Up")
        if len(self.pages) > 1:
            self.buttons.append("Left")
            self.buttons.append("Right")
        if len(self.pages) >= 5:
            self.buttons.append("Down")
    def next_page(self):
        if self.page < len(self.pages) - 1:
            self.page += 1
    def prev_page(self):
        if self.page > 0:
            self.page -= 1
    def first_page(self):
        self.page = 0
    def last_page(self):
        self.page = len(self.pages) - 1
    def goto_page(self, page):
        if page >= 0 and page < len(self.pages) - 1:
            self.page = page
    def emoji_pressed(self, emoji, user_id = None):
        button = emojiLookup[emoji]
        if button == "Up":
            self.first_page()
            return True
        elif button == "Down":
            self.last_page()
            return True
        elif button == "Left":
            self.prev_page()
            return True
        elif button == "Right":
            self.next_page()
            return True
    def get_content(self):
        return self.pages[self.page]
    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)
    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)
    def set_users(self, users):
        self.users = users
    def get_users(self):
        return self.users
    def add_button(self, button):
        if button not in self.buttons:
            self.buttons.append(button)
        self.refresh = True
    def remove_button(self, button):
        if button in self.buttons:
            self.buttons.remove(button)
        self.refresh = True
    def set_buttons(self, buttons):
        self.buttons = buttons
        self.refresh = True
    def clear_buttons(self):
        self.buttons = []
        self.refresh = True
    def get_buttons(self):
        return self.buttons
    def get_reactions(self):
        reactions = []
        for button in self.buttons:
            if button in buttonsLookup:
                reactions.append(buttonsLookup[button])
        return reactions
    def __str__(self):
        return "to-do"
            
