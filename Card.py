import random
from State import Color, Type

class CardManager:
	CardList = []
	@classmethod
	def init(cls):
		'''将一套标准的Uno卡组置于CardList中'''
		for i in [Color.Red, Color.Blue, Color.Green, Color.Yellow]:
			UnoTorsion(i)
			UnoNextPersonAdds(2, i)
			UnoToggleColor()
			UnoTorsion(i)
			UnoToggleColor()
			UnoNextPersonAdds(2, i)
			UnoForbidNextPerson(i)
			UnoNumberCard(i, 0)
			UnoNextPersonAdds(4)
			for j in range(1, 10):
				UnoNumberCard(i, j)
				UnoNumberCard(i, j)
	@classmethod
	def Enroll(cls, Card):
		'''注册,将卡片加入牌堆'''
		CardManager.CardList.append(Card)
	@classmethod
	def Extend(cls, ecl:list):
		'''扩展,将多个卡片加入牌堆'''
		CardManager.CardList.extend(ecl)
	@classmethod
	def DrawYourHoleCards(self) -> 'UnoNumberCard':
		'''生成基牌'''
		while True:
			rc = random.choice(self.CardList)
			if isinstance(rc, UnoNumberCard):
				self.CardList.remove(rc)
				return rc
	@classmethod
	def RemoveAllCards(cls):
		'''清空牌组'''
		cls.CardList.clear()
	@classmethod
	def GetAllCards(cls):
		'''获取所有卡牌'''
		return cls.CardList
	@classmethod
	def RemoveCard(cls, remove_card):
		'''移除指定卡牌'''
		cls.CardList.remove(remove_card)
	@staticmethod
	def FindCardFromInput(cardlist, findType:Type, cardColor:Color, number=0):
		resCard = []
		for i in cardlist:
			if findType == Type.Number:
				if i.type == findType and i.number == number:
					resCard.append(i)
			else:
				if i.type == findType and i.color == cardColor:
					resCard.append(i)
		return resCard
	@staticmethod
	def RemoveCardFromInput(cardlist:list, removeType:Type, cardColor:Color, number=0):
		wcf = cardlist.copy()
		for i in wcf:
			if removeType == Type.Number:
				if i.type == removeType and i.number == number:
					cardlist.remove(i)
			else:
				if i.type == removeType and i.color == cardColor:
					cardlist.remove(i)
		return cardlist
class PlaceholderTags: # 色彩占位牌
	def __init__(self, color:Color):
		self.color = color
		self.type = Type.Occupancy

class Card: # 所有卡牌的基类
	def __init__(self, color: Color):
		super().__init__()
		self.color = color
		CardManager.Enroll(self)

class UnoNumberCard(Card):
	def __init__(self, color: Color, number:int):
		super().__init__(color)
		self.number = number
		self.type = Type.Number
	def GetNumber(self) -> int:
		return self.number
        
class UnoToggleColor(Card):
	def __init__(self):
		super().__init__(Color.Tool)
		self.type = Type.ToggleColor

class UnoTorsion(Card):
	def __init__(self, color):
		super().__init__(color)
		self.type = Type.Torsion

class UnoForbidNextPerson(Card):
	def __init__(self, color):
		super().__init__(color)
		self.type = Type.ForbidNextPerson

class UnoNextPersonAdds(Card):
	def __init__(self, Addend:int, color:Color=Color.Tool):
		super().__init__(Color.Tool)
		self.addend = Addend
		if self.addend == 2:
			self.type = Type.NextPersonAdds_2
			self.color = color
		elif self.addend == 4:
			self.type = Type.NextPersonAdds_4
	def GetAddend(self) -> int:
		return self.addend

class PlayedDecks: # 打出的牌将存在这里
	CardList = []
	@classmethod
	def Enroll(cls, c:Card):
		cls.CardList.append(c)
	@classmethod
	def GetAllCards(cls) -> list:
		return cls.CardList

class Player:
	def __init__(self, tag):
		self.tag = tag
		self.PlayerCardList:list[Card] = []
	def GetAllCards(self):
		'''获取所有手牌'''
		return self.PlayerCardList
	def GetTag(self):
		'''获取标签'''
		return self.tag
	def Enroll(self, Card):
		'''注册卡牌'''
		CardManager.RemoveCard(Card)
		self.PlayerCardList.append(Card)
	def Out(self, Card) -> Card:
		'''打出卡牌'''
		self.PlayerCardList.remove(Card)
		PlayedDecks.Enroll(Card)
		return Card
	def GetDesignateColorCards(self, color:Color):
		cards = []
		for i in self.PlayerCardList:
			if i.color == color:
				cards.append(i)
		return cards
	def GetDesignateNumberCards(self, number):
		'''获取指定颜色卡牌'''
		cards = []
		for i in self.PlayerCardList:
			if isinstance(i, UnoNumberCard):
				if i.number == number:
					cards.append(i)
		return cards
	def DrawCards(self, quantity:int) -> list[Card]:
		'''抽牌'''
		DrawList = []
		for i in range(quantity):
			DrawList.append(random.choice(CardManager.GetAllCards()))
			CardManager.RemoveCard(DrawList[i])
		for i in DrawList:
			self.PlayerCardList.append(i)
		return DrawList
	def StatisticalColor(self) -> Color:
		'''统计玩家所持颜色'''
		colorCount = {Color.Red: 0, Color.Blue: 0, Color.Green: 0, Color.Yellow: 0}
		for i in self.PlayerCardList:
			if i.color != Color.Tool:
				colorCount[i.color] += 1
		for i, v in colorCount.items():
			if v == max(colorCount.values()):
				return i
	def RemoveAllCards(self):
		self.PlayerCardList = []

class GameState:
    CurrentColor = None
    PreviousCard = None # 上一张卡牌
    IncreaseStep = 1
    QuestionColor = None # 质疑时用的颜色
    GameProceeds = True
    Winner:Player = None
    StartTime = 0
    EndTime = 0
    IsHaveThinkTime = False


class PlayerGroup:
	def __init__(self, size, player_name='Player'):
		self.PlayerList = []
		self.size = size
		self.PlayerName = player_name
		for i in range(size):
			if i == 0:
				play = Player(self.PlayerName)
			else:
				play = Player(f'AI-{i}')
			for j in range(7):
				play.Enroll(random.choice(CardManager.GetAllCards()))
			self.PlayerList.append(play)
		self.index = 0
	def AddPlayer(self, tag):
		player = Player(tag)
		for i in range(7):
			player.Enroll(random.choice(CardManager.GetAllCards()))
		self.PlayerList.append(player)
	def GetNextPlayer(self) -> Player:
		self.index = (self.index + GameState.IncreaseStep) % self.size
		return self.PlayerList[self.index]
	def GetNextPlayerObject(self) -> Player:
		i = self.index
		return self.PlayerList[(i + GameState.IncreaseStep) % self.size]
	def GetCurrentPlayer(self) -> Player:
		return self.PlayerList[self.index]
	def GetAllPlayers(self) -> list[Player]:
		return self.PlayerList
	def GetPreviousPlayerObject(self) -> Player:
		i = self.index
		return self.PlayerList[(i - GameState.IncreaseStep * -1) % self.size]
	def GetPlayerName(self):
		return self.PlayerName