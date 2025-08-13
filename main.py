from math import ceil
import time
import Card
from State import Color, Type, ColorComparisonTable, CompareVocabulary
import colorama
import random

colorama.init(autoreset=True)

def ColorizedOutput(c: Card.Card | Color, pre_text=''):
    '''彩色化输出'''
    text = pre_text
    color = None
    mcc = None
    if isinstance(c, Color):
        mcc = c
    else:
        mcc = c.color
    match mcc:
        case Color.Red:
            color = colorama.Back.RED
            text += f'{color}红'
        case Color.Blue:
            color = colorama.Back.BLUE
            text += f'{color}蓝'
        case Color.Yellow:
            color = colorama.Back.YELLOW
            text += f'{color}黄'
        case Color.Green:
            color = colorama.Back.GREEN
            text += f'{color}绿'
        case Color.Tool:
            color = colorama.Back.LIGHTBLACK_EX
            text += f'{color}工具'
    if not isinstance(c, Color):
        if c.type == Type.Number:
            text += f"-{str(c.GetNumber())}"
        elif c.type == Type.Occupancy:
            text += f'{CompareVocabulary[c.type]}'
        else:
            text += f'-{CompareVocabulary[c.type]}'
    return text + colorama.Back.RESET

def ExpansionDecks(ReduceCards:int):
    '''检测牌堆是否有牌'''
    if len(Card.CardManager.GetAllCards()) - ReduceCards < 0:
        print(f"{colorama.Back.RED}牌堆的牌已摸尽,将弃牌堆重新洗牌加入牌堆")
        Card.CardManager.Extend(Card.PlayedDecks.GetAllCards())
        random.shuffle(Card.CardManager.CardList)
        Card.PlayedDecks.CardList = []

def PlayerPrint(p:Card.Player):
    '''打印玩家手牌'''
    index = 0
    time.sleep(0.1)
    print(f"上一张牌:{ColorizedOutput(Card.GameState.PreviousCard)}\t当前颜色:{ColorizedOutput(Card.GameState.CurrentColor)}")
    for i in p.GetAllCards():
        index += 1
        if index % 5 == 0:
            print()
        print(ColorizedOutput(i, f'[{index-1}]')+'\t', end="")
    print()

def CardEffectEffector(p:Card.PlayerGroup, c:Card.Card, L:Card.Card, mode=0):
    '''AI/玩家卡牌效果实现'''
    match c.type:
        case Type.Torsion:
            Card.GameState.IncreaseStep *= -1
            print("出牌顺序倒转")
        case Type.ForbidNextPerson:
            print(f"下一名玩家{p.GetNextPlayer().GetTag()}被禁止了")
        case Type.NextPersonAdds_2:
            P = p.GetCurrentPlayer()
            N = p.GetNextPlayer()
            ExpansionDecks(2)
            N.DrawCards(2)
            print(f"下一名玩家{N.GetTag()}被{P.GetTag()}+2了")
        case Type.NextPersonAdds_4:
            P = p.GetCurrentPlayer()
            N = p.GetNextPlayerObject()
            if mode == 0:
                Card.GameState.QuestionColor = L.color
                setColor = P.StatisticalColor()
            elif mode == 1:
                Card.GameState.QuestionColor = L.color
                PlayerPrint(p.GetCurrentPlayer())
                while True:
                    print(f"选择颜色:\n[0]{colorama.Back.RED}红色{colorama.Back.RESET}\t[1]{colorama.Back.GREEN}绿色{colorama.Back.RESET}\t[2]{colorama.Back.BLUE}蓝色{colorama.Back.RESET}\t[3]{colorama.Back.YELLOW}黄色")
                    cip = input()
                    match cip:
                        case '0':
                            setColor = Color.Red
                            break
                        case '1':
                            setColor = Color.Green
                            break
                        case '2':
                            setColor = Color.Blue
                            break
                        case '3':
                            setColor = Color.Yellow
                            break
                        
            Card.GameState.CurrentColor = setColor
            Card.GameState.PreviousCard = c
            print(f"玩家选择了{ColorComparisonTable[setColor]}")
            print(f"下一名玩家{N.GetTag()}被{P.GetTag()}+4了")
        case Type.ToggleColor:
            if mode == 0:
                MC = p.GetCurrentPlayer().StatisticalColor()
            elif mode == 1:
                PlayerPrint(p.GetCurrentPlayer())
                while True:
                    print(f"选择颜色:\n[0]{colorama.Back.RED}红色{colorama.Back.RESET}\t[1]{colorama.Back.GREEN}绿色{colorama.Back.RESET}\t[2]{colorama.Back.BLUE}蓝色{colorama.Back.RESET}\t[3]{colorama.Back.YELLOW}黄色")
                    c = input()
                    match c:
                        case '0':
                            MC = Color.Red
                            break
                        case '1':
                            MC = Color.Green
                            break
                        case '2':
                            MC = Color.Blue
                            break
                        case '3':
                            MC = Color.Yellow
                            break
            Card.GameState.CurrentColor = MC
            Card.GameState.PreviousCard = Card.PlaceholderTags(MC)
            print(f"玩家{p.GetCurrentPlayer().GetTag()}选择了{ColorComparisonTable[MC]}")
        

