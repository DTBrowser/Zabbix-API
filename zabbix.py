# Script By DTBrowser (Yan Dias)
# Run with Python 3
import json,sys,requests
import pandas as pd


def pegar_chave(alvo, usuario, senha):
        header = {"jsonrpc": "2.0", "method": "user.login", "params": {"user": usuario, "password": senha},"id": 0}
        chave = requests.post('http://'+alvo+'/zabbix/api_jsonrpc.php', json = header).json()['result']
        return chave

def pegar_hosts(chave, alvo):
        header = {"jsonrpc": "2.0", "method": "host.get", "params": {'output': ['hostid', 'host', 'status']}, 'auth': chave,"id": 1}
        resultado = requests.post('http://'+alvo+'/zabbix/api_jsonrpc.php', json = header).json()['result']
        return resultado

def pegar_array(chave, alvo):
        array = []
        header = {"jsonrpc": "2.0", "method": "host.get", "params": {'output': 'hostid'}, 'auth': chave,"id": 1}
        resultado = requests.post('http://'+alvo+'/zabbix/api_jsonrpc.php', json = header).json()['result']
        for i in resultado:
                array.append(i['hostid'])
        return array

def pegar_interfaces(chave, alvo, array):
        header = {"jsonrpc": "2.0", "method": "hostinterface.get", "params": {'hostids': array}, 'auth': chave,"id": 1}
        resultado = requests.post('http://'+alvo+'/zabbix/api_jsonrpc.php', json = header).json()['result']
        return resultado

def merge_dicionario(pegar_interfaces, pegar_hosts):
        chave_ip = {}
        for p in pegar_interfaces:
                chave_ip.update({p['hostid']:p['ip']})
        dicionario_final = {}
        coluna_id = []
        coluna_nome = []
        coluna_status = []
        temp_status = []
        coluna_ip = []

        for i in pegar_hosts:
                coluna_id.append(i['hostid'])
                coluna_nome.append(i['host'])
                temp_status.append(i['status'])

        for z in temp_status:
                if z == '1':
                        coluna_status.append('False')
                else:
                        coluna_status.append('True')

        for n in coluna_id:
                coluna_ip.append(chave_ip[n])
        dicionario_final.update({'id':coluna_id})
        dicionario_final.update({'nome':coluna_nome})
        dicionario_final.update({'status':coluna_status})
        dicionario_final.update({'ip':coluna_ip})

        return dicionario_final

def relatorio_excel(merge_dicionario):
        merge_dicionario = pd.DataFrame(merge_dicionario)
        documento = pd.ExcelWriter('relatorio.xlsx', engine='xlsxwriter')
        merge_dicionario.to_excel(documento, sheet_name='Relatorio')
        documento.save()



if len(sys.argv) < 3:
        print("Script by DTBrowser: Yan Dias")
        print("-> Parâmetros insuficientes")
        print("-> Uso: python3 zabbix.py <usuario> <senha> <ip>")
else:
        usuario = sys.argv[1]
        senha = sys.argv[2]
        alvo = sys.argv[3]

        try:
                chave = pegar_chave(alvo, usuario, senha)
                array = pegar_array(chave, alvo)
                resultado = merge_dicionario(pegar_interfaces(chave, alvo, array), pegar_hosts(chave, alvo))
                relatorio_excel(resultado)
                print("Script by DTBrowser: Yan Dias")
                print("-> Relatorio salvo: relatorio.xlsx")
        except Exception as err:
                print("Script by DTBrowser: Yan Dias")
                print("-> Erro ao tentar pegar as chaves ou em outra funcao")
                print(err)
