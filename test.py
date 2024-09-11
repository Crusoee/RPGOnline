import multiprocessing

def main():
    manager = multiprocessing.Manager()
    shared_dictionary_1 = manager.dict()
    shared_dictionary_2 = manager.dict()

    shared_dictionary_1 = {'ip1' : {'x': 1}, 'ip2' : {'x': 2}, 'ip3' : {'x': 3}}
    shared_dictionary_2 = {'ip1' : {'a': 1}, 'ip2' : {'a': 2}, 'ip3' : {'a': 3}}

    dictionary1 = dict(shared_dictionary_1)
    dictionary2 = dict(shared_dictionary_2)

    for key, value in dictionary1.items():
        dictionary1[key].update(dictionary2[key])

    print(dictionary1)

if __name__ == '__main__':
    main()