def CardComplianceChecking(checkCard:Card.Card):
    '''卡片合规性检测'''
    L = Card.GameState.PreviousCard
    if checkCard.color == L.color:
        return True
    if isinstance(checkCard, Card.UnoToggleColor):
        return True
    if isinstance(checkCard, Card.UnoNextPersonAdds):
        if checkCard.type == Type.NextPersonAdds_2:
            if checkCard.color == Card.GameState.CurrentColor:
                return True
            else:
                return False
        else:
            return True
    if isinstance(L, Card.UnoNumberCard):
        if isinstance(checkCard, Card.UnoNumberCard):
            if L.number == checkCard.number:
                return True
    return False

def AiCardDrawingLogic(p:Card.PlayerGroup):
    '''AI抽牌策略'''
    L = Card.GameState.PreviousCard
    P = p.GetCurrentPlayer()
    if len(P.GetDesignateColorCards(Color.Tool)) > 0:
        dc = random.choice(P.GetDesignateColorCards(Color.Tool))
        print(f"玩家{P.GetTag()}打出了{ColorizedOutput(dc)}")
        P.Out(dc)
        Card.GameState.PreviousCard = dc
        Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
        CardEffectEffector(p, Card.GameState.PreviousCard, L)
    else:
        ExpansionDecks(1)
        dc = P.DrawCards(1)
        if CardComplianceChecking(dc[0]):
            P.Out(dc[0])
            print(f"玩家{P.GetTag()}抽牌并打出{ColorizedOutput(dc[0])}")
            Card.GameState.PreviousCard = dc[0]
            Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
            CardEffectEffector(p, Card.GameState.PreviousCard, L)
        else:
            print(f"玩家{P.GetTag()}选择抽一张并跳过")

def AiPlus4Flow(p:Card.PlayerGroup):
    '''AI +4应对策略'''
    P = p.GetCurrentPlayer()
    rf = random.random()
    if len(P.GetAllCards()) > 7:
        rf -= 0.1
    else:
        rf += 0.1
    if rf >= 0.75:
        print(f"玩家{P.GetTag()}选择了质疑上个玩家未出完{ColorComparisonTable[Card.GameState.QuestionColor]}")
        if len(p.GetPreviousPlayerObject().GetDesignateColorCards(Card.GameState.QuestionColor)) > 0:
            print(f"玩家{P.GetTag()}质疑成功,玩家{p.GetPreviousPlayerObject().GetTag()}被+4了")
            Card.GameState.PreviousCard = Card.PlaceholderTags(Card.GameState.CurrentColor)
            ExpansionDecks(4)
            p.GetPreviousPlayerObject().DrawCards(4)
        else:
            print(f"玩家{P.GetTag()}质疑失败了,玩家{P.GetTag()}被+6了")
            Card.GameState.PreviousCard = Card.PlaceholderTags(Card.GameState.CurrentColor)
            ExpansionDecks(6)
            P.DrawCards(6)
    else:
        print(f"玩家{P.GetTag()}选择不质疑,接受+4")
        Card.GameState.PreviousCard = Card.PlaceholderTags(Card.GameState.CurrentColor)
        ExpansionDecks(4)
        P.DrawCards(4)
    Card.GameState.PreviousCard = Card.PlaceholderTags(Card.GameState.CurrentColor)

