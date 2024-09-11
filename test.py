import multiprocessing

def main():
    manager = multiprocessing.Manager()
    dictionary = manager.dict()

    dictionary["jim"] = {'x': 1, 'y': 2, 'z' : 3}

    print(dictionary['jim'])

    dictionary['jim']['x'] += 1

    print(dictionary['jim'])

if __name__ == '__main__':
    main()