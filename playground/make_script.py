import sys
import random
import ctypes
import os
import subprocess
import  scriptfs_util_userspace
syscall_num_scriptfs_pid = 333
syscall_num_scriptfs_state  =  334
syscall_num_scriptfs_context  = 335
libc = ctypes.CDLL(None)
syscall = libc.syscall
syscall(syscall_num_scriptfs_pid, os.getpid())
context_dir = {"poem": scriptfs_util_userspace.scriptfs_context.scriptfs_context_POEM.value,
                "short_novel": scriptfs_util_userspace.scriptfs_context.scriptfs_context_SHORT_NOVEL.value,
                "small_novel":scriptfs_util_userspace.scriptfs_context.scriptfs_context_SMALL_NOVEL.value,
                "medium_novel":scriptfs_util_userspace.scriptfs_context.scriptfs_context_MEDIUM_NOVEL.value,
                "large_novel":scriptfs_util_userspace.scriptfs_context.scriptfs_context_LARGE_NOVEL.value,
                 "super_novel":scriptfs_util_userspace.scriptfs_context.scriptfs_context_SUPER_NOVEL.value,
               "no_context":scriptfs_util_userspace.scriptfs_context.scriptfs_context_NO_CONTEXT.value }


state_dir = {"mount":scriptfs_util_userspace.scriptfs_state.scriptfs_state_MOUNT.value,
             "noop":scriptfs_util_userspace.scriptfs_state.scriptfs_state_NOOP.value,"read":scriptfs_util_userspace.scriptfs_state.scriptfs_state_READ.value,"write":scriptfs_util_userspace.scriptfs_state.scriptfs_state_WRITE.value}

#I know there are better ways to generate words(like reading from a giant file of words, which linux has).
#But I don't want to interact with the filesystem unless it is for our intent and purposes, because that will bring inaccuracies we don't want.

character_pool = ['a','b','c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
't', 'u', 'v', 'w', 'x', 'y', 'z' ]

def get_size(size):
    num_string =  ""
    start_size_label_index = 0
    for char in size:
        if char.isdigit():
            num_string += char
            start_size_label_index += 1
    return (int(num_string), size[start_size_label_index:] )


def get_random_word(min_size, max_size):
    """
    This functon generates a random word. The size of this new word
    is a random number between "min_size" and "max_size".
    """
    size =  random.randint(min_size,max_size)
    word  = ''
    for i in range(size):
        word += character_pool[random.randrange(0,len(character_pool))]
    return word

def open_and_zerofill_file(filepath, size, mode, fill_value = ' ' ):
    size_info = get_size(size)
    if(size_info[1].upper() == "MB"):
        size = size_info[0] * pow(2,20)
    elif size_info[1].upper() == "KB":
        size = size_info[0] * pow(2,10)
    f = open(filepath, mode)
    f.truncate(0)
    for i in range(size):
        f.write(fill_value.encode())
    return (f, size)

def random_writethrough(filepath, filesize, times_to_write):
    
    file_info = open_and_zerofill_file(filepath, filesize, 'w+b')
    f = file_info[0]
    size = file_info[1]
    for n in range(times_to_write):
        f.seek(random.randrange(size))
        print("seek location:", f.tell())
        f.write(get_random_word(0,1).encode())
    f.close()






def sequential_writethrough( filepath, size ):
    """
    This function will sequentially write to a file the amount specified by "size".
    For example if size were 32kb, this function will write 32kb worth of words to
    the end of the file. It does not matter whether the file exists or not.
    If the file exists, it will simply append the new contents to the end of the file.
    If the file does not exist, the function will create a new file at "filepath" and
    write the contents to that new file.
    The content of this file is randomly generated words by calling the function get_random_word.
    Since this is the writethrough function, it will call write(posix/python just probably write it
    somewhere in the buffercache) as soon as the random word is generated.
    """
    script_file  = open(filepath, 'a')
    size_info =  get_size(size)
    bytes_size = 0
    print("size_info:", size_info)
    print("size returned:", size_info[0])
    if size_info[1].upper() == "KB":
        print("KB match")
        bytes_size  = size_info[0] * pow(2,10)
        print("size after KB match:", bytes_size)
    elif size_info[1].upper() == "MB":
        bytes_size = size_info[0] * pow(2,20)
    elif size_info[1].upper() == "B":
        bytes_size = size_info[0]
    file_current_size = 0
    while file_current_size<bytes_size:
        word = get_random_word(3, 5)
        #print("file_current_size, bytes", file_current_size, bytes_size )
        while(file_current_size+len(word)>bytes_size):
            #print("while runnig")
            word = get_random_word(1,5)
        if(file_current_size+len(word)<bytes_size):
            script_file.write(word + " ")
            file_current_size += len(word + " ")
        else:
            script_file.write(word)
            file_current_size += len(word)
            #print("file_current_size:", file_current_size)
    script_file.close()


def generate_filename_list(original_name, number_of_names):
    new_names = []
    for number in range(number_of_names):
        new_names.append(original_name+"#"+str(number))
    return new_names

#def rand

if (len(sys.argv) < 7):
    print("USAGE: python3 ./make_script.py -c context_clue  size ./file_path\ mode cache_strategy\n For example:  python3 ./make_script.py -c 'poem' 20kb 'How Alice met Bob' seq wr_through  ")
    exit()

cache_strategy = sys.argv[10]
mode = sys.argv[9]
file_name = sys.argv[8]
size = sys.argv[7]
context = sys.argv[6]
scriptfs_state = sys.argv[4]
number_of_files = sys.argv[2]
print("working#1")
if(context in context_dir):
    return_val  = 0
    if( return_val != 0):
        print("return value from context syscall(failure code):",return_val)
        exit()
    else:
        print("looks like the context syscall did not fail. No promises. Be sure to check you dmesg dump\n")
else:
    print("Invalid context!\n Valid contexts:'poem', 'short_novel', 'medium_novel', 'large_novel', 'super_novel', 'no_context'\n") 
    exit()
if (syscall(syscall_num_scriptfs_state, state_dir[scriptfs_state]) == -1):
    print("It looks like the syscall to change state failed!")
    exit()
if(syscall(syscall_num_scriptfs_context, context_dir[context]) == -1):
    print("It looks like the sysall to change context failed!")
    exit()

#exit()
#if len(sys.argv)>5:
    #times_to_write = sys.argv[5]
if(int(number_of_files)>0):    
    files_list =  generate_filename_list(file_name, int(number_of_files))
else:
    files_list = [file_name]
if mode == "seq" and cache_strategy=="wr_through":
    for file in files_list:
        sequential_writethrough(file, size)

elif mode == "rand" and cache_strategy=="wr_through":
    random_writethrough(file_name, size,int(times_to_write) )

if (syscall(syscall_num_scriptfs_state, state_dir["noop"]) == -1):
    print("It looks like the syscall to change state failed!")
