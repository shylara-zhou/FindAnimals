SENSITIVE_WORDS = [
    '共产党', '政府', '习近平', '毛泽东', '邓小平',
    '色情', '黄色', '裸体', '性交', '做爱',
    '杀人', '自杀', '炸弹', '恐怖', '爆炸',
    '傻逼', '操你', '草你', '你妈', '他妈', '妈的',
]


def find_sensitive_word(text):
    if not text:
        return None
    for w in SENSITIVE_WORDS:
        if w and w in text:
            return w
    return None
