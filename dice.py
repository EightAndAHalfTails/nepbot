from random import randint

class RollResult:
    def __init__(self, rollstr:str, result:int):
        self.rollstr = rollstr
        self.result = result

    def __str__(self):
        return "{0.result} ({0.rollstr})".format(self)

    def isError(self):
        return self.result is None

def roll(sides:int, times:int=1):
    try:
        rolls = [randint(1, sides) for t in range(times)]
    except ValueError:
        raise Exception("There's no die like that!")
    num = sum(rolls)
    log = " + ".join("({})".format(r) for r in rolls)
    return RollResult(rollstr=log, result=num)

def parse(dicestr:str) -> RollResult:
    tmpstr = dicestr.lower()
    if '(' in tmpstr:
        if ')' not in tmpstr:
            raise Exception("Your brackets don't match up!")
        inbrac = parse(tmpstr[tmpstr.find('(')+1 : tmpstr.rfind(')')])
        whole  = parse(tmpstr[:tmpstr.find('(')] + str(inbrac.result) + tmpstr[tmpstr.rfind(')')+1:])
        whole.rollstr = tmpstr[:tmpstr.find('(')] + inbrac.rollstr + tmpstr[tmpstr.rfind(')')+1:]
        return whole
    if '+' in tmpstr:
        left = tmpstr[:tmpstr.find('+')]
        right = tmpstr[tmpstr.find('+')+1:]

        lres = parse(left)
        rres = parse(right)

        if lres.isError() or rres.isError():
            raise Exception
        
        result = lres.result + rres.result
                    
        # '2d6 + 10 + 1 + 2' -> '(3 + 4) + 13'
        try:
            resstr = str( int(lres.rollstr) + int(rres.rollstr) )
        except ValueError:
            resstr = "{0.rollstr} + {1.rollstr}".format(lres, rres)
        return RollResult(resstr, result)
    if '-' in tmpstr:
        left = tmpstr[:tmpstr.find('-')]
        right = tmpstr[tmpstr.find('-')+1:]

        lres = parse(left)
        rres = parse(right)
        
        if lres.isError() or rres.isError():
            raise Exception
        
        result = lres.result - rres.result
        try:
            resstr = str( int(lres.rollstr) - int(rres.rollstr) )
        except ValueError:
            resstr = "{0.rollstr} - {1.rollstr}".format(lres, rres)
        return RollResult(resstr, result)
    # if '*' in tmpstr:
    #     tmpstr = str(self.parse(tmpstr[:tmpstr.find('*')]) * self.parse(tmpstr[tmpstr.find('*')+1:]))
    # if 'x' in tmpstr:
    #     tmpstr = str(self.parse(tmpstr[:tmpstr.find('x')]) * self.parse(tmpstr[tmpstr.find('x')+1:]))
    # rollstr = tmpstr
    if 'd' in tmpstr:
        times = parse(tmpstr[:tmpstr.find('d')]).result
        if times is None:
            times = 1
        sides = parse(tmpstr[tmpstr.find('d')+1:]).result
        result = roll(times=times, sides=sides)
        return result
    try:
        result = RollResult(tmpstr, int(tmpstr))
        return result
    except ValueError:
        result = RollResult("Error", None)
        return result
