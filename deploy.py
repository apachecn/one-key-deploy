import subprocess as subp
import json
import psutil
import shutil
import os
from os import path
import jinja2

DOCKER_NGINX_LOG = '/var/log/nginx'
DOCKER_NGINX_CONF = '/etc/nginx/conf.d'
DOCKER_NGINX_RSRC = '/usr/share/nginx/html'

def d(name):
    return path.join(path.dirname(__file__), name)

def get_docker_containers():
    r = subp.Popen(
        'docker ps -a --format "{{.ID}}----{{.Ports}}----{{.Status}}----{{.Names}}"',
        stdout=subp.PIPE,
        stderr=subp.PIPE,
        shell=True,
    ).communicate()[0].decode('utf-8')
    res = []
    for line in r.split('\n'):
        tmp = line.split('----')
        if len(tmp) != 4: continue
        res.append({
            'ID': tmp[0],
            'Ports': tmp[1],
            'Status': tmp[2],
            'Names': tmp[3],
        })
    return res

def kill_port(port):
    netstats = psutil.net_connections('tcp')
    for n in netstats:
        if  n.laddr.port == port and \
            n.status == 'LISTEN':
            os.kill(n.pid, 9)
            print(f'KILL PID: {n.pid}')
    containers = get_docker_containers()
    for c in containers:
        if f':{port}->' in c['Ports']:
            subp.Popen(f'docker rm -f {c["ID"]}', shell=True)
            print(f'KILL CONTAINER: {c["ID"]}')

def mkdirs_safe(dir):
    if not path.exists(dir):
        os.makedirs(dir)

def main():
    config = json.loads(
        open(d('docs.json'), encoding='utf-8').read())
        
    # 创建网桥
    network = config["network"]
    subp.Popen(
        f'docker network create -d bridge {network}', 
        shell=True,
    ).communicate()
    
    # 启动文档容器
    for doc in config['docs']:
        if 'name' not in doc or \
           'repo' not in doc:
           continue
        
        name, repo = doc['name'], doc['repo']
        print(f'name: {name}, repo: {repo}')
        
        subp.Popen(f'docker rm -f {name}', shell=True).communicate()
        subp.Popen(f'docker pull {repo}', shell=True).communicate()
        subp.Popen(
            f'docker run -tid --name {name} --network {network} {repo}', 
            shell=True,
        ).communicate()
    
    # 释放配置文件
    data_dir = config['dataDir']
    mkdirs_safe(data_dir)
    conf_dir = path.join(data_dir, 'conf')
    mkdirs_safe(conf_dir)
    rsrc_dir = path.join(data_dir, 'html')
    mkdirs_safe(rsrc_dir)
    log_dir = path.join(data_dir, 'log')
    mkdirs_safe(log_dir)
    
    shutil.copy(
        d('asset/index.html'),
        path.join(rsrc_dir, 'index.html'),
    )
    shutil.copy(
        d('asset/50x.html'),
        path.join(rsrc_dir, '50x.html'),
    )
    conf_tmpl = open(d('asset/default.conf.j2'), encoding='utf-8').read()
    conf = jinja2.Template(conf_tmpl).render(docs=config['docs'])
    open(path.join(conf_dir, 'default.conf'), 'w', encoding='utf-8').write(conf)
    
    # 启动 Nginx
    name, port = config['name'], config['port']
    print(f'name: {name}, repo: nginx, port: {port}')
    kill_port(port)
    subp.Popen(f'docker rm -f {name}', shell=True).communicate()
    subp.Popen(f'docker pull nginx', shell=True).communicate()
    args = '\x20'.join([
        # 后台运行
        'docker run -tid',
        # 设置容器名称
        f'--name {name}',
        # 绑定端口
        f'-p {port}:80',
        # 绑定配置、资源和日志目录
        f'-v "{conf_dir}:{DOCKER_NGINX_CONF}"',
        f'-v "{rsrc_dir}:{DOCKER_NGINX_RSRC}"',
        f'-v "{log_dir}:{DOCKER_NGINX_LOG}"',
        # 设置网桥
        f'--network {network}',
        # 镜像名称
        'nginx',
    ])
    subp.Popen(args, shell=True).communicate()
    
if __name__ == '__main__': main()