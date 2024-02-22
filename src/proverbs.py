

proverb_len = (400 - (8 * 2)) // 8

def split_proverb(proverb):
    words = proverb.split(' ')
    paragraph = [words[0], ] 
    for word in words[1:]:
        if (len(paragraph[-1]) + len(word) + 1) <= proverb_len:
            paragraph[-1] = ' '.join([paragraph[-1], word])
        else:
            paragraph.append('  ' + word)
    return paragraph