def AiPicksOutCardQueue(p:Card.PlayerGroup, L, C) -> list[Card.Card]:
    '''AI 出牌序列'''
    PreDeck = []
    P = p.GetCurrentPlayer()
    if C != Color.Tool:
        PreDeck.extend(P.GetDesignateColorCards(C))
    PreDeck.extend(P.GetDesignateColorCards(Color.Tool))
    if isinstance(L, Card.UnoNumberCard):
        PreDeck.extend(P.GetDesignateNumberCards(L.number))
        PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.Number, P.StatisticalColor(), L.number))
    if len(p.GetNextPlayerObject().GetAllCards()) <= len(P.GetAllCards()):
        PreDeck.extend(P.GetDesignateColorCards(Color.Tool))
        PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.NextPersonAdds_2, C))
        PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.NextPersonAdds_4, C))
        PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.Torsion, C))
    if len(p.GetNextPlayerObject().GetAllCards()) < len(p.GetPreviousPlayerObject().GetAllCards()):
        for i in range(2):
            PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.Torsion, Card.GameState.CurrentColor))
    if len(P.GetAllCards()) <= 3:
        PreDeck.extend(P.GetDesignateColorCards(Color.Tool))
        if isinstance(L, Card.UnoNumberCard):
            PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.Number, P.StatisticalColor(), L.number))
    if P.StatisticalColor() != C:
        for i in range(2):
            PreDeck.extend(Card.CardManager.FindCardFromInput(P.GetAllCards(), Type.ToggleColor, Color.Tool))
    if P.StatisticalColor() == C:
        PreDeck = Card.CardManager.RemoveCardFromInput(PreDeck, Type.ToggleColor, Color.Tool)
    return PreDeck

def AiThinks(p:Card.PlayerGroup):
    '''AI 出牌函数'''
    if Card.GameState.IsHaveThinkTime:
        time.sleep(random.randint(1, 2))
    else:
        time.sleep(0.5)
    L = Card.GameState.PreviousCard
    C = Card.GameState.CurrentColor
    P = p.GetCurrentPlayer()
    DiscardResult = None
    if L.color == Color.Tool:
        if L.type == Type.NextPersonAdds_4:
            AiPlus4Flow(p)
    else:
        PreDeck = AiPicksOutCardQueue(p, L, C)
        if PreDeck:
            DiscardResult = random.choice(PreDeck)
        else:
            AiCardDrawingLogic(p)
        if DiscardResult != None:
            print(f"玩家{P.GetTag()}打出了{ColorizedOutput(DiscardResult)}")
            P.Out(DiscardResult)
            Card.GameState.PreviousCard = DiscardResult
            Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
            CardEffectEffector(p, Card.GameState.PreviousCard, L)
    if len(p.GetCurrentPlayer().GetAllCards()) == 1:
        print(f"玩家{p.GetCurrentPlayer().GetTag()}喊出了{colorama.Back.RED}Uno!")
    elif len(p.GetCurrentPlayer().GetAllCards()) == 0:
        Card.GameState.Winner = p.GetCurrentPlayer()
        Card.GameState.GameProceeds = False
    print('='*15)

