# ******************************************************************************
# *            Copyright (c) 2021 CSS518, chenhao<2411889319@qq.com>           *
# *                                                                            *
# *    Permission is hereby granted, free of charge, to any person obtaining   *
# *    a copy of this software and associated documentation files (the         *
# *    "Software"), to deal in the Software without restriction, including     *
# *    without limitation the rights to use, copy, modify, merge, publish,     *
# *    distribute, sublicense, and/or sell copies of the Software, and to      *
# *    permit persons to whom the Software is furnished to do so, subject to   *
# *    the following conditions:                                               *
# *                                                                            *
# *    The above copyright notice and this permission notice shall be          *
# *    included in all copies or substantial portions of the Software.         *
# *                                                                            *
# *    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,         *
# *    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF      *
# *    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND                   *
# *    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE  *
# *    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION  *
# *    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION   *
# *    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.         *
# ******************************************************************************


import os
import time
import re
from db import docker_name_to_student_name, student_id_to_name
"""
docker_name_to_student_name和student_no_to_name都是dict
分别存容器名到学生姓名的映射 学号到姓名的映射
docker_name_to_student_name = {
    'zhangsan': '张三',
}
student_id_to_name = {
    '1947xxxx': '张三'
}
"""


# 输出HTML头
def print_html_header():
    print("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GPU使用情况</title>
</head>
<body>
<main style="">
<h1>CSS518高性能工作站使用情况概览</h1>
注意：数据每5分钟更新一次    
<pre>
    """, file=f)

# 输出HTML尾
def print_html_footer():
    print("""
</pre>
</main>
</body>
</html>
    """, file=f)


def checknumber(s):
    for c in s:
        if '0' > s or s > '9':
            return False
    return True


# TODO: 优化，这个统计太慢了
def print_html_memory_usage():
    # 检查是否为全数字
    print('+--------------------------------------------------------+', file=f)
    print('|   student id              姓名              disk used  |', file=f)
    # 每个学生的数据都是放在以学号命名的文件夹下
    directory = os.listdir()
    for dir in directory:
        if checknumber(dir):
            sstr = os.popen(f" du -h --max-depth=0 ./{dir}").read()
            sstr = re.findall(r'(.*?)\s+\./.*?', sstr)
            disk_used = sstr[0]
            if dir in student_id_to_name.keys():
                student_name = student_id_to_name[dir]
            else:
                student_name = 'Unknown'
            print(f'| {dir:>12}              {student_name:<11}{disk_used:>14}    |', file=f)
    print('+--------------------------------------------------------+', file=f)


def show_nvidia_smi():
    process_id = os.popen(r"nvidia-smi")
    output = process_id.read()
    print(output, file=f)

# 显示谁在用GPU，是了哪几个GPU
def show_gpu_usage():
    process_id = os.popen(r"nvidia-smi | grep -A 25 ========================================| awk '{print $3}'")
    process_id = process_id.read()
    process_id = process_id.strip().split()

    gpu_id = os.popen(r"nvidia-smi | grep -A 25 ========================================| awk '{print $2}'")
    gpu_id = gpu_id.read()
    gpu_id = gpu_id.strip().split()

    container_names = os.popen(r"docker ps | grep Up|awk '{print $NF}'")
    container_names = container_names.read()
    container_names = container_names.strip().split()
    # print(process_id,gpu_id,container_names)
    for name in container_names:
        for gpu, pid in zip(gpu_id, process_id):
            s = os.popen("docker top " + name + " | grep " + pid)
            s = s.read()
            if s != '':
                if name in docker_name_to_student_name:
                    student_name = docker_name_to_student_name[name]
                else:
                    student_name = f'unknown real name, docker name is {name}'
                print(f"{{{gpu}}}	{pid}--------->{student_name}", file=f)
            # pri=os.popen("if [ -n \"{}\" ];then echo \"{{{}}}      {}------->{}\";fi".format(s,gpu,pid,name))
            # print(pri.read())

    # s=`docker top ${i} | grep ${j}`; if [ -n "${s}" ];
    # then echo $j"------->"$i &&echo ${s}


if __name__ == '__main__':
    while True:
        with open('/notedata/gpus.html', 'w') as f:
            print_html_header()
            show_nvidia_smi()
            show_gpu_usage()
            print_html_memory_usage()
            print_html_footer()
        print('sleep')
        # 每5分钟跑一次
        time.sleep(60 * 5)