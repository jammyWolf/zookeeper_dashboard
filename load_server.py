#encoding: utf-8
import os

def readFile(file_path):
    fp = open(file_path, 'rb')
    file_content = fp.readlines()
    fp.close()
    one_line_str = ""
    for each in file_content:
        one_line_str += each.strip('/\n') + ','
    one_line_str = one_line_str[:-1]
    return one_line_str

def writeFile(filepath, content):
    fp = open(filepath, 'wb+')
    fp.write(content)
    fp.close()

def listDir(file_dir, suffix):
    dir_list = os.listdir(file_dir)
    file_list = []
    for i in range(0, len(dir_list)):
        path = os.path.join(file_dir, dir_list[i])
        if os.path.isfile(path) and os.path.splitext(path)[-1] == suffix:
            file_list.append(path)
    for each in file_list:
        str = os.path.basename(each) + ' = ' + readFile(each) + '\n'
    writeFile('./conf/servers.py', str)
    
def main():
    listDir('conf', '.cfg')

if __name__ == '__main__':
    main()
