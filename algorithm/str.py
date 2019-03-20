def contain(str_a,str_b):
    hash = 0
    for a in str_a:
        hash |= (1 << (ord(a) - ord('A')))
    for b in str_b:
        if (hash & (1 << (ord(b) - ord('A')))) == 0:
            return False
    return True

if __name__ == '__main__':
    print(contain('AEBDC','DE'))