def PlayerActionFlow(p:Card.PlayerGroup):
    '''玩家 出牌函数'''
    WhetherItSAllLegal = False
    for i in p.GetCurrentPlayer().GetAllCards():
        if CardComplianceChecking(i):
            WhetherItSAllLegal = True
            break
    if Card.GameState.PreviousCard.color == Color.Tool:
        if Card.GameState.PreviousCard.type == Type.NextPersonAdds_4:
            print(f"是否质疑玩家{p.GetPreviousPlayerObject().GetTag()}手上的{ColorComparisonTable[Card.GameState.QuestionColor]}没出完(Y/N)")
            c = input()
            if c.upper() == 'N':
                print(f"你选择不质疑,接受玩家{p.GetPreviousPlayerObject().GetTag()}的+4")
                ExpansionDecks(4)
                p.GetCurrentPlayer().DrawCards(4)
            else:
                if len(p.GetPreviousPlayerObject().GetDesignateColorCards(Card.GameState.QuestionColor)) > 0:
                    print(f"质疑失败,你被玩家{p.GetPreviousPlayerObject().GetTag()}+6了")
                    ExpansionDecks(6)
                    p.GetCurrentPlayer().DrawCards(6)
                else:
                    print(f"质疑成功,玩家{p.GetPreviousPlayerObject().GetTag()}被+4了")
                    ExpansionDecks(4)
                    p.GetPreviousPlayerObject().DrawCards(4)
            Card.GameState.PreviousCard = Card.PlaceholderTags(Card.GameState.CurrentColor)
    elif WhetherItSAllLegal:
        PlayerPrint(p.GetCurrentPlayer())
        while True:
            try:
                command = input()
                OC = p.GetCurrentPlayer().GetAllCards()[int(command)]
                L = Card.GameState.PreviousCard
                if CardComplianceChecking(OC):
                    Card.GameState.PreviousCard = p.GetCurrentPlayer().Out(OC)
                    break
                else:
                    print(f"{colorama.Back.RED}不能打出!")
            except (IndexError, TypeError, ValueError):
                print(f"{colorama.Back.RED}非法输入!")
        Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
        print(f"玩家{p.GetCurrentPlayer().GetTag()}打出了{ColorizedOutput(OC)}")
        CardEffectEffector(p, OC, L, 1)
    else:
        ExpansionDecks(1)
        print("你当前已无牌可出,摸一张牌")
        rc = p.GetCurrentPlayer().DrawCards(1)
        if CardComplianceChecking(rc[0]):
            print(f"你摸到了{ColorizedOutput(rc[0])},是否打出(Y/N)")
            c = input()
            if c.upper() == 'N':
                return
            else:
                L = Card.GameState.PreviousCard
                p.GetCurrentPlayer().Out(rc[0])
                Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
                print(f"玩家{p.GetCurrentPlayer().GetTag()}打出了{ColorizedOutput(rc[0])}")
                CardEffectEffector(p, rc[0], L, 1)
        else:
            print(f"你摸到了{ColorizedOutput(rc[0])},但它并不能打出,请按回车确定")
            input()
    if len(p.GetCurrentPlayer().GetAllCards()) == 1:
        print(f"玩家{p.GetCurrentPlayer().GetTag()}喊出了{colorama.Back.RED}Uno!")
    elif len(p.GetCurrentPlayer().GetAllCards()) == 0:
        Card.GameState.Winner = p.GetCurrentPlayer()
        Card.GameState.GameProceeds = False
    print("="*15)

def init():
    '''初始化游戏各项参数'''
    Card.CardManager.RemoveAllCards()
    Card.CardManager.init()
    Card.GameState.CurrentColor = None
    Card.GameState.IncreaseStep = 1
    Card.GameState.PreviousCard = None
    Card.GameState.QuestionColor = None
    Card.GameState.GameProceeds = True
    Card.GameState.Winner = None
    Card.GameState.StartTime = 0
    Card.GameState.EndTime = 0
    Card.GameState.IsHaveThinkTime = True

