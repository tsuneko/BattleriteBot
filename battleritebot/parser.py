import os

def read(filepath):
    try:
        f = open(filepath, "r")
    except FileNotFoundError:
        raise FileNotFoundError
    data = {}
    for line in f.readlines():
        line = line.rstrip()
        if '=' in line:
            tokens = line.split('=')
            tokens[0] = tokens[0].strip()
            tokens[1] = tokens[1].strip()
            if tokens[1].startswith('[') and tokens[1].endswith(']'):
                tokens[1] = tokens[1][1:-1]
                if len(tokens[1]) == 0:
                    data[tokens[0]] = []
                else:
                    data[tokens[0]] = tokens[1].split(',')
            else:
                data[tokens[0]] = tokens[1]
    f.close()
    return data

def write(filepath, data):
    try:
        f = open(filepath, "w")
    except FileNotFoundError:
        raise FileNotFoundError
    for key in data:
        if type(data[key]) == str:
            f.write(key + "=" + data[key] + "\n")
        elif type(data[key]) == int or type(data[key]) == bool:
            f.write(key + "=" + str(data[key])  + "\n")
        elif type(data[key]) == list:
            f.write(key + "= [" + ",".join(data[key]) + "]\n")
    f.close()

def write_raw(filepath, string):
    try:
        f = open(filepath, "w")
    except FileNotFoundError:
        raise FileNotFoundError
    f.write(string)
    f.close()

def list(filepath):
	try:
		files = os.listdir(filepath)
		return files
	except FileNotFoundError:
		raise FileNotFoundError
