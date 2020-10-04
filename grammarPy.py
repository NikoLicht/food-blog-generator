class Grammar:
    def __init__(self, *args, **kwargs):
        pass

    def list_items(self, listWords):
        result = ""
        words = list(listWords)
        end = ""
        if (len(words) > 1):
            end = " and " + words.pop()

        for word in words:
            result += word + ", "

        result = result [:-2] + end
        return result

    def past_tense(self, word):
        result = word
        if word.endswith('e'):
            result += 'd'
        elif word.endswith('y'):
            result = word[:-1] + "ied"
        elif word.endswith('r'):
            result = word + "red"
        elif word == "raw":
            reuslt = word
        else:
            result += "ed"

        return result

    def ing(self, word):
        if word.endswith('e'):
            return word[:-1] + "ing"
        return word + "ing"