def CountingPeople(n:int):
    '''计算是否要扩展牌'''
    pn = ceil((n * 7 * 1.3) / 108) # 公式来自 AI
    for i in range(pn-1):
        Card.CardManager.init()

def PrintRemainingNumberCards(p:Card.PlayerGroup):
    '''打印各玩家剩余牌数'''
    index = 0
    print(f"=====各玩家剩余牌数=====")
    for i in p.GetAllPlayers():
        if index % 2 == 0 and index != 0:
            print()
        print(f"{i.GetTag()}\t{len(i.GetAllCards())}\t", end="")
        i.RemoveAllCards()
        index += 1
    print()

def MainLoop():
    while True:
        '''游戏主循环'''
        print(f'{colorama.Back.BLUE}{'='*5}Uno{'='*5}')
        print(f'{colorama.Back.RED}S:开始\t{colorama.Back.RED}A斗蛐蛐模式\t{colorama.Back.RED}Q:退出')
        command = input()
        match command:
            case 'S':
                init()
                while True:
                    try:
                        print("自定义人数(默认4人)")
                        cin = input()
                        if cin:
                            if int(cin) >= 2:
                                CountingPeople(int(cin))
                                p = Card.PlayerGroup(int(cin))
                                break
                            else:
                                print(f"{colorama.Back.RED}最少2人")
                        else:
                            p = Card.PlayerGroup(4)
                            break
                    except ValueError:
                        print(f"{colorama.Back.RED}输入不合法")
                Card.GameState.PreviousCard = Card.CardManager.DrawYourHoleCards()
                Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
                print(f"底牌为{ColorizedOutput(Card.GameState.PreviousCard)}")
                Card.GameState.StartTime = time.time()
                while Card.GameState.GameProceeds:
                    if p.GetCurrentPlayer().GetTag() == p.GetPlayerName():
                        PlayerActionFlow(p)
                    else:
                        AiThinks(p)
                    p.GetNextPlayer()
                Card.GameState.EndTime = time.time()
                print(f"玩家{Card.GameState.Winner.GetTag()}赢了!")
                print(f"对局时长{Card.GameState.EndTime - Card.GameState.StartTime}sec.")
                PrintRemainingNumberCards(p)
                init()
            case 'A':
                init()
                while True:
                    try:
                        print("自定义人数(默认4人)")
                        cin = input()
                        if cin:
                            if int(cin) >= 2:
                                CountingPeople(int(cin))
                                p = Card.PlayerGroup(int(cin), 'AI-0')
                                print(len(Card.CardManager.GetAllCards()))
                                break
                            else:
                                print(f"{colorama.Back.RED}最少2人")
                        else:
                            p = Card.PlayerGroup(4, 'AI-0')
                            break
                    except ValueError:
                        print(f"{colorama.Back.RED}输入不合法")
                print(f"是否减少AI的思考时间(Y/N)")
                cin = input()
                if cin.upper() == 'N':
                    Card.GameState.IsHaveThinkTime = True
                else:
                    Card.GameState.IsHaveThinkTime = False
                Card.GameState.PreviousCard = Card.CardManager.DrawYourHoleCards()
                Card.GameState.CurrentColor = Card.GameState.PreviousCard.color
                print(f"底牌为{ColorizedOutput(Card.GameState.PreviousCard)}")
                Card.GameState.StartTime = time.time()
                while Card.GameState.GameProceeds:
                    AiThinks(p)
                    p.GetNextPlayer()
                Card.GameState.EndTime = time.time()
                print(f"玩家{Card.GameState.Winner.GetTag()}赢了!")
                print(f"对局时长{Card.GameState.EndTime - Card.GameState.StartTime}sec.")
                PrintRemainingNumberCards(p)
                init()
            case 'Q':
                break

if __name__ == '__main__':
    MainLoop()