from enum import Enum
import colorama

class Color(Enum):
    Red = 0
    Green = 1
    Yellow = 2
    Blue = 3
    Tool = 4 # 适用与没颜色的卡牌

class Type(Enum):
    ToggleColor = 0
    Torsion = 1
    NextPersonAdds_2 = 2
    NextPersonAdds_4 = 3
    ForbidNextPerson = 4
    Number = 5
    Occupancy = 6

CompareVocabulary = {
	Type.Torsion: '倒转',
	Type.ToggleColor: '切换颜色',
	Type.ForbidNextPerson: '禁止下一人',
	Type.NextPersonAdds_2: '加2',
	Type.NextPersonAdds_4: '加4',
    Type.Occupancy: ''
}
ColorComparisonTable = {
    Color.Blue: f'{colorama.Back.BLUE}蓝色',
    Color.Green: f'{colorama.Back.GREEN}绿色',
    Color.Red: f'{colorama.Back.RED}红色',
    Color.Yellow: f'{colorama.Back.YELLOW}黄色'
}
